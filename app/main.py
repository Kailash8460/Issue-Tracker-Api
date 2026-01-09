from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "Issue Tracker API is running"}
