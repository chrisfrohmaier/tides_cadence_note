CREATE FUNCTION pg_temp.interp_flux (din double precision, dlow double precision, dhigh double precision, flow double precision, fhigh double precision)
    RETURNS double precision
    AS $$
    SELECT
        (din - dlow) * ((fhigh - flow) / (dhigh - dlow)) + (flow)
$$
LANGUAGE sql
IMMUTABLE;

CREATE TEMP TABLE sncat (
    snid bigint,
    ra double precision,
    dec double precision,
    trigstart double precision,
    trigend double precision,
    days int,
    sntype int,
    redshift double precision,
    ob_first_tile_id int,
    mjd_obs double precision,
    qmost_ra double precision,
    qmost_dec double precision,
    total_texp double precision,
    distance double precision
);
CREATE INDEX on sncat(snid);
CREATE INDEX on sncat(mjd_obs);

\set most4snphot 's10jan2021_4most_':field'_sn_phot'
\set snphot :prefix'_':field'_sn_phot'
\set fincsv :p'/':fin 
\set comma ','
\set indcmd '\\COPY sncat from ':fincsv' CSV HEADER DELIMITER ':'comma'';'
\echo :indcmd
:indcmd;

\timing

\set fsave :p'/':fname'.csv'
\echo :fsave
\f ','
\a
\o :fsave
\pset footer off

SELECT
    *,
    CASE WHEN flux_obs > 0 THEN - 2.5 * LOG(flux_obs) + 27.5 
    WHEN flux_obs <= 0 THEN NULL
    END mag_obs
    
FROM
    (
    SELECT
        sncat.snid,
        sncat.sntype,
        avg(mjd_diff) as mjd_diff,
        sncat.mjd_obs,
        min(mjd) AS mjd_low,
    max(mjd) AS mjd_high,
    min(fluxcal) AS flux_low,
    max(fluxcal) AS flux_high,
    pg_temp.interp_flux (sncat.mjd_obs, min(mjd), max(mjd), min(fluxcal), max(fluxcal)) as flux_obs
    
FROM
    sncat
    JOIN (
    SELECT
        sncat.snid,
        snp.mjd,
        sncat.mjd_obs,
        snp.fluxcal,
        sncat.mjd_obs - snp.mjd AS mjd_diff,
        dense_rank() OVER (PARTITION BY sncat.snid,
            sncat.mjd_obs ORDER BY abs(sncat.mjd_obs - snp.mjd) ASC) AS mjd_rank
FROM
    sncat
    JOIN :snphot snp ON sncat.snid = snp.snid
    WHERE
        snp.flt = 'r'
    GROUP BY
        mjd_obs,
        mjd,
        sncat.snid,
        fluxcal,
        mjd_diff) snjoin ON sncat.snid = snjoin.snid
        AND snjoin.mjd_obs = sncat.mjd_obs
    WHERE (mjd_rank = 1)
    OR (mjd_rank = 2)
GROUP BY
    sncat.snid,
    sncat.mjd_obs,
    sncat.sntype
ORDER BY
    sncat.snid) snmag
;

