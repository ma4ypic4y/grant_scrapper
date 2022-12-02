#!/bin/bash

docker run --rm -t --network host -v ${PWD}/../data:/app/data coord_parser