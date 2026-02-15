from PySide6.QtCore import QObject, QThreadPool, Signal, Slot
from .database import DatabaseManager
from .scanner import ScannerWorker


class AniplayCore(QObject):
    # Signals to update the UI
    scan_progress = Signal(int)
    scan_finished = Signal()

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.thread_pool = QThreadPool.globalInstance()
        self.active_tasks = 0

    def start_library_scan(self, root_path):
        """Launches a background scan of the user's library."""
        self.active_tasks += 1
        worker = ScannerWorker(root_path, self.db)

        # Connect signals to track task completion
        worker.signals.progress.connect(self.scan_progress.emit)
        worker.signals.finished.connect(self._on_task_finished)

        self.thread_pool.start(worker)

    def _on_task_finished(self):
        self.active_tasks -= 1
        if self.active_tasks == 0:
            self.scan_finished.emit()

    def is_busy(self):
        """Returns True if any background thread is currently running."""
        return self.active_tasks > 0