# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QComboBox)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 400)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title_label = QLabel(Form)
        self.title_label.setObjectName(u"title_label")

        self.verticalLayout.addWidget(self.title_label)

        self.path_layout = QHBoxLayout()
        self.path_layout.setObjectName(u"path_layout")
        self.path_label = QLabel(Form)
        self.path_label.setObjectName(u"path_label")

        self.path_layout.addWidget(self.path_label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.path_layout.addItem(self.horizontalSpacer)

        self.btn_select_folder = QPushButton(Form)
        self.btn_select_folder.setObjectName(u"btn_select_folder")

        self.path_layout.addWidget(self.btn_select_folder)


        self.verticalLayout.addLayout(self.path_layout)

        self.btn_scan = QPushButton(Form)
        self.btn_scan.setObjectName(u"btn_scan")

        self.verticalLayout.addWidget(self.btn_scan)

        self.chk_auto_scan = QCheckBox(Form)
        self.chk_auto_scan.setObjectName(u"chk_auto_scan")

        self.verticalLayout.addWidget(self.chk_auto_scan)

        self.elide_layout = QHBoxLayout()
        self.elide_layout.setObjectName(u"elide_layout")
        self.elide_label = QLabel(Form)
        self.elide_label.setObjectName(u"elide_label")
        self.elide_layout.addWidget(self.elide_label)
        self.elide_combobox = QComboBox(Form)
        self.elide_combobox.setObjectName(u"elide_combobox")
        self.elide_layout.addWidget(self.elide_combobox)
        self.verticalLayout.addLayout(self.elide_layout)
        
        self.data_label = QLabel(Form)
        self.data_label.setObjectName(u"data_label")

        self.verticalLayout.addWidget(self.data_label)

        self.btn_clear_covers = QPushButton(Form)
        self.btn_clear_covers.setObjectName(u"btn_clear_covers")

        self.verticalLayout.addWidget(self.btn_clear_covers)

        self.btn_clear_db = QPushButton(Form)
        self.btn_clear_db.setObjectName(u"btn_clear_db")

        self.verticalLayout.addWidget(self.btn_clear_db)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.title_label.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.path_label.setText(QCoreApplication.translate("Form", u"Library Folder:", None))
        self.btn_select_folder.setText(QCoreApplication.translate("Form", u"Select Folder", None))
        self.btn_scan.setText(QCoreApplication.translate("Form", u"Scan Library Now", None))
        self.chk_auto_scan.setText(QCoreApplication.translate("Form", u"Automatically scan library on startup", None))
        self.elide_label.setText(QCoreApplication.translate("Form", u"Title Text Truncation:", None))
        self.data_label.setText(QCoreApplication.translate("Form", u"Data Management", None))
        self.btn_clear_covers.setText(QCoreApplication.translate("Form", u"Clear Cover Cache", None))
        self.btn_clear_db.setText(QCoreApplication.translate("Form", u"Clear Library Database", None))
    # retranslateUi

