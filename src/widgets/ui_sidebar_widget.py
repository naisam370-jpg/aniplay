# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sidebar_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(180, 400)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btn_library = QPushButton(Form)
        self.btn_library.setObjectName(u"btn_library")

        self.verticalLayout.addWidget(self.btn_library)

        self.btn_search = QPushButton(Form)
        self.btn_search.setObjectName(u"btn_search")

        self.verticalLayout.addWidget(self.btn_search)
        
        self.btn_refresh = QPushButton(Form)
        self.btn_refresh.setObjectName(u"btn_refresh")
        
        self.verticalLayout.addWidget(self.btn_refresh)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_settings = QPushButton(Form)
        self.btn_settings.setObjectName(u"btn_settings")

        self.verticalLayout.addWidget(self.btn_settings)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_library.setText(QCoreApplication.translate("Form", u"Library", None))
        self.btn_search.setText(QCoreApplication.translate("Form", u"Search", None))
        self.btn_refresh.setText(QCoreApplication.translate("Form", u"Refresh", None))
        self.btn_settings.setText(QCoreApplication.translate("Form", u"Settings", None))
    # retranslateUi

