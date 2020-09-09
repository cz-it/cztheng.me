#!/usr/bin/env bash

rm -rf ../www/*
hugo -d ../www -v
#mkdir ../www/images
cp -rf ../logo.png ../www/images
cp -rf ../favicon.png ../www
cp -rf ../favicon.png ../www/favicon.ico
