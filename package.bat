@echo off
pip install pyinstaller
mkdir cache
cd cache
mkdir hooks
copy ..\other\hook-apscheduler.py hooks /Y
pyinstaller -F -i "..\icons\favicon.ico" "..\CountBoard.py" -w --additional-hooks-dir=./hooks
copy dist\CountBoard.exe .. /Y
cd ..
rmdir cache /S /Q