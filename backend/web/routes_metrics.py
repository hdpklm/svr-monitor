from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse

from web import repo_devices, repo_metrics, series, timeutil
from web.deps import api_user, page_user
from web.templating import templates

router = APIRouter()


def pick_device(devices, wanted):
	for device in devices:
		if device["id"] == wanted:
			return device
	return devices[0] if devices else None


@router.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request, device: int | None = None, user=Depends(page_user)):
	devices = await repo_devices.list_basic(user["id"])
	context = {
		"user": user,
		"devices": devices,
		"selected": pick_device(devices, device),
		"ranges": series.RANGE_LABELS,
		"steps": series.STEP_LABELS,
		"step_seconds": series.STEPS,
	}
	return templates.TemplateResponse(request, "metrics.html", context)


@router.get("/metrics/data")
async def metrics_data(
	response: Response,
	device: int,
	span: series.RangeKey = Query("24h", alias="range"),
	step: series.StepKey = "5m",
	user=Depends(api_user),
):
	owned = await repo_devices.find_owned(user["id"], device)
	if owned is None:
		raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

	range_seconds = series.RANGES[span]
	step_seconds = series.effective_step(range_seconds, series.STEPS[step])
	now_epoch = timeutil.to_epoch(timeutil.utc_now())
	buckets = series.bucket_range(now_epoch, range_seconds, step_seconds)

	rows = await repo_metrics.aggregate(owned["id"], timeutil.from_epoch(buckets[0]), step_seconds)
	latest = await repo_metrics.latest_slow(owned["id"])

	response.headers["Cache-Control"] = "no-store"
	return {
		"step": step_seconds,
		"range": range_seconds,
		"timestamps": buckets,
		"series": series.build_series(rows, buckets),
		"latest": latest,
		"last_seen": timeutil.to_epoch(owned["last_seen"]),
		"now": now_epoch,
	}
