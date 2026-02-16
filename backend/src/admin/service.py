from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, Date
from src.shopping.models import Order, OrderItem
from src.products.models import Product
from src.shopping.constants import OrderStatus

def get_admin_dashboard_stats(db: Session):
    stats = db.query(
        func.sum(Order.total_amount).label("total_revenue"),
        func.avg(Order.total_amount).label("aov"),
        func.count(Order.id).label("order_count")
    ).filter(Order.status.in_([OrderStatus.paid, OrderStatus.completed])).first()

    total_revenue = float(stats.total_revenue or 0)
    aov = float(stats.aov or 0)

    revenue_history = db.query(
        cast(Order.created_at, Date).label("day"),
        func.sum(Order.total_amount).label("daily_sum")
    ).filter(Order.status.in_([OrderStatus.paid, OrderStatus.completed])) \
     .group_by("day") \
     .order_by("day") \
     .all()

    revenue_chart = [
        {"date": str(row.day), "amount": float(row.daily_sum)} 
        for row in revenue_history
    ]

    profitable_products = db.query(
        OrderItem.product_name_snapshot.label("name"),
        func.sum(OrderItem.price * OrderItem.quantity).label("profit")
    ).join(Order).filter(Order.status.in_([OrderStatus.paid, OrderStatus.completed])) \
     .group_by(OrderItem.product_name_snapshot) \
     .order_by(desc("profit")) \
     .limit(5).all()

    top_products = [
        {"name": row.name, "profit": float(row.profit)} 
        for row in profitable_products
    ]

    conversion_stats = db.query(
        Product.name,
        Product.views,
        func.sum(OrderItem.quantity).label("sold_qty")
    ).join(OrderItem, Product.id == OrderItem.product_id) \
     .join(Order, Order.id == OrderItem.order_id) \
     .filter(Order.status.in_([OrderStatus.paid, OrderStatus.completed])) \
     .group_by(Product.id) \
     .all()

    conversions = []
    for row in conversion_stats:
        views = row.views or 0
        sold = int(row.sold_qty or 0)
        rate = (sold / views * 100) if views > 0 else 0
        conversions.append({
            "name": row.name,
            "views": views,
            "sold_quantity": sold,
            "conversion_rate": round(rate, 2)
        })

    return {
        "total_revenue": total_revenue,
        "average_order_value": round(aov, 2),
        "revenue_chart": revenue_chart,
        "top_profitable_products": top_products,
        "product_conversions": conversions
    }