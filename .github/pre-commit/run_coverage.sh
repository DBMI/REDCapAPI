cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls
coverage run
coverage xml
<<<<<<< HEAD
genbadge coverage --input-file coverage.xml --output-file .\\.github\\badges\\coverage-badge.svg
=======
python .\\venv\\Lib\\site-packages\\genbadge.py coverage --input-file coverage.xml --output-file .\\.github\\badges\\coverage-badge.svg
>>>>>>> master
