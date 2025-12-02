from sqlalchemy import Column, BigInteger, String, ForeignKeyConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# --- Meal ---
# Meal Images
class MealImage(Base):
    __tablename__ = "x_table"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=False, nullable=False)
    field1 = Column(String)
    field2 = Column(BigInteger, nullable=True)

    # TODO: relationship

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


# class MealImage(Base):
#     __tablename__ = "x_table"

#     id = Column(BigInteger, primary_key=True)
#     user_id = Column(BigInteger, unique=False, nullable=False)
#     field1 = Column(String)
#     field2 = Column(BigInteger, nullable=True)

#     __table_args__ = (
#         ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
#     )

# class MealImage(Base):
#     __tablename__ = "x_table"

#     id = Column(BigInteger, primary_key=True)
#     user_id = Column(BigInteger, unique=False, nullable=False)
#     field1 = Column(String)
#     field2 = Column(BigInteger, nullable=True)

#     __table_args__ = (
#         ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
#     )
