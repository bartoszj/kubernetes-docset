#!/bin/sh

rm Kubernetes.tgz &>/dev/null
rm -r Kubernetes.docset &>/dev/null
cp -r Kubernetes.docset-tmpl/ Kubernetes.docset
cp -r Documents/api-reference Kubernetes.docset/Contents/Resources/Documents/
cp -r docSet.dsidx Kubernetes.docset/Contents/Resources/
tar --exclude='.DS_Store' -cvzf Kubernetes.tgz Kubernetes.docset &>/dev/null
