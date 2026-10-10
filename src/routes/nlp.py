from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest, AnswerRequest
from controllers import NLPController
from models.enums import ResponseSignal
from models.ChunkModel import ChunkModel
from models.ProjectModel import ProjectModel

import logging

logger = logging.getLogger('uv-logger')

nlp_router = APIRouter(
prefix= "/api/v1/nlp",
tags=['api_v1', 'nlp']
)

# Push index for a project
@nlp_router.post("/index/push/{project_id}")
async def push_index(request: Request, project_id: str, push_request: PushRequest):

    project_model = ProjectModel(db_client=request.app.state.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={
                                    "signal": f"{ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}: {project_id}."
                                }
                                )

    chunk_model = ChunkModel(db_client=request.app.state.db_client)

    nlp_controller = NLPController(
        vector_DB_client=request.app.state.vectorDB_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser=request.app.state.template_parser
    )



    has_records = True
    page_no = 1
    inserted_items_count = 0
    should_reset = bool(push_request.do_reset)

    while has_records:

        page_chunks = await chunk_model.get_chunks_by_project_id(project_id=project.id, page_no=page_no)
        if len(page_chunks):
            inserted_items_count += len(page_chunks)
            page_no +=1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        inserted_signal = nlp_controller.index_into_vectorDB(
            project=project, 
            chunks=page_chunks, 
            do_reset=should_reset)

        should_reset = False

        if not inserted_signal:
            logger.error(f"Failed to index chunks for project {project_id} on page {page_no}.")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={
                                        "signal": f"{ResponseSignal.INDEXING_INTO_VECTORDB_FAILED_ERROR.value} for project {project_id} on page {page_no}."
                                    }
                                    )
        
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={
                                "signal": f"{ResponseSignal.INDEXING_INTO_VECTORDB_SUCCESS.value} for project {project_id}.",
                                "inserted_items_count": inserted_items_count
                            }
                            )


# Get vectorDB collection info
@nlp_router.get("/index/push/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = ProjectModel(db_client=request.app.state.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={
                                    "signal": f"{ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}: {project_id}."
                                }
                                )

    nlp_controller = NLPController(
        vector_DB_client=request.app.state.vectorDB_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser=request.app.state.template_parser
    )

    collection_info = nlp_controller.get_vectorDB_collection_info(project=project)

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={
                                "signal": f"{ResponseSignal.GETTING_VECTORDB_COLLECTION_INFO_SUCCESS.value} for project {project_id}.",
                                "collection_info": collection_info
                            }
                            )

# Search in the index
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = ProjectModel(db_client=request.app.state.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                            content={
                                    "signal": f"{ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}: {project_id}."
                                }
                                )

    nlp_controller = NLPController(
        vector_DB_client=request.app.state.vectorDB_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser=request.app.state.template_parser
    )

    retrieval_chunks = nlp_controller.search_vectorDB_collection(
        project=project,
        query_text=search_request.query,
        top_k=search_request.top_k
    )

    if not retrieval_chunks:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                            content={
                                    "signal": f"{ResponseSignal.SEARCH_VECTORDB_COLLECTION_FAILED.value} for project {project_id}."
                                }
                                )

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={
                                "signal": f"{ResponseSignal.SEARCH_VECTORDB_COLLECTION_SUCCESS.value} for project {project_id}.",
                                "retrieval_chunks": [result.model_dump() for result in retrieval_chunks]
                            }
                            )



@nlp_router.post("/index/answer/{project_id}")
async def rag_answer(request: Request, project_id: str, answer_request: AnswerRequest):

    project_model = ProjectModel(db_client=request.app.state.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={
                                    "signal": f"{ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}: {project_id}."
                                }
                                )

    nlp_controller = NLPController(
        vector_DB_client=request.app.state.vectorDB_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser=request.app.state.template_parser
    )

    answer, retrieval_chunks, user_prompt, system_prompt = nlp_controller.answer_rag_question(
        project=project,
        query_text=answer_request.query,
        top_k=answer_request.top_k
    )

    serialized_chunks = [chunk.model_dump() for chunk in retrieval_chunks]

    if not answer:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                    "signal": f"{ResponseSignal.RAG_ANSWER_FAILED.value} for project {project_id}.",
                                    "retrieval_chunks": serialized_chunks
                                }
                                )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                                "signal": f"{ResponseSignal.RAG_ANSWER_SUCCESS.value} for project {project_id}.",
                                "answer": answer,
                                "retrieval_chunks": serialized_chunks,
                                "system_prompt": system_prompt,
                                "user_prompt": user_prompt
                            }
                            )
