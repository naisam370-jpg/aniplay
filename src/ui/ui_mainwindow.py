# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QSlider,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1038, 591)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(125, 0))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btn_home = QPushButton(self.frame)
        self.btn_home.setObjectName(u"btn_home")

        self.verticalLayout.addWidget(self.btn_home)

        self.btn_library = QPushButton(self.frame)
        self.btn_library.setObjectName(u"btn_library")

        self.verticalLayout.addWidget(self.btn_library)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.btn_settings = QPushButton(self.frame)
        self.btn_settings.setObjectName(u"btn_settings")

        self.verticalLayout.addWidget(self.btn_settings)


        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)

        self.stacked_widget = QStackedWidget(self.centralwidget)
        self.stacked_widget.setObjectName(u"stacked_widget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.gridLayout_3 = QGridLayout(self.page_1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.scrollArea_2 = QScrollArea(self.page_1)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.episodeWidgetContents = QWidget()
        self.episodeWidgetContents.setObjectName(u"episodeWidgetContents")
        self.episodeWidgetContents.setGeometry(QRect(0, 0, 869, 553))
        self.gridLayout_4 = QGridLayout(self.episodeWidgetContents)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.scrollArea_2.setWidget(self.episodeWidgetContents)

        self.gridLayout_3.addWidget(self.scrollArea_2, 0, 0, 1, 1)

        self.stacked_widget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_5 = QGridLayout(self.page_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.lbl_big_poster = QLabel(self.page_2)
        self.lbl_big_poster.setObjectName(u"lbl_big_poster")
        self.lbl_big_poster.setMinimumSize(QSize(171, 191))

        self.gridLayout_5.addWidget(self.lbl_big_poster, 0, 0, 2, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_2, 0, 2, 1, 1)

        self.lbl_title = QLabel(self.page_2)
        self.lbl_title.setObjectName(u"lbl_title")
        self.lbl_title.setMinimumSize(QSize(631, 41))
        self.lbl_title.setMaximumSize(QSize(16777215, 41))
        self.lbl_title.setWordWrap(True)

        self.gridLayout_5.addWidget(self.lbl_title, 1, 1, 1, 2)

        self.lbl_synopsis = QLabel(self.page_2)
        self.lbl_synopsis.setObjectName(u"lbl_synopsis")
        self.lbl_synopsis.setMinimumSize(QSize(621, 81))
        self.lbl_synopsis.setWordWrap(True)

        self.gridLayout_5.addWidget(self.lbl_synopsis, 2, 0, 1, 2)

        self.combo_seasons = QComboBox(self.page_2)
        self.combo_seasons.setObjectName(u"combo_seasons")
        self.combo_seasons.setMinimumSize(QSize(201, 41))

        self.gridLayout_5.addWidget(self.combo_seasons, 2, 2, 1, 1)

        self.scrollArea = QScrollArea(self.page_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(871, 271))
        self.scrollArea.setWidgetResizable(True)
        self.episode_layout = QWidget()
        self.episode_layout.setObjectName(u"episode_layout")
        self.episode_layout.setGeometry(QRect(0, 0, 869, 269))
        self.gridLayout_6 = QGridLayout(self.episode_layout)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.scrollArea.setWidget(self.episode_layout)

        self.gridLayout_5.addWidget(self.scrollArea, 3, 0, 1, 3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.stacked_widget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout_2 = QGridLayout(self.page_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.video_container = QWidget(self.page_3)
        self.video_container.setObjectName(u"video_container")
        self.video_container.setStyleSheet(u"background-color: black;")

        self.gridLayout_2.addWidget(self.video_container, 0, 0, 1, 2)

        self.video_slider = QSlider(self.page_3)
        self.video_slider.setObjectName(u"video_slider")
        self.video_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_2.addWidget(self.video_slider, 1, 0, 1, 1)

        self.lbl_time = QLabel(self.page_3)
        self.lbl_time.setObjectName(u"lbl_time")

        self.gridLayout_2.addWidget(self.lbl_time, 1, 1, 1, 1)

        self.stacked_widget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.edit_library_path = QLineEdit(self.page_4)
        self.edit_library_path.setObjectName(u"edit_library_path")
        self.edit_library_path.setGeometry(QRect(20, 20, 251, 21))
        self.btn_browse_path = QPushButton(self.page_4)
        self.btn_browse_path.setObjectName(u"btn_browse_path")
        self.btn_browse_path.setGeometry(QRect(290, 20, 80, 21))
        self.btn_start_scan = QPushButton(self.page_4)
        self.btn_start_scan.setObjectName(u"btn_start_scan")
        self.btn_start_scan.setGeometry(QRect(390, 20, 80, 21))
        self.scan_progress = QProgressBar(self.page_4)
        self.scan_progress.setObjectName(u"scan_progress")
        self.scan_progress.setGeometry(QRect(20, 50, 391, 23))
        self.scan_progress.setValue(24)
        self.lbl_scan_status = QLabel(self.page_4)
        self.lbl_scan_status.setObjectName(u"lbl_scan_status")
        self.lbl_scan_status.setGeometry(QRect(420, 51, 47, 16))
        self.stacked_widget.addWidget(self.page_4)

        self.gridLayout.addWidget(self.stacked_widget, 0, 2, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stacked_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_home.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.btn_library.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.btn_settings.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.lbl_big_poster.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_title.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_synopsis.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_time.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.btn_browse_path.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.btn_start_scan.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.lbl_scan_status.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

