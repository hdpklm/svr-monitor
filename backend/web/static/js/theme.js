function cssVar(name) {
	return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function readTheme() {
	return {
		ink: cssVar("--ink-2"),
		grid: cssVar("--line"),
		axis: cssVar("--line-strong"),
		crosshair: cssVar("--ink-3"),
		series: [cssVar("--series-1"), cssVar("--series-2")],
	};
}
