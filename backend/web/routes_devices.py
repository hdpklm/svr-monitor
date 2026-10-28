from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

import security
from web import repo_devices, settings
from web.deps import api_user, page_user
from web.device_schemas import DeviceInput
from web.templating import templates

router = APIRouter()

KEY_HINT_LENGTH = 4


@router.get("/devices", response_class=HTMLResponse)
async def devices_page(request: Request, user=Depends(page_user)):
	context = {
		"user": user,
		"devices": await repo_devices.list_for_user(user["id"]),
		"api_url": f"{settings.BASE_URL}/api/metrics",
		"max_devices": settings.MAX_DEVICES,
	}
	return templates.TemplateResponse(request, "devices.html", context)


@router.post("/devices", status_code=201)
async def add_device(data: DeviceInput, user=Depends(api_user)):
	key = security.generate_key()
	try:
		device_id = await repo_devices.create(
			user["id"], data.name, data.description, security.hash_key(key), key[-KEY_HINT_LENGTH:]
		)
	except repo_devices.DeviceLimitError:
		raise HTTPException(status_code=409, detail=f"Máximo de {settings.MAX_DEVICES} dispositivos")
	return {"id": device_id, "key": key}


@router.put("/devices/{device_id}", status_code=204)
async def edit_device(device_id: int, data: DeviceInput, user=Depends(api_user)):
	if not await repo_devices.update(user["id"], device_id, data.name, data.description):
		raise HTTPException(status_code=404, detail="Dispositivo no encontrado")


@router.delete("/devices/{device_id}", status_code=204)
async def remove_device(device_id: int, user=Depends(api_user)):
	if not await repo_devices.delete(user["id"], device_id):
		raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
