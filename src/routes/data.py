from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse

import aiofiles

from models import ChunkModel, ProjectModel ,ResponseSignal, AssetTypeEnum
from models.db_schemes import DataChunk, Asset
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel

from .schemes.data import ProcessRequest
from helpers.configurations import get_settings, Settings
from controllers import DataController, ProcessController
import logging
import os


logger = logging.getLogger('uv-logger')

data_router = APIRouter(
prefix= "/api/v1/data",
tags=['api_v1', 'data']
)

# Upload file endpoint
@data_router.post('/upload/{project_id}')
async def upload_file(request: Request, project_id: str, file: UploadFile,
                        app_settings: Settings = Depends(get_settings)
                        ):
        project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)  # Initialize ProjectModel with the database client

        project = await project_model.get_project_or_create_one(project_id=project_id)  # Get or create the project
        if project.id is None:
                raise RuntimeError('Project was created without an id')

        # validate file properties
        is_valid, signal_result = DataController().validate_upload_file(file=file)

        if not is_valid:
                return JSONResponse(
                        content={
                                'signal': signal_result
                                },
                        status_code=status.HTTP_400_BAD_REQUEST)

        if not file.filename:
                return JSONResponse(
                        content={
                                'signal': ResponseSignal.FILE_UPLOAD_FAILED.value
                                },
                        status_code=status.HTTP_400_BAD_REQUEST)

        file_path, file_id = DataController().generate_unique_file_path(file_name=file.filename, project_id=project_id)

        try:
                async with aiofiles.open(file_path, "wb") as f:
                        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                                await f.write(chunk)
        except Exception as e:

                logger.error(f'error while uploading file: {e}')

                return JSONResponse(
                                content={
                                        'response signal': ResponseSignal.FILE_UPLOAD_FAILED.value
                                                },
                                                status_code=status.HTTP_400_BAD_REQUEST
                                                )

        asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)

        asset_record = await asset_model.create_asset(
                Asset.model_validate({
                        'asset_project_id': project.id,
                        'asset_type': file.content_type,
                        'asset_name': file_id,
                        'asset_size': os.path.getsize(file_path),
                        'asset_config': {
                                'file_path': file_path,
                                'original_file_name': file.filename
                        }
                })
        )

        return JSONResponse(
                content={
                        'response signal': ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                        'file_id': file_id,
                        'asset_id': str(asset_record.id)
                                }
                                )

# Process file endpoint
@data_router.post('/process/{project_id}')
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

        logger.info(f'Processing request for project {project_id}')

        file_id = process_request.file_id
        chunk_size: int = process_request.chunk_size
        overlap_size: int = process_request.overlap_size
        do_reset = process_request.do_reset

        project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)  # Initialize ProjectModel with the database client

        project = await project_model.get_project_or_create_one(project_id=project_id)  # Get or create the project
        if project.id is None:
                raise RuntimeError('Project was created without an id')

        asset_model = await AssetModel.create_instance(
                db_client=request.app.state.db_client
                )
        
        project_files_ids = {}
        if process_request.file_id:
                asset_record = await asset_model.get_asset_record(
                        asset_project_id=project.id, 
                        asset_name=process_request.file_id
                        )
                if asset_record is None:
                        return JSONResponse(
                                content={
                                        'response signal': ResponseSignal.FILE_ID_ERROR.value
                                                },
                                                status_code=status.HTTP_400_BAD_REQUEST
                                                )

                project_files_ids = {
                        asset_record.id: asset_record.asset_name
                }
                
        else:
                asset_model = await AssetModel.create_instance(
                        db_client=request.app.state.db_client
                        )  # Initialize AssetModel with the database client
                
                project_assets = await asset_model.get_all_project_assets(
                        asset_project_id=project.id, 
                        asset_type=AssetTypeEnum.TEXT_PLAIN.value
                        )
                
                project_files_ids = {
                        record.id : record.asset_name 
                        for record in project_assets
                }

        if len(project_files_ids) == 0:
                return JSONResponse(
                        content={
                                'response signal': ResponseSignal.NO_FILES_ERROR.value
                                        },
                                        status_code=status.HTTP_400_BAD_REQUEST
                                        )

        process_controller = ProcessController(project_id=project_id)

        number_of_records_inserted : int = 0
        number_of_files_processed = 0

        chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)  # Initialize ChunkModel with the database client

        if do_reset == 1:
                await chunk_model.delete_chunks_by_project_id(project_id=project.id)


        for asset_id, file_id in project_files_ids.items():

                logger.info(f'Processing file {file_id} in project {project_id}')

                file_content = process_controller.get_file_content(file_name=file_id)
                
                if file_content is None:
                        logger.error(f'No content found for file {file_id} in project {project_id}')
                        continue
                

                file_chunks = process_controller.process_file_content(
                        file_content=file_content, 
                        file_name=file_id,
                        chunk_size=chunk_size,
                        overlap_size=overlap_size)
                

                if file_chunks == None or len(file_chunks) == 0:
                        return JSONResponse(
                        content={
                                'response signal': ResponseSignal.PROCESSING_FAILED.value
                                        },
                                        status_code=status.HTTP_400_BAD_REQUEST
                                        )

                file_chunks_record = [
                        DataChunk(
                                chunk_text=chunk.page_content,
                                chunk_metadata=chunk.metadata,
                                chunk_order=index+1,
                                chunk_project_id=project.id,
                                chunk_asset_id=asset_id
                        ) for index, chunk in enumerate(file_chunks)

                ]

                number_of_records_inserted += await chunk_model.insert_many_chunks(chunks=file_chunks_record)
                number_of_files_processed += 1

        return JSONResponse(
                content={
                        'response signal': ResponseSignal.PROCESSING_SUCCESS.value,
                        'number_of_records_inserted': number_of_records_inserted,
                        'number_of_files_processed': number_of_files_processed
                                }
        )

