import logging

from fastapi import FastAPI
from mangum import Mangum

from services.api.routers.tasks import router as tasks_router

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI(title="Task Management API")

app.include_router(tasks_router)

# Lambda entrypoint
handler = Mangum(app)
