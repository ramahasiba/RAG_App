from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_UPLOAD_SUCCESS = "file_uploaded_successfully"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_FAILED = "file_processing_failed"
    PROCESSING_SUCCESS = "file_processed_successfully"
    LOADING_FILE_FAILED = "loading_file_failed"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_eith_this_id]666666666"