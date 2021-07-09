# TiDES Cadence Note
A repo for the TiDES cadence note simulation code.

This is for D3.3.1 for LSST:UK

## Requirements

### Postgres
A local install of a Postgres database is required.
This pipeline was developed on `psql 12.1`.
Please create a database with the name `tides` initiated with a standard `public` schema. See [here](https://www.postgresql.org/docs/12/sql-createdatabase.html) for instructions.
You will need to install `q3c` from this github repo [https://github.com/segasai/q3c](https://github.com/segasai/q3c). Q3C allows us to perform efficient spatial queries. 

### Python

`python >= 3.8` is required to run the code in this repo.

The following modules are required:

`astropy >= 4.0`

`numpy >= 1.19.5`

`pandas >= 0.2`

`sqlalchemy >=1.1`

`psycopg2 >=2.7`

## Password Protection

Some of the files require us to connect to a database that might be password protected. The files hosted on the remote Southampton postgres server certainly require login credentials. I have created a dummy `dbLogin.yml` file as an example of a file you need to modify with your own personal credentials. This will work if you are using local or remote hosted sql databases.
