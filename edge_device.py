"""
Edge Device Model
-----------------
Simulates the changing resource conditions of an edge device.
Other services on the device (camera stream, network stack, etc.) use some
CPU and memory, and this background load changes with time.

The SAME device is used for every algorithm, so the comparison is fair.

Cost rules applied to ALL algorithms:
  * Context switch  : CONTEXT_SWITCH ms each time the CPU changes process.
  * Memory shortage : if a process is dispatched when free memory is less
                      than it needs, pages must be swapped in -> SWAP_DELAY ms.
"""

import math

TOTAL_MEMORY = 1024     # MB
CONTEXT_SWITCH = 1      # ms
SWAP_DELAY = 3          # ms


class EdgeDevice:
    def __init__(self, total_memory=TOTAL_MEMORY):
        self.total_memory = total_memory

    def background_cpu(self, t):
        """CPU % used by other services at time t (varies 20%..70%)."""
        return round(45 + 25 * math.sin(t / 5))

    def background_memory(self, t):
        """Memory (MB) used by other services at time t (varies ~350..750)."""
        return round(550 + 200 * math.sin(t / 4 + 1))

    def free_memory(self, t):
        return self.total_memory - self.background_memory(t)

    def cpu_utilization(self, t):
        return self.background_cpu(t)

    def fits(self, process, t):
        """True if the device can run this process now without swapping/overload."""
        return (process.mem_need <= self.free_memory(t) and
                process.cpu_need + self.background_cpu(t) <= 100)
