from sqlalchemy import Column, Integer, String, ForeignKey, Uuid, Boolean
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class Users(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    public_id = Column(Uuid)
    name = Column(String(50))
    password = Column(String(250))
    admin = Column(Boolean, default=False)

class Events(base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    author_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    price = Column(Integer, nullable=False)

class Tickets(base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    buyer_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    event_id = Column(
        Integer,
        ForeignKey('events.id', ondelete='CASCADE'),
        nullable=False,
    )
    is_paid = Column(Boolean, default=False) 


