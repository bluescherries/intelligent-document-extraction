from backend.app.database.database import Base, engine
from backend.app.database.models import Document


print("=" * 60)
print("DATABASE TABLE CREATION")
print("=" * 60)

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
print("Database: documents.db")
print("Table: documents")