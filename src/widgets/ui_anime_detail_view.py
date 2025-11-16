# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anime_detail_view.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 300)
        self.main_layout = QVBoxLayout(Form)
        self.main_layout.setObjectName(u"main_layout")
        self.top_controls_layout = QHBoxLayout()
        self.top_controls_layout.setObjectName(u"top_controls_layout")
        self.btn_back = QPushButton(Form)
        self.btn_back.setObjectName(u"btn_back")

        self.top_controls_layout.addWidget(self.btn_back)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.top_controls_layout.addItem(self.horizontalSpacer)

        self.btn_toggle_view = QPushButton(Form)
        self.btn_toggle_view.setObjectName(u"btn_toggle_view")

        self.top_controls_layout.addWidget(self.btn_toggle_view)


        self.main_layout.addLayout(self.top_controls_layout)

        self.info_group_box = QGroupBox(Form)
        self.info_group_box.setObjectName(u"info_group_box")
        self.verticalLayout_2 = QVBoxLayout(self.info_group_box)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.description_label = QLabel(self.info_group_box)
        self.description_label.setObjectName(u"description_label")
        self.description_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.description_label)

        self.genres_label = QLabel(self.info_group_box)
        self.genres_label.setObjectName(u"genres_label")

        self.verticalLayout_2.addWidget(self.genres_label)


        self.main_layout.addWidget(self.info_group_box)

        self.content_group_box = QGroupBox(Form)
        self.content_group_box.setObjectName(u"content_group_box")
        self.verticalLayout_3 = QVBoxLayout(self.content_group_box)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.view_stack = QStackedWidget(self.content_group_box)
        self.view_stack.setObjectName(u"view_stack")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.view_stack.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.view_stack.addWidget(self.page_2)

        self.verticalLayout_3.addWidget(self.view_stack)


        self.main_layout.addWidget(self.content_group_box)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_back.setText(QCoreApplication.translate("Form", u"\u2190 Back", None))
        self.btn_toggle_view.setText(QCoreApplication.translate("Form", u"List View", None))
        self.info_group_box.setTitle(QCoreApplication.translate("Form", u"Synopsis", None))
        self.description_label.setText(QCoreApplication.translate("Form", u"Description", None))
        self.genres_label.setText(QCoreApplication.translate("Form", u"Genres", None))
        self.content_group_box.setTitle(QCoreApplication.translate("Form", u"Content", None))
    # retranslateUi

