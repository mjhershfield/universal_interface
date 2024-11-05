import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


app = QApplication([])

window = QWidget()
window.setWindowTitle("Lycan Universal Interface")
window.setGeometry(200, 200, WINDOW_WIDTH, WINDOW_HEIGHT)
helloMsg = QLabel("<h1>Welcome!</h1>", parent=window)
helloMsg.move(60, 40)

window.show()
sys.exit(app.exec())