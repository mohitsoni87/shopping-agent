from agent_api import _bootstrap  # noqa: F401  isort: skip
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shopping_agent_common.error_handling import register_exception_handlers
from shopping_agent_common.logging import configure_logging

from agent_api.api import api_router

configure_logging("agent-api")

app = FastAPI(title="Shopping Agent - Chat API")
register_exception_handlers(app)
# Wide open for the prototype browser UI; scope this to the deployed frontend
# origin before this goes anywhere near production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
