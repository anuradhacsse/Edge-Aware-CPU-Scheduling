"""
MODULE 2: Conventional CPU Scheduling
-------------------------------------
FCFS, SJF (non-preemptive), Priority (non-preemptive) and Round Robin.
These algorithms do NOT look at the edge device's CPU / memory status.
"""

from simulator import simulate


def fcfs(processes, device):
    """First Come First Serve: earliest arrival runs first."""
    return simulate(processes, device,
                    pick=lambda q, t, info: q[0])


def sjf(processes, device):
    """Shortest Job First: smallest burst time among ready processes."""
    return simulate(processes, device,
                    pick=lambda q, t, info: min(q, key=lambda p: (p.burst, p.arrival)))


def priority(processes, device):
    """Priority: smallest priority number (1 = highest) runs first."""
    return simulate(processes, device,
                    pick=lambda q, t, info: min(q, key=lambda p: (p.priority, p.arrival)))


def round_robin(processes, device, time_quantum=3):
    """Round Robin: each process gets a fixed time quantum in turn."""
    return simulate(processes, device,
                    pick=lambda q, t, info: q[0],
                    quantum=lambda p, t, info: time_quantum)
