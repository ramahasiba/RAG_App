from fastapi import APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter()

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    return {
        "message": f"Welcome to {app_name}!"
    }