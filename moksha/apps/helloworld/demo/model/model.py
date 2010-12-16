from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, Column
from demo.model import DeclarativeBase

class HelloWorldModel(DeclarativeBase):
    __tablename__ = 'helloworld'

    id = Column(Integer, autoincrement=True, primary_key=True)

    message = Column(Text)

    timestamp = Column(DateTime, default=datetime.now)
