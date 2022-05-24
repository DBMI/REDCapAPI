pylint $(git ls-files '.\dbmi_redcap\*.py') | ssed --quiet 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p'
