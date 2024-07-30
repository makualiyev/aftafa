<h1 align="center">
    <strong>🏺 aftafa</strong> data pipeline
</h1>
<p align="center">
Basic ETL pipeline for extracting and loading data from e-commerce (OZON, Wildberries, Yandex Market, etc.)
</p>

<sub>The project is under heavy development so many features are missing actually and its structure surely will be modified/refactored
and documented</sub>

## Overview
<div style="text-align: justify">This module can be helpful even if you're not trying to build a decent ETL pipeline, but rather want to fetch data from a marketplace API via a convenient client. But keep in mind that API methods provided in this module can only fetch data (not to confuse with HTTP methods) but can't change them in a way it is documented by a source vendor (e. g. for marketplaces it means: change prices, add new products, refresh dropshipping stocks and etc). Inspired by <a href=https://github.com/dlt-hub/dlt>dlt</a>, <a href=https://github.com/meltano/meltano>meltano</a>, <a href=https://github.com/cloudquery/cloudquery>cloudquery</a>.</div>

## Usage

```bash
foo@bar:~$ git clone https://github.com/makualiyev/aftafa.git
foo@bar:~$ cd aftafa
foo@bar:~$ python -m aftafa --version
...
```

## Prerequisites

`env` folder inside the module (`aftafa`) with `conf` file containing database URL. Soon it will be changed to `config.yaml` file for convenience.
* environment:
    *   project_folder: ?
    *   database_url: "{databasedriver}://{user}:{password}@{host}:{port}/{database}"
    *   meta_folder: "E:\\shoptalk\\local_\\meta"
    *   mail_output_folder: "E:\\shoptalk\\localpipeline_\\email"


# TO DO LIST

- [✓] add schema resolver in `utils`. It'll help us with parsing the Swagger/OpenAPI documentation
- [✓] add test suite --- ```python -m unittest test\client\ozon\test_ozon_supplier.py```
- [x] add `resource` class (ref: dlt-hub)
  - [x] JSONResource -> JSONLoader is not working correctly, check it with supply_orders JSON file from OZON.
- [x] add `mail_manager` into client.email [INPROCESS]
    - [x] implement client mail to email resource
- [x] OData client -> write a parser for $metadata XML file for ec

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
