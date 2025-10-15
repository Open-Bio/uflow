import sys
from uflow.App import uflow
from qtpy.QtWidgets import QApplication
import argparse
import os
import json


def main():
    app = QApplication(sys.argv)

    instance = uflow.instance(software="standalone")
    if instance is not None:
        instance.activateWindow()
        instance.show()

        parser = argparse.ArgumentParser(description="uflow CLI")
        parser.add_argument("-f", "--filePath", type=str, default="Untitled.pygraph")
        parsedArguments, unknown = parser.parse_known_args(sys.argv[1:])
        filePath = parsedArguments.filePath
        if not filePath.endswith(".pygraph"):
            filePath += ".pygraph"
        if os.path.exists(filePath):
            with open(filePath, "r") as f:
                data = json.load(f)
                instance.loadFromData(data)
                instance.currentFileName = filePath

        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)

        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
