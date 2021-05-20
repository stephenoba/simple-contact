# -*- coding: utf-8 -*-

"""This module provides a model to manage the core table."""
from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel, QSqlQueryModel


class Contact(OrderedDict):
    """
    This would represents an instance of a contact
    while it does not directly represent the object
    on the database, it would help in performing secondary
    actions on them.
    """
    def __init__(self, **kwargs):
        super(Contact, self).__init__(kwargs)
        self.name = kwargs.get("name", None)
        self.job = kwargs.get("job", None)
        self.email = kwargs.get("email", None)
        self.mobile = kwargs.get("mobile", None)

    def __repr__(self):
        return f"<Contact: {self.name}>"


class QuerySet(list):
    """
    QuerySet for a list or Contact objects
    """
    def __init__(self):
        super().__init__()

    def append(self, __object):
        if not isinstance(__object, Contact):
            msg = "Invalid type"
            raise TypeError(msg)
        return super().append(__object)

    def __repr__(self):
        return f"<Queryset: {super().__repr__()}>"


class ContactsModel:
    def __init__(self):
        self.model = self._create_model()

    @staticmethod
    def _create_model():
        """Create and set up the model."""
        tableModel = QSqlTableModel()
        tableModel.setTable("core")
        tableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        tableModel.select()
        headers = ("ID", "Name", "Job", "Email", "Mobile")
        for columnIndex, header in enumerate(headers):
            tableModel.setHeaderData(columnIndex, Qt.Horizontal, header)
        return tableModel

    @staticmethod
    def get_query_model():
        model = QSqlQueryModel()
        model.setQuery("SELECT name, job, email, mobile FROM core")
        return model

    def all(self):
        qs = QuerySet()
        model = self.get_query_model()
        row_count = model.rowCount()
        for i in range(row_count):
            name = model.record(i).value("name")
            job = model.record(i).value("job")
            email = model.record(i).value("email")
            mobile = model.record(i).value("mobile")
            contact = Contact(name=name, job=job, email=email, mobile=mobile)
            qs.append(contact)
        return qs

    def add_contact(self, data):
        """Add a contact to the database."""
        rows = self.model.rowCount()
        self.model.insertRows(rows, 1)
        for column, field in enumerate(data):
            self.model.setData(self.model.index(rows, column + 1), field)
        self.model.submitAll()
        self.model.select()

    def add_bulk_contact(self, data):
        for item in data:
            self.add_contact(item)

    def delete_contact(self, row):
        """Remove a contact from the database."""
        self.model.removeRow(row)
        self.model.submitAll()
        self.model.select()

    def clear_contacts(self):
        """Remove all core in the database."""
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.removeRows(0, self.model.rowCount())
        self.model.submitAll()
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()
