#!/bin/bash

# Create several of the databases needed to upload the TiDES catalogues.
echo Please enter the prefix name for the database tables you want to drop: "(e.g. s10april2020)"
echo --- Note: table prefix will be converted to lowercase ---
read userdbname1
tableprefix1=$(echo "$userdbname1" | tr '[:upper:]' '[:lower:]') #Converts to lowercase
echo ---
echo ---
echo --- Please enter the table prefix again

read userdbname2
tableprefix2=$(echo "$userdbname2" | tr '[:upper:]' '[:lower:]') #Converts to lowercase

if [ "$tableprefix1" = "$tableprefix2" ]
then
    echo - Table names match
    echo The following tables will be dropped:
    for t in "${tableprefix1}_wfd_sn_head" "${tableprefix1}_wfd_sn_phot" "${tableprefix1}_ddf_sn_head" "${tableprefix1}_ddf_sn_phot" "${tableprefix1}_ddf_sn_summary" "${tableprefix1}_wfd_sn_summary"
    do
    echo $t
    done
    read -p "Are you sure you want to drop these tables? (y/n) " prompt
    echo    # (optional) move to a new line
    if [[ $prompt =~ ^[Yy]$ ]]
    then
        echo Deleting...
        for t in "${tableprefix1}_wfd_sn_head" "${tableprefix1}_wfd_sn_phot" "${tableprefix1}_ddf_sn_head" "${tableprefix1}_ddf_sn_phot" "${tableprefix1}_ddf_sn_summary" "${tableprefix1}_wfd_sn_summary"
        do
        psql tides -c "DROP TABLE IF EXISTS ${t};"
        done
    else
        echo Tables will not be deleted
        echo Goodbye
        exit 1
    fi
else
    echo Table names $tableprefix1 and $tableprefix2 "do not match"
    echo Exiting...
    exit 1
fi

echo The following tables have been dropped:
for t in "${tableprefix1}_wfd_sn_head" "${tableprefix1}_wfd_sn_phot" "${tableprefix1}_ddf_sn_head" "${tableprefix1}_ddf_sn_phot" "${tableprefix1}_ddf_sn_summary" "${tableprefix1}_wfd_sn_summary"
do
echo $t
done