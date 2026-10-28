import {
	formatAge,
	formatDuration,
	formatLoad,
	formatPercent,
	formatTemperature,
} from "./format.js";

const DISK_PREFIX = "disk_used_percent:";

const LIVE_ITEMS = [
	{ series: "cpu_percent", label: "CPU", format: formatPercent },
	{ series: "ram_percent", label: "RAM", format: formatPercent },
];

const SLOW_ITEMS = [
	{ key: "load1", label: "Carga (1 min)", format: formatLoad },
	{ key: "swap_percent", label: "Swap", format: formatPercent },
	{ key: "cpu_temp_c", label: "Temperatura", format: formatTemperature },
	{ key: "uptime_s", label: "Encendido", format: formatDuration },
];

export function lastValue(values) {
	for (let index = values.length - 1; index >= 0; index -= 1) {
		if (values[index] !== null) {
			return values[index];
		}
	}
	return null;
}

function lastSeenText(data) {
	if (data.last_seen === null) {
		return "Sin datos";
	}
	return formatAge(Math.max(0, data.now - data.last_seen));
}

export function buildItems(data) {
	const items = [{ label: "Última muestra", value: lastSeenText(data) }];

	for (const entry of LIVE_ITEMS) {
		const values = data.series[entry.series];
		const value = values ? lastValue(values.avg) : null;
		if (value !== null) {
			items.push({ label: entry.label, value: entry.format(value) });
		}
	}
	for (const entry of SLOW_ITEMS) {
		if (data.latest[entry.key] !== undefined) {
			items.push({ label: entry.label, value: entry.format(data.latest[entry.key]) });
		}
	}
	for (const key of Object.keys(data.latest).sort()) {
		if (key.startsWith(DISK_PREFIX)) {
			items.push({ label: `Disco ${key.slice(DISK_PREFIX.length)}`, value: formatPercent(data.latest[key]) });
		}
	}
	return items;
}

function buildNode(item) {
	const node = document.createElement("div");
	node.className = "readout-item";

	const label = document.createElement("div");
	label.className = "readout-label";
	label.textContent = item.label;

	const value = document.createElement("div");
	value.className = "readout-value";
	value.textContent = item.value;

	node.append(label, value);
	return node;
}

export function renderReadout(container, data) {
	container.replaceChildren(...buildItems(data).map(buildNode));
}
