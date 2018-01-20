## Python

Python 3.6 required.

## Populate Kubernetes's documentation

In the Kubernetes direcotry:

```bash
./hack/generate-docs.sh
```

## How to generate the docset

The `api-reference` is copied from kubernetes's source code, under `docs/` directory.

Run `gen.py` and `build-doc.sh` to build the docset.

Or in one command:

```
rm -r Kubernetes.docset Kubernetes.tgz; python gen.py && ./build-doc.sh && tar --exclude='.DS_Store' -cvzf Kubernetes.tgz Kubernetes.docset
```
