"""Kullanici kontrollerini iceren panel."""
from PySide6.QtWidgets import QWidget

class ControlPanel(QWidget):
    """Baslat/durdur gibi butonlari icerir."""

    def __init__(self):
        super().__init__()
