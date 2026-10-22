"""
MODULE 1: Process Input & Task Management
-----------------------------------------
Generates and manages CPU processes for scheduling.
Each process has: Process ID, Arrival Time, Burst Time, Priority,
and the resources it needs on the edge device (CPU % and Memory MB).
"""

import csv
import random
from dataclasses import dataclass


@dataclass
class Process:
    pid: str            # Process ID, e.g. P1
    name: str           # Task name (edge / IoT workload)
    arrival: int        # Arrival Time (ms)
    burst: int          # Burst Time (ms)
    priority: int       # 1 = highest priority
    cpu_need: int       # CPU share the task needs (%)
    mem_need: int       # Memory the task needs (MB)


# Sample workload of a smart-manufacturing edge device
SAMPLE_PROCESSES = [
    Process("P1", "Video Analytics",     0, 12, 3, 45, 600),
    Process("P2", "Sensor Read",         1,  2, 1, 10,  64),
    Process("P3", "Data Logging",        2,  6, 4, 20, 200),
    Process("P4", "Machine Alert",       3,  3, 1, 15,  96),
    Process("P5", "Model Inference",     4,  8, 2, 50, 520),
    Process("P6", "Cloud Sync",          5, 10, 5, 25, 300),
    Process("P7", "Temperature Check",   6,  2, 2, 10,  48),
    Process("P8", "Firmware Check",      8,  5, 4, 20, 450),
]

TASK_NAMES = ["Sensor Read", "Video Analytics", "Data Logging", "Machine Alert",
              "Model Inference", "Cloud Sync", "Temperature Check", "Firmware Check"]


def generate_processes(n, seed=None):
    """Generate n random processes with Process ID, Arrival, Burst, Priority."""
    rng = random.Random(seed)
    processes = []
    arrival = 0
    for i in range(1, n + 1):
        processes.append(Process(
            pid=f"P{i}",
            name=rng.choice(TASK_NAMES),
            arrival=arrival,
            burst=rng.randint(1, 12),
            priority=rng.randint(1, 5),
            cpu_need=rng.choice([10, 15, 20, 25, 35, 45, 50]),
            mem_need=rng.choice([48, 64, 96, 200, 300, 450, 520, 600]),
        ))
        arrival += rng.randint(0, 3)
    return processes


def load_processes_csv(path):
    """Read processes from a CSV file (columns as in sample_processes.csv)."""
    processes = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            processes.append(Process(
                pid=row["pid"], name=row["name"],
                arrival=int(row["arrival"]), burst=int(row["burst"]),
                priority=int(row["priority"]),
                cpu_need=int(row["cpu_need"]), mem_need=int(row["mem_need"]),
            ))
    return processes


def read_processes_from_keyboard():
    """Let the user type process details."""
    n = int(input("Enter number of processes: "))
    processes = []
    for i in range(1, n + 1):
        print(f"\nProcess P{i}")
        processes.append(Process(
            pid=f"P{i}",
            name=input("  Task name        : ") or f"Task{i}",
            arrival=int(input("  Arrival time     : ")),
            burst=int(input("  Burst time       : ")),
            priority=int(input("  Priority (1=high): ")),
            cpu_need=int(input("  CPU need (%)     : ")),
            mem_need=int(input("  Memory need (MB) : ")),
        ))
    return processes


def show_processes(processes):
    print("\nINPUT PROCESSES")
    print(f"{'PID':<5}{'Task':<20}{'Arrival':>8}{'Burst':>7}{'Priority':>10}{'CPU%':>6}{'Mem(MB)':>9}")
    for p in processes:
        print(f"{p.pid:<5}{p.name:<20}{p.arrival:>8}{p.burst:>7}{p.priority:>10}{p.cpu_need:>6}{p.mem_need:>9}")
