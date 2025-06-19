"""Ana pencere."""
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    """Uygulamanin ana penceresi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Debate")
