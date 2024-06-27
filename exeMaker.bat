title exeMaker
pyinstaller --onefile --icon=icon.ico osump3.py
copy dist\osump3.exe osump3.exe
rd /s /q __pycache__ && rd /s /q build && rd /s /q dist
del /f /q osump3.spec
pause