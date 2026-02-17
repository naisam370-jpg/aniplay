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
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1038, 591)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
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


        self.horizontalLayout_2.addWidget(self.frame)

        self.stacked_widget = QStackedWidget(self.centralwidget)
        self.stacked_widget.setObjectName(u"stacked_widget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.horizontalLayout = QHBoxLayout(self.page_1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scrollArea_2 = QScrollArea(self.page_1)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 869, 553))
        self.horizontalLayout_3 = QHBoxLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.library_grid = QGridLayout()
        self.library_grid.setObjectName(u"library_grid")

        self.horizontalLayout_3.addLayout(self.library_grid)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout.addWidget(self.scrollArea_2)

        self.stacked_widget.addWidget(self.page_1)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_5 = QGridLayout(self.page_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_2, 1, 4, 1, 1)

        self.lbl_big_poster = QLabel(self.page_2)
        self.lbl_big_poster.setObjectName(u"lbl_big_poster")
        self.lbl_big_poster.setMinimumSize(QSize(171, 191))

        self.gridLayout_5.addWidget(self.lbl_big_poster, 1, 0, 3, 1)

        self.lbl_synopsis = QLabel(self.page_2)
        self.lbl_synopsis.setObjectName(u"lbl_synopsis")
        self.lbl_synopsis.setMinimumSize(QSize(621, 81))
        self.lbl_synopsis.setWordWrap(True)

        self.gridLayout_5.addWidget(self.lbl_synopsis, 4, 0, 1, 4)

        self.combo_seasons = QComboBox(self.page_2)
        self.combo_seasons.setObjectName(u"combo_seasons")
        self.combo_seasons.setMinimumSize(QSize(201, 41))
        self.combo_seasons.setEditable(True)

        self.gridLayout_5.addWidget(self.combo_seasons, 4, 4, 1, 1)

        self.scrollArea = QScrollArea(self.page_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(871, 271))
        self.scrollArea.setWidgetResizable(True)
        self.episode_container = QWidget()
        self.episode_container.setObjectName(u"episode_container")
        self.episode_container.setGeometry(QRect(0, 0, 869, 269))
        self.gridLayout_3 = QGridLayout(self.episode_container)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.episode_list_layout = QVBoxLayout()
        self.episode_list_layout.setObjectName(u"episode_list_layout")

        self.gridLayout_3.addLayout(self.episode_list_layout, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.episode_container)

        self.gridLayout_5.addWidget(self.scrollArea, 5, 0, 1, 5)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer, 1, 2, 1, 1)

        self.lbl_title = QLabel(self.page_2)
        self.lbl_title.setObjectName(u"lbl_title")
        self.lbl_title.setMinimumSize(QSize(631, 41))
        self.lbl_title.setMaximumSize(QSize(16777215, 41))
        self.lbl_title.setWordWrap(True)

        self.gridLayout_5.addWidget(self.lbl_title, 3, 1, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_5, 1, 1, 1, 1)

        self.lbl_rating = QLabel(self.page_2)
        self.lbl_rating.setObjectName(u"lbl_rating")

        self.gridLayout_5.addWidget(self.lbl_rating, 2, 1, 1, 1)

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
        self.gridLayout = QGridLayout(self.page_4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_browse_path = QPushButton(self.page_4)
        self.btn_browse_path.setObjectName(u"btn_browse_path")

        self.gridLayout.addWidget(self.btn_browse_path, 0, 1, 1, 1)

        self.edit_library_path = QLineEdit(self.page_4)
        self.edit_library_path.setObjectName(u"edit_library_path")

        self.gridLayout.addWidget(self.edit_library_path, 0, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(318, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 4, 4, 1, 1)

        self.btn_start_scan = QPushButton(self.page_4)
        self.btn_start_scan.setObjectName(u"btn_start_scan")

        self.gridLayout.addWidget(self.btn_start_scan, 0, 2, 1, 2)

        self.verticalSpacer_3 = QSpacerItem(20, 468, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 3, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(318, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 4, 2, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 497, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_4, 3, 3, 2, 1)

        self.scan_progress = QProgressBar(self.page_4)
        self.scan_progress.setObjectName(u"scan_progress")
        self.scan_progress.setValue(24)

        self.gridLayout.addWidget(self.scan_progress, 1, 0, 1, 4)

        self.lbl_scan_status = QLabel(self.page_4)
        self.lbl_scan_status.setObjectName(u"lbl_scan_status")

        self.gridLayout.addWidget(self.lbl_scan_status, 2, 0, 1, 3)

        self.stacked_widget.addWidget(self.page_4)

        self.horizontalLayout_2.addWidget(self.stacked_widget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stacked_widget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_home.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.btn_library.setText(QCoreApplication.translate("MainWindow", u"Library", None))
        self.btn_settings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.lbl_big_poster.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_synopsis.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.combo_seasons.setCurrentText("")
        self.lbl_title.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_rating.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_time.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.btn_browse_path.setText(QCoreApplication.translate("MainWindow", u"Browse Folders", None))
        self.btn_start_scan.setText(QCoreApplication.translate("MainWindow", u"Scan", None))
        self.lbl_scan_status.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

