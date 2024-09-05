cd $(dirname "$(realpath "$0")")/../
rm -rf build/ dist/ captametropolis.egg-info/
./setup.py sdist bdist_wheel
