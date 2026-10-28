export const STATS = [
	{ key: "avg", label: "media", width: 2, dash: [] },
	{ key: "max", label: "máx", width: 1, dash: [6, 4] },
	{ key: "min", label: "mín", width: 1, dash: [2, 3] },
];

const PERCENT = [{ factor: 1, label: "%", digits: 1 }];

export const CHARTS = [
	{
		id: "cpu",
		title: "CPU",
		max: 100,
		units: PERCENT,
		series: [{ name: "cpu_percent", label: "CPU" }],
	},
	{
		id: "ram",
		title: "RAM",
		max: 100,
		units: PERCENT,
		series: [{ name: "ram_percent", label: "RAM" }],
	},
	{
		id: "ram_used",
		title: "RAM usada",
		units: [
			{ factor: 1, label: "MB", digits: 0 },
			{ factor: 1024, label: "GB", digits: 2 },
		],
		series: [{ name: "ram_used_mb", label: "RAM usada" }],
	},
	{
		id: "network",
		title: "Red",
		units: [
			{ factor: 1, label: "kbps", digits: 0 },
			{ factor: 1000, label: "Mbps", digits: 2 },
			{ factor: 1_000_000, label: "Gbps", digits: 2 },
		],
		series: [
			{ name: "net_rx_kbps", label: "Bajada" },
			{ name: "net_tx_kbps", label: "Subida" },
		],
	},
	{
		id: "disk_io",
		title: "Disco (lectura y escritura)",
		units: [{ factor: 1, label: "MB/s", digits: 2 }],
		series: [
			{ name: "disk_read_mbps", label: "Lectura" },
			{ name: "disk_write_mbps", label: "Escritura" },
		],
	},
];

export function hasData(chart, seriesData) {
	return chart.series.some((entry) => seriesData[entry.name]);
}

export function pickUnit(units, peak) {
	let chosen = units[0];
	for (const unit of units) {
		if (peak >= unit.factor) {
			chosen = unit;
		}
	}
	return chosen;
}

export function peakValue(chart, seriesData, visibleStats) {
	let peak = 0;
	for (const entry of chart.series) {
		const values = seriesData[entry.name];
		if (!values) {
			continue;
		}
		for (const stat of STATS) {
			if (!visibleStats.has(stat.key)) {
				continue;
			}
			for (const value of values[stat.key]) {
				if (value !== null && value > peak) {
					peak = value;
				}
			}
		}
	}
	return peak;
}

export function scaleValues(values, factor) {
	return values.map((value) => (value === null ? null : value / factor));
}

export function datasetsFor(chart, seriesData, visibleStats, colors, unit) {
	const datasets = [];
	chart.series.forEach((entry, index) => {
		const values = seriesData[entry.name];
		if (!values) {
			return;
		}
		for (const stat of STATS) {
			if (!visibleStats.has(stat.key)) {
				continue;
			}
			datasets.push({
				label: `${entry.label} · ${stat.label}`,
				data: scaleValues(values[stat.key], unit.factor),
				borderColor: colors[index],
				borderWidth: stat.width,
				borderDash: stat.dash,
				pointRadius: 0,
				pointHoverRadius: 0,
				tension: 0,
				spanGaps: false,
			});
		}
	});
	return datasets;
}
