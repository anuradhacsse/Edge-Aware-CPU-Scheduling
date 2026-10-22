"""
MODULE 4: Performance Analysis & Visualization
----------------------------------------------
Waiting Time   = Turnaround Time - Burst Time
Turnaround Time= Completion Time - Arrival Time
Response Time  = First time on CPU - Arrival Time
Latency        = Response Time + overhead the process suffered
                 (context switch + swap delay)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def calculate_metrics(processes, result):
    rows = []
    for p in sorted(processes, key=lambda p: int(p.pid[1:]) if p.pid[1:].isdigit() else p.pid):
        ct = result["completion"][p.pid]
        tat = ct - p.arrival
        wt = tat - p.burst
        rt = result["first_start"][p.pid] - p.arrival
        lat = rt + result["overhead"][p.pid]
        rows.append({"pid": p.pid, "arrival": p.arrival, "burst": p.burst,
                     "completion": ct, "tat": tat, "wt": wt, "rt": rt, "latency": lat})
    n = len(rows)
    total_time = max(r["completion"] for r in rows) - min(p.arrival for p in processes)
    busy = sum(p.burst for p in processes)
    avg = {
        "wt": sum(r["wt"] for r in rows) / n,
        "tat": sum(r["tat"] for r in rows) / n,
        "rt": sum(r["rt"] for r in rows) / n,
        "latency": sum(r["latency"] for r in rows) / n,
        "cpu_util": 100 * busy / total_time,
        "throughput": n / total_time,
        "context_switches": result["context_switches"],
        "swaps": result["swaps"],
    }
    return rows, avg


def print_process_table(name, rows, avg, result):
    print(f"\n=== {name} ===")
    order = " -> ".join(f"{lbl}({s}-{e})" for lbl, s, e in result["timeline"]
                        if lbl not in ("CS", "Swap", "Idle"))
    print("Order:", order)
    print(f"{'PID':<5}{'AT':>4}{'BT':>4}{'CT':>5}{'TAT':>5}{'WT':>5}{'RT':>5}{'Latency':>9}")
    for r in rows:
        print(f"{r['pid']:<5}{r['arrival']:>4}{r['burst']:>4}{r['completion']:>5}"
              f"{r['tat']:>5}{r['wt']:>5}{r['rt']:>5}{r['latency']:>9}")
    print(f"Average  WT={avg['wt']:.2f}  TAT={avg['tat']:.2f}  RT={avg['rt']:.2f}  "
          f"Latency={avg['latency']:.2f}  CPU Util={avg['cpu_util']:.1f}%  "
          f"Context switches={avg['context_switches']}  Swaps={avg['swaps']}")


def print_comparison(summary):
    print("\n" + "=" * 86)
    print("PERFORMANCE COMPARISON (averages, time in ms)")
    print("=" * 86)
    print(f"{'Algorithm':<14}{'Waiting':>9}{'Turnaround':>12}{'Response':>10}{'Latency':>9}"
          f"{'CPU Util%':>11}{'Ctx Sw':>8}{'Swaps':>7}")
    for name, a in summary.items():
        print(f"{name:<14}{a['wt']:>9.2f}{a['tat']:>12.2f}{a['rt']:>10.2f}{a['latency']:>9.2f}"
              f"{a['cpu_util']:>11.1f}{a['context_switches']:>8}{a['swaps']:>7}")


def best_algorithm(summary):
    """Rank by average of WT, TAT, RT and Latency (lower = better)."""
    score = {n: (a["wt"] + a["tat"] + a["rt"] + a["latency"]) / 4 for n, a in summary.items()}
    best = min(score, key=score.get)
    print("\nOverall score (mean of WT, TAT, RT, Latency - lower is better):")
    for n, s in sorted(score.items(), key=lambda x: x[1]):
        print(f"  {n:<14}{s:6.2f}")
    print(f"\nMost efficient scheduling algorithm: {best}")
    return best


def plot_comparison(summary, out_dir):
    names = list(summary.keys())
    metrics = [("wt", "Waiting Time"), ("tat", "Turnaround Time"),
               ("rt", "Response Time"), ("latency", "Latency")]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for ax, (key, title) in zip(axes.flat, metrics):
        vals = [summary[n][key] for n in names]
        colors = ["black" if n == "Edge-Aware" else "white" for n in names]
        bars = ax.bar(names, vals, color=colors, edgecolor="black")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=9)
        ax.set_title(f"Average {title} (ms)")
        ax.tick_params(axis="x", labelsize=9)
    fig.suptitle("Edge-Aware vs Conventional CPU Scheduling")
    fig.tight_layout()
    path = os.path.join(out_dir, "comparison_chart.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_gantt(all_results, out_dir):
    fig, axes = plt.subplots(len(all_results), 1, figsize=(13, 1.3 * len(all_results) + 1),
                             sharex=True)
    for ax, (name, res) in zip(axes, all_results.items()):
        merged = []                       # join back-to-back slices of same process
        for lbl, s, e in res["timeline"]:
            if merged and merged[-1][0] == lbl and merged[-1][2] == s:
                merged[-1] = (lbl, merged[-1][1], e)
            else:
                merged.append((lbl, s, e))
        for lbl, s, e in merged:
            if lbl == "CS":
                ax.barh(0, e - s, left=s, color="lightgrey", edgecolor="black")
            elif lbl == "Swap":
                ax.barh(0, e - s, left=s, color="dimgrey", edgecolor="black")
            elif lbl == "Idle":
                ax.barh(0, e - s, left=s, color="white", edgecolor="black", hatch="//")
            else:
                ax.barh(0, e - s, left=s, color="white", edgecolor="black")
                ax.text((s + e) / 2, 0, lbl, ha="center", va="center", fontsize=8)
        ax.set_yticks([0])
        ax.set_yticklabels([name])
    axes[0].set_xlim(0, max(e for r in all_results.values() for _, _, e in r["timeline"]) + 1)
    axes[-1].set_xlabel("Time (ms)   [light grey = context switch, dark grey = swap delay]")
    fig.suptitle("Gantt Charts")
    fig.tight_layout()
    path = os.path.join(out_dir, "gantt_charts.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_device(device, end_time, out_dir):
    ts = list(range(0, end_time + 1))
    fig, ax1 = plt.subplots(figsize=(10, 3.5))
    ax1.plot(ts, [device.cpu_utilization(t) for t in ts], "k-", label="Background CPU %")
    ax1.set_ylabel("CPU utilization (%)")
    ax2 = ax1.twinx()
    ax2.plot(ts, [device.free_memory(t) for t in ts], "k--", label="Free memory (MB)")
    ax2.set_ylabel("Free memory (MB)")
    ax1.set_xlabel("Time (ms)")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper right")
    ax1.set_title("Edge Device Resource Conditions")
    fig.tight_layout()
    path = os.path.join(out_dir, "edge_device_resources.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
