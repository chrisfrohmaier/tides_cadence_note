--- CLUSTER mytable_q3c_ang2ipix_idx ON mytable;

\set tindex :tname'_q3c_ang2ipix_idx'

CREATE INDEX ON :tname (q3c_ang2ipix(ra, dec));

CLUSTER :tindex ON :tname;

ANALYZE :tname