"""
CLI module for `aftafa`. Ideally, the entry
point for our application. Main commands it
has:
* run
* test
* list
////////////////////////////////////////////
"""
from pathlib import Path

import click

from aftafa.common.pipeline import Pipeline, PipelineConfig


@click.group(
        help="aftafa helps you run pipelines in your environment.",
        no_args_is_help=True,
        invoke_without_command=True
)
@click.version_option(prog_name="aftafa", package_name="aftafa")
@click.pass_context
def cli(ctx: click.Context):
    pass


@click.command(help="Run pipeline with source and destination or provide a config file with \
               --config. For now it can support only raw pipelining, tbi.",
               no_args_is_help=True)
@click.option('--config', default=None, help='File with pipeline configuration')
@click.argument('source')
@click.argument('destination')
def run(
    source: str,
    destination: str,
    config: str
):
    click.secho(f'Running pipeline from {source} to {destination} using config file {config}', fg='yellow')
    pipe_cfg = PipelineConfig(config)
    p = Pipeline(pipeline_name=f'{source}-to-{destination}', pipeline_config=pipe_cfg)
    p.run(naive=True)
    click.secho(f'Pipeline {p.name} ran successfully!', fg='yellow')


@click.command(help="Test pipeline with source and destination or provide a config file with \
               --config.",
               no_args_is_help=True)
@click.option('--config', default=None, help='File with pipeline configuration')
@click.argument('source')
@click.argument('destination')
def test(
    source: str,
    destination: str,
    config: str
):
    click.secho(f'Testing pipeline from {source} to {destination} using config file {config}', fg='yellow')


@click.command(help="Lists all available pipelines (.py files in dir)")
def checklist():    
    click.secho(f"List of pipelines: ", bold=True, fg="cyan")
    for scr in list(Path(".").parent.parent.glob('*.py')):
        scr = scr.stem
        click.secho(scr, fg="cyan")


cli.add_command(run)
cli.add_command(test)
cli.add_command(checklist)


if __name__ == '__main__':
    pass
