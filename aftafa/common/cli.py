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

@click.group(
        help="Aftafa helps you run pipelines in your environment.",
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
def run(source, destination, config):
    click.secho(f'Running pipeline from {source} to {destination}', fg='yellow')
    if config:
        click.secho(f'Using config file -> ', fg='yellow')


@click.command(help="Lists all available pipelines (.py files in dir)")
def checklist():    
    click.secho(f"List of pipelines: ", bold=True, fg="cyan")
    for scr in list(Path(".").parent.parent.glob('*.py')):
        scr = scr.stem
        click.secho(scr, fg="cyan")


cli.add_command(run)
cli.add_command(checklist)

def main():
    cli()


if __name__ == '__main__':
    cli()
