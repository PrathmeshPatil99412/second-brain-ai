"""Aggregated API v1 router."""

from fastapi import APIRouter

from api.routers import chat, dashboard, documents, health, notes, search, summary

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(documents.router)
api_router.include_router(notes.router)
api_router.include_router(chat.router)
api_router.include_router(search.router)
api_router.include_router(summary.router)
api_router.include_router(dashboard.router)
api_router.include_router(health.router)
