# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLineEdit, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.search_input = QLineEdit(Form)
        self.search_input.setObjectName(u"search_input")

        self.verticalLayout.addWidget(self.search_input)

        self.results_scroll_area = QScrollArea(Form)
        self.results_scroll_area.setObjectName(u"results_scroll_area")
        self.results_scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName(u"scroll_content")
        self.scroll_content.setGeometry(QRect(0, 0, 376, 248))
        self.results_grid_layout = QGridLayout(self.scroll_content)
        self.results_grid_layout.setObjectName(u"results_grid_layout")
        self.results_scroll_area.setWidget(self.scroll_content)

        self.verticalLayout.addWidget(self.results_scroll_area)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.search_input.setPlaceholderText(QCoreApplication.translate("Form", u"Search your library (e.g., 'spy family')...", None))
    # retranslateUi

