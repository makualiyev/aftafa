<h1 align="center">Overview of architecture</h1>

The main idea is that a library should do one thing and do it well, e. g. solve somewhat atomic problems, say input a `txt` file, read it properly and load it to a destination `json` file. If we incapsulate this one operation in a class, then we get the problem that could be done in bash by `pipe`s and redirecting `STDIN` to the destination `cat file.txt > cat.json`. The idea of modern data pipelines spins from this simple idea of redirecting input to output, but with extra steps in between as validating the input, processing it, maybe converting to an intermediate exchange format and then loading it to the destination. This library also is built upon this idea, and we want to make it a little bit more domain specific and we draw inspiration from these libraries/frameworks:
  * meltano (+ Singer SDK)
  * dlt
  * cloudquery
  * benthos (Redpanda connect)
  * file.d

To put it more into perspective, let's address our core architecture concerns:
  * now we have a model where an abstract *Resource* is given to a *Pipeline* , which then gets its *Loader* and loads it to a *Destination*
  * ```mermaid
        graph LR;
            Resource-->Pipeline;
            Pipeline-->Loader;
            Loader-->Destination;
      ```
    is it optimal for our use case or should we lean more towards a pluggable architecture as in cloudquery
    ```mermaid
        graph LR;
            Plugin-->id1(Source plugin);
            Plugin-->id2(Destination plugin);
            id1-->id3((Config));
            id2-->id4((Config));
            id3-->id5[Sync];
            id4-->id5[Sync];
            id5-.->id6[Transform];
    ```
    or is it optimal for our case to build it like an on fly processor as in benthos, where actually everything is also treated as a plugin
    ```mermaid
        graph LR;
            input-->stdin;
            stdin-->idp(pipeline);
            idp-->idpr[processors];
            idpr-->output;
            output-->stdout;
    ```

So we have to answer these questions first to define our architecture concepts, balance tradeoffs, tailor them to our specific domain needs:

* What are the main **sources** of data that we will be getting?
  * **type of data input**: is it streams of data or batches?
  * **source of data input**: (where do they come from) is it cloud providers (AWS, GCP, Azure), filesystem (Parquet, JSON, XML), HTTP resources (REST API), databases (PostgreSQL, duckdb, Clickhouse), Email mailing list attachments or emails (XLSX, EML), scraped data (HTML) or something else?
  * **type of connector**: do we want to reuse connector as in HTTP Session pool, Database Session pool, Iterator reader for files, IMAP socket? What is probable size of data and can it be allocated in memory or should we use disk?
  * **how to declare a source**: say we are declaring HTTP source, should we pass a custom HTTP client for each different REST API source or should we create a fully customazible abstract HTTP source class that can be tailored for specific REST API
  * **configure a source**: how to pass credentials for HTTP source, should we pass them by environment variables, should they be passed in config files?
  * **do we need an intermediary step**: should we get raw byte content from REST API methods and pass them to a `source` output or should we deal with something like `requests.Response` object and extract what is needed directly from that?

* What is the **intermediary step** of our pipeline?
  * **format**: what should be the interchange format/protocol, JSON, protobuf?
  * **runtime**: what else should our pipelines include? *state management*

* What is our user interface?
  * **more complex cli or complex configuration management**: is it good idea to take everything in command line such as source definitions with maybe tuned options, config file directories and so on or should all the configuration live in a separate config file? what about readability of commands in cli and which is easier to read `run source --state=./state.json --config=./sourceconf.json ... destination` or `run pipeline --config=config.yaml`? What we want to look here is to check main implementations of config files in different data libraries/frameworks like `dbt_project.yml`, `meltano.yml`, `plugin.yaml` (cloudquery) and etc. Here we analyze all the different [configuration details](config.md) to come up with a solution.
  * **one UI** is cli only interface for pipelines or can we write our own pipeline in a file as in `dlt`?

<h1 align="center">Implementation</h1>

We are going to build this library using **Bottom-Up** approach starting by a simple CLI command `run pipeline.yml` or `run yandexmail file --config=meta.json` in Example 1.
Should there also be a StreamSource?

