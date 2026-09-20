/* ============================================================
   MEDFLOW — Chart Factories (charts.js)
   All Chart.js configurations for the application
   ============================================================ */

// ── Design Tokens mirrored from CSS ───────────────────────────
const MF = {
  green: {
    900: '#0d2118', 800: '#1a3d2b', 700: '#22503a',
    600: '#2d6a4f', 500: '#3a8a68', 400: '#52b788',
    300: '#74c69d', 200: '#b7e4c7', 100: '#d8f3dc', 50: '#f0faf3',
  },
  neutral: {
    50: '#fafaf8', 100: '#f5f3ef', 200: '#ede9e2',
    300: '#ddd8cf', 400: '#b8b3ab', 500: '#8c877f',
  },
  red:   '#ef4444',
  amber: '#f59e0b',
  blue:  '#3b82f6',
  teal:  '#14b8a6',
  purple:'#8b5cf6',
  text: {
    primary:   '#1a1815',
    secondary: '#625e58',
    tertiary:  '#8c877f',
  },
};

// Chart.js global defaults
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = MF.text.secondary;
Chart.defaults.plugins.legend.display = false;
Chart.defaults.plugins.tooltip.backgroundColor = MF.green[800];
Chart.defaults.plugins.tooltip.titleColor = '#fff';
Chart.defaults.plugins.tooltip.bodyColor = 'rgba(255,255,255,0.8)';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 6;
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;

// Store for all chart instances (for destroy/reinit)
const CHARTS = {};

function destroyChart(id) {
  if (CHARTS[id]) { CHARTS[id].destroy(); delete CHARTS[id]; }
}

// ── Helper: create gridded scale options ──────────────────────
function gridOpts(color = MF.neutral[200]) {
  return {
    grid: { color, drawBorder: false },
    border: { display: false },
    ticks: { color: MF.text.tertiary, font: { size: 11 } },
  };
}

// ── 1. Department Queue Bar Chart ─────────────────────────────
function initChartDeptQueue(canvasId, patients) {
  destroyChart(canvasId);
  const depts = ['Emergency','ICU','Cardiology','Neurology','General Medicine','Gynecology'];
  const counts = depts.map(d => patients.filter(p => p.department === d).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: depts.map(d => d.length > 12 ? d.replace(' ', '\n') : d),
      datasets: [{
        data: counts,
        backgroundColor: [
          MF.red, MF.green[600], MF.blue, MF.purple, MF.green[400], MF.teal,
        ],
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ...gridOpts('transparent'), grid: { display: false } },
        y: { ...gridOpts(), beginAtZero: true, ticks: { stepSize: 1, color: MF.text.tertiary, font:{size:11} } },
      },
    },
  });
}

// ── 2. Resource Snapshot Doughnut ─────────────────────────────
function initChartResourceSnapshot(canvasId, resources) {
  destroyChart(canvasId);
  const beds = resources.beds || { available: 5, total: 20 };
  const icu  = resources.icu  || { available: 2, total: 8 };
  const docs = resources.doctors || { available: 3, total: 10 };
  const nurs = resources.nurses  || { available: 6, total: 15 };

  const data = [
    beds.total - beds.available,
    icu.total  - icu.available,
    docs.total - docs.available,
    nurs.total - nurs.available,
  ];
  const avail = [beds.available, icu.available, docs.available, nurs.available];

  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Gen Beds', 'ICU', 'Doctors', 'Nurses'],
      datasets: [
        {
          label: 'In Use',
          data: data,
          backgroundColor: [MF.amber, MF.red, MF.blue, MF.green[500]],
          borderRadius: { topLeft: 0, topRight: 0, bottomLeft: 4, bottomRight: 4 },
          borderSkipped: false,
        },
        {
          label: 'Available',
          data: avail,
          backgroundColor: [
            `${MF.amber}33`, `${MF.red}33`, `${MF.blue}33`, `${MF.green[500]}33`,
          ],
          borderRadius: { topLeft: 4, topRight: 4, bottomLeft: 0, bottomRight: 0 },
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 10, font: {size:11}, color: MF.text.secondary } } },
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: { stacked: true, ...gridOpts(), beginAtZero: true },
      },
    },
  });
}

// ── 3. Urgency Mix Doughnut ───────────────────────────────────
function initChartUrgencyMix(canvasId, patients) {
  destroyChart(canvasId);
  const counts = [1,2,3,4,5].map(u => patients.filter(p => p.urgency === u).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Level 1 — Low','Level 2 — Moderate','Level 3 — Medium','Level 4 — High','Level 5 — Critical'],
      datasets: [{
        data: counts,
        backgroundColor: [MF.green[300], MF.green[500], MF.amber, MF.red, '#7f1d1d'],
        borderWidth: 2,
        borderColor: '#fff',
        hoverBorderColor: '#fff',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '62%',
      plugins: {
        legend: {
          display: true, position: 'right',
          labels: { boxWidth: 10, font:{size:11}, color: MF.text.secondary, padding: 8 },
        },
      },
    },
  });
}

// ── 4. Queue Dept Chart ───────────────────────────────────────
function initChartQueueDept(canvasId, queueData) {
  destroyChart(canvasId);
  const depts = ['Emergency','ICU','Cardiology','Neurology','General Medicine','Gynecology'];
  const counts = depts.map(d => queueData.filter(p => p.department === d).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'horizontalBar' in Chart ? 'horizontalBar' : 'bar',
    data: {
      labels: depts,
      datasets: [{
        data: counts,
        backgroundColor: MF.green[400],
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ...gridOpts(), beginAtZero: true },
        y: { grid: { display: false }, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
      },
    },
  });
}

// ── 5. Queue Wait Distribution ────────────────────────────────
function initChartQueueWait(canvasId, queueData) {
  destroyChart(canvasId);
  const bins = [0, 15, 30, 45, 60, 90, 120];
  const labels = ['0–15m','15–30m','30–45m','45–60m','60–90m','90m+'];
  const counts = labels.map((_, i) => {
    const lo = bins[i], hi = bins[i+1] || Infinity;
    return queueData.filter(p => p.estimated_waiting_time >= lo && p.estimated_waiting_time < hi).length;
  });
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: counts,
        backgroundColor: counts.map((_, i) =>
          i >= 4 ? MF.red : i >= 2 ? MF.amber : MF.green[400]
        ),
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero: true, ticks:{stepSize:1,color:MF.text.tertiary,font:{size:11}} },
      },
    },
  });
}

// ── 6. Predict by Department Bar ──────────────────────────────
function initChartPredictByDept(canvasId) {
  destroyChart(canvasId);
  const depts = ['Emergency','ICU','Cardiology','Neurology','General Medicine','Gynecology'];
  // Realistic baseline estimates (mins)
  const waitTimes = [38, 55, 22, 28, 18, 15];
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: depts,
      datasets: [{
        label: 'Est. Wait (mins)',
        data: waitTimes,
        backgroundColor: waitTimes.map(v => v > 40 ? MF.red : v > 25 ? MF.amber : MF.green[400]),
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ...gridOpts(), beginAtZero: true },
        y: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
      },
    },
  });
}

// ── 7. Prediction Trend Line ──────────────────────────────────
const PREDICTION_HISTORY = [];

function initChartPredictTrend(canvasId) {
  destroyChart(canvasId);
  const labels = PREDICTION_HISTORY.map((_, i) => `#${i+1}`);
  const values = PREDICTION_HISTORY.map(p => p.value);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['—'],
      datasets: [{
        data: values.length ? values : [null],
        borderColor: MF.green[500],
        backgroundColor: `${MF.green[500]}18`,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: MF.green[500],
        tension: 0.4,
        fill: true,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.tertiary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero: true },
      },
    },
  });
}

function updatePredictTrend(value) {
  PREDICTION_HISTORY.push({ value, ts: Date.now() });
  if (PREDICTION_HISTORY.length > 8) PREDICTION_HISTORY.shift();
  initChartPredictTrend('chart-predict-trend');
}

// ── 8. Resource Utilization Bar ───────────────────────────────
function initChartResourceUtil(canvasId) {
  destroyChart(canvasId);
  const labels = ['Gen Beds','ICU Beds','Doctors','Nurses','Op Rooms','Ambulances'];
  const utils  = [75, 75, 38, 28, 60, 20];
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: utils,
        backgroundColor: utils.map(v => v >= 70 ? MF.red : v >= 50 ? MF.amber : MF.green[400]),
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero: true, max: 100, ticks:{callback:v=>`${v}%`,color:MF.text.tertiary,font:{size:11}} },
      },
    },
  });
}

// ── 9. Resource Availability Trend ────────────────────────────
function initChartResourceTrend(canvasId) {
  destroyChart(canvasId);
  const labels = Array.from({length:12}, (_,i) => `-${11-i}h`);
  const beds  = [8, 7, 6, 7, 6, 5, 5, 6, 6, 5, 5, 5];
  const icu   = [4, 3, 3, 2, 2, 2, 3, 3, 2, 2, 2, 2];
  const docs  = [5, 4, 4, 4, 3, 3, 4, 4, 3, 3, 3, 3];
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label:'Gen Beds', data:beds, borderColor:MF.green[400], backgroundColor:'transparent', borderWidth:2, pointRadius:3, tension:0.4 },
        { label:'ICU Beds', data:icu,  borderColor:MF.red,         backgroundColor:'transparent', borderWidth:2, pointRadius:3, tension:0.4, borderDash:[4,3] },
        { label:'Doctors',  data:docs, borderColor:MF.blue,        backgroundColor:'transparent', borderWidth:2, pointRadius:3, tension:0.4 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: true, position:'top', labels:{boxWidth:10,font:{size:11},color:MF.text.secondary} } },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.tertiary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero: true },
      },
    },
  });
}

// ── 10. Alerts by Severity ────────────────────────────────────
function initChartAlertsSeverity(canvasId, alerts) {
  destroyChart(canvasId);
  const sevs = ['Critical','High','Medium','Low'];
  const counts = sevs.map(s => alerts.filter(a => a.severity === s).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: sevs,
      datasets: [{
        data: counts,
        backgroundColor: [MF.red, MF.amber, '#fbbf24', MF.green[400]],
        borderWidth: 2, borderColor: '#fff',
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '58%',
      plugins: { legend: { display:true, position:'right', labels:{boxWidth:10,font:{size:11},padding:8} } },
    },
  });
}

// ── 11. Alerts by Department ──────────────────────────────────
function initChartAlertsDept(canvasId, alerts) {
  destroyChart(canvasId);
  const depts = [...new Set(alerts.map(a => a.department))];
  const counts = depts.map(d => alerts.filter(a => a.department === d).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: depts,
      datasets: [{
        data: counts,
        backgroundColor: MF.green[400],
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false} },
      scales: {
        x: { ...gridOpts(), beginAtZero:true, ticks:{stepSize:1,color:MF.text.tertiary,font:{size:11}} },
        y: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
      },
    },
  });
}

// ── 12. Blood Distribution Doughnut ──────────────────────────
function initChartBloodDist(canvasId, bloodData) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: bloodData.map(b => b.blood_group),
      datasets: [{
        data: bloodData.map(b => b.units_available),
        backgroundColor: [
          MF.green[400], MF.green[600], MF.blue, MF.purple,
          MF.teal, MF.amber, MF.red, MF.green[300],
        ],
        borderWidth: 2, borderColor: '#fff',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '55%',
      plugins: {
        legend: { display:true, position:'right', labels:{boxWidth:10,font:{size:11},padding:8} },
      },
    },
  });
}

// ── 13. Blood Level Bar ───────────────────────────────────────
function initChartBloodLevels(canvasId, bloodData) {
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: bloodData.map(b => b.blood_group),
      datasets: [{
        data: bloodData.map(b => b.units_available),
        backgroundColor: bloodData.map(b =>
          b.units_available < 4 ? MF.red : b.units_available < 10 ? MF.amber : MF.green[400]
        ),
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false} },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero:true },
      },
    },
  });
}

// ── 14. Patient Flow Area Chart ───────────────────────────────
function initChartPatientFlow(canvasId, patients) {
  destroyChart(canvasId);
  const hours = Array.from({length:24}, (_,i) => `${String(i).padStart(2,'0')}:00`);
  // Simulate flow data from patient count
  const total = patients.length || 48;
  const admitted = hours.map((_, i) => Math.max(0, Math.round((total * 0.05) + Math.sin(i/4) * (total * 0.03) + Math.random() * 2));
  const active   = hours.map((_, i) => Math.round(total * 0.4 + Math.sin(i/3) * (total * 0.15)));

  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [
        {
          label: 'Active Patients',
          data: active,
          borderColor: MF.green[500],
          backgroundColor: `${MF.green[500]}20`,
          borderWidth: 2.5, pointRadius: 0, tension: 0.5, fill: true,
        },
        {
          label: 'Admissions',
          data: admitted,
          borderColor: MF.blue,
          backgroundColor: `${MF.blue}15`,
          borderWidth: 2, pointRadius: 0, tension: 0.5, fill: true,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display:true, position:'top', labels:{boxWidth:12,font:{size:11},color:MF.text.secondary} },
      },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.tertiary,font:{size:11},maxTicksLimit:12} },
        y: { ...gridOpts(), beginAtZero:true },
      },
    },
  });
}

// ── 15. Queue Dynamics Line ───────────────────────────────────
function initChartQueueDynamics(canvasId) {
  destroyChart(canvasId);
  const steps = Array.from({length:20}, (_,i) => `Step ${i+1}`);
  const queue = steps.map(() => Math.round(5 + Math.random() * 20));
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: steps,
      datasets: [{
        label: 'Queue Length',
        data: queue,
        borderColor: MF.amber,
        backgroundColor: `${MF.amber}18`,
        borderWidth: 2, pointRadius: 3, tension: 0.4, fill: true,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false} },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.tertiary,font:{size:11},maxTicksLimit:10} },
        y: { ...gridOpts(), beginAtZero:true },
      },
    },
  });
}

// ── 16. Case Distribution Doughnut ────────────────────────────
function initChartCaseDist(canvasId, patients) {
  destroyChart(canvasId);
  const depts = ['Emergency','ICU','Cardiology','Neurology','General Medicine','Gynecology'];
  const counts = depts.map(d => patients.filter(p => p.department === d).length);
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: depts,
      datasets: [{
        data: counts,
        backgroundColor: [MF.red, MF.green[600], MF.blue, MF.purple, MF.green[400], MF.teal],
        borderWidth: 2, borderColor: '#fff', hoverOffset: 6,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '55%',
      plugins: {
        legend: { display:true, position:'bottom', labels:{boxWidth:10,font:{size:10},padding:6,color:MF.text.secondary} },
      },
    },
  });
}

// ── 17. Wait Time by Dept Horizontal Bar ──────────────────────
function initChartWaitByDept(canvasId, queueData) {
  destroyChart(canvasId);
  const depts = ['Emergency','ICU','Cardiology','Neurology','General Medicine','Gynecology'];
  const avgs = depts.map(d => {
    const pts = queueData.filter(p => p.department === d);
    if (!pts.length) return Math.round(Math.random() * 30 + 10);
    return Math.round(pts.reduce((s,p) => s + p.estimated_waiting_time, 0) / pts.length);
  });
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: depts,
      datasets: [{
        label: 'Avg Wait (mins)',
        data: avgs,
        backgroundColor: avgs.map(v => v > 40 ? MF.red : v > 25 ? MF.amber : MF.green[400]),
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false} },
      scales: {
        x: { ...gridOpts(), beginAtZero:true },
        y: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
      },
    },
  });
}

// ── 18. Resource Util Analytics ───────────────────────────────
function initChartResUtilAnalytics(canvasId) {
  initChartResourceUtil(canvasId);
}

// ── 19. Strategy Benchmark ────────────────────────────────────
function initChartStrategyBench(canvasId) {
  destroyChart(canvasId);
  const labels = ['FCFS', 'Urgency-Only', 'MEDFLOW'];
  const values = [42.8, 31.5, 26.6];
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: [MF.neutral[400], MF.amber, MF.green[500]],
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{display:false},
        tooltip:{ callbacks:{ label: ctx => `${ctx.raw} mins avg wait` } }
      },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:12,weight:'600'}} },
        y: { ...gridOpts(), beginAtZero:true, ticks:{callback:v=>`${v}m`,color:MF.text.tertiary,font:{size:11}} },
      },
    },
  });
}

// ── 20. Admissions vs Discharges ──────────────────────────────
function initChartAdmDis(canvasId, total) {
  destroyChart(canvasId);
  const labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const n = total || 48;
  const adm = labels.map(() => Math.round(n * 0.1 + Math.random() * n * 0.06));
  const dis = labels.map((_,i) => Math.max(0, Math.round(adm[i] * (0.7 + Math.random() * 0.4)));
  const ctx = document.getElementById(canvasId).getContext('2d');
  CHARTS[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Admissions',
          data: adm,
          backgroundColor: MF.blue,
          borderRadius: { topLeft: 4, topRight: 4, bottomLeft: 0, bottomRight: 0 },
          borderSkipped: false,
        },
        {
          label: 'Discharges',
          data: dis,
          backgroundColor: MF.green[400],
          borderRadius: { topLeft: 4, topRight: 4, bottomLeft: 0, bottomRight: 0 },
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display:true, position:'top', labels:{boxWidth:10,font:{size:11},color:MF.text.secondary} },
      },
      scales: {
        x: { grid:{display:false}, border:{display:false}, ticks:{color:MF.text.secondary,font:{size:11}} },
        y: { ...gridOpts(), beginAtZero:true },
      },
    },
  });
}
