from fastapi import FastAPI
from app.database import test_connection

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "Issue Tracker API is running"}


@app.get("/test-db-connection")
def test_db_connection():
    try:
        result = test_connection()
        return {"database_connection": "successful", "result": result}
    except Exception as e:
        return {"database_connection": "failed", "error": str(e)}
