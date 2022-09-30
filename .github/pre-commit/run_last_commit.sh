TODAY=$(date +"%B %d, %Y")
cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCapAPI
python .\\venv\\Lib\\site-packages\\anybadge.py -l "last commit" -v "$TODAY" --overwrite --file .\\.github\\badges\\last-commit-badge.svg
