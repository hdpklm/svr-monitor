const AXIS_TIME = { hour: "2-digit", minute: "2-digit" };
const AXIS_DAY = { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" };
const FULL = { dateStyle: "medium", timeStyle: "medium" };

function fixed(value, digits) {
	return value.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function formatAxisTime(epoch, spansDays) {
	return new Date(epoch * 1000).toLocaleString(undefined, spansDays ? AXIS_DAY : AXIS_TIME);
}

export function formatDateTime(epoch) {
	return new Date(epoch * 1000).toLocaleString(undefined, FULL);
}

export function formatUnit(value, unit) {
	return `${value.toLocaleString(undefined, { maximumFractionDigits: unit.digits })} ${unit.label}`;
}

export function formatPercent(value) {
	return `${fixed(value, 1)} %`;
}

export function formatTemperature(value) {
	return `${fixed(value, 1)} °C`;
}

export function formatLoad(value) {
	return fixed(value, 2);
}

export function formatDuration(seconds) {
	const days = Math.floor(seconds / 86400);
	const hours = Math.floor((seconds % 86400) / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	if (days > 0) {
		return `${days} d ${hours} h`;
	}
	if (hours > 0) {
		return `${hours} h ${minutes} min`;
	}
	return `${minutes} min`;
}

export function formatAge(seconds) {
	if (seconds < 60) {
		return "ahora";
	}
	if (seconds < 3600) {
		return `hace ${Math.floor(seconds / 60)} min`;
	}
	if (seconds < 86400) {
		return `hace ${Math.floor(seconds / 3600)} h`;
	}
	return `hace ${Math.floor(seconds / 86400)} d`;
}

export function formatStep(seconds) {
	if (seconds >= 3600) {
		return `${seconds / 3600} h`;
	}
	return `${seconds / 60} min`;
}
