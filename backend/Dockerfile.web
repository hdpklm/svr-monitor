FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY requirements.txt requirements-web.txt ./
RUN uv pip install --system --no-cache -r requirements.txt -r requirements-web.txt

COPY *.py ./
COPY web ./web
COPY scripts ./scripts

RUN useradd --system --no-create-home app
USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
