from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import boto3, botocore


def init(app):
    global db
    global secret
    global s3
    global s3_bucket
    global purchase_api_key
    global host_url
    s3 = boto3.client(
        "s3",
        endpoint_url=app.config['S3_EP'],
        aws_access_key_id=app.config['S3_KEY'],
        aws_secret_access_key=app.config['S3_SECRET']
    )
    s3_bucket = app.config['S3_BUCKET']
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
    secret =  app.config['SECRET_KEY']
    purchase_api_key = app.config['PURCHASE_API_KEY']
    host_url = app.config['HOST_URL']
    print("Initialized")

