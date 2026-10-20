"""Routes FastAPI pour dialoguer avec un modèle servi par Ollama."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ministral-3:8b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="Message de l'utilisateur")
    model: str | None = Field(default=None, description=f"Modèle Ollama (défaut : {OLLAMA_MODEL})")
    system: str | None = Field(default=None, description="Prompt système optionnel")
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatResponse(BaseModel):
    model: str
    response: str


class HealthResponse(BaseModel):
    status: str
    model: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Client partagé : réutilise les connexions vers Ollama.
    app.state.ollama = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=OLLAMA_TIMEOUT)
    try:
        yield
    finally:
        await app.state.ollama.aclose()


app = FastAPI(title="Projet API", version="0.1.0", lifespan=lifespan)


def get_ollama(request: Request) -> httpx.AsyncClient:
    return request.app.state.ollama


OllamaClient = Annotated[httpx.AsyncClient, Depends(get_ollama)]


@app.get("/health", response_model=HealthResponse)
async def health(ollama: OllamaClient) -> HealthResponse:
    """Vérifie que l'API et le serveur Ollama répondent."""
    try:
        await ollama.get("/api/tags")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Ollama injoignable : {exc}") from exc
    return HealthResponse(status="ok", model=OLLAMA_MODEL)


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, ollama: OllamaClient) -> ChatResponse:
    """Envoie un message au modèle et renvoie sa réponse complète."""
    model = payload.model or OLLAMA_MODEL
    messages = []
    if payload.system:
        messages.append({"role": "system", "content": payload.system})
    messages.append({"role": "user", "content": payload.message})

    try:
        response = await ollama.post(
            "/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": payload.temperature},
            },
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur Ollama ({exc.response.status_code}) : {exc.response.text}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama injoignable sur {OLLAMA_BASE_URL} : {exc}",
        ) from exc

    data = response.json()
    return ChatResponse(model=data.get("model", model), response=data["message"]["content"])
