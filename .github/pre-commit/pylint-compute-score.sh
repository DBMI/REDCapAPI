pylint $(git ls-files '.\src\redcap_api\*.py') | sed --quiet 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p'
