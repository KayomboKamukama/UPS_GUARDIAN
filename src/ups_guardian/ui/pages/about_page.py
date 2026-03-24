"""About page."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AboutPage(QWidget):
    """Open-source app information."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("UPS Guardian"))
        layout.addWidget(QLabel("Lightweight Central UPS Monitoring for Multi-Station ICT Environments"))
        layout.addWidget(QLabel("Open-source • Local-first • Windows-focused"))
        layout.addWidget(QLabel("Phase 1 prototype: inventory, mock polling, alerting, and CSV reporting."))
        layout.addStretch(1)
