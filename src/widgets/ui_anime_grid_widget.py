# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anime_grid_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QScrollArea,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_AnimeGridWidget(object):
    def setupUi(self, AnimeGridWidget):
        if not AnimeGridWidget.objectName():
            AnimeGridWidget.setObjectName(u"AnimeGridWidget")
        AnimeGridWidget.resize(400, 300)
        AnimeGridWidget.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 398, 298))
        self.horizontalLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.grid_layout = QGridLayout()
        self.grid_layout.setObjectName(u"grid_layout")

        self.horizontalLayout.addLayout(self.grid_layout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        AnimeGridWidget.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(AnimeGridWidget)

        QMetaObject.connectSlotsByName(AnimeGridWidget)
    # setupUi

    def retranslateUi(self, AnimeGridWidget):
        pass
    # retranslateUi

