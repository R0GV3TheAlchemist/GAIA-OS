"""
core/routers/query.py

Direct inference / query endpoints:
  POST /query          — single-turn inference against a named Gaian
  POST /query/stream   — streaming version of the above

Canon Refs: C01, C04, C12, C15, C17, C21, C27, C30
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.auth import require_auth
from core.server_state import _RUNTIME_REGISTRY

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    gaian: str = Field(..., description="Slug of the Gaian runtime to query")
    prompt: str = Field(..., min_length=1, max_length=32_768)
    session_id: str | None = Field(default=None)


class QueryResponse(BaseModel):
    gaian: str
    reply: str
    session_id: str | None = None


def _get_runtime(gaian: str):
    rt = _RUNTIME_REGISTRY.get(gaian)
    if rt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active runtime for gaian '{gaian}'",
        )
    return rt


@router.post("", response_model=QueryResponse)
async def query(body: QueryRequest, _user=Depends(require_auth)):
    """Single-turn inference. Returns the full reply at once."""
    rt = _get_runtime(body.gaian)
    try:
        reply = await rt.query(body.prompt, session_id=body.session_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    return QueryResponse(gaian=body.gaian, reply=reply, session_id=body.session_id)


@router.post("/stream")
async def query_stream(body: QueryRequest, _user=Depends(require_auth)):
    """Streaming inference via Server-Sent Events."""
    rt = _get_runtime(body.gaian)

    async def token_stream():
        try:
            async for token in rt.stream(body.prompt, session_id=body.session_id):
                yield f"data: {token}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {exc}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")
