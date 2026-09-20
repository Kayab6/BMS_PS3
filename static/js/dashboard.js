/**
 * MEDFLOW Hospital Operations Center - Core Dashboard Engine
 * Orchestrates real-time telemetry, auto-refresh polling, data rendering,
 * ML wait time predictions, and Hugging Face AI operations insights.
 */

// State tracking
let autoRefreshInterval = null;
let isAutoRefreshActive = true;
const REFRESH_RATE_MS = 3000;

// Current system telemetry cache
let currentMetricsCache = null;
let currentResourcesCache = null;

/**
 * Main application initialization
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log('MEDFLOW Operations Center initializing...');

  // 1. Initialize charts
  if (typeof initCharts === 'function') {
    initCharts();
  }

  // 2. Initialize simulation controls
  if (typeof initSimulationControls === 'function') {
    initSimulationControls();
  }

  // 3. Setup event listeners
  setupEventListeners();

  // 4. Load initial dashboard data immediately
  loadDashboard();

  // 5. Start auto-refresh polling loop (every 3 seconds)
  startAutoRefresh();
});

/**
 * Setup UI interaction listeners
 */
function setupEventListeners() {
  // Auto-refresh toggle switch
  const autoRefreshToggle = document.getElementById('autoRefreshToggle');
  if (autoRefreshToggle) {
    autoRefreshToggle.addEventListener('change', (e) => {
      isAutoRefreshActive = e.target.checked;
      if (isAutoRefreshActive) {
        startAutoRefresh();
      } else {
        stopAutoRefresh();
      }
    });
  }

  // Inventory tab switching
  const invTabs = document.querySelectorAll('.inv-tab-btn');
  invTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      invTabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.inventory-section').forEach(s => s.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.dataset.target;
      const targetSection = document.getElementById(targetId);
      if (targetSection) targetSection.classList.add('active');
    });
  });

  // Queue search & filter
  const queueSearch = document.getElementById('queueSearchInput');
  const deptFilter = document.getElementById('queueDeptFilter');
  if (queueSearch) queueSearch.addEventListener('input', filterQueueTable);
  if (deptFilter) deptFilter.addEventListener('change', filterQueueTable);

  // ML Prediction form submission
  const predictBtn = document.getElementById('predictWaitBtn');
  if (predictBtn) {
    predictBtn.addEventListener('click', handlePredictWaitTime);
  }

  // ML Quick Sync with Live State button
  const syncBtn = document.getElementById('syncHospitalStateBtn');
  if (syncBtn) {
    syncBtn.addEventListener('click', syncFormWithHospitalState);
  }

  // Hugging Face AI Insight button
  const explainBtn = document.getElementById('generateAiExplainBtn');
  if (explainBtn) {
    explainBtn.addEventListener('click', handleGenerateAiInsight);
  }
}

/**
 * Auto-refresh polling management
 */
function startAutoRefresh() {
  stopAutoRefresh();
  isAutoRefreshActive = true;
  autoRefreshInterval = setInterval(() => {
    if (isAutoRefreshActive) {
      loadDashboard();
    }
  }, REFRESH_RATE_MS);
}

function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
}

/**
 * Master Load Dashboard Routine - Fetches all API data
 */
async function loadDashboard() {
  try {
    await Promise.allSettled([
      fetchMetrics(),
      fetchResources(),
      fetchQueue(),
      fetchBloodBank(),
      fetchMedicines(),
      fetchEquipment(),
      fetchAlerts(),
      fetchStrategyComparison()
    ]);
  } catch (err) {
    console.error('Error during dashboard load:', err);
  }
}

/**
 * 3. KPI Cards - GET /api/metrics
 */
async function fetchMetrics() {
  try {
    const res = await fetch('/api/metrics');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    currentMetricsCache = data;

    // Extract or compute 6 KPI values
    const patientsServed = data.patients_served ?? (data.total_patients - (data.waiting_patients || 0));
    const patientsWaiting = data.waiting_patients ?? data.queue_length ?? 0;
    const criticalPatients = data.critical_patients ?? Math.round(patientsWaiting * 0.25);
    const avgWaitTime = data.average_waiting_time ?? 24.5;
    const icuUtil = data.icu_utilization ?? 75.0;
    const overallUtil = data.overall_resource_utilization ?? 68.0;

    // Update DOM
    updateAnimatedCounter('kpiServed', patientsServed);
    updateAnimatedCounter('kpiWaiting', patientsWaiting);
    updateAnimatedCounter('kpiCritical', criticalPatients);
    updateAnimatedCounter('kpiAvgWait', avgWaitTime.toFixed(1));
    updateAnimatedCounter('kpiIcuUtil', Math.round(icuUtil));
    updateAnimatedCounter('kpiOverallUtil', Math.round(overallUtil));

    // Update queue chart with new queue length
    if (typeof updateQueueTrendChartData === 'function') {
      updateQueueTrendChartData(patientsWaiting);
    }
  } catch (err) {
    console.debug('Using cached/fallback metrics data:', err);
  }
}

/**
 * 4. Resource Status - GET /api/resources
 */
async function fetchResources() {
  try {
    const res = await fetch('/api/resources');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    currentResourcesCache = data;

    // Support both schema formats (top-level keys or nested hospital.r_type)
    const normalizeResource = (item, defaultTotal, defaultAvail) => {
      if (!item) return { total: defaultTotal, available: defaultAvail, allocated: defaultTotal - defaultAvail, utilization: 0, status: 'Good' };
      const total = item.total ?? item.capacity ?? defaultTotal;
      const available = item.available ?? (total - (item.allocated ?? 0));
      const allocated = item.allocated ?? Math.max(0, total - available);
      const util = total > 0 ? (allocated / total) * 100 : 0;
      let status = 'Optimal';
      let statusClass = 'badge-green';
      if (util >= 80) {
        status = 'Critical';
        statusClass = 'badge-red';
      } else if (util >= 60) {
        status = 'Moderate';
        statusClass = 'badge-amber';
      }
      return { total, available, allocated, utilization: util, status, statusClass };
    };

    const resources = {
      beds: normalizeResource(data.general_beds || data.beds, 50, 35),
      icu: normalizeResource(data.icu_beds || data.icu, 10, 2),
      doctors: normalizeResource(data.doctors, 20, 7),
      nurses: normalizeResource(data.nurses, 40, 16),
      or: normalizeResource(data.operating_rooms || data.or, 5, 2),
      ambulances: normalizeResource(data.ambulances, 5, 3)
    };

    // Render 6 resource cards
    renderResourceCard('resGenBeds', resources.beds);
    renderResourceCard('resIcuBeds', resources.icu);
    renderResourceCard('resDoctors', resources.doctors);
    renderResourceCard('resNurses', resources.nurses);
    renderResourceCard('resOperatingRooms', resources.or);
    renderResourceCard('resAmbulances', resources.ambulances);

    // Update resource utilization chart
    if (typeof updateResourceChartData === 'function') {
      updateResourceChartData(data);
    }
  } catch (err) {
    console.debug('Using fallback resource cards data:', err);
  }
}

function renderResourceCard(elementId, res) {
  const container = document.getElementById(elementId);
  if (!container) return;

  const countEl = container.querySelector('.resource-count');
  const barEl = container.querySelector('.progress-fill');
  const statusEl = container.querySelector('.resource-status-tag');
  const utilEl = container.querySelector('.resource-util-label');

  if (countEl) {
    countEl.innerHTML = `<strong>${res.available}</strong> / ${res.total} Avail`;
  }
  if (barEl) {
    barEl.style.width = `${Math.min(100, Math.max(5, res.utilization))}%`;
    barEl.className = 'progress-fill ' + (
      res.utilization >= 80 ? 'status-critical' :
      res.utilization >= 60 ? 'status-moderate' : 'status-good'
    );
  }
  if (statusEl) {
    statusEl.textContent = res.status;
    statusEl.className = 'resource-status-tag ' + res.statusClass;
  }
  if (utilEl) {
    utilEl.textContent = `${Math.round(res.utilization)}% in use`;
  }
}

/**
 * 5. Patient Queue - GET /api/queue
 */
let cachedQueueList = [];

async function fetchQueue() {
  try {
    const res = await fetch('/api/queue');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const queue = await res.json();
    cachedQueueList = queue;

    renderQueueTable(queue);

    // Update waiting time chart
    if (typeof updateWaitTimeChartData === 'function') {
      const avg = currentMetricsCache?.average_waiting_time ?? 25;
      updateWaitTimeChartData(queue, avg);
    }
  } catch (err) {
    console.debug('Error fetching patient queue:', err);
  }
}

function renderQueueTable(queue) {
  const tbody = document.getElementById('queueTableBody');
  const countBadge = document.getElementById('queueCountBadge');
  if (!tbody) return;

  if (countBadge) {
    countBadge.textContent = `${queue.length} Active`;
  }

  if (queue.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; padding: 2rem; color: var(--text-muted);">
          No patients waiting in queue. System optimal.
        </td>
      </tr>
    `;
    return;
  }

  // Sort by priority descending (or queue_position ascending)
  const sorted = [...queue].sort((a, b) => {
    if (b.priority != null && a.priority != null) return b.priority - a.priority;
    if (b.urgency !== a.urgency) return b.urgency - a.urgency;
    return (a.queue_position || 0) - (b.queue_position || 0);
  });

  tbody.innerHTML = sorted.map((p, idx) => {
    const urgency = p.urgency || 3;
    const urgencyClass = `urgency-${urgency}`;
    const waitTime = p.estimated_waiting_time ?? p.wait_time ?? Math.round(15 + idx * 4);
    const priority = p.priority != null ? Number(p.priority).toFixed(1) : (10.0 + urgency * 2 - idx * 0.2).toFixed(1);
    const patientId = p.patient_id ? `P-${p.patient_id}` : `P-${100 + idx}`;
    const name = p.name || `Patient #${p.patient_id || idx + 1}`;
    const dept = p.department || 'General Medicine';
    const status = (p.status || 'waiting').toUpperCase();

    return `
      <tr data-dept="${dept.toLowerCase()}" data-search="${name.toLowerCase()} ${patientId.toLowerCase()}">
        <td class="patient-id-cell">
          <div style="font-weight: 700;">${name}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${patientId}</div>
        </td>
        <td>
          <span class="badge-pill" style="background: rgba(255, 255, 255, 0.06); color: var(--text-secondary); border: 1px solid var(--border-color);">
            ${dept}
          </span>
        </td>
        <td>
          <span class="urgency-badge ${urgencyClass}">
            Level ${urgency}
          </span>
        </td>
        <td style="font-family: var(--font-mono); color: var(--text-primary);">
          ${waitTime} <span style="font-size: 0.75rem; color: var(--text-muted);">min</span>
        </td>
        <td>
          <span class="priority-score">${priority}</span>
        </td>
        <td>
          <span class="badge-pill ${status === 'ALLOCATED' || status === 'IN_TREATMENT' ? 'badge-blue' : 'badge-amber'}">
            ${status}
          </span>
        </td>
      </tr>
    `;
  }).join('');
}
/* ============================================================
   MEDFLOW — Dashboard & Routing (dashboard.js)
   SPA router, API layer, dashboard logic, queue logic
   ============================================================ */

'use strict';

// ── State ─────────────────────────────────────────────────────
const APP = {
  patients: [],
  queue: [],
  resources: {},
  metrics: {},
  currentPage: 'dashboard',
};

// ── API Layer ─────────────────────────────────────────────────
async function api(path, opts = {}) {
  try {
    const res = await fetch(path, opts);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[MEDFLOW API] ${path}`, e.message);
    return null;
  }
}

async function fetchMetrics()   { return await api('/api/metrics'); }
async function fetchPatients()  { return await api('/api/patients'); }
async function fetchQueue()     { return await api('/api/queue'); }
async function fetchResources() { return await api('/api/resources'); }

// ── Toast ─────────────────────────────────────────────────────
function showToast(msg, duration = 2800) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

// ── Clock ─────────────────────────────────────────────────────
function startClock() {
  const el = document.getElementById('header-clock');
  if (!el) return;
  function tick() {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
  }
  tick();
  setInterval(tick, 30000);
}

// ── Page Router ───────────────────────────────────────────────
const PAGE_META = {
  dashboard:   { title: 'Dashboard',              subtitle: 'Real-time hospital operations overview' },
  queue:       { title: 'Patient Priority Queue', subtitle: 'Live queue managed by the MEDFLOW scheduling algorithm' },
  'wait-time': { title: 'Wait Time Prediction',   subtitle: 'Predict patient waiting times using real-time hospital conditions' },
  resources:   { title: 'Resource Management',    subtitle: 'Monitor, allocate and optimise hospital resources in real time' },
  alerts:      { title: 'Operational Alerts',     subtitle: 'Stay ahead of emerging hospital operational constraints' },
  inventory:   { title: 'Inventory',              subtitle: 'Track supplies, availability and critical shortages' },
  analytics:   { title: 'Analytics & Reports',    subtitle: 'Turn hospital data into operational insights' },
  'ai-insights':{ title: 'AI Operations Insights',subtitle: 'Turn real-time hospital data into actionable operational insights' },
};

function navigateTo(page) {
  if (APP.currentPage === page) return;
  APP.currentPage = page;

  // Update pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(`page-${page}`);
  if (target) target.classList.add('active');

  // Update nav items
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const navItem = document.getElementById(`nav-${page}`);
  if (navItem) navItem.classList.add('active');

  // Update header
  const meta = PAGE_META[page] || {};
  const titleEl = document.getElementById('header-title');
  const subEl   = document.getElementById('header-subtitle');
  if (titleEl) titleEl.textContent = meta.title || page;
  if (subEl)   subEl.textContent   = meta.subtitle || '';

  // Show/hide run simulation button
  const btn = document.getElementById('btn-run-simulation');
  if (btn) btn.style.display = page === 'dashboard' ? '' : 'none';

  // Trigger page load
  onPageLoad(page);
}

function onPageLoad(page) {
  switch (page) {
    case 'dashboard':   loadDashboard(); break;
    case 'queue':       loadQueue(); break;
    case 'resources':   loadResourceCharts(); break;
    case 'alerts':      loadAlerts(); break;
    case 'inventory':   loadInventory(); break;
    case 'analytics':   loadAnalytics(); break;
    case 'ai-insights': loadAISignals(); break;
    case 'wait-time':
      initChartPredictByDept('chart-predict-by-dept');
      initChartPredictTrend('chart-predict-trend');
      break;
  }
}

// ── Nav click bindings ────────────────────────────────────────
function bindNav() {
  document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.page));
  });
}

// ── DASHBOARD ─────────────────────────────────────────────────
async function loadDashboard() {
  const [metrics, patients, resources] = await Promise.all([
    fetchMetrics(), fetchPatients(), fetchResources(),
  ]);

  if (metrics) {
    APP.metrics = metrics;
    setText('dash-waiting',   metrics.waiting_patients ?? '—');
    setText('dash-wait-time', metrics.average_waiting_time != null ? metrics.average_waiting_time.toFixed(1) : '—');
    setText('dash-beds',      metrics.beds_available ?? '—');
    setText('dash-icu',       metrics.icu_available ?? '—');
    setText('dash-total',     metrics.total_patients ?? '—');
    setText('dash-doctors',   metrics.doctors_available ?? '—');
    setText('dash-nurses',    metrics.nurses_available ?? '—');
    setText('dash-blood',     `${metrics.blood_units_available ?? '—'} units`);
    setText('dash-medicine',  `${metrics.medicine_stock ?? '—'} items`);
  }

  if (patients) {
    APP.patients = patients;
    initChartDeptQueue('chart-dept-queue', patients);
    initChartUrgencyMix('chart-urgency-mix', patients);
  }

  if (resources) {
    APP.resources = resources;
    initChartResourceSnapshot('chart-resource-snapshot', resources);
  }
}

// ── QUEUE ─────────────────────────────────────────────────────
async function loadQueue() {
  const queueData = await fetchQueue();
  if (!queueData) return;
  APP.queue = queueData;

  // Stats
  const total = queueData.length;
  const critical = queueData.filter(p => p.urgency === 5).length;
  const high     = queueData.filter(p => p.urgency === 4).length;
  const avgWait  = total > 0
    ? (queueData.reduce((s, p) => s + (p.estimated_waiting_time || 0), 0) / total).toFixed(1)
    : '0';

  setText('q-total',    total);
  setText('q-critical', critical);
  setText('q-high',     high);
  setText('q-avg-wait', avgWait);

  renderQueueTable(queueData);

  initChartQueueDept('chart-queue-dept', queueData);
  initChartQueueWait('chart-queue-wait', queueData);
}

function renderQueueTable(data) {
  const deptFilter = document.getElementById('queue-dept-filter')?.value || '';
  const filtered = deptFilter ? data.filter(p => p.department === deptFilter) : data;

  const tbody = document.getElementById('queue-tbody');
  if (!tbody) return;

  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:32px;color:var(--text-tertiary);">No patients in queue</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((p, idx) => {
    const urgencyColor = {1:'green',2:'green',3:'medium',4:'high',5:'critical'}[p.urgency] || 'medium';
    const urgencyLabel = {1:'Low',2:'Moderate',3:'Medium',4:'High',5:'Critical'}[p.urgency] || p.urgency;
    const statusClass  = p.status === 'allocated' ? 'badge-allocated' : 'badge-waiting';

    return `
      <tr class="alert-row">
        <td style="font-weight:600;color:var(--text-tertiary);">${idx + 1}</td>
        <td style="font-weight:600;">P-${String(p.patient_id).padStart(3,'0')}</td>
        <td>${p.department}</td>
        <td>
          <div style="display:flex;align-items:center;gap:8px;">
            <span class="badge badge-${urgencyColor}">${urgencyLabel}</span>
            <span style="font-size:11px;color:var(--text-tertiary);">L${p.urgency}</span>
          </div>
        </td>
        <td style="font-weight:600;">${p.estimated_waiting_time ?? '—'} min</td>
        <td><span class="badge ${statusClass}">${p.status}</span></td>
      </tr>
    `;
  }).join('');
}

function filterQueue() {
  renderQueueTable(APP.queue);
}

// ── SIMULATION ────────────────────────────────────────────────
async function runSimulation() {
  const btn = document.getElementById('btn-run-simulation');
  if (btn) {
    btn.innerHTML = '<span class="loading-spinner"></span> Running...';
    btn.disabled = true;
  }

  const result = await api('/api/simulation/start', { method: 'POST', headers: {'Content-Type':'application/json'} });

  if (btn) {
    btn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
      Run Simulation
    `;
    btn.disabled = false;
  }

  if (result?.success) {
    showToast('✓ Simulation complete — data updated');
    await loadDashboard();
  } else {
    showToast('⚠ Simulation encountered an issue');
  }
}

// ── RESOURCE CHARTS ───────────────────────────────────────────
async function loadResourceCharts() {
  const resources = await fetchResources();
  if (resources) APP.resources = resources;

  // Update live stats from API if available
  if (resources) {
    setText('res-beds-avail',    resources.beds?.available ?? 5);
    setText('res-icu-avail',     resources.icu?.available ?? 2);
    setText('res-doctors-avail', resources.doctors?.available ?? 10);
    setText('res-nurses-avail',  resources.nurses?.available ?? 18);
  }

  initChartResourceUtil('chart-resource-util');
  initChartResourceTrend('chart-resource-trend');
}

// ── ANALYTICS ─────────────────────────────────────────────────
async function loadAnalytics() {
  const [patients, queueData, metrics] = await Promise.all([
    fetchPatients(), fetchQueue(), fetchMetrics(),
  ]);

  if (patients) {
    initChartPatientFlow('chart-patient-flow', patients);
    initChartCaseDist('chart-case-dist', patients);
    initChartAdmDis('chart-adm-dis', patients.length);
  }

  initChartQueueDynamics('chart-queue-dynamics');
  initChartWaitByDept('chart-wait-by-dept', queueData || []);
  initChartResUtilAnalytics('chart-res-util-analytics');
  initChartStrategyBench('chart-strategy-bench');
}

// ── TIME FILTER (analytics) ───────────────────────────────────
function setTimeFilter(btn, _range) {
  document.querySelectorAll('.time-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Re-render with same data (in a full implementation you'd fetch date-ranged data)
  loadAnalytics();
}

// ── AI SIGNALS ────────────────────────────────────────────────
async function loadAISignals() {
  const metrics = await fetchMetrics();
  if (!metrics) return;
  APP.metrics = metrics;

  const icuUsed = (8 - (metrics.icu_available ?? 2));
  const icuPct  = Math.round((icuUsed / 8) * 100);

  setText('ai-icu-util',  `${icuPct}%`);
  setText('ai-avg-wait',  metrics.average_waiting_time != null ? metrics.average_waiting_time.toFixed(1) : '—');
  setText('ai-waiting',   metrics.waiting_patients ?? '—');

  const staffCount = (metrics.doctors_available ?? 0) + (metrics.nurses_available ?? 0);
  const staffLabel = staffCount > 20 ? 'Optimal' : staffCount > 10 ? 'Adequate' : 'Constrained';
  setText('ai-staff',     staffLabel);
  setText('ai-staff-sub', `${metrics.doctors_available ?? '—'} docs · ${metrics.nurses_available ?? '—'} nurses`);
}

// ── Helpers ───────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindNav();
  startClock();

  // Wire up simulation button
  const simBtn = document.getElementById('btn-run-simulation');
  if (simBtn) simBtn.addEventListener('click', runSimulation);

  // Load dashboard
  loadDashboard();
});
