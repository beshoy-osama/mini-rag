from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"

    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"

    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    CHUNKS_NOT_FOUND_ERROR = "chunks_not_found"
    INDEXING_INTO_VECTORDB_FAILED_ERROR = "indexing_failed"
    INDEXING_INTO_VECTORDB_SUCCESS = "indexing_success"

    GETTING_VECTORDB_COLLECTION_INFO_SUCCESS = "getting_vectorDB_collection_info_success"

    SEARCH_VECTORDB_COLLECTION_SUCCESS = "search_vectorDB_collection_success"
    SEARCH_VECTORDB_COLLECTION_FAILED = "search_vectorDB_collection_failed"