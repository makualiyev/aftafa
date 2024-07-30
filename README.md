<h1 align="center">
    <strong>🏺 aftafa</strong> data pipeline
</h1>
<p align="center">
Basic ETL pipeline for extracting and loading data from e-commerce (OZON, Wildberries, Yandex Market, etc.)</p>

<p align="center">⚠️ This project is under <strong>heavy development</strong> and yet to be a usable library, so many features are missing actually and its structure surely will be modified/refactored and documented</p>

# Overview
<div style="text-align: justify">This module can be helpful even if you're not trying to build a decent ETL pipeline, but rather want to fetch data from a marketplace API via a convenient client. But keep in mind that API methods provided in this module can only fetch data (not to confuse with HTTP methods) but can't change them in a way it is documented by a source vendor (e. g. for marketplaces it means: change prices, add new products, refresh dropshipping stocks and etc). Inspired by <a href=https://github.com/dlt-hub/dlt>dlt</a>, <a href=https://github.com/meltano/meltano>meltano</a>, <a href=https://github.com/cloudquery/cloudquery>cloudquery</a>.</div>

# Usage

```bash
foo@bar:~$ git clone https://github.com/makualiyev/aftafa.git
foo@bar:~$ cd aftafa
foo@bar:~$ python -m venv venv
foo@bar:~$ source venv/bin/acitvate
foo@bar:~$ python -m pip install -e .
foo@bar:~$ python -m pip install -r requirements.dev.txt
foo@bar:~$ python -m aftafa --version
```

# Development stack / ideas

* Current:
    * OS: Windows 10 / Ubuntu 22
    * IDE: Visual Studio Code / Vim
    * Linters, type checkers and etc.: no idea (mypy, pylint)
    * Database: PostgreSQL 14 / PostgreSQL 15, duckdb
    * Python libraries: SQLAlchemy, pydantic, pandas, xlwings
* Plans:
    * try implementing some functions in Go lang
    * Python libraries: [tenacity](https://github.com/jd/tenacity), [click](https://github.com/pallets/click), [structlog](https://github.com/hynek/structlog)
* Ideas:
    * Core architecture concerns
        * now we have a model where an abstract *Resource* is given to a *Pipeline* , which then gets its *Loader* and loads it to a *Destination*
        ```mermaid
            graph LR;
                Resource-->Pipeline;
                Pipeline-->Loader;
                Loader-->Destination;
        ```
        is it optimal for our use case or should we lean more towards a pluggable architecture as in cloudquery?
        * What should be the interchange format/protocol, JSON, protobuf?
        * What else should our pipelines include? *state management*
    * Dev concerns
        * too many dependencies that cause bloating, `venv` folder weighs 375,7 Mb

# TODO list

- [ ] remove unused dependencies
  - [ ] remove xlwings
  - [ ] replace `click` with `argparse`
  - [ ] `gspread` maybe?
  - [ ] remove `jupyter` + `ipython`
- [x] add `resource` class (ref: dlt-hub)
  - [ ] JSONResource -> JSONLoader is not working correctly, check it with supply_orders JSON file from OZON.
- [x] add `mail_manager` into client.email [INPROCESS]
    - [x] implement client mail to email resource
- [ ] implement logging and change all print statements
- [ ] add poetry to the project
- [ ] add schema resolver in `utils`. It'll help us with parsing the Swagger/OpenAPI documentation
- [ ] add test suite --- ```python -m unittest test\client\ozon\test_ozon_supplier.py```
- [ ] OData client -> write a parser for $metadata XML file for ec
