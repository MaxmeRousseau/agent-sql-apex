# Agent conversationnel pour requêtage SQL avec LLM Open Source et interface APEX

## Lancer en local

```bash
uv sync
uv run projet          # http://localhost:8000/docs
```

Ollama doit tourner sur `http://localhost:11434` (ou définir `OLLAMA_BASE_URL`).
Variables : `OLLAMA_BASE_URL`, `OLLAMA_MODEL` (défaut `ministral-3:3b`), `OLLAMA_TIMEOUT`, `HOST`, `PORT`.

## API

- `GET /health` : état de l'API et d'Ollama.
- `POST /chat` : envoie un message au modèle.

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Quelle est la capitale de la France ?"}'
```

```json
{"model": "ministral-3:3b", "response": "Paris."}
```

Champs optionnels : `model`, `system` (prompt système), `temperature` (0–2).

## Docker

```bash
docker compose up -d --build
```

`ollama-pull` télécharge `ministral-3:3b` au premier démarrage ; attendre la fin du pull avant le premier appel.
