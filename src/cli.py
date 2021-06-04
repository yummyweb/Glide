import click
import glob
import json
import sys
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
        "access_secret": "",
        "access_token": ""
    }

    with open(project_name + '.glide.json', 'w') as fp:
        fp.write(json.dumps(template, indent=4))

@click.command()
@click.argument('directory')
def deploy(directory):
    """
    Deploys a directory to given cloud provider.
    """
    for file in glob.glob("*.glide.json"):
        with open(file, 'r') as f:
            glideJson = json.loads(f.read())

            if glideJson['project_name'] != f.name.replace('.glide.json', ''):
                print('\033[91m' + "ERROR: Glide file does not exist. Please run init command." + '\033[0m')
                sys.exit(1)

            deployment = Deployment(glideJson['project_name'], directory)
            if glideJson['cloud_name'] == "netlify":
                deployment.deployToNetlify()

            elif glideJson['cloud_name'] == "vercel":
                deployment.deployToVercel()
            
            else:
                deployment.deployToAWS()

@click.command()
def sites():
    """
    Shows all available user sites.
    """
    if not glob.glob("*.glide.json"):
        click.echo('\033[91m' + "ERROR: Glide file not found. Please run init command." + '\033[0m')
        sys.exit(1)

    for file in glob.glob("*.glide.json"):
        with open(file, 'rb') as f:
            api = Api(file.replace('.glide.json', ''))
            table = []
            if eval(f.read())['cloud_name'] == "netlify":
                for site in api.getSites():
                    table.append([site['id'], site['name'], site['url']])

            else:
                for deployment in api.getDeployments()['deployments']:
                    table.append([deployment['uid'], deployment['name'], deployment['url']])
            
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