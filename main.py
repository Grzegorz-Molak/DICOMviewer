from PySide6.QtWidgets import QApplication
from dicomviewer import DicomViewer
import sys

"""
Runs DicomViewer application and shows it on the screen
"""
app = QApplication(sys.argv)
window = DicomViewer(app)
window.show()
app.exec()
