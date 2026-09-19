"""Scheduling strategy implementations."""

from __future__ import annotations

from enum import Enum
from typing import Any

from .priority import calculate_patient_priority


class Strategy(str, Enum):
	"""Supported patient ordering strategies."""

	FCFS = "FCFS"
	URGENCY_ONLY = "URGENCY_ONLY"
	MEDFLOW = "MEDFLOW"


class SchedulingStrategy:
	"""Common interface for patient scoring strategies."""

	name: Strategy

	def score_patient(
		self, patient: Any, current_time: float, hospital_state: Any = None
	) -> float:
		"""Return a higher-is-better score for ``patient``."""
		raise NotImplementedError


class FCFS(SchedulingStrategy):
	"""First-come, first-served ordering based on elapsed wait."""

	name = Strategy.FCFS

	def score_patient(self, patient: Any, current_time: float, hospital_state: Any = None) -> float:
		state = {"current_time": current_time} if hospital_state is None else hospital_state
		return calculate_patient_priority(patient, state, self.name.value)


class URGENCY_ONLY(SchedulingStrategy):
	"""Order patients solely by normalized clinical urgency."""

	name = Strategy.URGENCY_ONLY

	def score_patient(self, patient: Any, current_time: float, hospital_state: Any = None) -> float:
		state = {"current_time": current_time} if hospital_state is None else hospital_state
		return calculate_patient_priority(patient, state, self.name.value)


class MEDFLOW(SchedulingStrategy):
	"""Dynamic hybrid of urgency, waiting time, department, and feasibility."""

	name = Strategy.MEDFLOW

	def score_patient(self, patient: Any, current_time: float, hospital_state: Any = None) -> float:
		state = {"current_time": current_time} if hospital_state is None else hospital_state
		return calculate_patient_priority(patient, state, self.name.value)


def get_strategy(strategy: str | Strategy | SchedulingStrategy) -> SchedulingStrategy:
	"""Resolve a strategy name or return an already-instantiated strategy."""
	if isinstance(strategy, SchedulingStrategy):
		return strategy
	name = getattr(strategy, "value", strategy).upper()
	strategies = {Strategy.FCFS.value: FCFS, Strategy.URGENCY_ONLY.value: URGENCY_ONLY, Strategy.MEDFLOW.value: MEDFLOW}
	try:
		return strategies[name]()
	except KeyError as exc:
		raise ValueError(f"Unknown scheduling strategy: {strategy}") from exc
