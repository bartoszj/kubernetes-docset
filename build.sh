#!/usr/bin/env bash

set -ex

# Read parameters
tag=$1
if [ -z $tag ]; then
    echo '"tag" must be specified'
    exit 1
fi

# Paths
CWD=$(pwd)
export GOPATH=${CWD}/go
BUILD_PATH="${CWD}/build/$tag"
KUBERNETES_PATH="${GOPATH}/src/github.com/kubernetes/kubernetes"
WEBSITE_PATH="${GOPATH}/src/github.com/kubernetes/website"
REF_DOC_PATH="${GOPATH}/src/github.com/kubernetes-incubator/reference-docs"

# Clean build
rm -rf "${BUILD_PATH}"
mkdir -p "${BUILD_PATH}"

# Remove previous builds
cd "${CWD}"
rm -f "docSet.dsidx"
rm -f "Kubernetes.tgz"
rm -rf "Kubernetes.docset"

# Prepare docs
cp -r "Kubernetes.docset-tmpl" "Kubernetes.docset"

# Update Go:
go get -d -u -f github.com/kubernetes/kubernetes || true
go get -d -u -f github.com/kubernetes/website || true
go get -d -u -f github.com/kubernetes-incubator/reference-docs
go get ${GOPATH}/src/github.com/kubernetes-incubator/reference-docs/gen-apidocs

# Checkout and clean
cd "${KUBERNETES_PATH}"
git fetch --all --prune
git checkout -- .
git checkout v${tag}

# Generage API
# https://kubernetes.io/docs/contribute/generate-ref-docs/kubernetes-api/
cd "${REF_DOC_PATH}"
git checkout -- .
sed -e "s|WEBROOT=.*|WEBROOT=../../kubernetes/website|g" \
    -e "s|K8SROOT=.*|K8SROOT=../../kubernetes/kubernetes|g" \
    -e "s|APIDST=.*|APIDST=${CWD}/Kubernetes.docset/Contents/Resources/Documents/|g" \
    -e "s|sudo rm|rm|g" \
    -i .bac Makefile
rm Makefile.bac
make updateapispec
make api
make copyapi

# Copy extra files
cd "${CWD}"
rsync -ah --stats --delete "${WEBSITE_PATH}/static/js" "Kubernetes.docset/Contents/Resources/Documents/"

# Generate docs
python gen.py
cp -r "docSet.dsidx" "Kubernetes.docset/Contents/Resources/"

# Compress
tar --exclude='.DS_Store' -cvzf "Kubernetes.tgz" "Kubernetes.docset" &>/dev/null
mv "Kubernetes.tgz" "${BUILD_PATH}"
rm -rf "Kubernetes.docset"
