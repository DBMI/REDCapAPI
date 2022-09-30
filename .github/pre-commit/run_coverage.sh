cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCapAPI
coverage run
coverage xml
genbadge coverage --input-file coverage.xml --output-file .\\.github\\badges\\coverage-badge.svg
