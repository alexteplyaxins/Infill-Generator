# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowQfGcqn.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QMenu, QMenuBar,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSpinBox, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

from ui.auxilaries_widget import (MultiPlotWidget, PlotWidget, QPlainTextEditLogger, WebPlotWidget)
from ui.mplwidget1 import MplWidget1

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(986, 712)
        font = QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(10)
        self.actionOpen.setFont(font1)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionClose.setCheckable(False)
        self.actionClose.setFont(font1)
        self.action_About = QAction(MainWindow)
        self.action_About.setObjectName(u"action_About")
        self.actionPrint_configuration = QAction(MainWindow)
        self.actionPrint_configuration.setObjectName(u"actionPrint_configuration")
        self.actionPrint_configuration.setFont(font1)
        self.actionOpen_3D_model = QAction(MainWindow)
        self.actionOpen_3D_model.setObjectName(u"actionOpen_3D_model")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(700, 300))
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 9, 9, -1)
        self.widget1 = QWidget(self.centralwidget)
        self.widget1.setObjectName(u"widget1")
        self.horizontalLayout_1 = QHBoxLayout(self.widget1)
        self.horizontalLayout_1.setSpacing(0)
        self.horizontalLayout_1.setObjectName(u"horizontalLayout_1")
        self.horizontalLayout_1.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.tabWidget = QTabWidget(self.widget1)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QSize(720, 480))
        self.tabWidget.setFont(font1)
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.model3d = PlotWidget()
        self.model3d.setObjectName(u"model3d")
        self.frame_2 = QFrame(self.model3d)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(9, 9, 701, 441))
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.tabWidget.addTab(self.model3d, "")
        self.cell = PlotWidget()
        self.cell.setObjectName(u"cell")
        self.tabWidget.addTab(self.cell, "")
        self.layers = MultiPlotWidget()
        self.layers.setObjectName(u"layers")
        self.tabWidget.addTab(self.layers, "")
        self.preview = WebPlotWidget()
        self.preview.setObjectName(u"preview")
        self.tabWidget.addTab(self.preview, "")
        self.preview_layer = PlotWidget()
        self.preview_layer.setObjectName(u"preview_layer")
        self.preview_layer.setEnabled(True)
        self.ZLayer_sld = QSlider(self.preview_layer)
        self.ZLayer_sld.setObjectName(u"ZLayer_sld")
        self.ZLayer_sld.setGeometry(QRect(660, 10, 20, 421))
        self.ZLayer_sld.setValue(1)
        self.ZLayer_sld.setOrientation(Qt.Orientation.Vertical)
        # self.slider_printpath_preview = QWidget(self.preview_layer)
        # self.slider_printpath_preview.setObjectName(u"slider_printpath_preview")
        # self.slider_printpath_preview.setGeometry(QRect(20, 10, 621, 421))
        # self.slider_printpath_preview.setFrameShape(QFrame.Shape.StyledPanel)
        # self.slider_printpath_preview.setFrameShadow(QFrame.Shadow.Raised)
        self.tabWidget.addTab(self.preview_layer, "")

        ## Add Matplotline MplWidget
        self.MplWidget1 = MplWidget1(self.preview_layer)
        self.MplWidget1.setObjectName("MplWidget")
        self.MplWidget1.setGeometry(QRect(30, 30, 621, 421))
        # self.preview_layer.addWidget(self.MplWidget1)
        ################################
        
        self.horizontalLayout_1.addWidget(self.tabWidget)
        self.widget3 = QWidget(self.widget1)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget3.sizePolicy().hasHeightForWidth())
        self.widget3.setSizePolicy(sizePolicy1)
        self.widget3.setMinimumSize(QSize(230, 0))
        self.widget3.setMaximumSize(QSize(250, 16777215))
        font2 = QFont()
        font2.setPointSize(6)
        self.widget3.setFont(font2)
        self.verticalLayout_3 = QVBoxLayout(self.widget3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.widget3)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, -272, 200, 626))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(200, 0))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.widget = QWidget(self.scrollAreaWidgetContents)
        self.widget.setObjectName(u"widget")
        self.widget.setFont(font)
        self.formLayout_2 = QFormLayout(self.widget)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_10 = QLabel(self.widget)
        self.label_10.setObjectName(u"label_10")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        font3.setBold(True)
        self.label_10.setFont(font3)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_10)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.spinBox = QSpinBox(self.widget)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setFont(font1)
        self.spinBox.setMinimum(2)
        self.spinBox.setMaximum(3)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.spinBox)

        self.label_13 = QLabel(self.widget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font1)

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_13)

        self.x_cells = QSpinBox(self.widget)
        self.x_cells.setObjectName(u"x_cells")
        self.x_cells.setFont(font1)
        self.x_cells.setMinimum(1)
        self.x_cells.setMaximum(3)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.x_cells)

        self.label_14 = QLabel(self.widget)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setFont(font1)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_14)

        self.y_cells = QSpinBox(self.widget)
        self.y_cells.setObjectName(u"y_cells")
        self.y_cells.setFont(font1)
        self.y_cells.setMinimum(1)
        self.y_cells.setMaximum(3)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.y_cells)

        self.label_11 = QLabel(self.widget)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font3)

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_11)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font1)

        self.formLayout_2.setWidget(6, QFormLayout.LabelRole, self.label_5)

        self.scale = QDoubleSpinBox(self.widget)
        self.scale.setObjectName(u"scale")
        self.scale.setFont(font1)
        self.scale.setMinimum(0.100000000000000)
        self.scale.setMaximum(5.000000000000000)
        self.scale.setSingleStep(0.100000000000000)
        self.scale.setValue(1.000000000000000)

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.scale)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.formLayout_2.setWidget(7, QFormLayout.LabelRole, self.label_4)

        self.rows = QSpinBox(self.widget)
        self.rows.setObjectName(u"rows")
        self.rows.setFont(font1)
        self.rows.setMinimum(1)
        self.rows.setValue(5)

        self.formLayout_2.setWidget(7, QFormLayout.FieldRole, self.rows)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.formLayout_2.setWidget(8, QFormLayout.LabelRole, self.label_3)

        self.cols = QSpinBox(self.widget)
        self.cols.setObjectName(u"cols")
        self.cols.setFont(font1)
        self.cols.setMinimum(1)
        self.cols.setValue(5)

        self.formLayout_2.setWidget(8, QFormLayout.FieldRole, self.cols)

        self.label_15 = QLabel(self.widget)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font1)

        self.formLayout_2.setWidget(9, QFormLayout.LabelRole, self.label_15)

        self.layers_num = QSpinBox(self.widget)
        self.layers_num.setObjectName(u"layers_num")
        self.layers_num.setFont(font1)
        self.layers_num.setMinimum(1)
        self.layers_num.setMaximum(100)
        self.layers_num.setValue(10)

        self.formLayout_2.setWidget(9, QFormLayout.FieldRole, self.layers_num)

        self.label_16 = QLabel(self.widget)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFont(font3)

        self.formLayout_2.setWidget(10, QFormLayout.LabelRole, self.label_16)

        self.printer = QComboBox(self.widget)
        self.printer.setObjectName(u"printer")
        self.printer.setFont(font1)

        self.formLayout_2.setWidget(12, QFormLayout.FieldRole, self.printer)

        self.label_9 = QLabel(self.widget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font1)

        self.formLayout_2.setWidget(13, QFormLayout.LabelRole, self.label_9)

        self.layer_height = QDoubleSpinBox(self.widget)
        self.layer_height.setObjectName(u"layer_height")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.layer_height.sizePolicy().hasHeightForWidth())
        self.layer_height.setSizePolicy(sizePolicy2)
        self.layer_height.setFont(font1)
        self.layer_height.setMinimum(0.100000000000000)
        self.layer_height.setMaximum(0.500000000000000)
        self.layer_height.setSingleStep(0.100000000000000)
        self.layer_height.setValue(0.200000000000000)

        self.formLayout_2.setWidget(13, QFormLayout.FieldRole, self.layer_height)

        self.label_18 = QLabel(self.widget)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setFont(font1)

        self.formLayout_2.setWidget(14, QFormLayout.LabelRole, self.label_18)

        self.line_width = QDoubleSpinBox(self.widget)
        self.line_width.setObjectName(u"line_width")
        self.line_width.setFont(font1)
        self.line_width.setMinimum(0.200000000000000)
        self.line_width.setMaximum(2.000000000000000)
        self.line_width.setSingleStep(0.100000000000000)
        self.line_width.setValue(0.400000000000000)

        self.formLayout_2.setWidget(14, QFormLayout.FieldRole, self.line_width)

        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font1)

        self.formLayout_2.setWidget(15, QFormLayout.LabelRole, self.label_7)

        self.x_offset = QDoubleSpinBox(self.widget)
        self.x_offset.setObjectName(u"x_offset")
        self.x_offset.setFont(font1)
        self.x_offset.setSingleStep(0.100000000000000)
        self.x_offset.setValue(10.000000000000000)

        self.formLayout_2.setWidget(15, QFormLayout.FieldRole, self.x_offset)

        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font1)

        self.formLayout_2.setWidget(16, QFormLayout.LabelRole, self.label_8)

        self.y_offset = QDoubleSpinBox(self.widget)
        self.y_offset.setObjectName(u"y_offset")
        self.y_offset.setMinimumSize(QSize(0, 0))
        self.y_offset.setFont(font1)
        self.y_offset.setSingleStep(0.100000000000000)
        self.y_offset.setValue(10.000000000000000)

        self.formLayout_2.setWidget(16, QFormLayout.FieldRole, self.y_offset)

        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)

        self.formLayout_2.setWidget(17, QFormLayout.LabelRole, self.label_6)

        self.print_speed = QSpinBox(self.widget)
        self.print_speed.setObjectName(u"print_speed")
        self.print_speed.setFont(font1)
        self.print_speed.setMinimum(10)
        self.print_speed.setMaximum(120)
        self.print_speed.setSingleStep(0)
        self.print_speed.setValue(45)
        self.print_speed.setDisplayIntegerBase(10)

        self.formLayout_2.setWidget(17, QFormLayout.FieldRole, self.print_speed)

        self.label_19 = QLabel(self.widget)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setFont(font1)

        self.formLayout_2.setWidget(18, QFormLayout.LabelRole, self.label_19)

        self.nozzle_temp = QSpinBox(self.widget)
        self.nozzle_temp.setObjectName(u"nozzle_temp")
        self.nozzle_temp.setFont(font1)
        self.nozzle_temp.setMinimum(180)
        self.nozzle_temp.setMaximum(250)
        self.nozzle_temp.setValue(200)

        self.formLayout_2.setWidget(18, QFormLayout.FieldRole, self.nozzle_temp)

        self.label_20 = QLabel(self.widget)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font1)

        self.formLayout_2.setWidget(19, QFormLayout.LabelRole, self.label_20)

        self.bed_temp = QSpinBox(self.widget)
        self.bed_temp.setObjectName(u"bed_temp")
        self.bed_temp.setMinimumSize(QSize(0, 0))
        self.bed_temp.setFont(font1)
        self.bed_temp.setMinimum(40)
        self.bed_temp.setValue(60)

        self.formLayout_2.setWidget(19, QFormLayout.FieldRole, self.bed_temp)

        self.label_12 = QLabel(self.widget)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font1)

        self.formLayout_2.setWidget(20, QFormLayout.LabelRole, self.label_12)

        self.fan = QSpinBox(self.widget)
        self.fan.setObjectName(u"fan")
        self.fan.setFont(font1)
        self.fan.setMaximum(100)
        self.fan.setValue(100)

        self.formLayout_2.setWidget(20, QFormLayout.FieldRole, self.fan)

        self.label_17 = QLabel(self.widget)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font1)

        self.formLayout_2.setWidget(12, QFormLayout.LabelRole, self.label_17)

        self.allow_perimeter = QCheckBox(self.widget)
        self.allow_perimeter.setObjectName(u"allow_perimeter")

        self.formLayout_2.setWidget(11, QFormLayout.SpanningRole, self.allow_perimeter)


        self.verticalLayout_6.addWidget(self.widget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.split_button = QPushButton(self.widget3)
        self.split_button.setObjectName(u"split_button")
        self.split_button.setFont(font1)

        self.verticalLayout_3.addWidget(self.split_button)

        self.generate_button = QPushButton(self.widget3)
        self.generate_button.setObjectName(u"generate_button")
        self.generate_button.setFont(font1)

        self.verticalLayout_3.addWidget(self.generate_button)

        self.save_gcode_button = QPushButton(self.widget3)
        self.save_gcode_button.setObjectName(u"save_gcode_button")
        self.save_gcode_button.setMinimumSize(QSize(100, 0))
        self.save_gcode_button.setFont(font1)
        self.save_gcode_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_3.addWidget(self.save_gcode_button)

        self.generate_print_path = QPushButton(self.widget3)
        self.generate_print_path.setObjectName(u"generate_print_path")
        self.generate_print_path.setFont(font)

        self.verticalLayout_3.addWidget(self.generate_print_path)


        self.horizontalLayout_1.addWidget(self.widget3)


        self.verticalLayout.addWidget(self.widget1)

        self.widget2 = QWidget(self.centralwidget)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setEnabled(True)
        self.widget2.setMaximumSize(QSize(16777215, 150))
        self.verticalLayout_2 = QVBoxLayout(self.widget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(-1, -1, 6, -1)
        self.sliceProgBar = QProgressBar(self.widget2)
        self.sliceProgBar.setObjectName(u"sliceProgBar")
        self.sliceProgBar.setValue(24)

        self.verticalLayout_2.addWidget(self.sliceProgBar)

        self.logger = QPlainTextEditLogger(self.widget2)
        self.logger.setObjectName(u"logger")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.logger.sizePolicy().hasHeightForWidth())
        self.logger.setSizePolicy(sizePolicy3)
        self.logger.setMinimumSize(QSize(0, 100))
        self.logger.setMaximumSize(QSize(16777215, 100))
        font4 = QFont()
        font4.setFamilies([u"Courier"])
        font4.setPointSize(10)
        self.logger.setFont(font4)

        self.verticalLayout_2.addWidget(self.logger)


        self.verticalLayout.addWidget(self.widget2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 986, 21))
        self.menubar.setFont(font)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setFont(font1)
        self.menu_Help = QMenu(self.menubar)
        self.menu_Help.setObjectName(u"menu_Help")
        self.menu_Help.setFont(font)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.menuFile.addAction(self.actionOpen_3D_model)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menu_Help.addAction(self.action_About)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"CAD Infill Generator", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open DXF", None))
        self.actionOpen.setIconText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.actionOpen.setToolTip(QCoreApplication.translate("MainWindow", u"Open", None))
#endif // QT_CONFIG(tooltip)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionClose.setIconText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.action_About.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.actionPrint_configuration.setText(QCoreApplication.translate("MainWindow", u"Print configuration", None))
        self.actionOpen_3D_model.setText(QCoreApplication.translate("MainWindow", u"Open STL", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.model3d), QCoreApplication.translate("MainWindow", u"3D Model", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.cell), QCoreApplication.translate("MainWindow", u"Unit cell", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.layers), QCoreApplication.translate("MainWindow", u"Layers", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.preview), QCoreApplication.translate("MainWindow", u"Preview", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.preview_layer), QCoreApplication.translate("MainWindow", u"Printpath View", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Split", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Split layers", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"X cells", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Y cells", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Infill", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Rows", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Columns", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Layers", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Print\n"
"                                                                                    Settings", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Layer height", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Line width", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"X offset", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Y offset", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Print speed", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Nozzle temp", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Bed temp", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Fan", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Printer", None))
        self.allow_perimeter.setText(QCoreApplication.translate("MainWindow", u"Allow Perimeter", None))
        self.split_button.setText(QCoreApplication.translate("MainWindow", u"Split", None))
        self.generate_button.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
        self.save_gcode_button.setText(QCoreApplication.translate("MainWindow", u"Save gcode", None))
        self.generate_print_path.setText(QCoreApplication.translate("MainWindow", u"Generate print path", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

