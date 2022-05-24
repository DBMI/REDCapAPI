TODAY=$(date +"%B %d, %Y")
cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls
python .\\venv\\Lib\\site-packages\\anybadge.py -l "last commit" -v "$TODAY" --overwrite --file .\\.github\\badges\\last-commit-badge.svg
