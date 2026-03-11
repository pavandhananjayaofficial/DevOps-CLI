import time
import threading
from typing import Dict, Any, List, Callable, Optional

class TaskScheduler:
    """
    Background worker and scheduler for DevOps automation tasks.
    """

    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_task(self, name: str, interval_sec: int, action: Callable):
        self.tasks.append({
            "name": name,
            "interval": interval_sec,
            "action": action,
            "last_run": 0
        })
        print(f"[Scheduler] ⏰ Scheduled task: {name} (every {interval_sec}s)")

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        if self._thread:
            self._thread.start()
        print("[Scheduler] 🚀 Background worker started.")

    def _loop(self):
        while self._running:
            now = time.time()
            for task in self.tasks:
                if now - task["last_run"] >= task["interval"]:
                    print(f"[Scheduler] ⚡ Executing task: {task['name']}")
                    try:
                        task["action"]()
                    except Exception as e:
                        print(f"[Scheduler] ❌ Task {task['name']} failed: {e}")
                    task["last_run"] = now
            time.sleep(1)

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
