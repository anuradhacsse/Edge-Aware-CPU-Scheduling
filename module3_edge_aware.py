"""
MODULE 3: Edge-Aware CPU Scheduling (Proposed Method)
-----------------------------------------------------
At every scheduling decision the scheduler:

  1. MONITORS the edge device: current CPU utilization and free memory.

  2. FILTERS: keeps only processes that fit the current resources
        mem_need <= free memory   AND   cpu_need + CPU utilization <= 100 %
     (if nothing fits, it picks the process needing the least memory,
      so the CPU is never left idle and swapping is kept small).

  3. SCORES each fitting process (lower score = runs first):
        score = remaining_time * (1 + PRIORITY_WEIGHT * (priority - 1))
                - AGEING_WEIGHT * time_waiting_since_last_run
     -> short jobs first (low latency),
        high priority jobs first,
        long-waiting jobs slowly move up (no starvation).

  4. RUNS the chosen process for a small TIME SLICE, so that newly arrived
     short / urgent tasks get the CPU quickly (low response time).
     A task with only SHORT_JOB ms or less left is allowed to finish,
     which avoids unnecessary context switches.
"""

from simulator import simulate

PRIORITY_WEIGHT = 0.1
AGEING_WEIGHT = 0.1
TIME_SLICE = 2
SHORT_JOB = 5


def edge_score(p, t, info):
    remaining = info["remaining"][p.pid]
    waiting = t - info["last_run"][p.pid]
    return remaining * (1 + PRIORITY_WEIGHT * (p.priority - 1)) - AGEING_WEIGHT * waiting


def edge_pick(queue, t, info):
    device = info["device"]
    fitting = [p for p in queue if device.fits(p, t)]
    if not fitting:
        return min(queue, key=lambda p: (p.mem_need, p.arrival))
    return min(fitting, key=lambda p: (edge_score(p, t, info), p.arrival))


def edge_quantum(p, t, info):
    remaining = info["remaining"][p.pid]
    if remaining <= SHORT_JOB:
        return remaining
    return TIME_SLICE


def edge_aware(processes, device):
    return simulate(processes, device, pick=edge_pick, quantum=edge_quantum)
