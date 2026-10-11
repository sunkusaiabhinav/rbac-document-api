from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.role import Role
from app.models.user import User


users = [
    ("abhi", "admin123", "Admin"),
    ("rahul", "editor123", "Editor"),
    ("priya", "viewer123", "Viewer"),
]


with SessionLocal() as db:
    for username, password, role_name in users:

        existing_user = db.scalar(
            select(User).where(User.username == username)
        )

        if existing_user:
            continue

        role = db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if not role:
            raise ValueError(f"Role '{role_name}' does not exist")

        user = User(
            username=username,
            password_hash=hash_password(password),
            role_id=role.id,
        )

        db.add(user)

    db.commit()


print("Users created successfully!")