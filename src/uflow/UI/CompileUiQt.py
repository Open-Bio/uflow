import os
import subprocess


CURRENT_DIR = os.path.dirname(__file__).replace("\\", "/") + "/"
INTERPRETER_PATH = "python.exe"


def ui_to_py(ui_file):
    if not os.path.isfile(ui_file):
        msg = "no such file"
        print(msg)
        return msg
    py_file_name = os.path.splitext(ui_file)[0] + ".py"

    try:
        # 使用pyside6-uic命令行工具
        result = subprocess.run(
            ["pyside6-uic", ui_file], capture_output=True, text=True, check=True
        )
        with open(py_file_name, "w") as py_file:
            py_file.write(result.stdout)
        print("{0} converted to {1}.".format(ui_file.upper(), py_file_name.upper()))
    except subprocess.CalledProcessError as e:
        print("Error: compilation error.", e)
        print("stderr:", e.stderr)
    except FileNotFoundError:
        print(
            "Error: pyside6-uic not found. Please ensure PySide6 is properly installed."
        )

    bakFileName = py_file_name.replace(".py", "_backup.py")

    # convert to cross compatible code
    subprocess.call([INTERPRETER_PATH, "-m", "Qt", "--convert", py_file_name])

    if os.path.isfile(bakFileName):
        os.remove(bakFileName)
        print("REMOVING", bakFileName)


def compile():
    for d, dirs, files in os.walk(CURRENT_DIR):
        if "Python" in d or ".git" in d:
            continue
        for f in files:
            if "." in f:
                ext = f.split(".")[1]
                if ext == "ui":
                    uiFile = os.path.join(d, f)
                    ui_to_py(uiFile)


if __name__ == "__main__":
    compile()
