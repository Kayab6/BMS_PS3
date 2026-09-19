"""Heap-backed patient priority queue."""

from __future__ import annotations

import heapq
from typing import Any

from .strategies import SchedulingStrategy, get_strategy


def _field(patient: Any, name: str, default: Any = None) -> Any:
	if isinstance(patient, dict):
		return patient.get(name, default)
	return getattr(patient, name, default)


class HospitalPriorityQueue:
	"""Priority queue with lazy deletion for cancellation and re-triage."""

	def __init__(self) -> None:
		self._heap: list[tuple[float, float, str, Any]] = []
		self._entries: dict[str, tuple[float, float, str, Any]] = {}

	def push(self, patient: Any, priority: float) -> None:
		"""Add or replace a patient using the required heap tuple shape."""
		patient_id = str(_field(patient, "patient_id", _field(patient, "id", "")))
		arrival_time = float(_field(patient, "arrival_time", 0.0))
		entry = (-float(priority), arrival_time, patient_id, patient)
		self._entries[patient_id] = entry
		heapq.heappush(self._heap, entry)

	def _discard_stale(self) -> None:
		while self._heap and self._entries.get(self._heap[0][2]) != self._heap[0]:
			heapq.heappop(self._heap)

	def pop(self) -> tuple[float, Any]:
		"""Remove and return ``(priority, patient)`` for the best patient."""
		self._discard_stale()
		if not self._heap:
			raise IndexError("pop from an empty HospitalPriorityQueue")
		entry = heapq.heappop(self._heap)
		del self._entries[entry[2]]
		return -entry[0], entry[3]

	def peek(self) -> tuple[float, Any] | None:
		"""Return the best patient without removing it."""
		self._discard_stale()
		if not self._heap:
			return None
		entry = self._heap[0]
		return -entry[0], entry[3]

	def remove(self, patient_id: str) -> bool:
		"""Cancel a patient, returning whether it was waiting."""
		return self._entries.pop(str(patient_id), None) is not None

	def priority_for(self, patient_id: str) -> float | None:
		"""Return an active patient's score, or ``None`` if not waiting."""
		entry = self._entries.get(str(patient_id))
		return None if entry is None else -entry[0]

	def rebuild(
		self, patients: list[Any], current_time: float, strategy: str | SchedulingStrategy
	) -> None:
		"""Re-score all waiting patients using ``strategy``."""
		scorer = get_strategy(strategy)
		self._heap.clear()
		self._entries.clear()
		for patient in patients:
			self.push(patient, scorer.score_patient(patient, current_time))

	def candidates(self) -> list[Any]:
		"""Return active patients in current heap order for allocation checks."""
		return [entry[3] for entry in sorted(self._entries.values())]

	def is_empty(self) -> bool:
		return not self._entries

	def __len__(self) -> int:
		return len(self._entries)
