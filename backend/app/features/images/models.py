from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(max_length=500, unique=True)
    url: str = Field(max_length=1000)
    filename: str = Field(max_length=255)
    format: Optional[str] = Field(default=None, max_length=20)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    bytes: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
