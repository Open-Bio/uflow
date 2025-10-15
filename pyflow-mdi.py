import sys
from uflow.AppMDI import MDIMain
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QGuiApplication


def main():
    app = QApplication(sys.argv)

    instance = MDIMain()
    if instance is not None:
        instance.show()
        instance.activateWindow()
        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
