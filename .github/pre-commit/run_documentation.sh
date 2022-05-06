sphinx-apidoc -f -o C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls\\docs\\source C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls
sphinx-build -b html C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls\\docs\\source C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls\\docs\\build\\html
cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls\\docs\\build\\html
git add --all
git commit -m "Deploy updates." --no-verify
git push -u origin gh-pages
