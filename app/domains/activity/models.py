from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base

# Ассоциативная таблица для связи многие-ко-многим между activities и organizations.
activity_organizations = Table(
    "activity_organizations",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
    Column("organization_id", Integer, ForeignKey("organizations.id"), primary_key=True)
)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)

    # Self-referencing relationship: an activity can have many child activities.
    children = relationship(
        "Activity",
        backref="parent",
        remote_side=[id]
    )

    # Добавляем связь "organizations" (многие-ко-многим) с моделью Organization.
    organizations = relationship(
        "Organization",
        secondary=activity_organizations,
        back_populates="activities"
    )
