import time

from fastapi import FastAPI, Request

from app.core.logging import logger


def init_request_logger(app: FastAPI):

    @app.middleware("http")
    async def log_requests(
        request: Request,
        call_next,
    ):

        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start

        logger.info(
            f"{request.method} "
            f"{request.url.path} "
            f"{response.status_code} "
            f"{duration:.3f}s"
        )

        return response