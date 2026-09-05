import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import run_agent
from app.api.sessions import get_db
from app.models.db_models import Message, Session
from app.models.schemas import ChatRequest, ChatResponse, MessageResponse


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


async def get_conversation_history(
    session_id,
    db: AsyncSession,
) -> str:

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )

    messages = list(
        reversed(result.scalars().all())
    )

    return "\n".join(
        f"{message.role}: {message.content}"
        for message in messages
    )


async def get_session(
    session_id,
    db: AsyncSession,
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "session_not_found",
                "message": "Session not found.",
            },
        )

    return session


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
):

    await get_session(
        data.session_id,
        db,
    )

    conversation_history = await get_conversation_history(
        data.session_id,
        db,
    )

    user_message = Message(
        session_id=data.session_id,
        role="user",
        content=data.message,
    )

    db.add(user_message)

    try:
        await db.commit()

    except Exception as exc:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": "database_error",
                "message": "Unable to save the user message.",
            },
        ) from exc

    try:

        answer, sources = await run_agent(
            message=data.message,
            db=db,
            conversation_history=conversation_history,
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_unavailable",
                "message": str(exc),
            },
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_error",
                "message": "The assistant could not generate a response.",
            },
        ) from exc

    assistant_message = Message(
        session_id=data.session_id,
        role="assistant",
        content=answer,
        sources=sources,
    )

    db.add(assistant_message)

    try:
        await db.commit()
        await db.refresh(assistant_message)

    except Exception as exc:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": "database_error",
                "message": "Unable to save the assistant response.",
            },
        ) from exc

    return ChatResponse(
        message=MessageResponse.model_validate(
            assistant_message
        ),
        artifacts=[],
    )


@router.post("/stream")
async def chat_stream(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
):

    await get_session(
        data.session_id,
        db,
    )

    conversation_history = await get_conversation_history(
        data.session_id,
        db,
    )

    user_message = Message(
        session_id=data.session_id,
        role="user",
        content=data.message,
    )

    db.add(user_message)

    try:
        await db.commit()

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": "database_error",
                "message": "Unable to save the user message.",
            },
        )

    async def generate():

        try:

            answer, sources = await run_agent(
                message=data.message,
                db=db,
                conversation_history=conversation_history,
            )

            # Send the assistant response.
            yield (
                "data: "
                + json.dumps(
                    {
                        "token": answer,
                    }
                )
                + "\n\n"
            )

            assistant_message = Message(
                session_id=data.session_id,
                role="assistant",
                content=answer,
                sources=sources,
            )

            db.add(assistant_message)

            try:

                await db.commit()
                await db.refresh(assistant_message)

            except Exception:

                await db.rollback()

                yield (
                    "data: "
                    + json.dumps(
                        {
                            "error": "Unable to save the assistant response.",
                        }
                    )
                    + "\n\n"
                )

                return

            yield (
                "data: "
                + json.dumps(
                    {
                        "done": True,
                        "message_id": assistant_message.id,
                        "sources": sources,
                        "artifacts": [],
                    }
                )
                + "\n\n"
            )

        except RuntimeError as exc:

            await db.rollback()

            yield (
                "data: "
                + json.dumps(
                    {
                        "error": str(exc),
                    }
                )
                + "\n\n"
            )

        except Exception:

            await db.rollback()

            yield (
                "data: "
                + json.dumps(
                    {
                        "error": (
                            "The assistant could not generate a response."
                        ),
                    }
                )
                + "\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )