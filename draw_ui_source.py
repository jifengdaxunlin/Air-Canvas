# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mediapipe_draw.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1400, 880)
        self.label_video = QLabel(Form)
        self.label_video.setObjectName(u"label_video")
        self.label_video.setGeometry(QRect(10, 20, 1161, 841))
        self.label_video.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.but_color_select = QPushButton(Form)
        self.but_color_select.setObjectName(u"but_color_select")
        self.but_color_select.setGeometry(QRect(1200, 700, 181, 71))
        font = QFont()
        font.setFamilies([u"\u5e7c\u5706"])
        font.setPointSize(20)
        font.setBold(True)
        self.but_color_select.setFont(font)
        self.but_color_select.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")
        self.label_symble = QLabel(Form)
        self.label_symble.setObjectName(u"label_symble")
        self.label_symble.setGeometry(QRect(1200, 630, 181, 61))
        self.label_symble.setStyleSheet(u"QLabel {\n"
"    background-color: rgb(255, 255, 255);\n"
"    font-weight: bold;\n"
"    color: #bac2de;\n"
"}\n"
"")
        self.but_pic_select = QPushButton(Form)
        self.but_pic_select.setObjectName(u"but_pic_select")
        self.but_pic_select.setGeometry(QRect(1200, 790, 181, 61))
        self.but_pic_select.setFont(font)
        self.but_pic_select.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(1260, 400, 61, 221))
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_green_flag = QLabel(self.layoutWidget)
        self.label_green_flag.setObjectName(u"label_green_flag")
        font1 = QFont()
        font1.setFamilies([u"\u5e7c\u5706"])
        font1.setPointSize(12)
        self.label_green_flag.setFont(font1)
        self.label_green_flag.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_green_flag)

        self.verticalSlider_green = QSlider(self.layoutWidget)
        self.verticalSlider_green.setObjectName(u"verticalSlider_green")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalSlider_green.sizePolicy().hasHeightForWidth())
        self.verticalSlider_green.setSizePolicy(sizePolicy)
        self.verticalSlider_green.setStyleSheet(u"QSlider::groove:vertical {\n"
"    background: #313244;\n"
"    width: 6px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::sub-page:vertical {\n"
"    background: #313244;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::add-page:vertical {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #b4befe);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::handle:vertical {\n"
"    background: #f5e0dc;\n"
"    border: 2px solid #89b4fa;\n"
"    height: 16px;\n"
"    width: 16px;\n"
"    margin: 0 -5px;\n"
"    border-radius: 9px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover {\n"
"    background: #ffffff;\n"
"    border-color: #b4befe;\n"
"    transform: scale(1.2);\n"
"}")
        self.verticalSlider_green.setMaximum(255)
        self.verticalSlider_green.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout_2.addWidget(self.verticalSlider_green)

        self.label_green_num = QLabel(self.layoutWidget)
        self.label_green_num.setObjectName(u"label_green_num")
        font2 = QFont()
        font2.setPointSize(12)
        self.label_green_num.setFont(font2)
        self.label_green_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_green_num)

        self.layoutWidget_2 = QWidget(Form)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(1330, 400, 61, 221))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_red_flag = QLabel(self.layoutWidget_2)
        self.label_red_flag.setObjectName(u"label_red_flag")
        self.label_red_flag.setFont(font1)
        self.label_red_flag.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_red_flag)

        self.verticalSlider_red = QSlider(self.layoutWidget_2)
        self.verticalSlider_red.setObjectName(u"verticalSlider_red")
        sizePolicy.setHeightForWidth(self.verticalSlider_red.sizePolicy().hasHeightForWidth())
        self.verticalSlider_red.setSizePolicy(sizePolicy)
        self.verticalSlider_red.setStyleSheet(u"QSlider::groove:vertical {\n"
"    background: #313244;\n"
"    width: 6px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::sub-page:vertical {\n"
"    background: #313244;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::add-page:vertical {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #b4befe);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::handle:vertical {\n"
"    background: #f5e0dc;\n"
"    border: 2px solid #89b4fa;\n"
"    height: 16px;\n"
"    width: 16px;\n"
"    margin: 0 -5px;\n"
"    border-radius: 9px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover {\n"
"    background: #ffffff;\n"
"    border-color: #b4befe;\n"
"    transform: scale(1.2);\n"
"}")
        self.verticalSlider_red.setMaximum(255)
        self.verticalSlider_red.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout_3.addWidget(self.verticalSlider_red)

        self.label_red_num = QLabel(self.layoutWidget_2)
        self.label_red_num.setObjectName(u"label_red_num")
        self.label_red_num.setFont(font2)
        self.label_red_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_red_num)

        self.layoutWidget1 = QWidget(Form)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(1190, 400, 61, 221))
        self.verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_bule_flag = QLabel(self.layoutWidget1)
        self.label_bule_flag.setObjectName(u"label_bule_flag")
        self.label_bule_flag.setFont(font1)
        self.label_bule_flag.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_bule_flag)

        self.verticalSlider_blue = QSlider(self.layoutWidget1)
        self.verticalSlider_blue.setObjectName(u"verticalSlider_blue")
        sizePolicy.setHeightForWidth(self.verticalSlider_blue.sizePolicy().hasHeightForWidth())
        self.verticalSlider_blue.setSizePolicy(sizePolicy)
        self.verticalSlider_blue.setStyleSheet(u"QSlider::groove:vertical {\n"
"    background: #313244;\n"
"    width: 6px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::sub-page:vertical {\n"
"    background: #313244;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::add-page:vertical {\n"
"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #89b4fa, stop:1 #b4befe);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::handle:vertical {\n"
"    background: #f5e0dc;\n"
"    border: 2px solid #89b4fa;\n"
"    height: 16px;\n"
"    width: 16px;\n"
"    margin: 0 -5px;\n"
"    border-radius: 9px;\n"
"}\n"
"\n"
"QSlider::handle:vertical:hover {\n"
"    background: #ffffff;\n"
"    border-color: #b4befe;\n"
"    transform: scale(1.2);\n"
"}")
        self.verticalSlider_blue.setMaximum(255)
        self.verticalSlider_blue.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout.addWidget(self.verticalSlider_blue)

        self.label_blue_num = QLabel(self.layoutWidget1)
        self.label_blue_num.setObjectName(u"label_blue_num")
        self.label_blue_num.setFont(font2)
        self.label_blue_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_blue_num)

        self.layoutWidget2 = QWidget(Form)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(1190, 340, 190, 33))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget2)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label)

        self.font_size = QSpinBox(self.layoutWidget2)
        self.font_size.setObjectName(u"font_size")
        self.font_size.setStyleSheet(u"QSpinBox {\n"
"    background-color: #ffffff;\n"
"    color: #2b2d42;\n"
"    border: 1px solid #ced4da;\n"
"    border-radius: 6px;\n"
"    padding: 4px 10px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QSpinBox:hover {\n"
"    border-color: #4a90e2;\n"
"}\n"
"\n"
"QSpinBox:focus {\n"
"    border: 1.5px solid #4a90e2;\n"
"    background-color: #ffffff;\n"
"}")
        self.font_size.setMinimum(1)
        self.font_size.setMaximum(50)

        self.horizontalLayout.addWidget(self.font_size)

        self.layoutWidget3 = QWidget(Form)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(1190, 10, 188, 321))
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.but_open_save_face = QPushButton(self.layoutWidget3)
        self.but_open_save_face.setObjectName(u"but_open_save_face")
        font3 = QFont()
        font3.setFamilies([u"\u5e7c\u5706"])
        font3.setPointSize(12)
        font3.setBold(True)
        self.but_open_save_face.setFont(font3)
        self.but_open_save_face.setStyleSheet(u"QPushButton {\n"
"    background-color: #89b4fa;\n"
"    color: #11111b;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #b4befe;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")

        self.verticalLayout_4.addWidget(self.but_open_save_face)

        self.but_recognizer_LBPH = QPushButton(self.layoutWidget3)
        self.but_recognizer_LBPH.setObjectName(u"but_recognizer_LBPH")
        self.but_recognizer_LBPH.setFont(font3)
        self.but_recognizer_LBPH.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")

        self.verticalLayout_4.addWidget(self.but_recognizer_LBPH)

        self.but_close = QPushButton(self.layoutWidget3)
        self.but_close.setObjectName(u"but_close")
        self.but_close.setFont(font3)
        self.but_close.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")

        self.verticalLayout_4.addWidget(self.but_close)

        self.but_draw = QPushButton(self.layoutWidget3)
        self.but_draw.setObjectName(u"but_draw")
        self.but_draw.setFont(font3)
        self.but_draw.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")

        self.verticalLayout_4.addWidget(self.but_draw)

        self.but_save_pic = QPushButton(self.layoutWidget3)
        self.but_save_pic.setObjectName(u"but_save_pic")
        self.but_save_pic.setFont(font3)
        self.but_save_pic.setStyleSheet(u"QPushButton {\n"
"    background-color: #313244;\n"
"    color: #cdd6f4;\n"
"    border: 1px solid #45475a;\n"
"    border-radius: 8px;\n"
"    padding: 10px 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45475a;\n"
"    border-color: #89b4fa;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #181825;\n"
"    border-color: #74c7ec;\n"
"}")

        self.verticalLayout_4.addWidget(self.but_save_pic)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_video.setText("")
        self.but_color_select.setText(QCoreApplication.translate("Form", u"\u989c\u8272\u9009\u62e9", None))
        self.label_symble.setText("")
        self.but_pic_select.setText(QCoreApplication.translate("Form", u"\u5e95\u7247\u9009\u62e9", None))
        self.label_green_flag.setText(QCoreApplication.translate("Form", u"\u7eff", None))
        self.label_green_num.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_red_flag.setText(QCoreApplication.translate("Form", u"\u7ea2", None))
        self.label_red_num.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_bule_flag.setText(QCoreApplication.translate("Form", u"\u84dd", None))
        self.label_blue_num.setText(QCoreApplication.translate("Form", u"0", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u753b\u7b14\u7c97\u7ec6", None))
        self.but_open_save_face.setText(QCoreApplication.translate("Form", u"\u6253\u5f00\u6444\u50cf\u5934/\u4fdd\u5b58\u4eba\u8138", None))
        self.but_recognizer_LBPH.setText(QCoreApplication.translate("Form", u"LBPH\u68c0\u6d4b", None))
        self.but_close.setText(QCoreApplication.translate("Form", u"\u5173\u95ed\u6444\u50cf\u5934", None))
        self.but_draw.setText(QCoreApplication.translate("Form", u"\u6253\u5f00\u753b\u5e03", None))
        self.but_save_pic.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u56fe\u7247", None))
    # retranslateUi

