title exeMaker
pyinstaller --onefile --uac-admin --icon=icon.ico osump3.py
del /f /q osump3.spec osump3.exe
copy dist\osump3.exe osump3.exe
rd /s /q __pycache__ && rd /s /q build && rd /s /q dist
pause