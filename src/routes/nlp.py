from fastapi import FastAPI, APIRouter, status, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from routes.schemas.nlp import PushRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
import logging
from models import ResponseSignal

logger = logging.getLogger('uvicorn.error')
nlp_router = APIRouter(
    tags=["NLP"],
)

@nlp_router.post("/index/path/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    project_model =  await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    project = project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND.value
                }
        )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    chunks = chunk_model.get
    
