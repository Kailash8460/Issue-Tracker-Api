from sqlalchemy import CheckConstraint, Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    mobile_number = Column(String(10), nullable=True)
    password_hash = Column(String, nullable=False)
    issues = relationship("Issue", back_populates="assignee")
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "LENGTH(mobile_number) = 10", name="mobile_number_length_check"
        ),
    )
