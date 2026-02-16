from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import logging
from contextlib import asynccontextmanager
from src.shopping.service import cancel_pending_orders
from src.users.router import router as userRouter
from src.products.router import router as productRouter
from src.shopping.router import router as shoppingRouter
from src.logistics.router import router as logisticsRouter
from src.furgonetka.router import router as furgonetkaRouter
from src.admin.router import router as adminRouter
from src.email.router import router as emailRouter
from src.database import engine, Base, SessionLocal
from src.email.service import delete_too_old

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_periodic_tasks(time: int):
  while True:
    db = SessionLocal()
    try:
      cancel_pending_orders(db, time)
      delete_too_old(db, time)
    except Exception as e:
      logger.error(f"Error in periodical tasks: {e}")
    finally:
      db.close()
      
    await asyncio.sleep(time)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
  task = asyncio.create_task(run_periodic_tasks(1200))
  
  yield
  
  task.cancel()

Base.metadata.create_all(bind=engine)
app = FastAPI(lifespan=lifespan, title="E-commerce app")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=userRouter)
app.include_router(router=productRouter)
app.include_router(router=shoppingRouter)
app.include_router(router=logisticsRouter)
app.include_router(router=furgonetkaRouter)
app.include_router(router=emailRouter)
app.include_router(router=adminRouter)
