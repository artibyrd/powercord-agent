#!/usr/bin/env python3
"""Kill orphaned pytest or python test processes across the Powercord workspace."""
import os
import signal
import psutil

def main():
    current_pid = os.getpid()
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline:
                cmdline_str = " ".join(cmdline)
                if ("pytest" in cmdline_str or "test" in cmdline_str) and ("powercord" in cmdline_str or "ecosystem" in cmdline_str):
                    pid = proc.info['pid']
                    if pid != current_pid:
                        print(f"Killing stale test process {pid}: {cmdline_str}")
                        os.kill(pid, signal.SIGKILL)
                        killed += 1
        except Exception:
            pass
    print(f"Cleanup complete. Terminated {killed} processes.")

if __name__ == "__main__":
    main()
