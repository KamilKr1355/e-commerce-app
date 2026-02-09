from sqlalchemy import Column, String, Integer
from src.database import Base

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String)