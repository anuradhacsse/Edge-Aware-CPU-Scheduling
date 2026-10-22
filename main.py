"""
Edge-Aware CPU Scheduling for Reducing Latency Compared with
Conventional CPU Scheduling Algorithms  (CSA0402 - Operating Systems)

Run:
    python main.py                 -> sample smart-manufacturing workload
    python main.py --random 10     -> 10 random processes
    python main.py --csv file.csv  -> processes from a CSV file
    python main.py --input         -> type processes from keyboard
    python main.py --quantum 4     -> change Round Robin time quantum
"""

import argparse
import os

from module1_process_input import (SAMPLE_PROCESSES, generate_processes,
                                   load_processes_csv, read_processes_from_keyboard,
                                   show_processes)
from module2_conventional import fcfs, sjf, priority, round_robin
from module3_edge_aware import edge_aware
from module4_analysis import (calculate_metrics, print_process_table, print_comparison,
                              best_algorithm, plot_comparison, plot_gantt, plot_device)
from edge_device import EdgeDevice


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--random", type=int, help="number of random processes")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--csv", help="CSV file of processes")
    ap.add_argument("--input", action="store_true", help="enter processes manually")
    ap.add_argument("--quantum", type=int, default=3, help="Round Robin time quantum")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    # Module 1: Process input
    if args.input:
        processes = read_processes_from_keyboard()
    elif args.csv:
        processes = load_processes_csv(args.csv)
    elif args.random:
        processes = generate_processes(args.random, args.seed)
    else:
        processes = SAMPLE_PROCESSES
    show_processes(processes)

    device = EdgeDevice()

    # Module 2 + Module 3: Run all algorithms on the same device
    algorithms = {
        "FCFS": lambda: fcfs(processes, device),
        "SJF": lambda: sjf(processes, device),
        "Priority": lambda: priority(processes, device),
        f"RR (q={args.quantum})": lambda: round_robin(processes, device, args.quantum),
        "Edge-Aware": lambda: edge_aware(processes, device),
    }

    # Module 4: Analysis
    results, summary = {}, {}
    for name, run in algorithms.items():
        res = run()
        rows, avg = calculate_metrics(processes, res)
        print_process_table(name, rows, avg, res)
        results[name], summary[name] = res, avg

    print_comparison(summary)
    best_algorithm(summary)

    os.makedirs(args.out, exist_ok=True)
    end = max(e for r in results.values() for _, _, e in r["timeline"])
    files = [plot_comparison(summary, args.out),
             plot_gantt(results, args.out),
             plot_device(device, end, args.out)]
    print("\nGraphs saved:", *files, sep="\n  ")


if __name__ == "__main__":
    main()
