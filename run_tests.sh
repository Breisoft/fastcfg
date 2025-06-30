# Standard unittest discovery
PYTHONPATH=src python -m unittest discover tests -v

# With coverage
# PYTHONPATH=src coverage run -m unittest discover tests
# coverage report -m --include="src/*"
#coverage html  # For HTML report