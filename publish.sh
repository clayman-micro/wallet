#!/bin/sh

BRANCH_NAME=`git rev-parse --abbrev-ref HEAD`

if [ $BRANCH_NAME = "master" ]; then
    make build-image
    make publish-image
fi
