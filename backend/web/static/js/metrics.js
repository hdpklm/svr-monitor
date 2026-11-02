import { fetchSeries } from "./api.js";
import { renderCharts } from "./charts.js";
import { downloadCsv } from "./csv.js";
import { formatStep } from "./format.js";
import { renderReadout } from "./readout.js";

const REFRESH_MS = 60_000;
const STORAGE_KEY = "monitor_metrics_prefs";

const elements = {
	device: document.getElementById("device"),
	range: document.getElementById("range"),
	step: document.getElementById("step"),
	stats: [...document.querySelectorAll("input[name=stat]")],
	status: document.getElementById("status"),
	readout: document.getElementById("readout"),
	charts: document.getElementById("charts"),
	download: document.getElementById("download"),
};

let lastData = null;
let latestRequest = 0;

function hasOption(select, value) {
	return [...select.options].some((opt) => opt.value === String(value));
}

function loadPrefs() {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (!raw) {
			return;
		}
		const prefs = JSON.parse(raw);
		const urlParams = new URLSearchParams(location.search);
		if (!urlParams.has("device") && prefs.device && hasOption(elements.device, prefs.device)) {
			elements.device.value = prefs.device;
		}
		if (prefs.range && hasOption(elements.range, prefs.range)) {
			elements.range.value = prefs.range;
		}
		if (prefs.step && hasOption(elements.step, prefs.step)) {
			elements.step.value = prefs.step;
		}
		if (Array.isArray(prefs.stats) && prefs.stats.length > 0) {
			for (const input of elements.stats) {
				input.checked = prefs.stats.includes(input.value);
			}
		}
	} catch {
		// Ignore malformed localStorage data
	}
}

function savePrefs() {
	try {
		const prefs = {
			device: elements.device.value,
			range: elements.range.value,
			step: elements.step.value,
			stats: elements.stats.filter((input) => input.checked).map((input) => input.value),
		};
		localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
	} catch {
		// Ignore storage quota errors
	}
}

function readControls() {
	return {
		device: elements.device.value,
		range: elements.range.value,
		step: elements.step.value,
	};
}

function requestedStepSeconds() {
	return Number(elements.step.selectedOptions[0].dataset.seconds);
}

function visibleStats() {
	return new Set(elements.stats.filter((input) => input.checked).map((input) => input.value));
}

function describeStep(data) {
	const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
	const text = `Cada muestra agrupa ${formatStep(data.step)} · Actualizado ${timeStr}`;
	if (data.step === requestedStepSeconds()) {
		return text;
	}
	return `${text} (el periodo elegido es demasiado largo para una muestra más fina)`;
}

function draw() {
	renderCharts(elements.charts, lastData, visibleStats());
	renderReadout(elements.readout, lastData);
	elements.status.textContent = describeStep(lastData);
}

async function refresh() {
	latestRequest += 1;
	const request = latestRequest;
	try {
		const data = await fetchSeries(readControls());
		if (data === null || request !== latestRequest) {
			return;
		}
		lastData = data;
		draw();
	} catch (error) {
		if (request === latestRequest) {
			elements.status.textContent = `No se pudieron cargar los datos: ${error.message}`;
		}
	}
}

function rememberDevice() {
	history.replaceState(null, "", `?device=${elements.device.value}`);
}

loadPrefs();
rememberDevice();

elements.device.addEventListener("change", () => {
	savePrefs();
	rememberDevice();
	refresh();
});
elements.range.addEventListener("change", () => {
	savePrefs();
	refresh();
});
elements.step.addEventListener("change", () => {
	savePrefs();
	refresh();
});
elements.stats.forEach((input) =>
	input.addEventListener("change", () => {
		savePrefs();
		if (lastData) {
			draw();
		}
	}),
);
elements.download.addEventListener("click", () => {
	if (lastData) {
		downloadCsv(lastData, `metricas-${elements.device.value}-${elements.range.value}.csv`);
	}
});

window
	.matchMedia("(prefers-color-scheme: dark)")
	.addEventListener("change", () => lastData && draw());

document.addEventListener("visibilitychange", () => {
	if (!document.hidden) {
		refresh();
	}
});
setInterval(refresh, REFRESH_MS);

refresh();
