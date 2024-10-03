import sys
import ctypes
from PyQt5 import QtWidgets, QtCore, QtGui

# Constants for the Win32 API
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_LAYERED = 0x00080000

class OverlayWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                           QtCore.Qt.WindowStaysOnTopHint | 
                           QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)

        self.setGeometry(100, 100, 800, 600)
        self.transparency = 1.0  # Full opacity (1.0)

        # Create a slider for transparency adjustment
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setRange(0, 100)  # Range from 0% to 100%
        self.slider.setValue(100)  # Default value (fully opaque)
        self.slider.setGeometry(50, 20, 700, 30)
        self.slider.valueChanged.connect(self.adjust_transparency)

        # Create a label for instructions
        self.label = QtWidgets.QLabel("Adjust Transparency", self)
        self.label.setGeometry(50, 0, 200, 20)

        # Create a QTextEdit for notes
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setGeometry(50, 60, 700, 500)  # Adjust geometry as needed

        # Create a close button
        self.close_button = QtWidgets.QPushButton("×", self)
        self.close_button.setGeometry(self.width() - 30, 0, 30, 30)
        self.close_button.clicked.connect(self.close)

        # Create a save button
        self.save_button = QtWidgets.QPushButton("Save", self)
        self.save_button.setGeometry(self.width() - 100, self.height() - 40, 80, 30)
        self.save_button.clicked.connect(self.save_note)

        # Set a background color for the overlay
        self.update_overlay_style()  # Set initial style for the overlay

        # Track mouse position for resizing
        self.mouse_pressed = False
        self.mouse_start_position = None
        self.resize_active = False
        self.resize_direction = None

        # Set mouse tracking
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw the main background
        bg_color = QtGui.QColor(50, 50, 50, int(self.transparency * 255))
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())

        # Draw futuristic corners
        corner_color = QtGui.QColor(0, 255, 255, int(self.transparency * 255))  # Cyan color for corners
        painter.setBrush(corner_color)
        corner_size = 20

        # Top-left corner
        painter.drawPolygon(QtGui.QPolygon([
            QtCore.QPoint(0, 0),
            QtCore.QPoint(corner_size, 0),
            QtCore.QPoint(0, corner_size)
        ]))

        # Top-right corner
        painter.drawPolygon(QtGui.QPolygon([
            QtCore.QPoint(self.width(), 0),
            QtCore.QPoint(self.width() - corner_size, 0),
            QtCore.QPoint(self.width(), corner_size)
        ]))

        # Bottom-left corner
        painter.drawPolygon(QtGui.QPolygon([
            QtCore.QPoint(0, self.height()),
            QtCore.QPoint(corner_size, self.height()),
            QtCore.QPoint(0, self.height() - corner_size)
        ]))

        # Bottom-right corner
        painter.drawPolygon(QtGui.QPolygon([
            QtCore.QPoint(self.width(), self.height()),
            QtCore.QPoint(self.width() - corner_size, self.height()),
            QtCore.QPoint(self.width(), self.height() - corner_size)
        ]))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Determine the direction to resize
            if event.pos().x() < 20 and event.pos().y() < 20:  # Top-left corner
                self.resize_active = True
                self.resize_direction = "top-left"
            elif event.pos().x() < 20 and event.pos().y() > self.height() - 20:  # Bottom-left corner
                self.resize_active = True
                self.resize_direction = "bottom-left"
            elif event.pos().x() > self.width() - 20 and event.pos().y() < 20:  # Top-right corner
                self.resize_active = True
                self.resize_direction = "top-right"
            elif event.pos().x() > self.width() - 20 and event.pos().y() > self.height() - 20:  # Bottom-right corner
                self.resize_active = True
                self.resize_direction = "bottom-right"
            else:  # Move the widget
                self.mouse_pressed = True
                self.mouse_start_position = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.resize_active:
            if self.resize_direction == "top-left":
                diff = event.globalPos() - self.pos()
                new_width = max(self.minimumWidth(), self.width() - diff.x())
                new_height = max(self.minimumHeight(), self.height() - diff.y())
                self.setGeometry(self.x() + diff.x(), self.y() + diff.y(), new_width, new_height)
            elif self.resize_direction == "bottom-left":
                diff = event.globalPos() - self.pos()
                new_width = max(self.minimumWidth(), self.width() - diff.x())
                new_height = max(self.minimumHeight(), event.globalPos().y() - self.y())
                self.setGeometry(self.x() + diff.x(), self.y(), new_width, new_height)
            elif self.resize_direction == "top-right":
                diff = event.globalPos() - self.pos()
                new_width = max(self.minimumWidth(), event.globalPos().x() - self.x())
                new_height = max(self.minimumHeight(), self.height() - diff.y())
                self.setGeometry(self.x(), self.y() + diff.y(), new_width, new_height)
            elif self.resize_direction == "bottom-right":
                new_width = max(self.minimumWidth(), event.globalPos().x() - self.x())
                new_height = max(self.minimumHeight(), event.globalPos().y() - self.y())
                self.resize(new_width, new_height)
            self.update_widget_layout()
        elif self.mouse_pressed:
            # Move the widget
            self.move(event.globalPos() - self.mouse_start_position)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = False
            self.resize_active = False
            self.resize_direction = None

    def adjust_transparency(self, value):
        self.transparency = value / 100.0  # Scale from 0 to 1
        self.update_overlay_style()  # Update overlay style
        self.update()  # Trigger a repaint

    def update_overlay_style(self):
        bg_color = QtGui.QColor(50, 50, 50, int(self.transparency * 255))
        text_color = self.get_contrasting_color(bg_color)
        
        self.setStyleSheet(f"background-color: rgba(50, 50, 50, {self.transparency});")
        self.label.setStyleSheet(f"color: {text_color.name()};")
        self.text_edit.setStyleSheet(f"""
            background-color: rgba(50, 50, 50, {self.transparency});
            color: {text_color.name()};
            border: none;
        """)
        self.close_button.setStyleSheet(f"""
            background-color: rgba(255, 0, 0, {self.transparency});
            color: {text_color.name()};
            border: none;
            font-size: 20px;
        """)
        self.save_button.setStyleSheet(f"""
            background-color: rgba(0, 128, 0, {self.transparency});
            color: {text_color.name()};
            border: none;
        """)

    def get_contrasting_color(self, bg_color):
        # Calculate the perceived brightness of the background color
        brightness = (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000
        
        # Choose white or black text based on the background brightness
        if brightness > 128:
            return QtGui.QColor(0, 0, 0)  # Black text for light backgrounds
        else:
            return QtGui.QColor(255, 255, 255)  # White text for dark backgrounds

    def updateLayeredWindowAttributes(self):
        hwnd = ctypes.windll.user32.FindWindowW(None, self.windowTitle())
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(self.transparency * 255), 0x2)

    def update_widget_layout(self):
        # Update the layout of widgets when the window is resized
        self.slider.setGeometry(50, 20, self.width() - 100, 30)
        self.text_edit.setGeometry(50, 60, self.width() - 100, self.height() - 110)
        self.close_button.setGeometry(self.width() - 30, 0, 30, 30)
        self.save_button.setGeometry(self.width() - 100, self.height() - 40, 80, 30)

    def resizeEvent(self, event):
        # This method is called whenever the widget is resized
        super().resizeEvent(event)
        self.update_widget_layout()

    def save_note(self):
        # Open a file dialog to choose where to save the note
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Note", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
            QtWidgets.QMessageBox.information(self, "Note Saved", f"Your note has been saved to {file_name}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    overlay = OverlayWidget()
    overlay.setWindowTitle("Eye Protection Overlay")
    overlay.show()
    sys.exit(app.exec_())