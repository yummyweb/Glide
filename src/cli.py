import click
import glob
import json
from tabulate import tabulate
from src.api import Api
from src.deployment import Deployment

@click.command()
@click.argument('project_name')
def init(project_name):
    """
    Creates a basic glide config file.
    """
    template = {
        "project_name": project_name,
        "cloud_name": "",
        "client_id": "",
        "client_secret": "",
        "access_token": ""
    }

    with open(project_name + '.glide.json', 'w') as fp:
        fp.write(json.dumps(template, indent=4))

@click.command()
@click.argument('directory')
def deploy(directory):
    """
    Creates a basic glide config file.
    """
    for file in glob.glob("*.glide.json"):
        with open(file, 'rb') as f:
            deployment = Deployment(file.replace('.glide.json', ''), directory)
            if eval(f.read())['cloud_name'] == "netlify":
                deployment.deployToNetlify()

@click.command()
def sites():
    """
    Shows all available user sites.
    """
    for file in glob.glob("*.glide.json"):
        with open(file, 'rb') as f:
            api = Api(file.replace('.glide.json', ''))
            table = []
            for site in api.getSites():
                table.append([site['id'], site['name'], site['url']])
            
            click.echo(tabulate(table, headers=['Site ID', 'Site Name', 'Site URL'], tablefmt="psql"))

@click.group()
@click.version_option()
def cli():
    pass

cli.add_command(init)
cli.add_command(deploy)
cli.add_command(sites)


if __name__ =="__main__":
    cli()