const state = {
  token: window.localStorage.getItem("deployhub_token"),
  user: null,
};

async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    let detail = "Request failed";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (_error) {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  return response.json();
}

function renderList(targetId, items, mapper) {
  const target = document.getElementById(targetId);
  target.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("article");
    empty.className = "list-item empty";
    empty.innerHTML = "<h4>No data yet</h4><p>This area will populate after the host bridge and clients report state.</p>";
    target.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const wrapper = document.createElement("article");
    wrapper.className = "list-item";
    wrapper.innerHTML = mapper(item);
    target.appendChild(wrapper);
  });
}

function fmtBool(value) {
  return value ? "Yes" : "No";
}

function fmtDate(value) {
  if (!value) {
    return "n/a";
  }
  return new Date(value).toLocaleString();
}

function setBanner(targetId, text, type = "info") {
  const target = document.getElementById(targetId);
  target.textContent = text;
  target.dataset.state = type;
}

function updateSessionSummary() {
  const summary = document.getElementById("session-summary");
  const currentUser = document.getElementById("current-user");
  if (!state.user) {
    summary.textContent = "Login with the bootstrap admin from .env to manage paths already present on this machine.";
    currentUser.textContent = "Guest";
    return;
  }

  summary.textContent = `${state.user.full_name} • roles: ${state.user.roles.join(", ")} • permissions: ${state.user.permissions.length}`;
  currentUser.textContent = state.user.username;
}

async function loadSession() {
  if (!state.token) {
    state.user = null;
    updateSessionSummary();
    return;
  }

  try {
    state.user = await apiFetch("/api/auth/me", { method: "GET" });
    updateSessionSummary();
  } catch (error) {
    state.token = null;
    state.user = null;
    window.localStorage.removeItem("deployhub_token");
    updateSessionSummary();
    setBanner("login-message", `Session expired: ${error.message}`, "error");
  }
}

async function loadOverview() {
  const data = await apiFetch("/api/overview", { method: "GET" });

  document.getElementById("status-value").textContent = data.status;
  document.getElementById("shares-count").textContent = String(data.shares.length);
  document.getElementById("devices-count").textContent = String(data.devices.length);
  document.getElementById("auth-mode").textContent = data.auth_mode;

  renderList("shares-list", data.shares, (item) => `
    <h4>${item.name}</h4>
    <p>${item.source_path}</p>
    <div class="pill-row">
      <span class="pill">${item.access_mode}</span>
      <span class="pill">${item.publish_strategy}</span>
      <span class="pill">${item.smb_share_name || "SMB auto"}</span>
      <span class="pill">${item.policy_name || "No policy"}</span>
      <span class="pill accent">${item.access_state}</span>
    </div>
    <div class="pill-row">
      <span class="pill">SMB: ${fmtBool(item.expose_via_smb)}</span>
      <span class="pill">Web: ${fmtBool(item.expose_via_web)}</span>
      <span class="pill">Guest: ${fmtBool(item.allow_guest)}</span>
      <span class="pill">Read ${item.read_limit_mbps || 0} Mbps</span>
      <span class="pill">Bridge: ${item.last_bridge_status || "pending"}</span>
    </div>
    ${item.last_bridge_message ? `<p>${item.last_bridge_message}</p>` : ""}
    <p>${item.notes || "No note."}</p>
  `);

  renderList("devices-list", data.devices, (item) => `
    <h4>${item.hostname}</h4>
    <p>${item.ip_address} • last seen ${fmtDate(item.last_seen_at)}</p>
    <div class="pill-row">
      <span class="pill">${item.profile}</span>
      <span class="pill">${item.state}</span>
      <span class="pill">Agent ${item.agent_version || "pending"}</span>
      ${item.active_job ? `<span class="pill warning">${item.active_job}</span>` : ""}
    </div>
  `);

  renderList("jobs-list", data.jobs, (item) => `
    <h4>${item.name}</h4>
    <p>${item.job_type} • ${item.target_selector}</p>
    <div class="pill-row">
      <span class="pill">${item.state}</span>
      <span class="pill">Queued ${item.queued}</span>
      <span class="pill">OK ${item.succeeded}</span>
      <span class="pill warning">Fail ${item.failed}</span>
    </div>
    <p>${item.share_name || "No share"} ${item.package_name ? `• ${item.package_name}` : ""}</p>
    <p>${item.last_message}</p>
  `);

  renderList("policies-list", data.policies, (item) => `
    <h4>${item.name}</h4>
    <p>${item.description}</p>
    <div class="pill-row">
      <span class="pill">Read ${item.read_limit_mbps} Mbps</span>
      <span class="pill">Install only: ${fmtBool(item.install_only)}</span>
      <span class="pill">Browse: ${fmtBool(item.allow_browse)}</span>
      <span class="pill">Download: ${fmtBool(item.allow_download)}</span>
      <span class="pill">SMB: ${fmtBool(item.allow_smb)}</span>
      <span class="pill">Web: ${fmtBool(item.allow_web)}</span>
      <span class="pill">Guest: ${fmtBool(item.allow_guest)}</span>
    </div>
  `);

  renderList("packages-list", data.packages, (item) => `
    <h4>${item.name}</h4>
    <p>${item.category} • ${item.installer_type} • v${item.version}</p>
    <div class="pill-row">
      <span class="pill">${item.share_slug}</span>
      <span class="pill">Silent: ${fmtBool(item.silent_supported)}</span>
      <span class="pill">${item.is_enabled ? "Enabled" : "Disabled"}</span>
    </div>
    <p>${item.entry_path}</p>
  `);
}

async function handleLogin(event) {
  event.preventDefault();
  const payload = {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value,
  };

  try {
    const response = await apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.token = response.access_token;
    state.user = response.user;
    window.localStorage.setItem("deployhub_token", state.token);
    updateSessionSummary();
    setBanner("login-message", "Session opened successfully.", "success");
    await loadOverview();
  } catch (error) {
    setBanner("login-message", error.message, "error");
  }
}

async function handleShareCreate(event) {
  event.preventDefault();
  if (!state.token) {
    setBanner("share-message", "Login first before registering shares.", "error");
    return;
  }

  const form = new FormData(event.currentTarget);
  const payload = {
    slug: form.get("slug"),
    name: form.get("name"),
    source_path: form.get("source_path"),
    smb_share_name: form.get("smb_share_name") || null,
    access_mode: form.get("access_mode"),
    publish_strategy: form.get("publish_strategy"),
    expose_via_smb: form.get("expose_via_smb") === "on",
    expose_via_web: form.get("expose_via_web") === "on",
    allow_guest: form.get("allow_guest") === "on",
    notes: form.get("notes") || "",
  };

  try {
    await apiFetch("/api/shares", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setBanner("share-message", "Share registered successfully.", "success");
    event.currentTarget.reset();
    await loadOverview();
  } catch (error) {
    setBanner("share-message", error.message, "error");
  }
}

function handleLogout() {
  state.token = null;
  state.user = null;
  window.localStorage.removeItem("deployhub_token");
  updateSessionSummary();
  setBanner("login-message", "Local session cleared.", "info");
}

async function boot() {
  document.getElementById("login-form").addEventListener("submit", handleLogin);
  document.getElementById("share-form").addEventListener("submit", handleShareCreate);
  document.getElementById("logout-button").addEventListener("click", handleLogout);
  await loadSession();

  if (!state.token) {
    document.getElementById("status-value").textContent = "login-required";
    return;
  }

  try {
    await loadOverview();
  } catch (error) {
    document.getElementById("status-value").textContent = "error";
    setBanner("login-message", error.message, "error");
  }
}

boot();
