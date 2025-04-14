# Software Setup Information
## Option 1: .EXE - Preferred (Windows only - currently)
Simply download the gui.exe from the latest Release.
Click the .exe file to execute, and you are all set!
> [!Note]
> Make sure the Lycan system (through the FTDI board) is plugged in before you run the program

## Option 2: Create a Python virtual environment (Windows or Linux)

> [!NOTE]
> The Lycan API currently requires &ge;Python 3.8, but Python &ge;3.13 is preferred
> For older Python distributions (ie. &le;3.13), use "python" instead of "py" in the following commands

> [!NOTE]  
> Don't use the Github repo for your virtual environment location

### On Windows:
```
py -m venv C:/path/to/new/virtual/environment
```

### On Linux:
```
py -m venv /path/to/new/virtual/environment
```

## Activate the VENV
### On Windows (CMD):
```
C:/> <path to venv>/Scripts/activate.bat
```

### On Linux (bash):
```
source <path to venv>/bin/activate
```

## Install the required modules
### On Windows (CMD):
```
cd <path to Github Repo>/software/python/
py -m pip install -r requirements.txt
```

### On Linux (bash):
```
cd <path to Github Repo>/software/python/
python3 -m pip install -r requirements.txt
```

> [!NOTE]
> Make sure to run any python scripts for Lycan from within the virtual environment.
> In VSCode, this can be done by ensuring that you use the Python interpreter found within the virtual environment directory.
> In the terminal, make sure you activate the venv before running Python

## When done using the VENV...
```
deactivate
```
