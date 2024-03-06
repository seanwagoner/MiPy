# MicroPython for Infineon PSoC 6 Boards
## List of peripheral libraries
- DPS368 - Waterproof Pressure Sensor 
  
- TLV493D - Magnetic 3D Sensor

- BME280 - Temperature / Humidity Sensor

- LCD16x2 - LCD 16x2 Liquid Crystal Display

- HCSR04 - Distance Sensor

- HBridgeKit2Go - Motor Controller

- VL53L0X - Time of Flight Sensor

## How To Install MicroPython
Use following guide to download MicroPython. Currently, the only supported board for MicroPython development is the **CY8CPROTO-062-4343W**

The following website has detailed instructions regarding downloading and using MicroPython 
[MicroPython for PSoC 6](https://ifx-micropython.readthedocs.io/en/latest/psoc6/quickref.html)

**Notes for Windows:** After downloading the mpy-psoc6 utility script, make sure to change the encoding of the file to ANSI. This can be done as follows:
1. Locate the file and open the file in a text editor that supports encoding conversion such as Windows Notepad.
2. In the menu, settings, or after selecting **_Save As..._**, look for an option related to encoding or character set.
3. Select "ANSI" or "windows-1252" as the encoding option.
4. Save the file.

## Develop using VS Code
In order to use MicroPython with VS Code rather than Arduino Lab (The IDE automatically installed with MicroPython) we will be using a third-party, open source extension from RT-Thread called [RT-Thread MicroPython](https://marketplace.visualstudio.com/items?itemName=RT-Thread.rt-thread-micropython)

__Why use VS Code?__ - VS Code has much more functionality than Arduino Lab and is an industry standard. Although Arduino Lab is designed specifically for MicroPython development, VS Code's GitHub Integration, and robust Code Error Detection makes developing with VS Code much easier. Arduino Lab unfortunately is a very barebones IDE with minimal functionality and no Code Error Detection. 

The RT-Thread MicroPython extension has great documentation but below is a summarized version of said documentation tailored specifically for the **CY8CPROTO-062-4343W**.

### Preparation
If you want to use the MicroPython autocompletion feature (you can skip the next step if you don't need autocompletion for now), you need to do the following:

1. Install the [Python plug-in](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

2. Install [Python3](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjCtJ7w4tyEAxVfJjQIHRkzAgAQFnoECAcQAQ&url=https%3A%2F%2Fwww.python.org%2Fdownloads%2F&usg=AOvVaw3VuYRIaaa-SL5nRa6pfny0&opi=89978449) 
   on your PC and add it to the system environment variables as instructed by the Python plug-in

If you already have the above plug-ins and programs installed on your PC, you can skip these preparation step.

### Note for Ubuntu Support
This plug-in is supported by Ubuntu 18.04+. In order to avoid frequent access to serial port permissions under ubuntu system, the current user needs to be added to the user group dialout. Manually enter the following command: ```$USERNAME``` is the current USERNAME of the system:

```sudo usermod -ag dialout $USERNAME```

**Note:** the configuration change requires to restart the operating system for the configuration to take effect.

### Creating a MicroPython Project
The first step for MicroPython development is to create a MicroPython project within which all subsequent operations must run. Since the RT-Thread MicroPython extension does not provide any examples for the PSoC 6, we will start with a blank / new project. To create such project, look for the button that looks like a box with a plus on the VS Code status bar in the lower left corner.

### Connect to PSoC 6 Board
You can connect to the PSoC 6 development board by clicking the connection button in the lower left corner on the VS Code status bar and then selecting the port your device is connected to from the pop-up list. You will also always be prompted to connect to a device if you try to run files directly on the board prior to connecting to the board.

**Note:** You will have to check which port your PSoC board is connected to. Arduino Lab detects this automatically, so you could use Arduino Lab to check which port your MicroPython enabled board is connected to. 

### Run MicroPython Code Snippets and/or Entire Files
If you just want to debug a small amount of code without downloading files to the development board, you can use the __*code snippet function*__. You can run the selected code in the REPL environment by highlighting the snippet you want to run in the editor, and then select ```Execute the Selected MicroPython Code on the Device``` from the right-click menu.

If you want to quickly run a single file directly on the development board, right-click the .py file you want to run from the RT-Thread MicroPython Workspace and from the right-click menu, select ```Run the MicroPython File Directly on the Device```. This function downloads the current python file to the memory of the development board to run, achieving the effect of rapid debugging. We can also use the shortcut key ```Alt + q``` to trigger this function.

## Downloading/Running/Removing files on PSoC
__Note:__ When downloading and removing files from the PSoC Board, you can only be connected to the board via one platform whether that be an IDE or the terminal using ```ampy```. If you are using ampy to remove files, make sure Arduino Lab, VS Code, or any other IDE is not also connected to the board.

### Using VS Code & [RT-Thread MicroPython](https://marketplace.visualstudio.com/items?itemName=RT-Thread.rt-thread-micropython)
__Downloading Files/Folders to Board:__ To upload files or folders to the board, right-click the .py file you want to run from the RT-Thread MicroPython Workspace and from the right-click menu, select ```Download the file/folder to the device```.

__Running Code:__ If you want to run snippets of code, or a single file not already downloaded to the board, refer to the previous section. 

__Removing Files/Folders from Board:__

### Using MicroPython Tool [ampy](https://pypi.org/project/adafruit-ampy/)
Ampy is meant to be a simple command line tool to manipulate files and run code on a MicroPython board over its serial connection. With ampy you can send files from your computer to the board's file system, download files from a board to your computer, and even send a Python script to a board to be executed. To download ampy to your device, use the following [link](https://pypi.org/project/adafruit-ampy/) detailing how to install and run ampy

__Downloading Files/Folders to Board:__

__Running Code:__

__Removing Files/Folders from Board:__

### Using [Arduino Lab](https://labs.arduino.cc/en/labs/micropython)
__Downloading Files/Folders to Board:__

__Running Code:__

__Removing Files/Folders from Board:__

## Known Limitations
Information regarding [PSoC 6 file structure](https://ifx-micropython.readthedocs.io/en/latest/psoc6/mpy-usage.html)
1. Using ```ampy```, all commands work with PSoC Board except for ```run```. Using ```run``` only works immediately after the same file you plan to execute has been downloaded to the board using ```put```.
   

2. VSCode does not have a manner in which to view the file structure of the MicroPython board (at least for Windows). Therefore, if a developer wants to use the libraries above, they would need to use a different IDE such as [Thonny](https://thonny.org/), [Mu Editor](https://codewith.mu/), or [Arduino Lab](https://labs.arduino.cc/en/labs/micropython) to run onboard files.


3. Any referenced libraries **must** be downloaded to the board inorder for the code relying on said dependencies to run.
