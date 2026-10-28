import { sendJson } from "./api.js";
import { formatAge, formatDateTime } from "./format.js";

const REFRESH_MS = 60_000;

const elements = {
	add: document.getElementById("add-device"),
	dialog: document.getElementById("device-dialog"),
	form: document.getElementById("device-form"),
	title: document.getElementById("device-title"),
	submit: document.getElementById("device-submit"),
	error: document.getElementById("device-error"),
	keyDialog: document.getElementById("key-dialog"),
	keyValue: document.getElementById("key-value"),
	keyDone: document.getElementById("key-done"),
};

const state = { editingId: null };

function showError(message) {
	elements.error.textContent = message;
	elements.error.hidden = message === "";
}

function openForm({ id = null, name = "", description = "" }) {
	state.editingId = id;
	elements.title.textContent = id === null ? "Añadir dispositivo" : "Editar dispositivo";
	elements.submit.textContent = id === null ? "Crear dispositivo" : "Guardar cambios";
	elements.form.elements.name.value = name;
	elements.form.elements.description.value = description;
	showError("");
	elements.dialog.showModal();
	elements.form.elements.name.focus();
}

function readForm() {
	return {
		name: elements.form.elements.name.value.trim(),
		description: elements.form.elements.description.value.trim(),
	};
}

async function submitForm(event) {
	event.preventDefault();
	elements.submit.disabled = true;
	try {
		if (state.editingId === null) {
			const created = await sendJson("POST", "/devices", readForm());
			elements.dialog.close();
			elements.keyValue.value = created.key;
			elements.keyDialog.showModal();
		} else {
			await sendJson("PUT", `/devices/${state.editingId}`, readForm());
			location.reload();
		}
	} catch (error) {
		showError(error.message);
	} finally {
		elements.submit.disabled = false;
	}
}

async function removeDevice(row) {
	if (!confirm(`¿Eliminar "${row.dataset.name}"? También se borrarán todas sus métricas.`)) {
		return;
	}
	try {
		await sendJson("DELETE", `/devices/${row.dataset.id}`);
		location.reload();
	} catch (error) {
		alert(error.message);
	}
}

async function copyField(button) {
	const field = document.getElementById(button.dataset.copy);
	await navigator.clipboard.writeText(field.value);
	const label = button.textContent;
	button.textContent = "Copiado";
	setTimeout(() => {
		button.textContent = label;
	}, 1500);
}

function renderTimes() {
	const now = Math.floor(Date.now() / 1000);
	for (const node of document.querySelectorAll("time[data-epoch]")) {
		const epoch = Number(node.dataset.epoch);
		if (!node.dataset.epoch) {
			node.textContent = "Nunca";
			continue;
		}
		node.textContent = formatAge(Math.max(0, now - epoch));
		node.title = formatDateTime(epoch);
	}
}

elements.add?.addEventListener("click", () => openForm({}));
elements.form.addEventListener("submit", submitForm);
elements.keyDone.addEventListener("click", () => location.reload());
elements.keyDialog.addEventListener("cancel", () => location.reload());

document.querySelectorAll("[data-close]").forEach((button) =>
	button.addEventListener("click", () => button.closest("dialog").close()),
);
document.querySelectorAll("[data-copy]").forEach((button) =>
	button.addEventListener("click", () => copyField(button)),
);
document.querySelectorAll("tbody tr").forEach((row) => {
	row.querySelector("[data-action=edit]").addEventListener("click", () =>
		openForm({ id: Number(row.dataset.id), name: row.dataset.name, description: row.dataset.description }),
	);
	row.querySelector("[data-action=delete]").addEventListener("click", () => removeDevice(row));
});

renderTimes();
setInterval(() => {
	if (!document.hidden && !document.querySelector("dialog[open]")) {
		location.reload();
	}
}, REFRESH_MS);
