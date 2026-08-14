from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(__type_pos=String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(__type_pos=String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(__type_pos=String(255), nullable=False)
