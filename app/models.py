from sqlalchemy import Column, Integer, String, ForeignKey, Uuid, Boolean
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class Users(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    public_id = Column(Uuid)
    name = Column(String(50))
    password = Column(String(250))
    admin = Column(Boolean)

