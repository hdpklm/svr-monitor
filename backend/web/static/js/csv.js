const STAT_KEYS = ["avg", "min", "max"];

export function toCsv(data) {
	const names = Object.keys(data.series).sort();
	const header = ["timestamp", ...names.flatMap((name) => STAT_KEYS.map((stat) => `${name}_${stat}`))];
	const rows = data.timestamps.map((epoch, index) => [
		new Date(epoch * 1000).toISOString(),
		...names.flatMap((name) => STAT_KEYS.map((stat) => data.series[name][stat][index] ?? "")),
	]);
	return [header, ...rows].map((row) => row.join(",")).join("\n");
}

export function downloadCsv(data, filename) {
	const blob = new Blob([toCsv(data)], { type: "text/csv;charset=utf-8" });
	const link = document.createElement("a");
	link.href = URL.createObjectURL(blob);
	link.download = filename;
	link.click();
	URL.revokeObjectURL(link.href);
}
