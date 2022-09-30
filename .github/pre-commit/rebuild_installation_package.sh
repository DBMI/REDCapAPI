cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCapAPI
python setup.py check
python setup.py sdist
python setup.py bdist_wheel --universal
git add dist -f
git commit -m "Deploy updated installation package." --no-verify
git push -u origin develop