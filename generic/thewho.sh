#!/bin/bash -e

w | tail --lines=+3 | awk '{print $1}' | sort -u

