from random import randint
from uuid import uuid4

from sqlalchemy import Column, String, TIMESTAMP, BOOLEAN, NUMERIC, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


def get_year(context):
    ts = context.get_current_parameters()['timestamp']
    if ts:
        return randint(2000, ts.year)


def get_month(context):
    ts = context.get_current_parameters()['timestamp']
    if ts:
        return randint(ts.month, 12)


def get_day(context):
    ts = context.get_current_parameters()['timestamp']
    if ts:
        return randint(ts.day, 30)


class UserContributes(Base):
    __tablename__ = "users_contributes"

    id_sk = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    id = Column(NUMERIC, nullable=True, index=False)
    type = Column(String, nullable=True, unique=False, index=False)
    namespace = Column(String, nullable=True, unique=False, index=False)
    title = Column(String, nullable=True, unique=False, index=False)
    comment = Column(String, nullable=True, unique=False, index=False)
    timestamp = Column(TIMESTAMP, nullable=True, unique=False, index=False)
    user = Column(String, nullable=True, unique=False, index=True)
    bot = Column(BOOLEAN, nullable=True, unique=False, index=False)
    minor = Column(BOOLEAN, unique=False, index=False)
    # timestamp parsed to year, month, day
    year = Column(Integer, nullable=True, unique=False, default=get_year)
    month = Column(Integer, nullable=True, unique=False, default=get_month)
    day = Column(Integer, nullable=True, unique=False, default=get_day)

    def __repr__(self):
        return str({
            "id_sk": self.id_sk,
            "id": self.id,
            "type": self.type,
            "namespace": self.namespace,
            "title": self.title,
            "comment": self.comment,
            "timestamp": self.timestamp,
            "user": self.user,
            "bot": self.bot,
            "minor": self.minor,
            "year": self.year,
            "month": self.month,
            "day": self.day,
        })

    def get_user_info(self):
        return {
            "user": self.user,
        }


class UserContributeByTitle(Base):
    __tablename__ = "users_contribute_by_title"

    user = Column(String, primary_key=True)
    title = Column(String, primary_key=True)
    count = Column(Integer, nullable=True, unique=False)


class ArticleTitleCount(Base):
    __tablename__ = "article_title_count"

    title = Column(String, primary_key=True)
    count = Column(Integer, nullable=True, unique=False)
