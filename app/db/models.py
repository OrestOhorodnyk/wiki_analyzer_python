from sqlalchemy import Column, String, TIMESTAMP, BOOLEAN, NUMERIC
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.db.database import Base


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
