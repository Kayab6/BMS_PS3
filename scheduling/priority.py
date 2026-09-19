"""Priority calculations for hospital patient scheduling."""

from __future__ import annotations

from collections.abc import Mapping
from math import tanh
from typing import Any


DEFAULT_WEIGHTS = {
	"urgency_weight": 0.45,
	"wait_time_weight": 0.30,
	"dept_weight": 0.15,
	"feasibility_weight": 0.10,
}


def _value(source: Any, *names: str, default: Any = None) -> Any:
	"""Read the first available field from a mapping or an object."""
	for name in names:
		if isinstance(source, Mapping) and name in source:
			return source[name]
		if hasattr(source, name):
			return getattr(source, name)
	return default


def _unit_interval(value: Any, default: float = 0.0) -> float:
	try:
		return max(0.0, min(1.0, float(value)))
	except (TypeError, ValueError):
		return default


def _normalize_urgency(value: Any) -> float:
	"""Normalize common triage scales (1-5 and 0-10) to 0-1."""
	try:
		urgency = float(value)
	except (TypeError, ValueError):
		return 0.0
	if urgency <= 5:
		return max(0.0, min(1.0, urgency / 5.0))
	return max(0.0, min(1.0, urgency / 10.0))


def calculate_priority(
	urgency: float,
	waiting_time: float,
	department_priority: float = 1.0,
	resource_feasibility: float = 1.0,
	weights: dict | None = None,
) -> float:
	"""Return a higher-is-better weighted priority score.

	Urgency accepts either a 1-5 or 0-10 scale. Waiting time is converted to a
	bounded, increasing value so long waits improve priority without
	overwhelming clinical urgency.
	"""
	configured = {**DEFAULT_WEIGHTS, **(weights or {})}
	wait = max(0.0, float(waiting_time))
	wait_score = 1.0 - (1.0 / (1.0 + wait))
	return float(
		configured["urgency_weight"] * _normalize_urgency(urgency)
		+ configured["wait_time_weight"] * wait_score
		+ configured["dept_weight"] * _unit_interval(department_priority)
		+ configured["feasibility_weight"] * _unit_interval(resource_feasibility)
	)


def calculate_patient_priority(
	patient: Any,
	hospital_state: Any = None,
	strategy: str = "MEDFLOW",
) -> float:
	"""Calculate a patient score from a dataclass, object, or dictionary."""
	current_time = _value(hospital_state, "current_time", "time", default=None)
	if current_time is None:
		current_time = _value(patient, "current_time", "simulated_time", default=None)
	arrival_time = _value(patient, "arrival_time", "arrived_at", default=0.0)
	try:
		waiting_time = max(0.0, float(current_time) - float(arrival_time))
	except (TypeError, ValueError):
		waiting_time = 0.0

	strategy_name = getattr(strategy, "value", strategy).upper()
	urgency = _value(patient, "urgency", "triage_score", "acuity", default=0.0)
	if strategy_name == "FCFS":
		return waiting_time
	if strategy_name == "URGENCY_ONLY":
		return _normalize_urgency(urgency)
	return calculate_priority(
		urgency,
		waiting_time,
		_value(patient, "department_priority", "department_weight", default=1.0),
		_value(patient, "resource_feasibility", "feasibility", default=1.0),
	)
