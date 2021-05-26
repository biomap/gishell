# GIShell Command Line Tools
### ArcGIS Online Python API command shell

#### To Use:


1) open a terminal
1) install fresh virtualenv
2) run `pip install -r requirements.txt`
3) run `\path\to\venv\bin\python3 command.py` 

This will open a subterminal inside of terminal.

You will need to use `login` to do anything ATM.
From there `search` (sorta) works as well as `user`.

Super rough but wanted to see what I could do with this terminal and the API.
The idea being that cmdline tools require you to login each time you issue a cmd.
This holds the GIS object open (creates a session) and you can interactively work with the API from there. 