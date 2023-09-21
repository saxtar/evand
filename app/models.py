from sqlalchemy import Column, Integer, String, ForeignKey, Uuid, Boolean
from sqlalchemy.orm import declarative_base, relationship
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

base = declarative_base()

class Users(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    public_id = Column(Uuid)
    email = Column(String(50))
    password = Column(String(250))
    admin = Column(Boolean, default=False)
    image = Column(String(1000))
    banner = Column(String(1000))
    desc = Column(String(250)) 
    phone = Column(String(250)) 

class Categories(base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
#    events = relationship('Events', secondary='event_category', backref='event_categories')

class Events(base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    desc = Column(String(10000))
    banner = Column(String(1000))
    location = Column(String(1000))
    tags = Column(String(250))
    start_date = Column(String(250))
    end_date = Column(String(250))
    city = Column(String(250))
    event_type = Column(String(250))
    author_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    categories = relationship('Categories', secondary='event_category', backref='category_events')
    tickets = relationship('Tickets', backref='events') 


class Tickets(base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    remaining = Column(Integer, nullable=False)
    date = Column(String(250))
    desc = Column(String(250))
    event_id = Column(
        Integer,
        ForeignKey('events.id', ondelete='CASCADE'),
        nullable=False,
    )

class EventCategory(base):
    __tablename__ = 'event_category'
    id = Column(Integer, primary_key=True)
    event_id = Column(
        Integer,
        ForeignKey('events.id', ondelete='CASCADE'),
        nullable=False,
    )
    category_id = Column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=False,
    )


class Purchases(base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    buyer_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    ticket_id = Column(
        Integer,
        ForeignKey('tickets.id', ondelete='CASCADE'),
        nullable=False,
    )
    is_paid = Column(Boolean, default=False) 


class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
