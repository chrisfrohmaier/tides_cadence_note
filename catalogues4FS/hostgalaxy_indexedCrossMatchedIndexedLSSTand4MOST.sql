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
\set fsave :p'/':prefix'_':field'_hostgalaxy_':suffix'_IndexQ.csv'
\echo :fsave
\f ','
\a
\o :fsave
\pset footer off

-- \f ','
-- \a
-- \o '/Users/cfrohmaier/Documents/TiDES/lsstFellow/Jan2021/catalogues4FS/crossMatchedOutputDDF_20210205.csv'
-- \pset footer off

-- SNe that pass the cut:
-- At least 2 observations in 2 filters before peak and 
-- at least 2 observations in 2 filters within 30 days after peak
-- All the host galaxies get sent to the 4MOST queue
-- Note: Need to count the bumber of galaxies that get 2 observations (i.e. 2 hours)

\timing

SELECT
            qgal.*,
            qp.ob_first_tile_id,
            qp.mjd_obs,
            qp.ra as qmost_ra,
            qp.dec as qmost_dec,
            qp.total_texp,
            q3c_dist(qp.ra, qp.dec,qgal.ra, qgal.dec)
        FROM (SELECT * from (
        SELECT
        snh.snid,
        snh.peakmjd,
        snh.ra, -- Indexed on SN Ra, Dec, stick with that for now
        snh.dec, -- If big issue, make index on hostgal ra dec too
        snh.hostgal_ra,
        snh.hostgal_dec,
        snh.sntype,
        snh.redshift_final as redshift,
        count(DISTINCT (flt)) AS uni_filter, -- Counts the distinct number of filters each object is observed in
        count(*) AS obs_count, -- Counts total number of 5 sigma detection,
        count(DISTINCT(floor(mjd))) filter (where mjd<snh.peakmjd) AS pre_epochs, -- Counts the number of epoch before peak
        count(DISTINCT(floor(mjd))) filter (where mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_epochs, -- Counts the number of epoch before peak
        count(DISTINCT (flt)) filter (where mjd<snh.peakmjd) AS num_pre_filters,
        count(DISTINCT (flt)) filter (where mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS num_post_filters,
        max(snp.mjd) filter (where snp.fluxcal>63.0957) AS trigstart, --63.0957 flux is 23rd mag
        count(DISTINCT(floor(mjd))) filter (where flt='g' and mjd<snh.peakmjd) AS pre_g,
        count(DISTINCT(floor(mjd))) filter (where flt='g' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_g,
        count(DISTINCT(floor(mjd))) filter (where flt='r' and mjd<snh.peakmjd) AS pre_r,
        count(DISTINCT(floor(mjd))) filter (where flt='r' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_r,
        count(DISTINCT(floor(mjd))) filter (where flt='i' and mjd<snh.peakmjd) AS pre_i,
        count(DISTINCT(floor(mjd))) filter (where flt='i' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_i,
        count(DISTINCT(floor(mjd))) filter (where flt='z' and mjd<snh.peakmjd) AS pre_z,
        count(DISTINCT(floor(mjd))) filter (where flt='z' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_z,
        count(DISTINCT(floor(mjd))) filter (where flt='g' and mjd>snh.peakmjd) AS post_g_all,
        count(DISTINCT(floor(mjd))) filter (where flt='r' and mjd>snh.peakmjd) AS post_r_all,
        count(DISTINCT(floor(mjd))) filter (where flt='i' and mjd>snh.peakmjd) AS post_i_all,
        count(DISTINCT(floor(mjd))) filter (where flt='z' and mjd>snh.peakmjd) AS post_z_all
        FROM
        :snhead snh
        JOIN :snphot snp ON snh.snid = snp.snid
        WHERE
        snp.fluxcal / snp.fluxcalerr >= 5 -- We 5sigma significance on any observations
        AND snp.flt IN ('g', 'r', 'i', 'z')
        -- Only including observations in griz
        GROUP BY
        snh.snid, snh.peakmjd,snh.ra, -- Indexed on SN Ra, Dec, stick with that for now
        snh.dec, -- If big issue, make index on hostgal ra dec too
        snh.hostgal_ra,
        snh.hostgal_dec,
        snh.sntype,
        snh.redshift_final) subq
        WHERE
        (subq.pre_epochs > 2 and subq.num_pre_filters>2) and (subq.post_epochs > 2 and subq.num_post_filters>2)) qgal, 
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
        ) qp
WHERE q3c_join(qp.ra, qp.dec,qgal.ra, qgal.dec,1.15624) and mjd_obs>=trigstart

-- SELECT
--             qsn.snid,
--             qsn.ra,
--             qsn.dec,
--             qsn.trigstart,
--             qsn.trigend,
--             qsn.days,
--             qsn.sntype,
--             qsn.redshift,
--             qp.ob_first_tile_id,
--             qp.mjd_obs,
--             qp.ra as qmost_ra,
--             qp.dec as qmost_dec,
--             qp.total_texp,
--             q3c_dist(qp.ra, qp.dec,qsn.ra, qsn.dec)
--         FROM (
--             SELECT DISTINCT (epochs.snid),
--             snh.ra,
--             snh.dec,
--             min(rmjd) + 0.5 AS trigstart, -- I add 0.5 days to give us realistic wriggle room on the trigger
--             max(rmjd) + 5 AS trigend, -- All OBs are active for 5 days after the final 5 sigma observation.
--             max(rmjd) - min(rmjd) AS days,
--             snh.sntype,
--             snh.redshift_final AS redshift
--             FROM
--                 (
--                     SELECT
--                     snp.snid,
--                     floor(mjd) AS rmjd, -- 
--                     flt,
--                     fluxcal,
--                     fluxcalerr,
--                     sim_magobs,
--                     zpt,
--                     dense_rank() OVER (PARTITION BY snp.snid ORDER BY floor(mjd) ASC) AS obs_rank
--                     FROM
--                     :snphot snp
--                     WHERE
--                     snp.snid IN (
--                     SELECT
--                         snid
--                     FROM
--                         (
--                             SELECT
--                             *
--                             FROM (
--                                     SELECT
--                                     snh.snid,
--                                     count(DISTINCT (flt)) AS uni_filter, -- Counts the distinct number of filters each object is observed in
--                                     count(*) AS obs_count
--                                     -- Counts the number of observations
--                                     FROM
--                                     :snhead snh
--                                     JOIN :snphot snp ON snh.snid = snp.snid
--                                     WHERE
--                                     snp.fluxcal / snp.fluxcalerr >= 5 -- We 5sigma significance on any observations
--                                     AND snp.flt IN ('g', 'r', 'i', 'z')
--                                     -- Only including observations in griz
--                                     GROUP BY
--                                     snh.snid) subq
--                                     WHERE
--                                     subq.obs_count > 2 -- Objects must be observed at least twice
--                                     AND subq.uni_filter > 3
--                         ) uni_snid)
--                     AND fluxcal / fluxcalerr >= 5
--                     AND flt IN ('g', 'r', 'i', 'z')
--                 ) epochs
--                 JOIN :snhead snh ON epochs.snid = snh.snid
--             WHERE
--             fluxcal > 100 -- This corredponds to a depth of mag 22.5
--                 AND obs_rank >= 2
--             -- Obs rank means we always require an observation on a second night before triggering
--             GROUP BY
--             epochs.snid,
--             snh.ra,
--             snh.dec,
--             snh.sntype,
--             snh.redshift_final
--         ) qsn, 
--         (
--             SELECT DISTINCT
--             (ob_first_tile_id),
--             count(ob_first_tile_id),
--             jd_diff+60035.5 as mjd_obs,
--             ra,
--             dec,
--             sum(texp) AS total_texp
--             FROM
--                 qmost_tiles
--             WHERE
--             vid = :qvid
--                     AND monyear = :'monyear'
--                 GROUP BY
--             ob_first_tile_id,
--             jd_diff,
--             ra,
--             dec
--         ) qp
-- WHERE q3c_join(qp.ra, qp.dec,qsn.ra, qsn.dec,1.15624) and mjd_obs>=trigstart and mjd_obs<=trigend;




-- with q1 AS (
--     SELECT * from (
--         SELECT
--         snh.snid,
--         snh.peakmjd,
--         snh.ra, -- Indexed on SN Ra, Dec, stick with that for now
--         snh.dec, -- If big issue, make index on hostgal ra dec too
--         snh.hostgal_ra,
--         snh.hostgal_dec,
--         count(DISTINCT (flt)) AS uni_filter, -- Counts the distinct number of filters each object is observed in
--         count(*) AS obs_count, -- Counts total number of 5 sigma detection,
--         count(DISTINCT(floor(mjd))) filter (where mjd<snh.peakmjd) AS pre_epochs, -- Counts the number of epoch before peak
--         count(DISTINCT(floor(mjd))) filter (where mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_epochs, -- Counts the number of epoch before peak
--         count(DISTINCT (flt)) filter (where mjd<snh.peakmjd) AS num_pre_filters,
--         count(DISTINCT (flt)) filter (where mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS num_post_filters,
--         max(snp.mjd) filter (where snp.fluxcal>63.0957) AS final_5sig_det --63.0957 flux is 23rd mag
--         -- Counts the number of observations
--         FROM
--         baseline_1pt7_ddf_sn_head snh
--         JOIN baseline_1pt7_ddf_sn_phot snp ON snh.snid = snp.snid
--         WHERE
--         snp.fluxcal / snp.fluxcalerr >= 5 -- We 5sigma significance on any observations
--         AND snp.flt IN ('g', 'r', 'i', 'z')
--         -- Only including observations in griz
--         GROUP BY
--         snh.snid, snh.peakmjd) subq
--         WHERE
--         (subq.pre_epochs > 2 and subq.num_pre_filters>2) and (subq.post_epochs > 2 and subq.num_post_filters>2)
--         LIMIT 20
-- )

-- -- count(DISTINCT(floor(mjd))) filter (where flt='g' and mjd<snh.peakmjd) AS pre_g,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='g' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_g,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='r' and mjd<snh.peakmjd) AS pre_r,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='r' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_r,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='i' and mjd<snh.peakmjd) AS pre_i,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='i' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_i,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='z' and mjd<snh.peakmjd) AS pre_z,
-- -- count(DISTINCT(floor(mjd))) filter (where flt='z' and mjd>snh.peakmjd and mjd-snh.peakmjd<50) AS post_z,


-- SELECT * from (SELECT DISTINCT
--             (ob_first_tile_id),
--             count(ob_first_tile_id),
--             jd_diff+60035.5 as mjd_obs,
--             ra,
--             dec,
--             sum(texp) AS total_texp
--             FROM
--                 qmost_tiles
--             WHERE
--             vid = 44
--                     AND monyear = 'nov2020'
--                 GROUP BY
--             ob_first_tile_id,
--             jd_diff,
--             ra,
--             dec) subq where subq.total_texp>45 limit 20;