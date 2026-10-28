import { CHARTS, datasetsFor, hasData, peakValue, pickUnit } from "./chartConfig.js";
import { formatAxisTime, formatDateTime, formatUnit } from "./format.js";
import { readTheme } from "./theme.js";

const DAY_SECONDS = 86400;
const NARROW_SCREEN = 600;
const instances = new Map();

function tickLimit() {
	return window.innerWidth < NARROW_SCREEN ? 4 : 8;
}

const crosshair = {
	id: "crosshair",
	afterDatasetsDraw(chart) {
		const active = chart.tooltip?.getActiveElements?.() ?? [];
		if (active.length === 0) {
			return;
		}
		const { ctx, chartArea } = chart;
		const x = active[0].element.x;
		ctx.save();
		ctx.beginPath();
		ctx.moveTo(x, chartArea.top);
		ctx.lineTo(x, chartArea.bottom);
		ctx.lineWidth = 1;
		ctx.strokeStyle = chart.options.plugins.crosshair.color;
		ctx.stroke();
		ctx.restore();
	},
};

function ensurePanel(container, chart) {
	const existing = container.querySelector(`[data-chart="${chart.id}"]`);
	if (existing) {
		return existing;
	}
	const panel = document.createElement("section");
	panel.className = "panel";
	panel.dataset.chart = chart.id;

	const title = document.createElement("h2");
	title.textContent = chart.title;

	const wrap = document.createElement("div");
	wrap.className = "canvas-wrap";

	const canvas = document.createElement("canvas");
	canvas.setAttribute("role", "img");
	canvas.setAttribute("aria-label", `Gráfica de ${chart.title}`);

	wrap.append(canvas);
	panel.append(title, wrap);
	container.append(panel);
	return panel;
}

function buildOptions(chart, unit, theme, data, datasetCount) {
	return {
		animation: false,
		responsive: true,
		maintainAspectRatio: false,
		interaction: { mode: "index", intersect: false },
		plugins: {
			crosshair: { color: theme.crosshair },
			legend: {
				display: datasetCount > 1,
				align: "end",
				labels: { usePointStyle: true, pointStyle: "line", boxWidth: 28, color: theme.ink },
			},
			tooltip: {
				callbacks: {
					title: (items) => formatDateTime(data.timestamps[items[0].dataIndex]),
					label: (item) => `${item.dataset.label}: ${formatUnit(item.parsed.y, unit)}`,
				},
			},
		},
		scales: {
			x: {
				grid: { display: false },
				border: { color: theme.axis },
				ticks: { color: theme.ink, maxTicksLimit: tickLimit(), maxRotation: 0, autoSkipPadding: 16 },
			},
			y: {
				beginAtZero: true,
				max: chart.max,
				border: { display: false },
				grid: { color: theme.grid },
				ticks: { color: theme.ink, callback: (value) => formatUnit(value, unit) },
			},
		},
	};
}

export function renderCharts(container, data, visibleStats) {
	const theme = readTheme();
	const spansDays = data.range > DAY_SECONDS;
	const labels = data.timestamps.map((epoch) => formatAxisTime(epoch, spansDays));

	for (const chart of CHARTS) {
		const panel = ensurePanel(container, chart);
		panel.hidden = !hasData(chart, data.series);
		if (panel.hidden) {
			continue;
		}

		const unit = pickUnit(chart.units, peakValue(chart, data.series, visibleStats));
		const datasets = datasetsFor(chart, data.series, visibleStats, theme.series, unit);
		const options = buildOptions(chart, unit, theme, data, datasets.length);
		const existing = instances.get(chart.id);
		if (existing) {
			existing.data = { labels, datasets };
			existing.options = options;
			existing.update("none");
			continue;
		}
		instances.set(
			chart.id,
			new window.Chart(panel.querySelector("canvas"), {
				type: "line",
				data: { labels, datasets },
				options,
				plugins: [crosshair],
			}),
		);
	}
}
