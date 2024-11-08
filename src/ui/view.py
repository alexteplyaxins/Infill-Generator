"""view.py

This module contains the main window for the CAD Infill Generator software.
It provides the interface for loading DXF files, splitting layers, generating infill previews,
and saving G-code for 3D printing.

Classes
-------
Window
    The main application window for managing user interactions and displaying the GUI.
"""
import threading

from PySide6.QtWidgets import(
    QMainWindow,
    QMessageBox, 
    QFileDialog
)
from ui.mainwindow1 import Ui_MainWindow
from model.model import Model
import logging
from constants import *

from ui.VTKWindow import VtkViewer
import model.gcode_line as gcode_line

from model.slicer import Slicer


logger = logging.getLogger(LOGGER)


class Window(QMainWindow, Ui_MainWindow):
    """Main application window for the CAD Infill Generator software.
    
    This class provides the interface for loading DXF files, splitting them into layers, generating 
    infill patterns, and exporting G-code files for 3D printing. It connects various signals and 
    slots to handle user inputs and actions.

    Parameters
    ----------
    model : Model
        The backend model handling the data and operations for the application.
    parent : QWidget, optional
        The parent widget of the main window (default is None).

    Attributes
    ----------
    model : Model
        The model that stores the DXF file data and manages infill generation.
    printer : QComboBox
        A dropdown to select the type of printer for infill generation.
    spinBox : QSpinBox
        Input for setting the number of layers.
    x_cells : QSpinBox
        Input for setting the number of X cells for splitting layers.
    y_cells : QSpinBox
        Input for setting the number of Y cells for splitting layers.
    rows : QSpinBox
        Input for setting the number of rows for infill generation.
    cols : QSpinBox
        Input for setting the number of columns for infill generation.
    scale : QDoubleSpinBox
        Input for setting the scale factor for infill generation.
    offset : tuple
        Stores the X and Y offset values for infill pattern generation.
    preview : QWidget
        Widget that shows the generated infill preview.
    
    Methods
    -------
    connectSignalsSlots()
        Connects UI elements to corresponding functions.
        
    about()
        Displays an "About" dialog providing information about the software.
    
    update_cell(plot_func)
        Updates the cell plot using the provided plot function.
        
    update_layers(items, plot_func)
        Updates the layer plots with new items and a plot function.
        
    update_preview(html)
        Displays the HTML preview of the generated infill.
    
    clear_all()
        Clears all plots and previews from the window.
        
    open_file()
        Opens a DXF file, processes it, and updates the cell plot.
        
    split_layers()
        Splits the loaded DXF file into layers for infill generation.
    
    generate_preview()
        Generates a preview of the 3D print infill based on the selected settings.
        
    save_gcode()
        Exports the generated infill pattern as a G-code file.
    """
    def __init__(self, model: Model):
        """Initializes the main window and sets up the UI.

        Parameters
        ----------
        model : Model
            The data model managing the DXF and infill generation.
        parent : QWidget, optional
            The parent widget of this window (default is None).
        """
        super().__init__()
        self.setWindowTitle("CAD Infill Generator")
        self.setupUi(self)
        self.connectSignalsSlots()
        self.printer.addItems(PRINTER)
        self.model = model
        self.vtkViewer = VtkViewer(self.frame_2)  
        

    def connectSignalsSlots(self):
        """Connects UI elements (buttons, menus) to corresponding functions.
        """
        self.actionClose.triggered.connect(self.close)
        self.action_About.triggered.connect(self.about)
        self.actionOpen_3D_model.triggered.connect(self.open3dmodel)
        self.actionOpen.triggered.connect(self.open_file)
        self.split_button.clicked.connect(self.split_layers)
        self.generate_button.clicked.connect(self.generate_preview)
        self.save_gcode_button.clicked.connect(self.save_gcode)
        self.generate_print_path.clicked.connect(self.gen_print_path)
        self.ZLayer_sld.valueChanged.connect(self.ZLayer_sldF)

        logger.addHandler(self.logger.getHandler())
        logger.setLevel("INFO")        

    def about(self):
        """Displays an "About" dialog providing information about the software.
        """
        QMessageBox.about(
            self,
            "About",
            "<p>A program to generate infill patterns from CAD files."
            "<p>For more information, please contact <a href=\"https://sites.google.com/view/ims-lab-hust/home\">IMS Lab</a>.</p>",
        )
    
    def open3dmodel(self):
        file_name = QFileDialog.getOpenFileName(self, "Open File", "", "STL Files (*.stl);; All Files (*)")[0] # Open File
        if file_name:
            self.model.update_model3d(file_name, self.sliceProgBar, self.allow_perimeter.isChecked())
            self.model3d = self.model.model3d
            self.vtkViewer.load_3d_object(file_name)
            self.init_slicer()

        
    def init_slicer(self):
        self.slicer = Slicer([self.model3d], 
                             logger, 
                             self.sliceProgBar, 
                             self.allow_perimeter)
        
    def update_cell(self, plot_func):
        """Updates the cell plot in the UI with a provided plot function.

        Parameters
        ----------
        plot_func : function
            A function that generates the plot to be displayed in the cell widget.
        """
        self.cell.plot_fig(plot_func)

    def update_layers(self, items, plot_func):
        """Updates the layer plot with provided items and plot function.

        Parameters
        ----------
        items : list
            A list of items representing the splitted layers to be plotted.
        plot_func : function
            A function to plot the layers.
        """
        self.layers.update_plot(items, plot_func)

    def update_preview(self, html):
        """Updates the preview area with the generated fullcontrol plotly HTML representation of the infill pattern.

        Parameters
        ----------
        html : str
            lHTML string representing the infill pattern preview.
        """
        self.preview.show_graph(html)

    def clear_all(self):
        """Clears all displayed content in the layers and preview areas.
        """
        self.layers.clear()
        self.preview.clear()

    def open_file(self):
        """Opens a file dialog to load a DXF file and processes it to generate an infill pattern.

        Raises
        ------
        Exception
            If there is an error opening or processing the file.
        """
        try:
            fname = QFileDialog.getOpenFileName(self, "Open File", "", "DXF files (*.dxf)")[0] #File name
            self.model.update(fname) #Update the model with the dxf file
            self.clear_all() #Clear all plots
            self.update_cell(self.model.get_cell_plot()) #Update the cell plot
        except Exception as e:
            logger.error(str(e))
            QMessageBox.critical(
                self,
                "File error",
                str(e)
            )
    
    def split_layers(self):
        """ Splits the loaded DXF file into multiple layers based on user inputs.

        Raises
        ------
        Exception
            If there is an error during the layer splitting process.
        """
        try:
            #Get user's input
            n = self.spinBox.value()
            x = self.x_cells.value()
            y = self.y_cells.value()
            #Decompose layers then update layers plot
            self.model.split_layers(n, x, y)
            self.layers.update_plot(self.model.get_layers_items(), self.model.get_layers_plot())
        except Exception as e:
            logger.error(str(e))
            QMessageBox.critical(
                self,
                "Splits error",
                str(e)
            )
    
    def generate_preview(self):
        """Generates a preview of the infill pattern based on user-selected settings.

        Raises
        ------
        Exception
            If there is an error during infill generation.
        """
        try:
            #Get user's inputs
            split_id = self.layers.picker.currentIndex()
            rows = self.rows.value()
            cols = self.cols.value()
            num_layers = self.layers_num.value()
            scale = self.scale.value()
            offset = (self.x_offset.value(), self.y_offset.value())
            printer = self.printer.currentText()
            print_speed = self.print_speed.value()
            setting = {
                'print_speed': print_speed*60,
                'extrusion_width': self.line_width.value(),
                'extrusion_height': self.layer_height.value(), 
                'nozzle_temp': self.nozzle_temp.value(), 
                'bed_temp': self.bed_temp.value(), 
                'fan_percent': self.fan.value()
            }
            #Generate print path and update preview
            self.model.generate_printpath(
                split_id=split_id,
                rows=rows, cols=cols,
                offset=offset,
                scale=scale, 
                num_layers=num_layers,
                printer=printer,
                setting=setting
            )
            self.update_preview(html=self.model.generate_preview())
        except Exception as e:
            logger.error(str(e))
            QMessageBox.critical(
                self,
                "Splits error",
                str(e)
            )
    
    def save_gcode(self):
        """Saves the generated infill pattern as a G-code file.

        Raises
        ------
        Exception
            If there is an error during the file saving process.
        """
        try:
            fname, _ = QFileDialog.getSaveFileName(self, "Save File", "", "G-code files (*.gcode)") #File name
            self.model.save_gcode(fname) #Save gcode to file name
        except Exception as e:
            logger.error(str(e))
            QMessageBox.critical(
                self,
                "Splits error",
                str(e)
            )

    def gen_print_path(self):

        if not self.slicer.gcode_data or self.slicer.gcode_data is None:
            self.slicer.slice_to_file()
            self.update_plot3d(self.slicer.gcode_data)


    def ZLayer_sldF(self, value):
        self.MplWidget1.canvas.axes.clear()
        iPath = 0
        if self.zLayer != []:
            self.ZLayer_sld.setRange(1, len(self.zLayer) - 1)
            self.ZLayer_sld.setPageStep(1)
            self.ZLayer_sld.setTickInterval(1)
            if value < len(self.zLayer):  # Lấy các list path trong Layer
                # self.ui.ZValue_lbl.setText('Lớp ' + str(value))
                iLayer = self.zLayer[value]
                for sLayer in iLayer:  # Lấy các tham số trong list path
                    iPath += 1
                    if sLayer[0] != '':  # List các tọa độ X
                        T = sLayer[3][len(sLayer[3]) - 1]
                        G = sLayer[4][len(sLayer[4]) - 1]
                        self.plotData1(
                            sLayer[0], sLayer[1], self.color[T - 1], self.linetype[G], 1.5, '')
        self.MplWidget1.canvas.axes.set_title(
            ' Mô tả lớp in thứ ' + str(value))
        #self.ui.MplWidget1.canvas.axes.axis('scaled')
        self.MplWidget1.canvas.axes.set_aspect('equal', 'box')
        self.MplWidget1.canvas.draw()

    def plotData(self, XL, YL, ZL, linecolor, linetype, linewidth, label):
        if label != '':
            # Hiển thị trong tab Gcode
            self.MplWidget1.canvas.axes.plot(
                XL, YL, ZL, linestyle=linetype, linewidth=linewidth, color=linecolor, label=label)
            self.MplWidget1.canvas.axes.legend(loc='upper left')

        else:
            # Hiển thị trong tab Gcode
            self.MplWidget1.canvas.axes.plot(
                XL, YL, ZL, linestyle=linetype, linewidth=linewidth, color=linecolor)

    def plotData1(self, XL, YL, linecolor, linetype, linewidth, label):
        if label != '':
            self.MplWidget1.canvas.axes.plot(
                XL, YL, linestyle=linetype, linewidth=linewidth, color=linecolor, label=label)
            self.MplWidget1.canvas.axes.legend(loc='upper left')
        else:
            self.MplWidget1.canvas.axes.plot(
                XL, YL, linestyle=linetype, linewidth=linewidth, color=linecolor)
    

    def update_plot3d(self, gcode_lines):

        # threading.Thread(target=self.slicer, daemon=True).start()

        logger.info("INFO Rendering the 3D layers")
        self.MplWidget1.canvas.axes.clear()
        self.pathType = 'Gcode'
        
        self.getPlotData(gcode_lines)
        # if self.zLayer != []:
        #      self.ui.Zmin_lbl.setText('1')
        #      self.ui.Zmax_lbl.setText(str(len(self.zLayer) - 1))
        #      self.ui.ZValue_lbl.setText('Lớp 1')
        
        self.ZLayer_sld.setSliderPosition(1)
        # self.ui.ZLayer_sld.setSliderPosition(1)
        
        self.MplWidget1.canvas.axes.set_title (' Mô tả đường in Gcode')
        
        # get text from editline pyqt5
        # xs = float(self.ui.Scale_txt.text())
        # ys = float(self.ui.Scale_txt_2.text())
        # zs = float(self.ui.Scale_txt_3.text())
        
        # self.plot3d_view_signal.emit([xs, ys, zs])
        self.ZLayer_sldF(1)
    

    def getPlotData(self, gcode_lines):
        Lx = []
        Ly = []
        Lz = []
        self.zLayer = []  # Chứa các lớp
        iT = []
        iG = []
        iLayer = []  # Chứa các path trong 1 lớp
        sLayer = []  # Cùng path
        eAngle = 0
        sAngle = 0

        oldLine = gcode_line.gcode_line()
        toolList = []
        newLine = gcode_line.gcode_line()
        oldLine = gcode_line.gcode_line()
        self.color = ['blue', 'red', 'green', 'brown', 'brown']
        self.linetype = ['dashed', 'solid', 'solid', 'solid', 'solid']
        index = 0
        case = 0
        for line in gcode_lines:
            label = ''
            if (line != '') and (";" not in line) and ("'" not in line):
                newLine.code = line
                newLine.R = 0
                newLine.I = 0
                newLine.J = 0
                newLine.getGcodeline(line)
                
                if oldLine.T != newLine.T and oldLine.T != -1:
                    
                    label = ''
                    if not oldLine.T in toolList:
                        toolList.append(oldLine.T)
                        label = 'T0' + str(oldLine.T)
                if (newLine.Z != oldLine.Z or newLine.G != oldLine.G or newLine.T != oldLine.T) and oldLine.T != -1 and oldLine.G<4 and newLine.G<4:
                    if Lx != []:
                        self.plotData(
                            Lx, Ly, Lz, self.color[oldLine.T - 1], self.linetype[oldLine.G], 1.5, label)
                        sLayer.append(Lx)
                        sLayer.append(Ly)
                        sLayer.append(Lz)
                        sLayer.append(iT)
                        sLayer.append(iG)
                        iLayer.append(sLayer)
                        Lx = []
                        Ly = []
                        Lz = []
                        iT = []
                        iG = []
                        sLayer = []
                        Lx.append(oldLine.X)
                        Ly.append(oldLine.Y)
                        Lz.append(oldLine.Z)
                        iT.append(oldLine.T)
                        iG.append(oldLine.G)

                if newLine.Z != oldLine.Z and newLine.Z != 0:
                    
                    self.zLayer.append(iLayer)
                    iLayer = []
                if 'X' in line or 'Y' in line or 'Z' in line:
                   # print(line)
                    if newLine.G == 2 or newLine.G == 3:
                        if newLine.R == 0: #(I-J)
                            pCenter = convert.getCenter(oldLine.X, oldLine.Y, newLine.I, newLine.J)
                            newLine.R = convert.getRadius(oldLine.X, oldLine.Y, pCenter[0], pCenter[1])
                        else:  # Case R                          
                            pCenter = convert.center(oldLine.X, oldLine.Y, newLine.X, newLine.Y, newLine.R, newLine.G)
                            sAngle = round(convert.angle_trunc(convert.getAngle(pCenter[0], pCenter[1], oldLine.X, oldLine.Y)),6)
                            eAngle = round(convert.angle_trunc(convert.getAngle(pCenter[0], pCenter[1], newLine.X, newLine.Y)),6)
                        # print (sAngle)
                        # print(eAngle)
                        if newLine.G ==2:
                            if eAngle>round(pi,6):
                                eAngle = eAngle-2*pi
                            else:
                                if sAngle<round(pi,6):
                                    sAngle = 2*pi + sAngle
                        if newLine.G ==3:
                            if sAngle>round(pi,6):
                                sAngle = sAngle - 2*pi
                            else:
                                if eAngle<round(pi,6):
                                    eAngle = eAngle +2*pi

                        deltaAngle = abs(eAngle - sAngle) # Check full circle
                        if deltaAngle == 0: # Full circle
                            nPoint = floor(abs(2.0 * pi) / 0.1)
                            angles = convert.interpolation(0, 2.0 * pi, nPoint)
                        else:  # Arc
                            # print("-------------")
                            # print (sAngle)
                            # print(eAngle)
                            nPoint = floor(abs(eAngle - sAngle)/0.1)
                            angles = convert.interpolation(sAngle, eAngle, nPoint)    
                           # print(angles)       
                        for a in angles:
                            Lx.append(pCenter[0] + newLine.R*cos(a))
                            Ly.append(pCenter[1] + newLine.R*sin(a))
                            Lz.append(newLine.Z)
                            iT.append(newLine.T)
                            iG.append(newLine.G)
                        Lx.append(newLine.X)
                        Ly.append(newLine.Y)
                        Lz.append(newLine.Z)
                        iT.append(newLine.T)
                        iG.append(newLine.G)
                    else:
                        Lx.append(newLine.X)
                        Ly.append(newLine.Y)
                        Lz.append(newLine.Z)
                        iT.append(newLine.T)
                        iG.append(newLine.G)
                oldLine.set(newLine)
                index += 1
                if index == len(gcode_lines) - 1 or 'M30' in line:
                    
                    if not newLine.T in toolList:
                        # print('LastTool')
                        toolList.append(newLine.T)
                        label = 'T0' + str(newLine.T)
                    try:
                        
                        self.plotData(
                            Lx, Ly, Lz, self.color[oldLine.T - 1], self.linetype[oldLine.G], 1.5, label)
                    except: 
                        pass
                    sLayer.append(Lx)
                    sLayer.append(Ly)
                    sLayer.append(Lz)
                    sLayer.append(iT)
                    sLayer.append(iG)
                    iLayer.append(sLayer)
                    self.zLayer.append(iLayer)
        