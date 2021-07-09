--- DDF HEAD Indexes

CREATE INDEX ON :ddfhead (snid);
CREATE INDEX ON :ddfhead (nobs);

--- WFD HEAD Indexes
CREATE INDEX ON :wfdhead (snid);
CREATE INDEX ON :wfdhead (nobs);

--- DDF PHOT Indexes
CREATE INDEX ON :ddfphot (snid);
CREATE INDEX ON :ddfphot (sim_magobs);
CREATE INDEX ON :ddfphot (mjd);
CREATE INDEX ON :ddfphot (fluxcal);
CREATE INDEX ON :ddfphot (fluxcalerr);
CREATE INDEX ON :ddfphot (flt);

--- WFD PHOT Indexes
CREATE INDEX ON :wfdphot (snid);
CREATE INDEX ON :wfdphot (sim_magobs);
CREATE INDEX ON :wfdphot (mjd);
CREATE INDEX ON :wfdphot (fluxcal);
CREATE INDEX ON :wfdphot (fluxcalerr);
CREATE INDEX ON :wfdphot (flt);

ANALYZE :ddfhead;
ANALYZE :wfdhead;
ANALYZE :ddfphot;
ANALYZE :wfdphot;
