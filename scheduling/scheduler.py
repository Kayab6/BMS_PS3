"""Allocation-aware scheduling orchestration."""

from __future__ import annotations

from typing import Any, Protocol

from .priority_queue import HospitalPriorityQueue


class ResourceManagerProtocol(Protocol):
	"""Minimal resource-manager contract required by the scheduler."""

	def can_allocate(self, patient: Any) -> bool: ...

	def allocate(self, patient: Any) -> bool: ...


def _patient_id(patient: Any) -> str:
	if isinstance(patient, dict):
		return str(patient.get("patient_id", patient.get("id", "")))
	return str(getattr(patient, "patient_id", getattr(patient, "id", "")))


class Scheduler:
	"""Coordinate queue order with resource availability without owning data."""

	def schedule_next(
		self, queue: HospitalPriorityQueue, resource_manager: ResourceManagerProtocol
	) -> tuple[Any | None, bool]:
		"""Allocate the highest-ranked currently feasible patient.

		Blocked patients remain in the queue, so a resource bottleneck does not
		permanently prevent other feasible patients from being scheduled.
		"""
		for patient in queue.candidates():
			if resource_manager.can_allocate(patient):
				priority = queue.priority_for(_patient_id(patient))
				queue.remove(_patient_id(patient))
				if resource_manager.allocate(patient):
					return patient, True
				queue.push(patient, priority if priority is not None else 0.0)
				return patient, False
		return None, False

	def batch_schedule(
		self,
		queue: HospitalPriorityQueue,
		resource_manager: ResourceManagerProtocol,
		max_allocations: int = 10,
	) -> list[Any]:
		"""Schedule up to ``max_allocations`` feasible patients."""
		if max_allocations < 0:
			raise ValueError("max_allocations must be non-negative")
		allocated: list[Any] = []
		for _ in range(max_allocations):
			patient, success = self.schedule_next(queue, resource_manager)
			if not success or patient is None:
				break
			allocated.append(patient)
		return allocated


if __name__ == "__main__":
	from dataclasses import dataclass

	from .strategies import MEDFLOW, FCFS, URGENCY_ONLY

	@dataclass
	class DemoPatient:
		patient_id: str
		arrival_time: float
		urgency: float

	class DemoResourceManager:
		def can_allocate(self, patient: DemoPatient) -> bool:
			return patient.patient_id != "P1"

		def allocate(self, patient: DemoPatient) -> bool:
			return True

	demo_patients = [
		DemoPatient("P1", 0.0, 5.0),
		DemoPatient("P2", 1.0, 2.0),
		DemoPatient("P3", 2.0, 4.0),
		DemoPatient("P4", 3.0, 1.0),
	]
	for strategy in (FCFS(), URGENCY_ONLY(), MEDFLOW()):
		demo_queue = HospitalPriorityQueue()
		for demo_patient in demo_patients:
			demo_queue.push(demo_patient, strategy.score_patient(demo_patient, 5.0))
		scheduled, success = Scheduler().schedule_next(
			demo_queue, DemoResourceManager()
		)
		print(f"{strategy.name.value}: {scheduled.patient_id if success else 'none'}")
