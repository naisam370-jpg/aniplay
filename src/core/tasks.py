from PySide6.QtCore import QRunnable, QObject, Signal, Slot

class WorkerSignals(QObject):
    finished = Signal()
    result = Signal(object)
    progress = Signal(int)

class ScannerWorker(QRunnable):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        # 1. Start Directory Walking
        # 2. Perform XXHash on new files
        # 3. Insert into Database
        # 4. Emit progress
        self.signals.progress.emit(50)
        self.signals.finished.emit()