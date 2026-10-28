async function readError(response) {
	try {
		const body = await response.json();
		return typeof body.detail === "string" ? body.detail : "Los datos no son válidos";
	} catch {
		return `Error ${response.status}`;
	}
}

function redirectToLogin() {
	location.href = "/login";
	return null;
}

export async function fetchSeries({ device, range, step }) {
	const query = new URLSearchParams({ device, range, step });
	const response = await fetch(`/metrics/data?${query}`, {
		headers: { Accept: "application/json" },
		cache: "no-store",
	});
	if (response.status === 401) {
		return redirectToLogin();
	}
	if (!response.ok) {
		throw new Error(await readError(response));
	}
	return response.json();
}

export async function sendJson(method, url, body) {
	const response = await fetch(url, {
		method,
		headers: { "Content-Type": "application/json", Accept: "application/json" },
		body: body === undefined ? undefined : JSON.stringify(body),
	});
	if (response.status === 401) {
		return redirectToLogin();
	}
	if (!response.ok) {
		throw new Error(await readError(response));
	}
	return response.status === 204 ? null : response.json();
}
