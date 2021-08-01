#!/bin/bash
if [ -x $(which python3) ]
then
    python3 -B monitoring $*
else
    python -B monitoring $*
fi
