"""Clean up this project's browser process trees on Linux."""
import os
from pathlib import Path
import signal
import time


def find_browser_processes(driver_path):
    processes = {}
    roots = set()
    for entry in Path('/proc').glob('[0-9]*'):
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            args = (entry / 'cmdline').read_bytes().split(b'\0')
            stat = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            pid = int(entry.name)
            processes[pid] = (int(stat[1]), stat[19])
            if args and os.fsdecode(args[0]) == driver_path:
                roots.add(pid)
        except (OSError, ValueError, IndexError):
            continue
    targets = set(roots)
    while True:
        children = {pid for pid, (parent, _) in processes.items() if parent in targets}
        if children <= targets:
            break
        targets.update(children)
    return {pid: processes[pid][1] for pid in targets}


def signal_processes(targets, sig):
    for pid, started in targets.items():
        try:
            # Check process identity again to avoid signalling a reused PID.
            stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            if stat[19] == started:
                os.kill(pid, sig)
        except (OSError, IndexError):
            continue


def cleanup_browser_processes(driver_path):
    if not Path('/proc').is_dir():
        return
    targets = find_browser_processes(driver_path)
    if targets:
        signal_processes(targets, signal.SIGTERM)
        time.sleep(1)
        signal_processes(targets, signal.SIGKILL)
