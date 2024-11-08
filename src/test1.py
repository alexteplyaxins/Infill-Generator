import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk

class VtkViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print(parent)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.vtkWidget)
        
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.frame = QFrame()
        self.setCentralWidget(self.frame)
        
        self.viewer = VtkViewer(self.frame)
        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.viewer)
        self.frame.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
