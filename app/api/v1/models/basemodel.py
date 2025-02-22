from sqlalchemy import Column, DateTime, Boolean, UUID, Integer, Table, ForeignKey, String
from uuid import uuid4
from datetime import datetime
from app.api.v1.db import db  # Assuming db is your DB utility module
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from app.api.v1.db.db_conn import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

lecturer_course_association = Table(
    'lecturer_course_association',
    Base.metadata,
    Column('lecturer_id', Integer, ForeignKey('lecturers.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)
student_course_association = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)
class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, default=None)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    async def new(cls, session: AsyncSession, model) -> object:
        """Add a new record to the database."""
        return await db.new(session, model)

    @classmethod
    async def add_all(cls, session: AsyncSession, models: list) -> list:
        """Add multiple records to the database."""
        return await db.add_all(session, models)
    @classmethod
    async def get_all(cls, session: AsyncSession) -> list:
        """Retrieve all records."""
        return await db.get_all(session, cls)

    @classmethod
    async def filter_by(cls, session: AsyncSession, **filters) -> object:
        """Retrieve records using filters."""
        return await db.filter_by(session, cls, **filters)

    @classmethod
    async def update(cls, session: AsyncSession, model, **kwargs) -> object:
        """Update a record with new data."""
        return await db.update(session, model, **kwargs)

    @classmethod
    async def delete(cls, session: AsyncSession, model) -> object:
        """Mark a record as deleted (soft delete)."""
        return await db.delete(session, model)

    async def to_dict_async(self, session: AsyncSession, seen=None) -> dict:
        """
        Convert an async SQLAlchemy model to a dictionary,
        ensuring relationships are preloaded asynchronously.
        """
        if seen is None:
            seen = set()
        if id(self) in seen:
            return None  # Prevent infinite recursion
        seen.add(id(self))

        result = {}

        # Handle regular fields (columns)
        for key in self.__table__.columns.keys():
            value = getattr(self, key)
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            result[key] = value

        # Ensure relationships are loaded asynchronously
        for relationship in self.__mapper__.relationships:
            rel_name = relationship.key
            related_obj = getattr(self, rel_name, None)

            if related_obj is None:
                continue  # Skip if the relationship is empty

            # ✅ Fetch relationships explicitly to avoid lazy-loading errors
            if relationship.uselist:
                related_objs = await session.execute(select(relationship.mapper.class_).where(relationship.mapper.class_.id == self.id))
                result[rel_name] = [await obj.to_dict_async(session, seen=seen) for obj in related_objs.scalars()]
            else:
                related_obj = await session.execute(select(relationship.mapper.class_).where(relationship.mapper.class_.id == self.id))
                single_obj = related_obj.scalars().first()
                result[rel_name] = await single_obj.to_dict_async(session, seen=seen) if single_obj else None

        return result