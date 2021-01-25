#!/bin/bash

readonly PROJECT=pyvmsnap
readonly OUTPUTFILE=/usr/local/orbit/$PROJECT/data/output

if [ -f $OUTPUTFILE ]
then
    cat $OUTPUTFILE
    rm $OUTPUTFILE
fi