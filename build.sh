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
BUILD_PATH="${CWD}/build/$tag"
KUBERNETES_PATH="${CWD}/kubernetes"

# Clean build
rm -rf "${BUILD_PATH}"
mkdir -p "${BUILD_PATH}"

# Checkout and clean
git clone "https://github.com/kubernetes/kubernetes.git" || true
cd "${KUBERNETES_PATH}"
git fetch --all --prune
git checkout -- .
git checkout v${tag}

# Remove previous builds
cd "${CWD}"
rm -f "docSet.dsidx"
rm -f "Kubernetes.tgz"
rm -rf "Kubernetes.docset"

# Build
cp -r "Kubernetes.docset-tmpl" "Kubernetes.docset"
rsync -ah --stats --delete "${KUBERNETES_PATH}/docs/api-reference" "Kubernetes.docset/Contents/Resources/Documents/"
python gen.py
cp -r "docSet.dsidx" "Kubernetes.docset/Contents/Resources/"

# Compress
tar --exclude='.DS_Store' -cvzf "Kubernetes.tgz" "Kubernetes.docset" &>/dev/null
mv "Kubernetes.tgz" "${BUILD_PATH}"
rm -rf "Kubernetes.docset"
