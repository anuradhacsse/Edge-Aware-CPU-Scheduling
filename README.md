# Edge-Aware CPU Scheduling for Reducing Latency
CSA0402 – Operating Systems | Mini Project Implementation (Python)

## Requirements
Python 3.8+ and matplotlib:

    pip install matplotlib

## How to run

    python main.py                         # sample smart-manufacturing workload
    python main.py --csv sample_processes.csv
    python main.py --random 10 --seed 3    # random processes
    python main.py --input                 # enter processes from keyboard
    python main.py --quantum 4             # change Round Robin quantum

Results are printed on screen. Graphs are saved in the `output/` folder.

## Files (one per module in the PPT)

| File | Module |
|---|---|
| module1_process_input.py | Module 1 – Process Input & Task Management (PID, Arrival, Burst, Priority, CPU %, Memory) |
| module2_conventional.py | Module 2 – FCFS, SJF, Priority, Round Robin |
| module3_edge_aware.py | Module 3 – Edge-Aware CPU Scheduling (proposed) |
| module4_analysis.py | Module 4 – WT, TAT, RT, Latency, tables and graphs, best algorithm |
| edge_device.py | Edge device model: changing CPU utilization and free memory |
| simulator.py | Common CPU simulator used by all algorithms |
| main.py | Runs everything |

## Edge device model (same for all algorithms)
* Other services on the device use 20–70 % CPU and 350–750 MB memory; this changes with time.
* Context switch = 1 ms.
* If a process is dispatched when free memory is less than it needs → 3 ms swap delay.

## Edge-Aware algorithm (Module 3)
1. Read the current CPU utilization and free memory.
2. Keep only processes that fit: `mem_need ≤ free memory` and `cpu_need + CPU utilization ≤ 100 %`.
3. Pick the process with the lowest score:
   `score = remaining × (1 + 0.1 × (priority − 1)) − 0.1 × waiting time`
   → short jobs and high-priority jobs first; ageing stops starvation.
4. Run it for a 2 ms time slice. If 5 ms or less is left, let it finish (avoids extra context switches).

## Formulas
* Turnaround Time = Completion Time − Arrival Time
* Waiting Time = Turnaround Time − Burst Time
* Response Time = First CPU time − Arrival Time
* Latency = Response Time + overhead (context switch + swap delay) suffered by the process
* CPU Utilization = total burst time / total schedule length × 100

## Sample result (sample_processes.csv)

| Algorithm | Waiting | Turnaround | Response | Latency |
|---|---|---|---|---|
| FCFS | 27.75 | 33.75 | 25.75 | 27.75 |
| SJF | 23.88 | 29.88 | 21.88 | 23.88 |
| Priority | 25.88 | 31.88 | 23.88 | 25.88 |
| RR (q=3) | 37.50 | 43.50 | 12.12 | 16.12 |
| **Edge-Aware** | **20.50** | **26.50** | 12.62 | **14.75** |

Edge-Aware gives the lowest waiting time, turnaround time and latency.
Round Robin has a slightly lower response time but much higher waiting time.

Note: on random workloads Edge-Aware is the best overall in about 2 out of 3 cases;
SJF sometimes wins when there is little memory pressure. This can be discussed in the report.
