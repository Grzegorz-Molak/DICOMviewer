import os

from PySide6.QtWidgets import QMainWindow, QFileDialog
from GUI.menu import MenuViewer
from GUI.viewer import Viewer
from DICOM.readfolder import *
import matplotlib
matplotlib.use('Qt5Agg')


class DicomViewer(QMainWindow):
    """
    Class represents whole runnable application with GUI.

    Application allows user to choose dicom's file(s) or folder and load them. Loaded images can be chosen and displayed.
    Sliders allow user to set windowing: Window Level and Window Width.Third slider provides sliding through photos
    functionality. Down's left region displays current x, y and HU value if cursor is over image. Pressing a mouse
    button and dragging draws region of interest on image. Basic statistics of ROI is being displayed: area, mean and
    standard deviation.

    Attributes
    ----------
    app : QApplication
        application running this GUI
    menu_bar : MenuViewer
        menu, allows user to open file(s) or folder
    main_window : Viewer
        contains all content: displays image and sessions panel
    sessions : dict
         stores loaded dicom files. The files are sorted with session and series.

    Methods
    -------
    slider_released()
        Updates image windowing
    file_chosen()
        Allows user to choose file(s) to read
    folder_chosen()
        Allows user to choose folder to read
    sessions_change()
        Updates sessions options
    series_change()
        Updates series options
    dicoms_change()
        Updates images list
    image_change()
        Updates displayed image
    slider_image_changed()
        Updated displayed image after slider is being used


    """
    def __init__(self, app):
        """
        Creates attributes, connects signals with appropriate slots.

        The connected signals are folder signals, sessions, series and images signals and sliders signals.

        Parameter
        ---------
        app : QApplication
            The application that runs this GUI
        """
        super().__init__()
        self.app = app
        self.menu_bar = MenuViewer()
        self.setMenuBar(self.menu_bar)
        self.main_window = Viewer()
        self.sessions = dict()

        self.menu_bar.open_folder.triggered.connect(self.folder_chosen)
        self.menu_bar.open_file.triggered.connect(self.file_chosen)
        self.main_window.sessionsLayout.sessions.activated.connect(self.series_change)
        self.main_window.sessionsLayout.series.activated.connect(self.dicoms_change)
        self.main_window.sessionsLayout.dicoms.currentRowChanged.connect(self.image_change)
        self.main_window.slider_level.valueChanged.connect(self.slider_released)
        self.main_window.slider_window.valueChanged.connect(self.slider_released)
        self.main_window.slider_image.valueChanged.connect(self.slider_image_changed)

        self.setCentralWidget(self.main_window)

    def slider_released(self):
        """
        Changes image windowing depending on slider values
        """
        self.main_window.window_image(self.main_window.slider_level.value(), self.main_window.slider_window.value())
        self.main_window.slider_level_label.setText(str(self.main_window.slider_level.value()))
        self.main_window.slider_window_label.setText(str(self.main_window.slider_window.value()))
        self.main_window.showImageWindowed()

    def file_chosen(self):
        """
        Allows user to choose file(s), reads and displays in session panel
        """
        dirname = os.path.dirname(os.path.dirname(__file__))
        file_names, _ = QFileDialog.getOpenFileNames(self, "Open File", dirname, "Images (*.dcm)")
        if not file_names:
            return
        self.sessions = clusterDicoms(readDicomFiles(file_names))
        # self.main_window.setImage(file_names[0])
        self.main_window.slider_level.show()
        self.main_window.slider_window.show()
        self.main_window.slider_level_label_min.setText("-1000")
        self.main_window.slider_level_label_max.setText("8190")
        self.main_window.slider_window_label_min.setText("0")
        self.main_window.slider_window_label_max.setText("8190")
        self.sessions_change()

    def folder_chosen(self):
        """
        Allows user to choose folder, reads it recursively and displays in session panel.
        """
        dirname = os.path.dirname(os.path.dirname(__file__))
        dir = QFileDialog.getExistingDirectory(self, "Open Directory", dirname)
        if dir == "":
            return
        self.sessions = clusterDicoms(readFolder(dir + "/**/*.dcm"))
        self.main_window.slider_level.show()
        self.main_window.slider_window.show()
        self.main_window.slider_level_label_min.setText("-1000")
        self.main_window.slider_level_label_max.setText("8190")
        self.main_window.slider_window_label_min.setText("0")
        self.main_window.slider_window_label_max.setText("8190")
        self.sessions_change()

    def sessions_change(self):
        """
        Updates sessions checkbox options after new images are loaded.
        """
        self.main_window.sessionsLayout.set_sessions(list(self.sessions.keys()))

        self.series_change(0)

    def series_change(self, index):
        """
        Updates series checkbox after session is changed.

        Parameter
        ---------
        index : int
            Index of chosen session
        """
        if not self.sessions.keys():
            return
        name = list(self.sessions.keys())[index]
        self.main_window.sessionsLayout.set_series((self.sessions[name].keys()))
        self.dicoms_change(0)

    def dicoms_change(self, index):
        """
        Updates images list after series is changed.

        Parameter
        ---------
        index : int
            Index of chosen series
        """
        self.main_window.delete_rect(None)
        if not self.sessions.keys():
            return
        sessionIndex = self.main_window.sessionsLayout.sessions.currentIndex()
        session = list(self.sessions.keys())[sessionIndex]
        seriesName = list(self.sessions[session].keys())[index]
        series = self.sessions[session][seriesName]
        self.main_window.sessionsLayout.set_dicoms([serie.filename.split("\\")[-1] for serie in series])
        self.main_window.slider_image.setRange(1, len(series))
        self.main_window.setImage(series[0])
        self.slider_released()

    def image_change(self):
        """
        Updates displayed image to user's choice.
        """
        num = self.main_window.sessionsLayout.dicoms.currentRow()
        sessionIndex = self.main_window.sessionsLayout.sessions.currentIndex()
        seriesIndex = self.main_window.sessionsLayout.series.currentIndex()
        session = list(self.sessions.keys())[sessionIndex]
        seriesName = list(self.sessions[session].keys())[seriesIndex]
        series = self.sessions[session][seriesName]
        self.main_window.setImage(series[num])
        self.slider_released()

    def slider_image_changed(self, value):
        """
        Updates displayed image after slider is used
        Parameter
        ---------
        value : index of chosen image
        """
        self.main_window.sessionsLayout.dicoms.setCurrentRow(value)


