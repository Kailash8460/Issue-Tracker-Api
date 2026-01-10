from fastapi import FastAPI
from app.database import Base, test_connection, engine
from app.models import *
from app.routers import comments, users, issues, labels

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "Issue Tracker API is running"}


# To check the database connection
@app.get("/test-db-connection")
def test_db_connection():
    try:
        result = test_connection()
        return {"database_connection": "successful", "result": result}
    except Exception as e:
        return {"database_connection": "failed", "error": str(e)}


# Create the database tables on startup
@app.on_event("startup")
def on_startup():
    # User.__table__.create(bind=engine, checkfirst=True)
    # Issue.__table__.create(bind=engine, checkfirst=True)
    # Comment.__table__.create(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)


app.include_router(users.router)
app.include_router(issues.router)
app.include_router(comments.router)
app.include_router(labels.router)
