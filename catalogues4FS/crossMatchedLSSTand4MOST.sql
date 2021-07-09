--- INPUTS:
-- - p: The directory path you want to savethe output file in
-- - prefix: the table prefix e.g. s10jan2021
-- - field: wfd or ddf
-- - suffix: Some random words to id this file from others you might make

-- - qvid: THe version ID in the qmost file
-- - monyear: The month/year name for the 4MOST pointing

\set snhead :prefix'_':field'_sn_head'
\set snphot :prefix'_':field'_sn_phot'

--- This script will simulate a crude observing queue to create a list of targets for 4MOST.
--- Our basic observing criteria should be:
--- ~ At least 2 observations seperated by 12 hours
--- ~ in any 2 filters from griz
--- ~ detected at a 5 sigma significance
---
--- Each target will be valid for 5 days (we can discuss this and update accordingly) after the
--- most recent observation
--- Let's first select all the objects
-- Uncomment below if you want to save the output as a csv
\set fsave :p'/':prefix'_':field'_liveQueue_':suffix'.csv'
\echo :fsave
\f ','
\a
\o :fsave
\pset footer off

-- \f ','
-- \a
-- \o '/Users/cfrohmaier/Documents/TiDES/lsstFellow/Jan2021/catalogues4FS/crossMatchedOutputDDF_20210205.csv'
-- \pset footer off


WITH
    uni_snid
    AS
    (
        -- Stores a list of unique SNIDs
        SELECT
            *
        FROM (
        SELECT
                snh.snid,
                count(DISTINCT (flt)) AS uni_filter, -- Counts the distinct number of filters each object is observed in
                count(*) AS obs_count
            -- Counts the number of observations
            FROM
                :snhead snh
                JOIN :snphot snp ON snh.snid = snp.snid
            WHERE
        snp.fluxcal / snp.fluxcalerr >= 5 -- We 5sigma significance on any observations
                AND snp.flt IN ('g', 'r', 'i', 'z')
            -- Only including observations in griz
            GROUP BY
        snh.snid) subq
        WHERE
        subq.obs_count > 2 -- Objects must be observed at least twice
            AND subq.uni_filter > 3
        -- Objects must be observed in at least 3 filters
    ),
    epochs
    AS
    (
        -- This function creates the light curves 
        SELECT
            snp.snid,
            floor(mjd) AS rmjd, -- 
            flt,
            fluxcal,
            fluxcalerr,
            sim_magobs,
            zpt,
            dense_rank() OVER (PARTITION BY snp.snid ORDER BY floor(mjd) ASC) AS obs_rank
        FROM
            :snphot snp
        WHERE
        snp.snid IN (
            SELECT
                snid
            FROM
                uni_snid)
            AND fluxcal / fluxcalerr >= 5
            AND flt IN ('g', 'r', 'i', 'z')
    ),
    queuemost
    AS
    (
        SELECT DISTINCT (epochs.snid),
            snh.ra,
            snh.dec,
            min(rmjd) + 0.5 AS trigstart, -- I add 0.5 days to give us realistic wriggle room on the trigger
            max(rmjd) + 5 AS trigend, -- All OBs are active for 5 days after the final 5 sigma observation.
            max(rmjd) - min(rmjd) AS days,
            snh.sntype,
            snh.redshift_final AS redshift
        FROM
            epochs
            JOIN :snhead snh ON epochs.snid = snh.snid
        WHERE
    fluxcal > 100 -- This corredponds to a depth of mag 22.5
            AND obs_rank >= 2
        -- Obs rank means we always require an observation on a second night before triggering
        GROUP BY
    epochs.snid,
    snh.ra,
    snh.dec,
    snh.sntype,
    snh.redshift_final
    ),
    qpointings
    AS
    (
        SELECT DISTINCT
            (ob_first_tile_id),
            count(ob_first_tile_id),
            jd_diff+60035.5 as mjd_obs,
            ra,
            dec,
            sum(texp) AS total_texp
        FROM
            qmost_tiles
        WHERE
    vid = :qvid
            AND monyear = :'monyear'
        GROUP BY
    ob_first_tile_id,
    jd_diff,
    ra,
    dec
    ),
    snein4most
    AS
    (
        SELECT
            qsn.snid,
            qsn.ra,
            qsn.dec,
            qsn.trigstart,
            qsn.trigend,
            qsn.days,
            qsn.sntype,
            qsn.redshift,
            qp.ob_first_tile_id,
            qp.mjd_obs,
            qp.ra as qmost_ra,
            qp.dec as qmost_dec,
            qp.total_texp,
            q3c_dist(qp.ra, qp.dec,qsn.ra, qsn.dec)
        FROM queuemost qsn, qpointings qp
        WHERE q3c_join(qp.ra, qp.dec,qsn.ra, qsn.dec,1.15624) and mjd_obs>=trigstart and mjd_obs<=trigend

    )

SELECT * from snein4most;


