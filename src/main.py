from fastapi import FastAPI
from src.users.router import router as userRouter
from src.products.router import router as productRouter
from src.shopping.router import router as shoppingRouter
from src.database import engine, Base
import src.shopping.models
import src.products.models
import src.logistics.models
import src.users.models

Base.metadata.create_all(bind=engine)
app = FastAPI(title="E-commerce app")

app.include_router(router=userRouter)
app.include_router(router=productRouter)
app.include_router(router=shoppingRouter)
