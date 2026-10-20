# Agent conversationnel pour requêtage SQL avec LLM Open Source et interface APEX

## Lancer en local

L'API utilise l'Ollama **de la machine hôte** (configuré dans `.env`).

```bash
docker compose up -d --build        # backend sur http://localhost:8000/docs
uv sync && uv run projet            # ou directement sur l'hôte
```

- Depuis le conteneur, l'hôte est joignable via `host.docker.internal:11434` (valeur d'`OLLAMA_BASE_URL` dans `.env`, avec `extra_hosts` pour Linux).
- Sur l'hôte, `uv run projet` utilise `http://localhost:11434` par défaut.
- Le modèle est `OLLAMA_MODEL` dans `.env` (`ministral-3:8b`).

Pour utiliser un Ollama conteneurisé à la place :

```bash
# .env : OLLAMA_BASE_URL=http://ollama:11434
docker compose --profile compose-ollama up -d
```

## API

- `GET /health` : état de l'API et d'Ollama.
- `POST /chat` : envoie un message au modèle.

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Quelle est la capitale de la France ?"}'
```

```json
{"model": "ministral-3:8b", "response": "Paris."}
```

Champs optionnels : `model`, `system` (prompt système), `temperature` (0–2).
