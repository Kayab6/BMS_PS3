from simulation.engine import run_simulation
import pprint

print("--- Running Normal Scenario ---")
results = run_simulation("normal")
print("\nMetrics:")
pprint.pprint(results["metrics"])
print("\nFinal Hospital Status (Beds):")
pprint.pprint(results["final_resources"]["hospital"]["bed"])


print("\n\n--- Running Emergency Surge Scenario ---")
surge_results = run_simulation("emergency_surge")
print("\nMetrics:")
pprint.pprint(surge_results["metrics"])
print("\nFinal Hospital Status (Beds):")
pprint.pprint(surge_results["final_resources"]["hospital"]["bed"])
