#!/usr/bin/env bash

hugo -d ../www
#mkdir ../www/images
cp -rf ../logo.png ../www/images
cp -rf ../favicon.png ../www
