#!/bin/bash

##This first loop reads in the flags from the commandline
## n, numprocs: is the number of processors we'll use for some of the heavier tasks
## p, path: is the base directory to be searching for the FITS and CSV files

while getopts n:p: flag
do 
    case "${flag}" in
        n) numproc=${OPTARG};;
        p) path=${OPTARG};;
    esac
done

echo "Search path: $path";
#find /data/cf5g09/tides/paperSims2021/March2021/TestOpSim/footprint8 \( -name "*HEAD.FITS*" -not -path "*SALT2*" -not -path "*-V19*" \) -type f
#find /data/cf5g09/tides/paperSims2021/March2021/TestOpSim/footprint8 \( -name "*HEAD.FITS*" -and -path "*SALT2*" \) -type

find $path \( -name "*HEAD.FITS*" -not -path "*SALT2*" -not -path "*-V19*" \) -type f > ${path}/files2convertFITStoCSV_nonIa_or_CC.txt
find $path \( -name "*HEAD.FITS*" -and -path "*SALT2*" \) -type f > ${path}/files2convertFITStoCSV_SALT2.txt
find $path \( -name "*HEAD.FITS*" -and -path "*-V19*" \) -type f > ${path}/files2convertFITStoCSV_V19.txt
echo "Found files, saved in files2convertFITStoCSV_{TRANSIENT_TYPES}.txt"

echo -------

#exit

# Create several of the databases needed to upload the TiDES catalogues.
echo Please enter the prefix name for the database tables: "(e.g. s10april2020)"
echo --- Note: table prefix will be converted to lowercase ---
echo --- Note2: Please indicate if this is a 4MOST candence upload in the prefix
echo e.g. s10april2020_4most
read userdbname
tableprefix=$(echo "$userdbname" | tr '[:upper:]' '[:lower:]') #Converts to lowercase
echo --- Making Table ---
echo

startScriptTime=$SECONDS
## Here we will make the postgres tables

## LSST Observations
wfdtablehead="${tableprefix}_wfd_sn_head"
wfdtablephot="${tableprefix}_wfd_sn_phot"

ddftablehead="${tableprefix}_ddf_sn_head"
ddftablephot="${tableprefix}_ddf_sn_phot"

ddfsummary="${tableprefix}_ddf_sn_summary"
wfdsummary="${tableprefix}_wfd_sn_summary"


# ## 4MOST Observations
# wfdtablehead4most="${tableprefix}_4most_wfd_sn_head"
# wfdtablephot4most="${tableprefix}_4most_wfd_sn_phot"

# ddftablehead4most="${tableprefix}_4most_ddf_sn_head"
# ddftablephot4most="${tableprefix}_4most_ddf_sn_phot"

psql tides -v wfdhead=$wfdtablehead -v wfdphot=$wfdtablephot -v ddfhead=$ddftablehead -v ddfphot=$ddftablephot \
-v wfdsummary=$wfdsummary -v ddfsummary=$ddfsummary -f makeTables.sql

echo The following tables have been made:
echo $wfdtablehead
echo $wfdtablephot
echo $ddftablehead
echo $ddftablephot
echo $ddfsummary
echo $wfdsummary

echo --------

## Now we will convert the HEAD, PHOT and summary files to CSV
## Write a python script that takes one input file.
## Have a text file input to the main script of all the SNANA output files
## We'll make it multicore pooled with xargs

echo "Converting SNANA ouput FITS files to CSV"
echo "--- This may take a while ---"
#This loop reads the text file
startLoop=$SECONDS

echo "--- Doing non-SALT and non-V19 templates---"
while read c;
    do
    echo python makeCSVfromSNANA.py -p $c;
    done < ${path}/files2convertFITStoCSV_nonIa_or_CC.txt | xargs -I CMD -P $numproc bash -c CMD
echo Done non-SALT non-V19 in: $(( SECONDS - startScriptTime )) seconds
startV=$SECONDS
echo "--- Doing V19 templates---"
while read c;
    do
    echo python makeCSVfromSNANA.py -p $c;
    done < ${path}/files2convertFITStoCSV_V19.txt | xargs -I CMD -P 3 bash -c CMD
echo Done V19 in: $(( SECONDS - startV )) seconds
startSALT=$SECONDS
echo "--- Doing SALT2 templates---"
while read c;
    do
    echo python makeCSVfromSNANA.py -p $c;
    done < ${path}/files2convertFITStoCSV_SALT2.txt | xargs -I CMD -P 1 bash -c CMD
echo Done SALT2 in: $(( SECONDS - startSALT )) seconds

echo "All input FITS Files converted to CSV in" $(( SECONDS - startLoop )) "seconds"
echo "Files saved in same directory as the input FITS"

echo -------
## Now we need to make a file containing all the HEAD file paths

echo "Searching for *WFD_*HEAD.csv files in: $path";

find $path -name "*WFD*_*HEAD.csv" -type f > ${path}/files2UploadtoDB_WFD_HEAD.txt

echo "Found files, saved in files2UploadtoDB_WFD_HEAD.txt"

echo -------

echo "Searching for *DDF_*HEAD.csv files in: $path";

find $path -name "*DDF*_*HEAD.csv" -type f > ${path}/files2UploadtoDB_DDF_HEAD.txt

echo "Found files, saved in files2UploadtoDB_DDF_HEAD.txt"

echo -------

## Now we need to make a file containing all the PHOT file paths

echo "Searching for *WFD*_*PHOT.csv files in: $path";

find $path -name "*WFD*_*PHOT.csv" -type f > ${path}/files2UploadtoDB_WFD_PHOT.txt

echo "Found files, saved in files2UploadtoDB_WFD_PHOT.txt"

echo -------

echo "Searching for *DDF*_*PHOT.csv files in: $path";

find $path -name "*DDF*_*PHOT.csv" -type f > ${path}/files2UploadtoDB_DDF_PHOT.txt

echo "Found files, saved in files2UploadtoDB_DDF_PHOT.txt"

echo -------


## Now we need to upload the WFD HEAD csv files to the database
echo -------

echo "Uploading the WFD HEAD Files";

while read c;
    do
    echo "\\\copy ${wfdtablehead} FROM \'${c}\' WITH DELIMITER \',\' CSV HEADER;";
    done < ${path}/files2UploadtoDB_WFD_HEAD.txt | xargs -I CMD -P $numproc bash -c "psql tides -U cf5g09 -c \"CMD\""

echo -------

echo "Uploading the DDF HEAD Files";

while read c;
    do
    echo "\\\copy ${ddftablehead} FROM \'${c}\' WITH DELIMITER \',\' CSV HEADER;";
    done < ${path}/files2UploadtoDB_DDF_HEAD.txt | xargs -I CMD -P $numproc bash -c "psql tides -U cf5g09 -c \"CMD\""

echo -------


## Now we need to upload the PHOT csv files to the database

echo "Uploading the WFD PHOT Files";

while read c;
    do
    echo "\\\copy ${wfdtablephot} FROM \'${c}\' WITH DELIMITER \',\' CSV HEADER;";
    done < ${path}/files2UploadtoDB_WFD_PHOT.txt | xargs -I CMD -P $numproc bash -c "psql tides -U cf5g09 -c \"CMD\""

echo -------

echo "Uploading the DDF PHOT Files";

while read c;
    do
    echo "\\\copy ${ddftablephot} FROM \'${c}\' WITH DELIMITER \',\' CSV HEADER;";
    done < ${path}/files2UploadtoDB_DDF_PHOT.txt | xargs -I CMD -P $numproc bash -c "psql tides -U cf5g09 -c \"CMD\""

echo -------

## Now we need to run a script to do database maintainence

echo ------- Database Maintainence
echo "------- This may take a loooooong time -------"

psql tides -v wfdhead=$wfdtablehead -v wfdphot=$wfdtablephot -v ddfhead=$ddftablehead -v ddfphot=$ddftablephot \
-f postUploadDBMaintence.sql

psql tides -v tname=$wfdtablehead -f spatialIndexCluster.sql
psql tides -v tname=$ddftablehead -f spatialIndexCluster.sql

echo ----- DONE -------
echo The whole process took $(( SECONDS - startScriptTime )) seconds