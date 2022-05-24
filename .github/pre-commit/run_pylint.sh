cd C:\\Users\\Kevin.Delaney\\PycharmProjects\\REDCap_API_Calls
SCORE=$(sh .\\.github\\pre-commit\\pylint-compute-score.sh)"/10.00"
<<<<<<< HEAD
anybadge -l pylint -v "$SCORE" --overwrite --file .\\.github\\badges\\pylint-badge.svg 2=red 4=orange 8=yellow 10=green
=======
python .\\venv\\Lib\\site-packages\\anybadge.py -l pylint -v "$SCORE" --overwrite --file .\\.github\\badges\\pylint-badge.svg 2=red 4=orange 8=yellow 10=green
>>>>>>> master
