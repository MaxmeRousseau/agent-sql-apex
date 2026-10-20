import os


def main() -> None:
    """Point d'entrée `uv run projet` / image Docker."""
    import uvicorn

    uvicorn.run(
        "projet.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
