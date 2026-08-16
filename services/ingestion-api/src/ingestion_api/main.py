from fastapi import FastAPI
from shopping_agent_common.error_handling import register_exception_handlers
from shopping_agent_common.logging import configure_logging

from ingestion_api.api import api_router

configure_logging("ingestion-api")

app = FastAPI(title="Shopping Agent - Ingestion API")
register_exception_handlers(app)
app.include_router(api_router)
