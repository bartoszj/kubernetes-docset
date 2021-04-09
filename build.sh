#!/usr/bin/env bash

set -ex

# Read parameters
tag=$1
if [ -z $tag ]; then
    echo '"tag" must be specified'
    exit 1
fi
RELEASE=${tag}
RELEASE_SHORT=${tag%.*}

# Paths
CWD=$(pwd)
export GOPATH=${CWD}/go
BUILD_PATH="${CWD}/build/${tag}"
KUBERNETES_PATH="${GOPATH}/src/github.com/kubernetes/kubernetes"
WEBSITE_PATH="${GOPATH}/src/github.com/kubernetes/website"
REF_DOC_PATH="${GOPATH}/src/github.com/kubernetes-sigs/reference-docs"

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
git clone https://github.com/kubernetes/kubernetes ${KUBERNETES_PATH} || true
git -C ${KUBERNETES_PATH} fetch --all --prune
git -C ${KUBERNETES_PATH} clean -fdx
git -C ${KUBERNETES_PATH} checkout -- .
git -C ${KUBERNETES_PATH} checkout v${tag}

git clone https://github.com/kubernetes/website ${WEBSITE_PATH} || true
git -C ${WEBSITE_PATH} fetch --all --prune
git -C ${WEBSITE_PATH} clean -fdx
git -C ${WEBSITE_PATH} checkout -- .
git -C ${WEBSITE_PATH} pull -- .

git clone https://github.com/kubernetes-sigs/reference-docs ${REF_DOC_PATH} || true
git -C ${REF_DOC_PATH} fetch --all --prune
git -C ${REF_DOC_PATH} clean -fdx
git -C ${REF_DOC_PATH} checkout -- .
git -C ${REF_DOC_PATH} pull -- .

# Checkout and clean
cd "${KUBERNETES_PATH}"

# Generage API
# # https://kubernetes.io/docs/contribute/generate-ref-docs/kubernetes-api/
cd "${REF_DOC_PATH}"
export K8S_WEBROOT=${WEBSITE_PATH}
export K8S_ROOT=${KUBERNETES_PATH}
export K8S_RELEASE=${RELEASE}
make updateapispec
# make api
make copyapi

# Copy files
cd "${CWD}"
rsync -ah --stats --delete "${WEBSITE_PATH}/static/docs/reference/generated/kubernetes-api/v${RELEASE_SHORT}/" "Kubernetes.docset/Contents/Resources/Documents/"
mkdir -p "Kubernetes.docset/Contents/Resources/Documents/css"
mkdir -p "Kubernetes.docset/Contents/Resources/Documents/js"
mkdir -p "Kubernetes.docset/Contents/Resources/Documents/fonts"
cp ${WEBSITE_PATH}/static/css/style_apiref.css "Kubernetes.docset/Contents/Resources/Documents/css/"
cp ${WEBSITE_PATH}/static/css/bootstrap-*.min.css "Kubernetes.docset/Contents/Resources/Documents/css/"
cp ${WEBSITE_PATH}/static/css/fontawesome-*.min.css "Kubernetes.docset/Contents/Resources/Documents/css/"
cp ${WEBSITE_PATH}/static/fonts/fontawesome-webfont.woff "Kubernetes.docset/Contents/Resources/Documents/fonts/"
cp ${WEBSITE_PATH}/static/fonts/fontawesome-webfont.woff2 "Kubernetes.docset/Contents/Resources/Documents/fonts/"
cp ${WEBSITE_PATH}/static/js/jquery-*.min.js "Kubernetes.docset/Contents/Resources/Documents/js/"
cp ${WEBSITE_PATH}/static/js/jquery.scrollTo-*.min.js "Kubernetes.docset/Contents/Resources/Documents/js/"
cp ${WEBSITE_PATH}/static/js/bootstrap-*.min.js "Kubernetes.docset/Contents/Resources/Documents/js/"
cp ${WEBSITE_PATH}/static/js/scroll-apiref.js "Kubernetes.docset/Contents/Resources/Documents/js/"

# Generate docs
python gen.py
cp -r "docSet.dsidx" "Kubernetes.docset/Contents/Resources/"

# Compress
tar --exclude='.DS_Store' -cvzf "Kubernetes.tgz" "Kubernetes.docset" &>/dev/null
mv "Kubernetes.tgz" "${BUILD_PATH}"
rm -rf "Kubernetes.docset"
