#!/bin/bash

while getopts p: flag
do 
    case "${flag}" in
        p) path=${OPTARG};;
    esac
done

echo "Search path: $path";

find $path -name "*HEAD.FITS*" -type f > files2convertFITStoCSV.txt