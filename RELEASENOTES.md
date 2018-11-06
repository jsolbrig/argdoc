# Creating Releases

1. Get everything checked
2. Run tests
3. Increment version number in argdoc/version.py
4. Create PYPI release files:
    - `python setup.py sdist bdist_wheel`
5. Final check in
6. Push to github
7. Release to PYPI
    - `twine upload dist/ArgDoc-<version_number>*` (e.g. `twine upload dist/ArgDoc-0.1.2*`)
