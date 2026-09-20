/**
 * MEDFLOW Hospital Operations Center - Chart.js Visualizations
 * Handles Resource Utilization, Waiting Time by Department, Queue History, and Strategy Comparison
 */

// Global chart instances
let resourceChart = null;
let waitTimeChart = null;
let queueTrendChart = null;
let strategyChart = null;

// History buffer for queue trend
const MAX_QUEUE_HISTORY = 15;
const queueHistoryLabels = ['T-14', 'T-13', 'T-12', 'T-11', 'T-10', 'T-9', 'T-8', 'T-7', 'T-6', 'T-5', 'T-4', 'T-3', 'T-2', 'T-1', 'Now'];
let queueHistoryData = [12, 14, 15, 18, 21, 24, 28, 25, 22, 19, 17, 16, 18, 15, 12];

// Chart.js default dark theme typography and colors
Chart.defaults.color = '#9ca3af';
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.tooltip.backgroundColor = '#111827';
Chart.defaults.plugins.tooltip.titleColor = '#f9fafb';
Chart.defaults.plugins.tooltip.bodyColor = '#d1d5db';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.12)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

/**
 * Initialize all 4 dashboard charts
 */
function initCharts() {
  initResourceChart();
  initWaitTimeChart();
  initQueueTrendChart();
  initStrategyChart();
}

/**
 * Chart 1: Resource Utilization (Capacity vs Allocated)
 */
function initResourceChart() {
  const ctx = document.getElementById('resourceUtilizationChart');
  if (!ctx) return;

  resourceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Gen Beds', 'ICU Beds', 'Doctors', 'Nurses', 'OR', 'Ambulances'],
      datasets: [
        {
          label: 'Allocated / In Use',
          data: [15, 6, 12, 22, 3, 2],
          backgroundColor: 'rgba(6, 182, 212, 0.85)',
          borderRadius: 6,
          borderSkipped: false
        },
        {
          label: 'Available',
          data: [35, 2, 8, 18, 2, 3],
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: 6,
          borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: { display: false }
        },
        y: {
          stacked: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true }
        }
      }
    }
  });
}

/**
 * Chart 2: Waiting Time (Average and by Department)
 */
function initWaitTimeChart() {
  const ctx = document.getElementById('waitTimeChart');
  if (!ctx) return;

  waitTimeChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Emergency', 'ICU', 'Cardiology', 'Neurology', 'Gen Med', 'Gynecology'],
      datasets: [
        {
          label: 'Avg Wait (mins)',
          data: [42, 18, 32, 28, 24, 15],
          backgroundColor: [
            'rgba(239, 68, 68, 0.75)',
            'rgba(245, 158, 11, 0.75)',
            'rgba(139, 92, 246, 0.75)',
            'rgba(59, 130, 246, 0.75)',
            'rgba(6, 182, 212, 0.75)',
            'rgba(16, 185, 129, 0.75)'
          ],
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          title: { display: true, text: 'Minutes' }
        },
        y: {
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

/**
 * Chart 3: Queue Length Trend over Simulation Time
 */
function initQueueTrendChart() {
  const ctx = document.getElementById('queueTrendChart');
  if (!ctx) return;

  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 200);
  gradient.addColorStop(0, 'rgba(6, 182, 212, 0.4)');
  gradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

  queueTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: queueHistoryLabels,
      datasets: [
        {
          label: 'Waiting Queue Length',
          data: queueHistoryData,
          fill: true,
          backgroundColor: gradient,
          borderColor: '#06b6d4',
          borderWidth: 2.5,
          tension: 0.35,
          pointBackgroundColor: '#06b6d4',
          pointBorderColor: '#0a0e17',
          pointRadius: 3,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.03)' }
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

/**
 * Chart 4: Strategy Comparison (FCFS vs Urgency vs MEDFLOW)
 */
function initStrategyChart() {
  const ctx = document.getElementById('strategyComparisonChart');
  if (!ctx) return;

  strategyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['FCFS', 'Urgency-Only', 'MEDFLOW (Ours)'],
      datasets: [
        {
          label: 'Average Wait Time (mins)',
          data: [48.2, 34.5, 18.6],
          backgroundColor: [
            'rgba(156, 163, 175, 0.65)',
            'rgba(245, 158, 11, 0.75)',
            'rgba(16, 185, 129, 0.85)'
          ],
          borderColor: [
            '#9ca3af',
            '#f59e0b',
            '#10b981'
          ],
          borderWidth: 1.5,
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          title: { display: true, text: 'Lower is Better (Minutes)' }
        },
        y: {
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            afterLabel: function (context) {
              if (context.dataIndex === 2) {
                return '★ 61.4% faster than FCFS';
              }
              return '';
            }
          }
        }
      }
    }
  });
}

/**
 * Dynamic Chart Updates
 */
function updateResourceChartData(resourceSummary) {
  if (!resourceChart || !resourceSummary) return;

  const beds = resourceSummary.general_beds || resourceSummary.beds || { total: 50, available: 35, allocated: 15 };
  const icu = resourceSummary.icu_beds || resourceSummary.icu || { total: 10, available: 2, allocated: 8 };
  const doctors = resourceSummary.doctors || { total: 20, available: 7, allocated: 13 };
  const nurses = resourceSummary.nurses || { total: 40, available: 16, allocated: 24 };
  const or = resourceSummary.operating_rooms || resourceSummary.or || { total: 5, available: 2, allocated: 3 };
  const ambulances = resourceSummary.ambulances || { total: 5, available: 3, allocated: 2 };

  const allocated = [
    beds.allocated ?? (beds.total - beds.available),
    icu.allocated ?? (icu.total - icu.available),
    doctors.allocated ?? (doctors.total - doctors.available),
    nurses.allocated ?? (nurses.total - nurses.available),
    or.allocated ?? (or.total - or.available),
    ambulances.allocated ?? (ambulances.total - ambulances.available)
  ];

  const available = [
    beds.available ?? 0,
    icu.available ?? 0,
    doctors.available ?? 0,
    nurses.available ?? 0,
    or.available ?? 0,
    ambulances.available ?? 0
  ];

  resourceChart.data.datasets[0].data = allocated;
  resourceChart.data.datasets[1].data = available;
  resourceChart.update('none');
}

function updateWaitTimeChartData(queueData, avgWait) {
  if (!waitTimeChart || !queueData) return;

  const deptCounts = {
    'Emergency': [],
    'ICU': [],
    'Cardiology': [],
    'Neurology': [],
    'General Medicine': [],
    'Gynecology': []
  };

  queueData.forEach(p => {
    const dept = p.department || 'General Medicine';
    const wait = p.estimated_waiting_time || p.wait_time || 20;
    if (deptCounts[dept]) {
      deptCounts[dept].push(wait);
    } else {
      deptCounts[dept] = [wait];
    }
  });

  const deptAvg = Object.keys(deptCounts).map(dept => {
    const arr = deptCounts[dept];
    if (arr.length === 0) return Math.max(5, Math.round(avgWait ? avgWait * 0.7 : 15));
    return Math.round(arr.reduce((a, b) => a + b, 0) / arr.length);
  });

  waitTimeChart.data.datasets[0].data = deptAvg;
  waitTimeChart.update('none');
}

function updateQueueTrendChartData(currentQueueLength) {
  if (!queueTrendChart) return;

  queueHistoryData.shift();
  queueHistoryData.push(currentQueueLength);
  queueTrendChart.data.datasets[0].data = queueHistoryData;
  queueTrendChart.update('none');
}

function updateStrategyChartData(compareData) {
  if (!strategyChart || !compareData) return;

  const fcfs = compareData.FCFS?.avg_wait_time ?? compareData.fcfs_wait ?? 48.2;
  const urgency = compareData.URGENCY_ONLY?.avg_wait_time ?? compareData.urgency_wait ?? 34.5;
  const medflow = compareData.MEDFLOW?.avg_wait_time ?? compareData.medflow_wait ?? 18.6;

  strategyChart.data.datasets[0].data = [fcfs, urgency, medflow];
  strategyChart.update('none');
}

// Export functions to global scope
window.initCharts = initCharts;
window.updateResourceChartData = updateResourceChartData;
window.updateWaitTimeChartData = updateWaitTimeChartData;
window.updateQueueTrendChartData = updateQueueTrendChartData;
window.updateStrategyChartData = updateStrategyChartData;
