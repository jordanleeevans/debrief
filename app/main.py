from fastapi import FastAPI
from http import HTTPStatus
from app.core.settings import Settings

app = FastAPI(title="Debfrief API", version="1.0.0")


@app.get("/")
def health_check():
    return {
        "status": HTTPStatus.OK,
        "message": "Debfrief API is running",
        "settings": Settings().dict(),
    }
