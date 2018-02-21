# Tests

Install test dependencies with `pip3 install -r test/requirements.txt`.
Run tests with `pytest`. Find coverage with `pytest --cov=prettyparse`.

## Uploading Coverage

```Bash
export CODACY_PROJECT_TOKEN='<TOKEN>'
pytest --cov=prettyparse --cov-report=xml
python-codacy-coverage -r coverage.xml
```
