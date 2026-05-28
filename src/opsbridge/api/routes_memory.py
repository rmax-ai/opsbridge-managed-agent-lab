"""Memory and dreaming API routes."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, ConfigDict, Field

from .state import MockBackendStore

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryStoreResponse(BaseModel):
    """JSON view of a memory store."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    memory_type: str


class MemoryStoreListResponse(BaseModel):
    """List response for memory stores."""

    model_config = ConfigDict(extra="forbid")

    stores: list[MemoryStoreResponse]


class CreateDreamRequest(BaseModel):
    """Request payload for a mock dream job."""

    model_config = ConfigDict(extra="forbid")

    memory_store_id: str
    session_ids: list[str] = Field(default_factory=list)
    instructions: str


class DreamResponse(BaseModel):
    """JSON view of a mock dream."""

    model_config = ConfigDict(extra="forbid")

    id: str
    memory_store_id: str
    session_ids: list[str]
    instructions: str
    status: str
    created_at: datetime


def _store(request: Request) -> MockBackendStore:
    """Return the shared backend store."""
    return cast(MockBackendStore, request.app.state.backend)


@router.get("/stores", response_model=MemoryStoreListResponse)
async def list_memory_stores(request: Request) -> MemoryStoreListResponse:
    """List memory stores."""
    stores = [
        MemoryStoreResponse.model_validate(record.model_dump())
        for record in _store(request).list_memory_stores()
    ]
    return MemoryStoreListResponse(stores=stores)


@router.post("/dreams", response_model=DreamResponse, status_code=status.HTTP_201_CREATED)
async def create_dream(request: Request, payload: CreateDreamRequest) -> DreamResponse:
    """Create a mock dream job."""
    dream = _store(request).create_dream(
        memory_store_id=payload.memory_store_id,
        session_ids=payload.session_ids,
        instructions=payload.instructions,
    )
    return DreamResponse.model_validate(dream.model_dump())
