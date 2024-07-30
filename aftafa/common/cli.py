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

@click.group(help="Aftafa helps you run pipelines in your environment.")
# @click.version_option(__version__)
# @click.pass_context(ctx)
def cli():
    pass

@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.secho(f'Hello {name}', fg='green')

@click.command(help="Run pipeline with source and destination or provide a config file with --config")
@click.option('--config', default=None, help='File with pipeline configuration')
@click.argument('source')
@click.argument('destination')
def run(source, destination, config):
    click.secho(f'Running pipeline from {source} to {destination}', fg='yellow')
    


@click.command()
def checklist():    
    click.secho(f"List of pipelines: ", bold=True, fg="cyan")
    for scr in list(Path(".").parent.parent.glob('*.py')):
        scr = scr.stem
        click.secho(scr, fg="cyan")


cli.add_command(hello)
cli.add_command(run)
cli.add_command(checklist)

def main():
    cli()


if __name__ == '__main__':
    cli()
