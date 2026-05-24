class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundError(AppException):
    def __init__(self, document_id: str):
        super().__init__(f"Document {document_id} not found", 404)


class DocumentProcessingError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Document processing failed: {message}", 422)


class RetrievalError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Retrieval failed: {message}", 500)


class LLMError(AppException):
    def __init__(self, message: str):
        super().__init__(f"LLM error: {message}", 503)


class FileValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, 400)
