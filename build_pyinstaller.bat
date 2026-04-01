@ECHO OFF

:: Build for exe distribution
pip install pyinstaller --upgrade

pyinstaller ^
    --onefile ^
    -n cuhkit ^
    --icon "imgs/icon-48x48.ico" ^
    --add-data "src/cuhkit/projects/templates;cuhkit/projects/templates" ^
    src\cuhkit\cli.py