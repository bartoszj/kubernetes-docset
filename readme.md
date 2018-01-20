## Python

Python 3.6 required.

## Populate Kubernetes's documentation

In the Kubernetes direcotry:

```bash
./hack/generate-docs.sh
```

## How to generate the docset

The `api-reference` is copied from kubernetes's source code, under `docs/` directory.

run `gen.py` and `build-doc.sh` to build the docset.
