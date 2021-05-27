from os import system

# pyinstaller --noconsole --onefile --icon=../icons/neptune.ico "nepEXE.py"

try:
    system('start dist\\Neptune(jpgNameConverter)\\Neptune(jpgNameConverter).exe')
except:
    pass
