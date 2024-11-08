
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class NoInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        pass

    def OnLeftButtonDown(self):
        pass

    def OnRightButtonDown(self):
        pass

    def OnMiddleButtonDown(self):
        pass

    def OnMouseWheelForward(self):
        pass

    def OnMouseWheelBackward(self):
        pass


class Vtk2DView(QWidget):
    def __init__(self, frame, slider, step):
        super().__init__()
        self.frame = frame
        self.slider = slider
        self.step = step

        self._setup_vtk()
        self._ren.GetActiveCamera().Dolly(0.8)
        self._ren.ResetCameraClippingRange()
        self.boundaryActor = None
        self.actor = None
        # # Adjusting slider maximum value based on Z-extent
        # self.slider.setMaximum(int(self.z_max * 100))  # Scaling to avoid float precision issues

    def init(self, stl_file_path):
        self._load_model(object_file_path=stl_file_path)
        self.setup_slice_plane()
        self.create_clipper()

    def closeEvent(self, event):
        # super().closeEvent(event)
        self._vtkWidget.Finalize()
        self._vtkWidget.GetRenderWindow().Finalize()

    def _setup_vtk(self, scale=200):
        # VTK setting
        self._ren = vtk.vtkRenderer()
        self._vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self._vtkWidget.GetRenderWindow().AddRenderer(self._ren)
        colors = vtk.vtkNamedColors()
        self._ren.SetBackground(colors.GetColor3d("DarkGray"))
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.addWidget(self._vtkWidget)

        self.set_diagonal_view()

        self._vtkWidget.SetInteractorStyle(NoInteractorStyle())

    def set_diagonal_view(self, scale=200):
        camera = self._ren.GetActiveCamera()
        camera.SetPosition(scale, scale, 0.5 * scale)  # Position the camera at an offset in X, Y, and Z
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a central point in your scene)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the Y-axis

        self._ren.ResetCamera()  # Adjust the view to fit the scene
        self._vtkWidget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def _load_model(self, object_file_path):
        # Loading STL
        object_extension = object_file_path.split('.')[-1].lower()
        if object_extension == 'stl':
            self.reader = vtk.vtkSTLReader()
        elif object_extension == 'obj':
            self.reader = vtk.vtkOBJReader()
        else:
            print('ERROR, Not support {0} file'.format(object_file_path))
        self.reader.SetFileName(object_file_path)
        self.reader.Update()

    def setup_slice_plane(self):
        bounds = self.reader.GetOutput().GetBounds()
        self.z_min = bounds[4]
        self.z_max = bounds[5]
        # Slicing Plane Slider
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self._update_plane)

    def create_clipper(self):
        # Create Clipper
        self.clipPlane = vtk.vtkPlane()
        z_position = self.slider.value() / 100.0 * (self.z_max - self.z_min)  # Assuming Z in range 0-1 for simplicity
        self.clipPlane.SetOrigin(0, 0, z_position)
        self.clipPlane.SetNormal(0, 0, 1)

        # Create a vtkClipPolyData filter to clip the mesh
        self.clipper = vtk.vtkClipPolyData()
        self.clipper.SetInputConnection(self.reader.GetOutputPort())
        self.clipper.SetClipFunction(self.clipPlane)
        # This ensures that only the part below the clipping plane is retained
        self.clipper.SetInsideOut(1)
        self.clipper.Update()

        # Update the mapper to use the clipped output
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.clipper.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.2, 0.5, 0.8)

        self._ren.AddActor(self.actor)
        # Cutter for boundary highlight
        self.cutter = vtk.vtkCutter()
        self.cutter.SetCutFunction(self.clipPlane)
        self.cutter.SetInputConnection(self.reader.GetOutputPort())
        self.cutter.Update()

        # Mapper for the boundary
        boundaryMapper = vtk.vtkPolyDataMapper()
        boundaryMapper.SetInputConnection(self.cutter.GetOutputPort())

        # Actor for the boundary with a distinct color, e.g., red
        self.boundaryActor = vtk.vtkActor()
        self.boundaryActor.SetMapper(boundaryMapper)
        self.boundaryActor.GetProperty().SetColor(1.0, 1.0, 0.0)  # Yellow
        self._ren.AddActor(self.boundaryActor)
        self._ren.ResetCamera()

    def show(self):
        self._vtkWidget.Initialize()
        self._vtkWidget.Start()

    def _update_plane(self):
        z_position = self.slider.value() / 100.0 * (self.z_max - self.z_min) # Assuming Z in range 0-1 for simplicity
        # Reverse the Z position of the clipping plane
        # z_position = self.z_max - (self.slider.value() / 100.0 * (self.z_max - self.z_min))
        self.clipPlane.SetOrigin(0, 0, z_position)
        self.clipPlane.SetNormal(0, 0, 1)
        self._vtkWidget.GetRenderWindow().Render()
        self.cutter.Update()
        # self._vtkWidget.GetRenderWindow().Render()

        # Extract boundary coordinates
        boundary_points = self.cutter.GetOutput().GetPoints()
        num_points = boundary_points.GetNumberOfPoints()
        boundary_coords = []
        for i in range(num_points):
            boundary_coords.append(boundary_points.GetPoint(i))
        # print(boundary_coords)

        self._vtkWidget.GetRenderWindow().Render()

        return boundary_coords  # Return the boundary coordinates

    def clear_view(self):
        self._ren.RemoveAllViewProps()
        self._ren.ResetCamera()
        # Update the renderer to reflect the changes
        self._vtkWidget.GetRenderWindow().Render()
        # Assuming `stlActor` is the actor related to your STL model:
        if self.boundaryActor is not None:
            self._ren.RemoveActor(self.boundaryActor)
        if self.actor is not None:
            self._ren.RemoveActor(self.actor)






