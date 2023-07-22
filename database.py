from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#sqlalchemy_database_url='postgresql://<username>:<password>@<ip-address/hostname>'
sqlalchemy_database_url=f'postgresql://postgres:password123@localhost/fastapi'

engine=create_engine(sqlalchemy_database_url)

Sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()