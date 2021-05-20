# -*- coding: utf-8 -*-
# core/main.py

"""
This module provides Contacts application.
"""

import sys

from PyQt5.QtWidgets import QApplication

from .database import create_connection
from .views import Window


def main():
    """Contacts main function."""
    # Create the application
    app = QApplication(sys.argv)
    # Connect to the database before creating any window
    if not create_connection("contacts.sqlite"):
        sys.exit(1)
    # Create the main window
    win = Window()
    win.show()
    # Run the event loop
    sys.exit(app.exec())
