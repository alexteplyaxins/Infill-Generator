import os
import vtk
import argparse
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
# from PyQt5.QtWidgets import QVBoxLayout, QWidget
# from PyQt5.QtGui import QCloseEvent
from PySide6.QtCore import QRect

from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QCloseEvent

import random

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("MiddleButtonPressEvent", self.middle_button_press_event)
        self.AddObserver("MiddleButtonReleaseEvent", self.middle_button_release_event)
        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)

    def middle_button_press_event(self, obj, event):
        self.StartPan()
        return

    def middle_button_release_event(self, obj, event):
        self.EndPan()
        return

    def right_button_press_event(self, obj, event):
        self.StartPan()
        return

    def right_button_release_event(self, obj, event):
        self.EndPan()
        return

    def OnLeftButtonDown(self):
        self.Rotate()

    def OnMiddleButtonDown(self):
        self.Pan()


class VtkViewer(QWidget):
    def __init__(self, widget=None):
        super().__init__(widget) #####
        self.create_vtk_widget(widget)
        # Reset camera
        self.renderer.GetActiveCamera().Dolly(0.8)
        self.renderer.ResetCameraClippingRange()

    def closeEvent(self, event):
        # super().closeEvent(event)
        self.vtk_widget.Finalize()
        self.vtk_widget.GetRenderWindow().Finalize()
        
    def show(self):
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

    def create_vtk_widget(self, frame):
        colors = vtk.vtkNamedColors()
        self.actorSTL = []
        self.baseActor = vtk.vtkActor()
        self.Rotating = 0
        self.Panning = 0
        self.Zooming = 0
        self.vtk_widget = QVTKRenderWindowInteractor(frame)
        # Add the custom mouse manipulation action as Solidwork
        self.vtk_widget.SetInteractorStyle(CustomInteractorStyle())
        
        frame_layout = QVBoxLayout(self)
        # frame_layout = QWidget(self)
        
        frame_layout.addWidget(self.vtk_widget)
        
        # Set up VTK renderer and objects
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        # Add workspace with green background
        self.renderer.SetBackground(colors.GetColor3d("LightBlue"))
        self.setGeometry(QRect(20, 35, 670, 401))
        # draw axes
        self.add_axes_actor()

        # default view port
        self.set_default_view()
        self.add_workspace_plane()

    def add_axes_actor(self):
        axes = vtk.vtkAxesActor()
        self.orientation_widget = vtk.vtkOrientationMarkerWidget()
        self.orientation_widget.SetOrientationMarker(axes)
        self.orientation_widget.SetInteractor(self.vtk_widget.GetRenderWindow().GetInteractor())
        # self.orientation_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
        self.orientation_widget.SetEnabled(1)
        self.orientation_widget.InteractiveOn()

    def set_default_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(scale, scale, 0.5 * scale)  # Position the camera at an offset in X, Y, and Z
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a central point in your scene)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the Y-axis

        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_front_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(scale, 0, 0)  # Position the camera along the negative Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the positive Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_back_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(-scale, 0, 0)  # Position the camera along the negative Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the positive Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_left_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, -scale, 0)  # Position the camera along the negative Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the positive Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_right_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, scale, 0)  # Position the camera along the negative Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the positive Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_bottom_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, -scale)  # Position the camera along the negative Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, scale, 0)  # Set the up direction to be the positive Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_top_view(self, scale=200):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, scale)  # Position the camera along the positive Z-axis
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a point on the XY plane)
        camera.SetViewUp(0, -scale, 0)  # Set the up direction to be the negative Y-axis
        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def set_diagonal_view(self, scale=100):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(scale, scale, 0.5 * scale)  # Position the camera at an offset in X, Y, and Z
        camera.SetFocalPoint(0, 0, 0)  # Look at the origin (or a central point in your scene)
        camera.SetViewUp(0, 0, scale)  # Set the up direction to be the Y-axis

        self.renderer.ResetCamera()  # Adjust the view to fit the scene
        self.vtk_widget.GetRenderWindow().Render()  # Render the scene with the new camera view

    def add_workspace_plane(self, width=200, height=200, grid_size=10):
        # Create a rectangular plane based on the given width and height
        half_width = width / 2.0
        half_height = height / 2.0
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(-half_width, -half_height, 0)
        plane.SetPoint1(half_width, -half_height, 0)
        plane.SetPoint2(-half_width, half_height, 0)
        plane.SetResolution(100, 100)  # This will create a grid pattern on the plane
        # Set the grid resolution based on the grid size
        plane.SetResolution(int(width / grid_size), int(height / grid_size))

        # Map the plane to a grid
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetEdgeColor(0.1, 0.1, 0.1)  # Set grid color
        actor.GetProperty().EdgeVisibilityOn()  # Show grid

        # Add the plane to the renderer
        self.renderer.AddActor(actor)
        # Add the plane to the renderer
        self.renderer.AddActor(actor)

    def clear_view(self):
        self.renderer.RemoveAllViewProps()
        # Update the renderer to reflect the changes
        self.vtk_widget.GetRenderWindow().Render()

        # Recreate workspace
        self.add_workspace_plane()
        self.set_diagonal_view()

    def load_3d_object(self, object_file_path):
        if not object_file_path:
            return False
        # Load the STL file
        if not os.path.isfile(object_file_path):
            return False
        obj_extension = object_file_path.split('.')[-1].lower()
        # check input object extension is obj or stl
        if obj_extension != 'obj' and obj_extension != 'stl':
            return False
        if obj_extension == 'obj':
            reader = vtk.vtkOBJReader()
        elif obj_extension == 'stl':
            reader = vtk.vtkSTLReader()
        else:
            return False
        reader.SetFileName(object_file_path)

        # Compute the center of the STL geometry's bounding box
        bounds = reader.GetOutput().GetBounds()
        center = [(bounds[1] + bounds[0]) / 2.0, (bounds[3] + bounds[2]) / 2.0, (bounds[5] + bounds[4]) / 2.0]

        transform = vtk.vtkTransform()
        transform.Translate(-center[0], -center[1], -center[2])  # Translate in X and Y to the origin, and set Z to 0.
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(reader.GetOutputPort())
        transformFilter.SetTransform(transform)

        # Map the STL to an actor and add to the renderer
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transformFilter.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Generate a random color
        r = random.uniform(0.5, 1)
        g = random.uniform(0.5, 1)
        b = random.uniform(0.5, 1)
        actor.GetProperty().SetColor(r, g, b)
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        print("Complete")
        return True
