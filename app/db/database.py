from sqlalchemy import create_engine , Column , String 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 

# MySQL Database URL 

DATABASE_URL  = "mysql+pymysql://root:root@localhost/schema_db"

# Create database connection 
engine = create_engine(DATABASE_URL)
SessionLocal  = sessionmaker(autocommit = False , autoflush= False , bind = engine)
Base  = declarative_base ()

def get_db():
    db  = SessionLocal ()
    try:
        yield db
    finally:
        db.close ()