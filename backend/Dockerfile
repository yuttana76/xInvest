# Stage 1: Builder — compile deps into a venv, discarded after this stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y pip setuptools wheel

# Stage 2: Runtime — only the venv + runtime system libs, no compiler toolchain
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# libpq5 (not -dev): psycopg2-binary bundles its own libpq, so this covers any
# other package that dynamically links against the client library at runtime.
RUN apt-get update && apt-get install -y \
    libpq5 \
    fonts-thai-tlwg \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 django && adduser --system --uid 1001 --gid 1001 django

COPY --from=builder /opt/venv /opt/venv
COPY . .
RUN mkdir -p /app/static && chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
