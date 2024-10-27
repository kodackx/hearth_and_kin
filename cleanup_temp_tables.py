from sqlalchemy import create_engine, inspect
from src.core.config import settings

# Use your actual database URL here
engine = create_engine(settings.DATABASE_URL)

inspector = inspect(engine)

with engine.connect() as connection:
    for table_name in inspector.get_table_names():
        if table_name.startswith('_alembic_tmp_'):
            connection.execute(f'DROP TABLE IF EXISTS {table_name}')
            print(f"Dropped table: {table_name}")

print("Cleanup complete.")