# AGENTS.md

## Contexte
- Objectif (README) : agent conversationnel de requêtage SQL via LLM open source (Ollama), interface APEX.
- API FastAPI dans `src/projet/app.py` : `GET /health`, `POST /chat` (proxy non-streaming vers `Ollama POST /api/chat`).
- `src/projet/__init__.py:main()` lance uvicorn ; c'est le point d'entrée `uv run projet` et le `CMD` Docker.
- Python 3.15 (`.python-version`), `requires-python >=3.14`. Toolchain **uv** exclusivement (`uv.lock` committé) : `uv sync`, `uv add`, jamais `pip install`.

## Commandes
- Installer : `uv sync`
- Lancer : `uv run projet` (port 8000, docs sur `/docs`)
- Dev avec reload : `uv run uvicorn projet.app:app --reload`
- Appel direct : `curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{"message":"..."}'`
- `main.py` à la racine est un vestige non utilisé (`print("hello world")`), pas le point d'entrée.
- Aucun test, linter, formatter ni CI configuré ; `pytest` n'est pas une dépendance.
- Docker : `docker compose up -d --build backend` (image `projet-backend`, conteneur `backend-service`, port 8000), logs `docker compose logs -f backend`.
- Compose lance aussi `ollama` (11434) et `ollama-pull`, qui télécharge `ministral-3:3b` ; attendre la fin du pull avant le premier `/chat`.

## Config modèle
- `OLLAMA_BASE_URL` (défaut `http://localhost:11434`), `OLLAMA_MODEL` (défaut `ministral-3:3b`), `OLLAMA_TIMEOUT` (120 s), `HOST`, `PORT`.
- En local, Ollama n'expose pas forcément `ministral-3:3b` : passer `OLLAMA_MODEL` à un modèle présent (`ollama list`).
- Modèle/modèle inconnu → 502 avec le détail Ollama ; Ollama injoignable → 503.

## Pièges Docker (vérifiés)
- Le venv est créé directement dans `/opt/.venv` via `UV_PROJECT_ENVIRONMENT` puis copié au même chemin. Ne pas revenir à `/app/.venv` : les shebangs des scripts (`#!/app/.venv/bin/python`) casseraient le runtime (`exec: no such file or directory`).
- `uv sync` est en 2 étapes (`--no-install-project`, puis `COPY . .` + sync) : le projet est un package `uv_build` en src-layout, donc `src/` doit exister avant l'installation du projet.
- Le fichier est `dockerfile` (minuscule) alors que compose référence `Dockerfile` : ne fonctionne que sur macOS (FS insensible à la casse).
- `CMD ["projet"]` (script installé), pas `python -m` : il n'y a pas de `__main__.py`.
- Garder `[build-system] uv_build>=0.13.3,<0.14.0` aligné avec l'`uv:latest` de l'image (0.13.3) ; sinon warning de version. L'uv local peut être plus ancien (0.12.20).
- `.dockerignore` exclut `.venv`, `.git`, `.env`, `model.env`.
