from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

import database
import repository
import transform
from auth import authenticate
from schemas import Payload
from scripts.db_migration import sync_db


@asynccontextmanager
async def lifespan(app):
	await database.open_pool()
	try:
		await sync_db()
	except Exception as e:
		print(f"Aviso durante sincronización de base de datos en arranque: {e}")
	yield
	await database.close_pool()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.post("/api/metrics", status_code=204)
async def receive_metrics(payload: Payload, client_id: int = Depends(authenticate)):
	await repository.save_payload(
		client_id,
		payload.timestamp,
		transform.to_metric_rows(client_id, payload),
		transform.to_slow_rows(client_id, payload),
	)
