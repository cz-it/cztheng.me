#!/usr/bin/env bash

rm -rf ../www/*
hugo -d ../www
#mkdir ../www/images
cp -rf ../logo.png ../www/images
cp -rf ../favicon.png ../www
