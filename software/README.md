# Software Setup Information
## Option 1: .EXE - Preferred (Windows only - currently)
Simply download the gui.exe or lycan_loopback.exe file from the software/dist or software/dist/lycan_loopback directory.
Click the .exe file to execute, and you are all set!
> [!Note]
> Make sure the Lycan system (through the FTDI board) is plugged in before you run the programs

## Option 2: Create a Python virtual environment (Windows or Linux)

> [!NOTE]  
> Don't use the Github repo for your virtual environment location

### On Windows:
```
python -m venv C:/path/to/new/virtual/environment
```

### On Linux:
```
python -m venv /path/to/new/virtual/environment
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

# Lycan Testing Scripts
## Loopback
