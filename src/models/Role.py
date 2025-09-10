from sqlalchemy import Table, Column, Integer, ForeignKey, String, PrimaryKeyConstraint  # Import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from config import Base  # Ensure this Base is consistently imported from your database setup

# Association table for many-to-many relationship between User and Role
user_roles_association = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),  # Correct: matches User's __tablename__
    Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE')),  # Correct: matches Role's __tablename__
    PrimaryKeyConstraint('user_id', 'role_id')  # Add composite primary key
)


class Role(Base):
    __tablename__ = "role"  # Keep as "role" as per your existing design
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # e.g., "admin", "doctor", "patient"

    # Define relationship to User via the association table
    # IMPORTANT: back_populates must match the attribute name in the User model
    users = relationship(
        "User",  # Referring to the User model class
        secondary=user_roles_association,
        back_populates="roles",  # Changed from "role" to "roles" to match User model
        collection_class=set  # Use a set for efficient lookup and uniqueness
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
