from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def init(app):
    global db
    global secret
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    secret =  app.config['SECRET_KEY']
    print("Initialized")
