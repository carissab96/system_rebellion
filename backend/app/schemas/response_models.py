from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """Standard response status values"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PENDING = "pending"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"

class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error, if applicable")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class StandardResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    status: ResponseStatus = Field(..., description="Response status")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[ErrorDetail] = Field(None, description="Error details if status is not success")
    meta: Optional[Dict[str, Any]] = Field(
        None, 
        description="Metadata about the response"
    )
    
    # Note: json_encoders removed - use custom serializers in Pydantic V2 if needed
    # model_config = ConfigDict(json_encoders={...})

class PaginationLinks(BaseModel):
    """Pagination links for paginated responses"""
    self: str = Field(..., description="Link to the current page")
    first: str = Field(..., description="Link to the first page")
    prev: Optional[str] = Field(None, description="Link to the previous page")
    next: Optional[str] = Field(None, description="Link to the next page")
    last: str = Field(..., description="Link to the last page")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(StandardResponse[List[T]]):
    """Paginated API response format"""
    links: PaginationLinks = Field(..., description="Pagination links")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

class ErrorResponse(StandardResponse[None]):
    """Error response format"""
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Always 'error'")
    error: ErrorDetail = Field(..., description="Error details")
    data: None = Field(None, description="Always null for error responses")

# Helper functions for creating responses
def success_response(
    data: Any = None,
    status: ResponseStatus = ResponseStatus.SUCCESS,
    meta: Optional[Dict[str, Any]] = None,
) -> StandardResponse:
    """Create a successful response"""
    return StandardResponse(status=status, data=data, meta=meta)

def error_response(
    message: str,
    code: str = "internal_error",
    status_code: int = 500,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> ErrorResponse:
    """Create an error response"""
    error = ErrorDetail(
        code=code,
        message=message,
        field=field,
        details=details or {},
    )
    status = {
        400: ResponseStatus.VALIDATION_ERROR,
        401: ResponseStatus.UNAUTHORIZED,
        403: ResponseStatus.FORBIDDEN,
        404: ResponseStatus.NOT_FOUND,
        429: ResponseStatus.RATE_LIMITED,
    }.get(status_code, ResponseStatus.INTERNAL_ERROR)
    
    return ErrorResponse(status=status, error=error)

def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    base_url: str,
    query_params: Optional[Dict[str, Any]] = None,
) -> PaginatedResponse:
    """Create a paginated response"""
    query_params = query_params or {}
    total_pages = (total + page_size - 1) // page_size
    
    def build_url(p: int) -> str:
        params = query_params.copy()
        params["page"] = p
        params["page_size"] = page_size
        query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        return f"{base_url}?{query}"
    
    links = PaginationLinks(
        self=build_url(page),
        first=build_url(1),
        prev=build_url(page - 1) if page > 1 else None,
        next=build_url(page + 1) if page < total_pages else None,
        last=build_url(total_pages) if total_pages > 0 else build_url(1),
    )
    
    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
    
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        data=items,
        links=links,
        meta=meta,
    )
