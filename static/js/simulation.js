/**
 * MEDFLOW Hospital Operations Center - Simulation Controller
 * Manages Start, Reset, Scenario selection, and status monitoring
 */

let simulationTimer = null;
let simulatedClockMinutes = 0;

/**
 * Initialize simulation control listeners
 */
function initSimulationControls() {
  const startBtn = document.getElementById('startSimBtn');
  const resetBtn = document.getElementById('resetSimBtn');
  const scenarioSelect = document.getElementById('scenarioSelect');

  if (startBtn) {
    startBtn.addEventListener('click', handleStartSimulation);
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', handleResetSimulation);
  }

  if (scenarioSelect) {
    scenarioSelect.addEventListener('change', (e) => {
      console.log('Selected scenario:', e.target.value);
    });
  }

  // Initial status check
  fetchSimulationStatus();
}

/**
 * Handle Start Simulation click
 */
async function handleStartSimulation() {
  const startBtn = document.getElementById('startSimBtn');
  const scenarioSelect = document.getElementById('scenarioSelect');
  const scenario = scenarioSelect ? scenarioSelect.value : 'normal';

  if (startBtn) {
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="spinner"></span> Starting...';
  }

  updateSimulationStatusUI('running', 'RUNNING');

  try {
    const response = await fetch('/api/simulation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_type: scenario })
    });

    const data = await response.json();
    if (data.success) {
      console.log('Simulation started successfully:', data);
      startLocalSimClock();
      if (typeof window.loadDashboard === 'function') {
        window.loadDashboard();
      }
    } else {
      console.error('Simulation start failed:', data.error);
      alert('Failed to start simulation: ' + (data.error || 'Unknown error'));
      updateSimulationStatusUI('idle', 'IDLE');
    }
  } catch (err) {
    console.error('Error starting simulation:', err);
    // Graceful optimistic state for frontend demo
    startLocalSimClock();
    if (typeof window.loadDashboard === 'function') {
      window.loadDashboard();
    }
  } finally {
    if (startBtn) {
      startBtn.disabled = false;
      startBtn.innerHTML = '▶ Start Simulation';
    }
  }
}

/**
 * Handle Reset Simulation click
 */
async function handleResetSimulation() {
  const resetBtn = document.getElementById('resetSimBtn');

  if (resetBtn) {
    resetBtn.disabled = true;
    resetBtn.innerHTML = '<span class="spinner"></span> Resetting...';
  }

  stopLocalSimClock();
  simulatedClockMinutes = 0;
  updateSimClockDisplay(0);
  updateSimulationStatusUI('idle', 'IDLE');

  try {
    const response = await fetch('/api/simulation/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    console.log('Simulation reset:', data);
  } catch (err) {
    console.warn('Backend reset call encountered error or offline:', err);
  } finally {
    if (resetBtn) {
      resetBtn.disabled = false;
      resetBtn.innerHTML = '↺ Reset';
    }
    if (typeof window.loadDashboard === 'function') {
      window.loadDashboard();
    }
  }
}

/**
 * Fetch current simulation status from backend
 */
async function fetchSimulationStatus() {
  try {
    const response = await fetch('/api/simulation/status');
    if (!response.ok) return;

    const data = await response.json();
    const status = (data.status || 'idle').toLowerCase();
    
    if (status === 'running') {
      updateSimulationStatusUI('running', 'RUNNING');
      if (!simulationTimer) startLocalSimClock();
    } else if (status === 'completed') {
      updateSimulationStatusUI('normal', 'COMPLETED');
      stopLocalSimClock();
    } else {
      updateSimulationStatusUI('idle', 'IDLE');
      stopLocalSimClock();
    }

    if (data.time != null && data.time > 0) {
      simulatedClockMinutes = data.time;
      updateSimClockDisplay(data.time);
    }
  } catch (err) {
    console.debug('Simulation status polling note:', err);
  }
}

/**
 * Helper to update the top status badge
 */
function updateSimulationStatusUI(type, text) {
  const statusPill = document.getElementById('simStatusPill');
  const statusText = document.getElementById('simStatusText');
  if (!statusPill || !statusText) return;

  statusPill.className = 'status-pill ' + type;
  statusText.textContent = text;
}

/**
 * Local simulation clock for real-time visualization
 */
function startLocalSimClock() {
  if (simulationTimer) clearInterval(simulationTimer);
  simulationTimer = setInterval(() => {
    simulatedClockMinutes += 5;
    updateSimClockDisplay(simulatedClockMinutes);
    if (simulatedClockMinutes >= 1440) { // 24 hours
      stopLocalSimClock();
      updateSimulationStatusUI('normal', 'COMPLETED');
    }
  }, 1000);
}

function stopLocalSimClock() {
  if (simulationTimer) {
    clearInterval(simulationTimer);
    simulationTimer = null;
  }
}

function updateSimClockDisplay(totalMinutes) {
  const clockEl = document.getElementById('simClockDisplay');
  if (!clockEl) return;

  const hours = Math.floor(totalMinutes / 60) % 24;
  const mins = totalMinutes % 60;
  const day = Math.floor(totalMinutes / 1440) + 1;
  const formatted = `D${day} ${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
  clockEl.textContent = formatted;
}

// Export functions to global scope
window.initSimulationControls = initSimulationControls;
window.fetchSimulationStatus = fetchSimulationStatus;
