<h1 align="center">
    <strong>🏺 aftafa</strong> data pipeline
</h1>
<p align="center">
Work in progress lightweight Python ELT library with e-commerce (OZON, Wildberries, Yandex Market, etc.) domain</p>

<p align="center">⚠️ This project is under <strong>heavy development</strong> and yet to be a usable library, so many features are missing actually and its structure surely will be modified/refactored and documented</p>

# Overview
<div style="text-align: justify">This module can be helpful even if you're not trying to build a decent ETL pipeline, but rather want to fetch data from a marketplace API via a convenient client. But keep in mind that API methods provided in this module can only fetch data (not to confuse with HTTP methods) but can't change them in a way it is documented by a source vendor (e. g. for marketplaces it means: change prices, add new products, refresh dropshipping stocks and etc). Inspired by <a href=https://github.com/dlt-hub/dlt>dlt</a>, <a href=https://github.com/meltano/meltano>meltano</a>, <a href=https://github.com/cloudquery/cloudquery>cloudquery</a>, <a href=https://github.com/redpanda-data/benthos>benthos</a>, <a href=https://github.com/ozontech/file.d>file.d</a>.</div>

# Usage

[Architecture overview](docs/overview.md).
```bash
foo@bar:~$ git clone https://github.com/makualiyev/aftafa.git
foo@bar:~$ cd aftafa
foo@bar:~$ python -m venv venv
foo@bar:~$ source venv/bin/acitvate
foo@bar:~$ python -m pip install -e .
foo@bar:~$ python -m pip install -r requirements.dev.txt
foo@bar:~$ python -m aftafa --version
```
You can check a working example of a pipeline moving data from email to a raw file [here](examples/email-to-rawfile/example.py).

# Development stack / ideas

* Current:
    * **OS**: Windows 10 / Ubuntu 22
    * **Text Editor, IDE**: Visual Studio Code / Vim
    * **Linters, type checkers and etc**: no idea (mypy, pylint)
    * **Database**: PostgreSQL 14 / PostgreSQL 15, duckdb
    * **Python libraries**: SQLAlchemy, pydantic, pandas, xlwings
    * **Development design**: I assume it can be called TDD
* Plans:
    * try implementing some functions in Go lang
    * Python libraries: [tenacity](https://github.com/jd/tenacity), [click](https://github.com/pallets/click), [structlog](https://github.com/hynek/structlog)
* Ideas:
    * Dev concerns
        * too many dependencies that cause bloating, `venv` folder weighs 375,7 Mb

# TODO list

- [ ] remove unused dependencies
  - [ ] remove xlwings
  - [ ] replace `click` with `argparse`
  - [ ] `gspread` maybe?
  - [ ] remove `jupyter` + `ipython`
- [ ] configuration file parser
- [ ] `DataSource` source class implementation, change naive `extract` method to return generators (yield data -> more efficient)
  - [ ] JSONDataSource -> JSONDataDestination is not working correctly, check it with supply_orders JSON file from OZON.
- [ ] implement logging and change all print statements
- [ ] add poetry to the project
- [ ] add schema resolver in `utils`. It'll help us with parsing the Swagger/OpenAPI documentation
- [ ] add test suite --- ```python -m unittest test\client\ozon\test_ozon_supplier.py```
- [ ] OData client -> write a parser for $metadata XML file for ec
