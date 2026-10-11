from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(
        require_roles("Admin", "Editor")
    ),
    db: Session = Depends(get_db),
):
    document = Document(
        title=document_data.title,
        content=document_data.content,
        owner_id=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
def get_documents(
    current_user: User = Depends(
        require_roles("Admin", "Editor", "Viewer")
    ),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Document)
    ).all()


@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: int,
    current_user: User = Depends(
        require_roles("Admin")
    ),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(Document.id == document_id)
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }

@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: int,
    document_data: DocumentCreate,
    current_user: User = Depends(
        require_roles("Admin", "Editor")
    ),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(Document.id == document_id)
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    document.title = document_data.title
    document.content = document_data.content

    db.commit()
    db.refresh(document)

    return document