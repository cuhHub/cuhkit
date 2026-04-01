@ECHO OFF

pip install twine --upgrade
py -m twine upload dist/*.tar.gz dist/*.whl