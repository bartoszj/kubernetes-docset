## Python

Python 3.7 required.

```bash
python3.7 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Swagger (optional)

https://kubernetes.io/docs/contribute/generate-ref-docs/contribute-upstream/#generating-the-openapi-spec-and-related-files
https://kubernetes.io/docs/contribute/generate-ref-docs/kubernetes-api/

## How to generate the docset

Run this command to build documentation for given version:

```bash
./build.sh <version>
# Example:
./build.sh 1.14.0
```
