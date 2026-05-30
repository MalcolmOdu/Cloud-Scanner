## We are keeping the base in its own file so Alembic can import it cleanly without pulling in the rest of the app.

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass