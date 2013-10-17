#!/usr/bin/python3

import sys

sys.dont_write_bytecode = True

import os

import subprocess

import re

import gphoto2

from PyQt4 import QtCore, QtGui

from imageviewer import ImageViewer

class Thread(QtCore.QThread):
  def __init__(self, func, *args, **kwargs):
    super(Thread, self).__init__()
    self.func, self.args, self.kwargs = func, args, kwargs
    self.start()

  def run(self):
    self.func(*self.args, **self.kwargs)

class BookScanner(QtGui.QMainWindow):
  @staticmethod
  def _exec(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

  def __init__(self):
    super(BookScanner, self).__init__()

    self.working_directory = os.path.dirname(os.path.realpath(__file__))

    self.left_camera_is_free = True
    self.right_camera_is_free = True

    self.current_directory = None

    self.setWindowTitle('BookScanner')
    self.setWindowIcon(QtGui.QIcon('{0}/icon.png'.format(self.working_directory)))

    self.setMinimumSize(1190, 710)

    fg = self.frameGeometry()
    fg.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
    self.move(fg.topLeft())

    self.background = QtGui.QLabel(self)
    self.background.setGeometry(0, 0, 4000, 2000)
    self.background.setStyleSheet('background-image: url({0}/background.png)'.format(self.working_directory))

    self.logo = QtGui.QLabel(self)
    self.logo.setGeometry(30, 30, 170, 100)
    self.logo.setStyleSheet('background-image: url({0}/logo.png)'.format(self.working_directory))

    self.directory_btn = QtGui.QPushButton('Select directory', self)
    self.directory_btn.setGeometry(230, 30, 200, 30)
    self.directory_btn.clicked.connect(self.select_directory)

    self.directory_lbl = QtGui.QLabel(self)
    self.directory_lbl.setGeometry(460, 30, 400, 30)

    self.automatic_numeration_box = QtGui.QCheckBox(self)
    self.automatic_numeration_box.setGeometry(890, 30, 30, 30)

    self.automatic_numeration_lbl = QtGui.QLabel('Automatic numbering', self)
    self.automatic_numeration_lbl.setGeometry(920, 30, 200, 30)

    self.filename_left_lbl = QtGui.QLabel('Filename for left camera:', self)
    self.filename_left_lbl.setGeometry(230, 90, 220, 30)

    self.filename_left_field = QtGui.QLineEdit(self)
    self.filename_left_field.setGeometry(450, 90, 220, 30)

    self.filename_right_lbl = QtGui.QLabel('Filename for right camera:', self)
    self.filename_right_lbl.setGeometry(700, 90, 220, 30)

    self.filename_right_field = QtGui.QLineEdit(self)
    self.filename_right_field.setGeometry(920, 90, 220, 30)

    self.image_left = ImageViewer(self)
    self.image_left.setGeometry(30, 160, 550, 460)

    self.image_right = ImageViewer(self)
    self.image_right.setGeometry(610, 160, 550, 460)

    self.shoot_btn = QtGui.QPushButton('Make photos', self)
    self.shoot_btn.setGeometry(30, 650, 200, 30)
    self.shoot_btn.clicked.connect(self.shoot)

    QtGui.QShortcut(QtGui.QKeySequence('Space'), self, self.shoot)

    self.shoot_left_btn = QtGui.QPushButton('Make left photo', self)
    self.shoot_left_btn.setGeometry(260, 650, 200, 30)
    self.shoot_left_btn.clicked.connect(self.shoot_left)

    self.shoot_right_btn = QtGui.QPushButton('Make right photo', self)
    self.shoot_right_btn.setGeometry(490, 650, 200, 30)
    self.shoot_right_btn.clicked.connect(self.shoot_right)

  def select_directory(self):
    self.current_directory = QtGui.QFileDialog.getExistingDirectory(self, 'Select directory')
    self.directory_lbl.setText('Current directory: ' + self.current_directory)

  def shoot(self):
    if self.validate_cameras(2) and self.validate_directory():
      self.shoot_left()
      self.shoot_right()

  def shoot_left(self):
    if self.validate_cameras(1) and self.validate_directory() and self.validate_filename_left():
      self.left_camera_is_free = False
      self.update_controls_states()

      self.thread_left = Thread(self.load_left)
      self.thread_left.finished.connect(self.render_left)

  def shoot_right(self):
    if self.validate_cameras(2) and self.validate_directory() and self.validate_filename_right():
      self.right_camera_is_free = False
      self.update_controls_states()

      self.thread_right = Thread(self.load_right)
      self.thread_right.finished.connect(self.render_right)

  def validate_cameras(self, n):
    if len(gphoto2.devices()) < n:
      QtGui.QMessageBox.warning(self, 'Warning', 'The number of connected cameras should be at least {0}.'.format(n))
      return False

    return True

  def validate_directory(self):
    if not self.current_directory:
      QtGui.QMessageBox.warning(self, 'Warning', 'Current directory is not set.')
      return False

    return True

  def validate_filename_left(self):
    if not self.filename_left_field.text():
      QtGui.QMessageBox.warning(self, 'Warning', 'Filename for left camera is not set.')
      return False

    if os.path.isfile(self.path_left('jpg')):
      reply = QtGui.QMessageBox.question(self, 'Question', 'File with filename for left camera already exists. Rewrite?',
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
      if reply != QtGui.QMessageBox.Yes: return False

    return True

  def validate_filename_right(self):
    if not self.filename_right_field.text():
      QtGui.QMessageBox.warning(self, 'Warning', 'Filename for right camera is not set.')
      return False

    if os.path.isfile(self.path_right('jpg')):
      reply = QtGui.QMessageBox.question(self, 'Question', 'File with filename for right camera already exists. Rewrite?',
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
      if reply != QtGui.QMessageBox.Yes: return False

    return True

  def update_controls_states(self):
    self.shoot_btn.setEnabled(self.left_camera_is_free and self.right_camera_is_free)

    self.filename_left_field.setEnabled(self.left_camera_is_free)
    self.shoot_left_btn.setEnabled(self.left_camera_is_free)

    self.filename_right_field.setEnabled(self.right_camera_is_free)
    self.shoot_right_btn.setEnabled(self.right_camera_is_free)

  def load_left(self):
    gphoto2.devices()[0].capture(self.path_left('%C'))
    self._exec('convert "{0}" -rotate 270 "{0}"'.format(self.path_left('jpg')))

  def render_left(self):
    self.left_camera_is_free = True
    self.update_controls_states()

    self.image_left.configure(self.path_left('jpg'), 0.25)

    if self.automatic_numeration_box.isChecked():
      self.filename_left_field.setText(self.next_filename(self.filename_left_field.text()))

  def load_right(self):
    gphoto2.devices()[1].capture(self.path_right('%C'))
    self._exec('convert "{0}" -rotate 90 "{0}"'.format(self.path_right('jpg')))

  def render_right(self):
    self.right_camera_is_free = True
    self.update_controls_states()

    self.image_right.configure(self.path_right('jpg'), 0.25)

    if self.automatic_numeration_box.isChecked():
      self.filename_right_field.setText(self.next_filename(self.filename_right_field.text()))

  def path_left(self, format):
    return '{0}/{1}.{2}'.format(self.current_directory, self.filename_left_field.text(), format)

  def path_right(self, format):
    return '{0}/{1}.{2}'.format(self.current_directory, self.filename_right_field.text(), format)

  def next_filename(self, filename):
    match = re.search('^\d+', filename)

    if match:
      return str(int(match.group(0)) + 2).rjust(len(match.group(0)), '0')
    else:
      return filename

if __name__ == '__main__':
  app = QtGui.QApplication(sys.argv)
  win = BookScanner()
  win.show()
  sys.exit(app.exec_())

