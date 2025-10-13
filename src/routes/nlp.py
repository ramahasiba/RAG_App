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

    has_records = True
    page_no = 1
    inserted_items_count = 0

    while has_records:
        page_chunks = chunk_model.get_project_chunks(
            project_id=project.project_id, 
            page_no=page_no
        )
        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project, 
            chunks=page_chunks,
            do_reset=push_request.do_reset
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_count": inserted_items_count
        }
    ) 