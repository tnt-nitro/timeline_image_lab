function byId(id) {
  return document.getElementById(id);
}

async function loadMerged() {
  const path = byId("mergedPath").value.trim();
  if (!path) return;

  try {
    const res = await fetch(path);
    if (!res.ok) {
      alert("Kann Merged-JSON nicht laden: " + res.status);
      return;
    }
    const d = await res.json();
    bindMerged(d, path);
  } catch (e) {
    alert("Fehler beim Laden der Datei.\nHinweis: Bei Direktöffnung per file:// blockieren Browser oft fetch().\nNutze ggf. einen lokalen Static-Server (z. B. python -m http.server).");
    console.error(e);
  }
}

function bindMerged(d, mergedPath) {
  // Header
  byId("runId").textContent = d.run_id || "–";
  byId("version").textContent = d.version != null ? String(d.version) : "–";
  if (d.summary) {
    const s = d.summary;
    byId("summary").textContent =
      `${s.issues_total ?? 0} | C:${s.critical ?? 0} M:${s.major ?? 0} m:${s.minor ?? 0}`;
  } else {
    byId("summary").textContent = "–";
  }

  // Basis-Pfad für den Run ableiten (relativ zum Dashboard)
  // Beispiel: ../runs/2026-02-10_ref01/merged/merged_v002.json
  const mergedUrl = new URL(mergedPath, window.location.href);
  const parts = mergedUrl.pathname.split("/");
  // Entferne ".../merged/merged_vXXX.json"
  parts.pop(); // merged_vXXX.json
  parts.pop(); // merged
  const runBase = parts.join("/") + "/";

  // Trace: Bilder
  const trace = d.trace || {};
  const renderPrev = trace.render_prev ? runBase + trace.render_prev : "";
  const renderNext = trace.render_next ? runBase + trace.render_next : "";
  const annotationPng = trace.annotation_png ? runBase + trace.annotation_png : "";

  byId("renderPrev").src = renderPrev || "";
  byId("renderNext").src = renderNext || "";
  byId("annotationOverlay").src = annotationPng || "";

  // Overlay aus, wenn keine Annotation
  if (!annotationPng) {
    byId("toggleOverlay").checked = false;
    byId("annotationOverlay").classList.add("hidden");
  }

  // Feedback-Items laden (separat, wenn Pfad vorhanden)
  const inputs = d.inputs || {};
  const feedbackRel = inputs.feedback;
  if (feedbackRel) {
    const feedbackUrl = runBase + feedbackRel;
    loadFeedbackItems(feedbackUrl);
  } else {
    renderFeedbackItems([]);
  }

  // Prompts laden (nur als Text, wenn vorhanden)
  loadPromptText(d.derived?.prompt_final || d.inputs?.prompt_base, "promptFinal");
  loadPromptText(d.inputs?.prompt_base, "promptBase");
  loadPromptText(d.derived?.prompt_patch, "promptPatch");
}

async function loadFeedbackItems(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      renderFeedbackItems([]);
      return;
    }
    const fb = await res.json();
    renderFeedbackItems(fb.items || []);
  } catch (e) {
    console.error(e);
    renderFeedbackItems([]);
  }
}

function renderFeedbackItems(items) {
  const list = byId("feedbackList");
  list.innerHTML = "";
  if (!items.length) {
    const p = document.createElement("p");
    p.textContent = "Keine Feedback-Items.";
    p.style.fontSize = "12px";
    p.style.color = "#666";
    list.appendChild(p);
    return;
  }

  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = "feedback-item";

    const header = document.createElement("div");
    header.className = "feedback-item-header";
    const left = document.createElement("div");
    left.textContent = item.area || "(ohne Area)";
    const right = document.createElement("div");

    const typeSpan = document.createElement("span");
    typeSpan.className = "badge " + (item.type || "");
    typeSpan.textContent = item.type || "?";

    const sevSpan = document.createElement("span");
    sevSpan.className = "badge " + (item.severity || "");
    sevSpan.textContent = item.severity || "?";

    right.appendChild(typeSpan);
    right.appendChild(document.createTextNode(" "));
    right.appendChild(sevSpan);

    header.appendChild(left);
    header.appendChild(right);

    const body = document.createElement("div");
    body.className = "feedback-item-body";
    const note = document.createElement("div");
    note.textContent = item.note || "";
    const exp = document.createElement("div");
    if (item.expected) {
      exp.textContent = "Expected: " + item.expected;
      exp.className = "feedback-item-meta";
    }

    const meta = document.createElement("div");
    meta.className = "feedback-item-meta";
    meta.textContent = `ID: ${item.annotation_id || "-"} | Tool: ${item.annotation_ref?.tool || "-"} | Color: ${item.annotation_ref?.color || "-"}`;

    body.appendChild(note);
    if (item.expected) body.appendChild(exp);
    body.appendChild(meta);

    div.appendChild(header);
    div.appendChild(body);
    list.appendChild(div);
  });
}

async function loadPromptText(relPath, targetId) {
  const pre = byId(targetId);
  if (!relPath) {
    pre.textContent = "(keine Datei)";
    return;
  }
  try {
    const res = await fetch("../" + relPath.replace(/^\.?\//, ""));
    if (!res.ok) {
      pre.textContent = "(nicht ladbar: " + relPath + ")";
      return;
    }
    const txt = await res.text();
    pre.textContent = txt;
  } catch (e) {
    console.error(e);
    pre.textContent = "(Fehler beim Laden: " + relPath + ")";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  byId("loadBtn").addEventListener("click", loadMerged);
  byId("toggleOverlay").addEventListener("change", (e) => {
    const overlay = byId("annotationOverlay");
    if (e.target.checked && overlay.src) {
      overlay.classList.remove("hidden");
    } else {
      overlay.classList.add("hidden");
    }
  });

  // Optional: beim Start versuchen, Default-Pfad zu laden
  // loadMerged();
});

