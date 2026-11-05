# Image de base maintenue et récente (Python 3.13, Debian slim)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Correctifs de sécurité du système
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances installées avant le code (meilleur cache Docker).
# pip ne sert qu'à l'installation : il est ensuite retiré de l'image de production
# (surface d'attaque réduite ; pip embarque aussi du code tiers vulnérable signalé par Trivy).
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && pip uninstall -y pip

# Utilisateur sans privilèges : le code reste en lecture seule pour lui,
# seul le dossier de la base SQLite est modifiable
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/instance \
    && chown appuser:appuser /app/instance
COPY app ./app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/login')"

# Serveur WSGI de production (pas le serveur de développement Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--no-control-socket", \
     "--access-logfile", "-", "app:create_app()"]
