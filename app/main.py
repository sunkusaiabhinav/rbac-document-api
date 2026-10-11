from fastapi import Depends, FastAPI

from app.database.connection import Base, engine
from app.models import User, Role
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles


Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(documents_router)


@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role_id": current_user.role_id,
    }


@app.get("/admin-only")
def admin_only(
    current_user: User = Depends(require_roles("Admin")),
):
    return {
        "message": "Welcome Admin",
        "username": current_user.username,
    }


@app.get("/editor-area")
def editor_area(
    current_user: User = Depends(
        require_roles("Admin", "Editor")
    ),
):
    return {
        "message": "Welcome Admin/Editor",
        "username": current_user.username,
    }


@app.get("/documents-access")
def view_documents(
    current_user: User = Depends(
        require_roles("Admin", "Editor", "Viewer")
    ),
):
    return {
        "message": "Documents accessible",
        "username": current_user.username,
    }