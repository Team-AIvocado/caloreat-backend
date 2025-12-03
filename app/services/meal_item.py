from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    JSON,
    ForeignKey,
    DateTime,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class XModel(Base):
    __tablename__ = "x_table"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False, nullable=True)
    field1 = Column(String)
    field2 = Column(BigInteger, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
