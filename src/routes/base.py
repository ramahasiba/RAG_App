from fastapi import APIRouter
base_router = APIRouter()

base_router.get("/")
async def welcome():
    return {
        "message": "Welcome!"
    }