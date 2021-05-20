# -*- coding: utf-8 -*-

"""
This module provides views to manage the core table.
"""

import csv
import os

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCompleter,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import QStringListModel
# from PyQt5.QtGui import QColor, QPalette

from .model import ContactsModel

allowed_headers = ["name", "job", "email", "mobile"]


# noinspection PyAttributeOutsideInit
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Contacts")
        self.resize(750, 350)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.contactsModel = ContactsModel()
        self.suggestions = self.get_suggestions()
        self.setup_ui()

    @staticmethod
    def get_suggestions():
        suggestions = []
        suggestionQuery = QSqlQueryModel()
        suggestionQuery.setQuery("SELECT name FROM core")
        for n in range(suggestionQuery.rowCount()):
            name = suggestionQuery.record(n).value("name")
            suggestions.append(name.lower())
        return suggestions

    def setup_ui(self):
        """Setup the main window's GUI."""
        self.filter_model = QSortFilterProxyModel()
        self.filter_model.setSourceModel(self.contactsModel.model)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(1)
        # self.filter_model.removeColumn(0)

        # Create the table view widget
        self.table = QTableView()
        # self.table.setModel(self.contactsModel.model)
        self.table.setModel(self.filter_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.resizeColumnsToContents()

        # create completer
        self.searchModel = QStringListModel()
        self.searchModel.setStringList(self.suggestions)
        self.completer = QCompleter()
        self.completer.setModel(self.searchModel)

        # create the search bar and connect to filter and suggestions
        self.searchBar = QLineEdit()
        self.searchBar.setObjectName("Search")
        self.searchBar.textChanged.connect(self.filter_model.setFilterRegExp)
        self.searchBar.setCompleter(self.completer)
        self.searchBar.setMaximumWidth(500)

        # Create buttons
        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.open_add_dialog)
        self.addBulkButton = QPushButton("Add Bulk")
        self.addBulkButton.clicked.connect(self.open_file)
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.delete_contact)
        self.backUpButton = QPushButton("Back up")
        self.backUpButton.clicked.connect(self.backup_contacts)
        self.clearAllButton = QPushButton("Clear All")
        self.clearAllButton.clicked.connect(self.clear_contacts)
        # Lay out the GUI
        layout = QVBoxLayout()
        layout.addWidget(self.addButton)
        layout.addWidget(self.addBulkButton)
        layout.addWidget(self.deleteButton)
        layout.addStretch()
        layout.addWidget(self.backUpButton)
        layout.addWidget(self.clearAllButton)
        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.searchBar)
        tableLayout.addWidget(self.table)
        self.layout.addLayout(tableLayout)
        self.layout.addLayout(layout)

        # palette = self.palette()
        # palette.setColor(QPalette.Window, QColor("blue"))
        # self.setPalette(palette)

    def open_add_dialog(self):
        """Open the Add Contact dialog."""
        dialog = AddDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.contactsModel.add_contact(dialog.data)
            self.table.resizeColumnsToContents()

    def open_file(self):
        dialog = AddBulkDialog(self)
        if dialog.exec() == QFileDialog.Accepted:
            self.contactsModel.add_bulk_contact(dialog.data)
            self.table.resizeColumnsToContents()

    def delete_contact(self):
        """Delete the selected contact from the database."""
        row = self.table.currentIndex().row()
        if row < 0:
            return

        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want to remove the selected contact?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )

        if messageBox == QMessageBox.Ok:
            self.contactsModel.delete_contact(row)

    def backup_contacts(self):
        dialog = BackupDialog(self)
        if dialog.exec() == QFileDialog.Accepted:
            QMessageBox.information(
                self,
                "Success!",
                f"Backup created in {dialog.file}",
            )

    def clear_contacts(self):
        """Remove all core from the database."""
        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want to remove all your core?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )

        if messageBox == QMessageBox.Ok:
            self.contactsModel.clear_contacts()


# noinspection PyAttributeOutsideInit
class AddDialog(QDialog):
    """Add Contact dialog."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent=parent)
        self.setWindowTitle("Add Contact")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the Add Contact dialog's GUI."""
        # Create line edits for data fields
        self.nameField = QLineEdit()
        self.nameField.setObjectName("Name")
        self.jobField = QLineEdit()
        self.jobField.setObjectName("Job")
        self.emailField = QLineEdit()
        self.emailField.setObjectName("Email")
        self.mobileField = QLineEdit()
        self.mobileField.setObjectName("Mobile")
        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Name:", self.nameField)
        layout.addRow("Job:", self.jobField)
        layout.addRow("Email:", self.emailField)
        layout.addRow("Mobile:", self.mobileField)
        self.layout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = []
        for field in (self.nameField, self.jobField, self.emailField, self.mobileField):
            if not field.text():
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"You must provide a contact's {field.objectName()}",
                )
                self.data = None  # Reset .data
                return

            self.data.append(field.text())

        if not self.data:
            return

        super().accept()


# noinspection PyAttributeOutsideInit
class AddBulkDialog(QDialog):
    """Add Contact dialog."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent=parent)
        self.setWindowTitle("Add Bulk Contacts ")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the Add Contact dialog's GUI."""
        # Create line edits for data fields
        self.fileField = QLineEdit()
        self.fileField.setObjectName("File")
        # self.fileField.setDisabled(True)
        self.addButton = QPushButton("Add File")
        self.addButton.clicked.connect(self.select_file)
        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("File:", self.fileField)
        layout.addWidget(self.addButton)
        self.layout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def select_file(self):
        dialog = QFileDialog()
        file_name = dialog.getOpenFileName(
            self, 'Open File', '/home',
            "CSV files (*.csv)",
            options=QFileDialog.DontUseNativeDialog)[0]
        self.fileField.setText(file_name)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = []
        field = self.fileField
        if not field.text():
            QMessageBox.critical(
                self,
                "Error!",
                f"You must provide a contact's {field.objectName()}",
            )
        file = field.text()
        with open(file, 'r') as f:
            csv_reader = csv.DictReader(f)
            if allowed_headers == csv_reader.fieldnames:
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"Invalid headers. allowed headers '{allowed_headers}'",
                )
            for item in csv_reader:
                self.data.append(item.values())

        if not self.data:
            return

        super().accept()


# noinspection PyAttributeOutsideInit
class BackupDialog(QDialog):
    """Add Contact dialog."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent=parent)
        self.setWindowTitle("Backup Contacts")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.data = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the Add Contact dialog's GUI."""
        # Create line edits for data fields
        # Create line edits for data fields
        self.folderField = QLineEdit()
        self.folderField.setObjectName("Folder")
        self.filenameField = QLineEdit()
        self.filenameField.setObjectName("Filename")
        self.filenameField.setText(".csv")
        self.backupButton = QPushButton("Select Folder")
        self.backupButton.clicked.connect(self.select_folder)
        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Folder:", self.folderField)
        layout.addWidget(self.backupButton)
        layout.addRow("Filename:", self.filenameField)
        self.layout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setOrientation(Qt.Horizontal)
        self.buttonsBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonsBox)

    def select_folder(self):
        dialog = QFileDialog()
        folder_name = dialog.getExistingDirectory(
            self, 'Open File', '/home',
            options=QFileDialog.DontUseNativeDialog)
        self.folderField.setText(folder_name)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.file = None
        folderField = self.folderField
        filenameField = self.filenameField
        if not folderField.text() or not filenameField.text():
            QMessageBox.critical(
                self,
                "Error!",
                f"You must provide a {folderField.objectName()} and a {filenameField.objectName()}",
            )
        file = f"{folderField.text()}/{filenameField.text()}"
        _, ext = os.path.splitext(file)
        if not ext or ext != ".csv":
            QMessageBox.critical(
                self,
                "Error!",
                f"File {file} must be in '.csv' format",
            )
        contacts = ContactsModel().all()
        with open(file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=allowed_headers)
            writer.writeheader()

            for contact in contacts:
                writer.writerow(contact)

        self.file = file
        super().accept()
