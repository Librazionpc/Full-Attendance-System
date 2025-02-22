from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

class DBM:
    async def new(self, session: AsyncSession, model):
        """
        Add a new record to the database.
        """
        session.add(model)
        await session.commit()
        await session.refresh(model)  # Refresh the model to get updated data (like auto-incremented IDs)
        return model

    async def add_all(self, session: AsyncSession, models):
        """
        Add multiple records to the database.
        """
        session.add_all(models)
        await session.commit()
        return models

    async def get(self, session: AsyncSession, model_class, record_id):
        """
        Retrieve a record by its primary key.
        """
        try:
            query = await session.get(model_class, record_id)
            if not query:
                raise NoResultFound(f"{model_class.__name__} with id {record_id} not found.")
            return query
        except NoResultFound as e:
            print(e)
            return None

    async def get_all(self, session: AsyncSession, model_class):
        """
        Retrieve all records of a model.
        """
        async with session.begin():  # ✅ Ensures transaction begins
            stmt = select(model_class)
            results = await session.execute(stmt)
            data = results.scalars().all()
            print(f"✅ Retrieved {len(data)} records")  # Debugging
            return data

    async def filter_by(self, session: AsyncSession, model_class, **filters):
        """
        Retrieve records using filters.
        """
        
        stmt = select(model_class).filter_by(**filters)
        results = await session.execute(stmt)
        return results.scalars().all()

    async def update(self, session: AsyncSession, model, **kwargs):
        """
        Update a record with new data.
        """
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        await session.commit()
        await session.refresh(model)  # Refresh the model to get updated data
        return model

    async def delete(self, session: AsyncSession, model):
        """
        Delete a record from the database.
        """
        await session.delete(model)
        await session.commit()
        return True
