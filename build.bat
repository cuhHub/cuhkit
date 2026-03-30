@ECHO OFF

rmdir dist /S /q

pip freeze > requirements.txt
py -m build