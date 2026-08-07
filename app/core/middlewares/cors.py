from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.pydantic_settings import settings


def init_cors(app: FastAPI):

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )