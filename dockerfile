# ----------------------
# Stage 1: Builder
# ----------------------
FROM python:3.15-slim-trixie AS builder

# Copier uv pour gérer le lock / venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Créer le venv directement à son emplacement final : ainsi les shebangs
# des scripts (ex. /opt/.venv/bin/projet) restent valides dans l'image runtime.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/.venv

# 1) Installer uniquement les dépendances (couche mise en cache)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 2) Copier le code source puis installer le projet lui-même
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ----------------------
# Stage 2: Runtime
# ----------------------
FROM python:3.15-slim-trixie AS runtime

# Mettre à jour les paquets système (correction de CVE OpenSSL)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Créer utilisateur non-root
RUN useradd -m -u 1001 appuser

WORKDIR /app

# Copier le venv depuis le builder vers /opt/.venv
COPY --from=builder /opt/.venv /opt/.venv

# Ajouter le venv au PATH
ENV PATH="/opt/.venv/bin:$PATH"

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copier le code source
COPY --chown=appuser:appuser . .

# Passer à l’utilisateur non-root
USER appuser

# Lancer le point d'entrée défini dans [project.scripts]
CMD ["projet"]
