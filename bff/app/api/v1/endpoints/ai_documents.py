"""AI Documents API endpoints for RAG system."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.schemas.ai import (
    DocumentCreate,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    PaginationParams,
    AIErrorResponse
)
from app.schemas.user import UserResponse
from app.services.ai_rag_service import AIRAGService

router = APIRouter(prefix="/ai/documents", tags=["AI Documents"])


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Document",
    description="Create and process a new document for RAG system"
)
async def create_document(
    document_data: DocumentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DocumentResponse:
    """Create a new document."""
    
    try:
        service = AIRAGService(db)
        return await service.create_document(document_data, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}"
        )


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="Upload a file and create document for RAG system"
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    name: Optional[str] = Query(None, description="Document name (defaults to filename)"),
    visibility: str = Query("private", regex="^(private|shared|public)$", description="Document visibility"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DocumentResponse:
    """Upload and process a document file."""
    
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type from filename
        file_type = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
        
        # Create document data
        document_data = DocumentCreate(
            name=name or file.filename,
            content=content.decode('utf-8', errors='ignore'),  # Basic text extraction
            file_type=file_type,
            metadata={
                'original_filename': file.filename,
                'file_size': len(content),
                'content_type': file.content_type
            },
            visibility=visibility
        )
        
        service = AIRAGService(db)
        return await service.create_document(document_data, current_user.id)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content could not be decoded as text"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="List Documents",
    description="List documents with optional filtering and pagination"
)
async def list_documents(
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    processing_status: Optional[str] = Query(None, description="Filter by processing status"),
    visibility: Optional[str] = Query(None, description="Filter by visibility"),
    search: Optional[str] = Query(None, description="Search in document names and content"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[DocumentResponse]:
    """List documents."""
    
    try:
        pagination = PaginationParams(
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        service = AIRAGService(db)
        documents, total = await service.list_documents(
            user_id=current_user.id,
            file_type=file_type,
            processing_status=processing_status,
            search=search,
            visibility=visibility,
            pagination=pagination
        )
        
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get Document",
    description="Get document by ID"
)
async def get_document(
    document_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DocumentResponse:
    """Get document by ID."""
    
    try:
        service = AIRAGService(db)
        document = await service.get_document(document_id, current_user.id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Document",
    description="Delete document and its chunks"
)
async def delete_document(
    document_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete document."""
    
    try:
        service = AIRAGService(db)
        success = await service.delete_document(document_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post(
    "/{document_id}/share",
    response_model=dict,
    summary="Share Document",
    description="Share document with specified users"
)
async def share_document(
    document_id: UUID,
    shared_with: List[UUID],
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Share document with users."""
    
    try:
        service = AIRAGService(db)
        success = await service.share_document(document_id, current_user.id, shared_with)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document shared successfully", "shared_with": shared_with}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share document: {str(e)}"
        )


@router.post(
    "/{document_id}/reprocess",
    response_model=dict,
    summary="Reprocess Document",
    description="Reprocess document for updated chunking and embeddings"
)
async def reprocess_document(
    document_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Reprocess document."""
    
    try:
        service = AIRAGService(db)
        success = await service.reprocess_document(document_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document reprocessing started", "document_id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reprocess document: {str(e)}"
        )


@router.get(
    "/{document_id}/chunks",
    response_model=List[dict],
    summary="Get Document Chunks",
    description="Get chunks for a document"
)
async def get_document_chunks(
    document_id: UUID,
    limit: Optional[int] = Query(None, ge=1, le=200, description="Maximum number of chunks"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get document chunks."""
    
    try:
        service = AIRAGService(db)
        return await service.get_document_chunks(document_id, current_user.id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document chunks: {str(e)}"
        )


@router.post(
    "/search",
    response_model=DocumentSearchResponse,
    summary="Search Documents",
    description="Search documents using vector, keyword, or hybrid search"
)
async def search_documents(
    request: DocumentSearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DocumentSearchResponse:
    """Search documents."""
    
    try:
        service = AIRAGService(db)
        return await service.search_documents(request, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document search failed: {str(e)}"
        )


@router.get(
    "/search/simple",
    response_model=DocumentSearchResponse,
    summary="Simple Document Search",
    description="Simple document search with query parameter"
)
async def simple_search(
    q: str = Query(..., description="Search query"),
    search_type: str = Query("hybrid", regex="^(vector|keyword|hybrid)$", description="Search type"),
    top_k: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> DocumentSearchResponse:
    """Simple document search."""
    
    try:
        request = DocumentSearchRequest(
            query=q,
            top_k=top_k,
            search_type=search_type
        )
        
        service = AIRAGService(db)
        return await service.search_documents(request, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document search failed: {str(e)}"
        )


@router.get(
    "/processing/status",
    response_model=dict,
    summary="Get Processing Status",
    description="Get document processing status overview"
)
async def get_processing_status(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get processing status."""
    
    try:
        service = AIRAGService(db)
        return await service.get_processing_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing status: {str(e)}"
        )


# Batch operations

@router.post(
    "/batch/delete",
    response_model=dict,
    summary="Batch Delete Documents",
    description="Delete multiple documents at once"
)
async def batch_delete_documents(
    document_ids: List[UUID],
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Batch delete documents."""
    
    try:
        service = AIRAGService(db)
        
        success_count = 0
        failed_count = 0
        
        for document_id in document_ids:
            try:
                success = await service.delete_document(document_id, current_user.id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        return {
            "message": "Batch delete completed",
            "successful": success_count,
            "failed": failed_count,
            "total": len(document_ids)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch delete failed: {str(e)}"
        )


@router.post(
    "/batch/reprocess",
    response_model=dict,
    summary="Batch Reprocess Documents",
    description="Reprocess multiple documents at once"
)
async def batch_reprocess_documents(
    document_ids: List[UUID],
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Batch reprocess documents."""
    
    try:
        service = AIRAGService(db)
        
        success_count = 0
        failed_count = 0
        
        for document_id in document_ids:
            try:
                success = await service.reprocess_document(document_id, current_user.id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        return {
            "message": "Batch reprocessing started",
            "successful": success_count,
            "failed": failed_count,
            "total": len(document_ids)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch reprocess failed: {str(e)}"
        )