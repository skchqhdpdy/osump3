title exeMaker
pyinstaller --onefile --uac-admin --icon=icon.ico osump3.py
copy dist\osump3.exe osump3.exe
del /f /q osump3.spec
rd /s /q __pycache__ && rd /s /q build && rd /s /q dist
pause