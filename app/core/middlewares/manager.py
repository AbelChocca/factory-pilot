from fastapi import FastAPI

from .cors import init_cors
from .exception import init_exception_handlers
from .request_logger import init_request_logger


def init_middlewares(app: FastAPI):

    init_cors(app)

    init_exception_handlers(app)

    init_request_logger(app)