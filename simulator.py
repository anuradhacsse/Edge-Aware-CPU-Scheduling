"""
Common CPU simulator used by every scheduling algorithm.

An algorithm only has to supply two things:
  pick(queue, time, info)     -> which ready process runs next
  quantum(process, time, info)-> how long it may run (None = until it finishes)
"""

from edge_device import CONTEXT_SWITCH, SWAP_DELAY


def simulate(processes, device, pick, quantum=None):
    procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    remaining = {p.pid: p.burst for p in procs}
    last_run = {p.pid: p.arrival for p in procs}     # used for ageing
    first_start, completion = {}, {}
    overhead = {p.pid: 0 for p in procs}             # context switch + swap time
    timeline = []                                    # (label, start, end)

    time, idx, last_pid = 0, 0, None
    queue = []                                       # ready queue (FIFO order)
    info = {"remaining": remaining, "last_run": last_run, "device": device}

    def admit(upto):
        nonlocal idx
        while idx < len(procs) and procs[idx].arrival <= upto:
            queue.append(procs[idx])
            idx += 1

    admit(time)
    while len(completion) < len(procs):
        if not queue:                                # CPU idle
            nxt = procs[idx].arrival
            timeline.append(("Idle", time, nxt))
            time = nxt
            admit(time)
            continue

        p = pick(queue, time, info)
        queue.remove(p)

        if p.pid not in first_start:
            first_start[p.pid] = time

        # Context switch cost
        if last_pid is not None and last_pid != p.pid:
            timeline.append(("CS", time, time + CONTEXT_SWITCH))
            time += CONTEXT_SWITCH
            overhead[p.pid] += CONTEXT_SWITCH

        # Memory not available -> swap delay
        if p.mem_need > device.free_memory(time) and last_pid != p.pid:
            timeline.append(("Swap", time, time + SWAP_DELAY))
            time += SWAP_DELAY
            overhead[p.pid] += SWAP_DELAY

        q = quantum(p, time, info) if quantum else None
        run = remaining[p.pid] if q is None else min(q, remaining[p.pid])
        timeline.append((p.pid, time, time + run))
        time += run
        remaining[p.pid] -= run
        last_run[p.pid] = time
        last_pid = p.pid

        admit(time)                                  # new arrivals join first
        if remaining[p.pid] == 0:
            completion[p.pid] = time
        else:
            queue.append(p)                          # preempted -> back of queue

    return {"first_start": first_start, "completion": completion,
            "overhead": overhead, "timeline": timeline,
            "context_switches": sum(1 for t in timeline if t[0] == "CS"),
            "swaps": sum(1 for t in timeline if t[0] == "Swap")}
