@ECHO OFF

:: Build for pip distribution
rmdir dist /S /q

pip install build --upgrade
py -m build