# -*- coding: utf-8 -*-
'''
    Simple PySide6 based test for Unreal Editor

    See entry point at the bottom of file for a brief note on what works,
    and what does not.
'''

import os
import sys
import unreal

# Insert ourselves to sys.path
thisDir = os.path.dirname(__file__)
libDir = os.path.join(thisDir, 'lib')
for path in [thisDir, libDir]:
    if not path in sys.path:
        sys.path.insert(0, path)

# (Hopefully) grab relevant PySide modules and demo UI
from PySide6 import QtGui, QtCore, QtWidgets
import demoWindow_ui as window


class DemoWindow(QtWidgets.QMainWindow):
    '''Demo window'''

    def __init__(self, parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        self.ui = window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.tickHandle = None
        self.pyShutdownHandle = None
        self.ticks = []

    def _registerTickCallback(self):
        '''Register tick callback with Unreal'''

        if not self.tickHandle:
            print('Registering Unreal tick callback')
            self.tickHandle = unreal.register_slate_post_tick_callback(self.eventTick)
            print('Registering Unreal Python shutdown callback')
            self.pyShutdownHandle = unreal.register_python_shutdown_callback(self._pythonShutdownCallback)

    def _unregisterTickCallback(self):
        '''Unregister tick callback with Unreal'''

        if self.tickHandle:
            print('Unregistering Unreal tick callback')
            unreal.unregister_slate_post_tick_callback(self.tickHandle)
            self.tickHandle = None

    def _pythonShutdownCallback(self):
        '''Python is shutting down'''

        if self.pyShutdownHandle:
            print('Unregistering Unreal Python shutdown callback')
            unreal.unregister_python_shutdown_callback(self.pyShutdownHandle)
            self.pyShutdownHandle = None

        print('Closing window and triggering delete')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # in actual implementation, this is not always True
        self.close() # triggers `self._unregisterTickCallback`

    def eventTick(self, delta: float):
        '''Event tick from Unreal has been received'''

        self.ticks.insert(0, delta)
        if len(self.ticks) > 20:
            self.ticks = self.ticks[:20]

        self.ui.ticks.setPlainText('\n'.join([f'{x}' for x in self.ticks]))

    def closeEvent(self, event: QtGui.QCloseEvent):
        '''Dialog is closing'''

        print('Window close event')
        self._unregisterTickCallback()
        event.accept()

    def showEvent(self, event: QtGui.QShowEvent):
        '''Dialog is opening'''

        print('Window show event')
        self._registerTickCallback()
        event.accept()


# Doesn't seem to matter if these are global or not
# Update: Yes it does seem to matter, see `showWindow` below with `global` call
UNREAL_APP = None
WINDOW = None


# The point of this entry method is because in actual implementation,
# these windows are imported modules -- not standalone scripts to be executed
def showWindow():

    # This seems to take care of it. So perhaps it was GC related after all
    global UNREAL_APP, WINDOW

    UNREAL_APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    WINDOW = DemoWindow()
    WINDOW.show()
    unreal.parent_external_window_to_slate(WINDOW.winId())



if __name__ == '__main__':

    # This causes a crash:
    # Update: with `global` call, crashes no longer
    showWindow()

    # This works as expected:
    # UNREAL_APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    # WINDOW = DemoWindow()
    # WINDOW.show()
    # unreal.parent_external_window_to_slate(WINDOW.winId())