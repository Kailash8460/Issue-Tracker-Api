from fastapi import FastAPI
from app.database import test_connection, engine
from app.models.user import User
from app.models.issue import Issue
from app.routers import users, issues

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
    User.__table__.create(bind=engine, checkfirst=True)
    Issue.__table__.create(bind=engine, checkfirst=True)


app.include_router(users.router)
app.include_router(issues.router)
