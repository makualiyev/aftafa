# Pipeline configuration

So here are the examples of different ELT libraries' configs.
## Meltano
```yaml
env:
    # root level env
    MY_ENV_VAR: top_level_env_var
plugins:
    extractors:
    - name: tap-google-analytics
    variant: meltano
    env:
        # root level plugin env
        MY_ENV_VAR: plugin_level_env_var
    loaders:
    - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
environments:
- name: dev
    env:
    # environment level env
    MY_ENV_VAR: environment_level_env_var
    config:
    plugins:
        extractors:
        - name: tap-google-analytics
            variant: meltano
            env:
            # environment level plugin env
            MY_ENV_VAR: environment_level_plugin_env_var
schedules:
- name: daily-google-analytics-load
    interval: '@daily'
    extractor: tap-google-analytics
    loader: target-postgres
    transform: skip
    start_date: 2024-08-24 00:00:00
    env:
    SCHEDULE_SPECIFIC_ENV_VAR: schedule_specific_value
```


## benthos
```yaml
input:
  type: amqp
  amqp:
    url: amqp://guest:guest@localhost:5672/
    consumer_tag: benthos-consumer
    exchange: benthos-exchange
    exchange_type: direct
    key: benthos-key
    prefetch_count: 10
    prefetch_size: 0
    queue: benthos-queue
output:
  type: stdout
```


## cloudquery
```yaml
kind: source
spec:
  name: aws
  path: cloudquery/aws
  registry: cloudquery
  version: "v27.11.1"
  tables: ["aws_s3_buckets"]
  destinations: ["postgresql"]
---
kind: destination
spec:
  name: postgresql
  path: cloudquery/postgresql
  registry: cloudquery
  version: "v8.3.1"
  spec:
    connection_string: ${PG_CONNECTION_STRING}
```