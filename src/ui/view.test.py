import unittest
from unittest.mock import MagicMock
from ui.view import Window
from model.model import Model
import model.slicer as Slicer

class TestWindow(unittest.TestCase):

    def setUp(self):
        self.model = MagicMock(spec=Model)
        self.window = Window(self.model)

if __name__ == '__main__':
    unittest.main()
def test_init_slicer(self):
    # Mock the necessary attributes and methods
    self.model3d = MagicMock()
    self.logger = MagicMock()
    self.sliceProgBar = MagicMock()
    self.allow_perimeter = MagicMock()

    # Call the method
    self.window.init_slicer()

    # Assert that Slicer was called with the correct arguments
    Slicer.assert_called_once_with(
        [self.window.model3d],
        logger=self.window.logger,
        prog_bar=self.window.sliceProgBar,
        enable_perims=self.window.allow_perimeter
    )

    # Assert that self.slicer was set to the result of Slicer()
    self.assertIsNotNone(self.window.slicer)
    self.assertEqual(self.window.slicer, Slicer.return_value)