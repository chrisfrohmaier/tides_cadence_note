\set fin :'fpath'
\echo :fin
--- \echo COPY :tname FROM :fpath WITH DELIMITER ',' CSV HEADER;
\COPY :tname FROM :fin WITH DELIMITER ',' CSV HEADER;
