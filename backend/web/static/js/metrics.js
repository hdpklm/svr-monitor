import { fetchSeries } from "./api.js";
import { renderCharts } from "./charts.js";
import { downloadCsv } from "./csv.js";
import { formatStep } from "./format.js";
import { renderReadout } from "./readout.js";

const REFRESH_MS = 60_000;

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
	const text = `Cada muestra agrupa ${formatStep(data.step)}`;
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

elements.device.addEventListener("change", () => {
	rememberDevice();
	refresh();
});
elements.range.addEventListener("change", refresh);
elements.step.addEventListener("change", refresh);
elements.stats.forEach((input) =>
	input.addEventListener("change", () => {
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
setInterval(() => {
	if (!document.hidden) {
		refresh();
	}
}, REFRESH_MS);

refresh();
