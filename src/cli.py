import click
import glob
import json
import sys
from tabulate import tabulate
from src.api import Api
from src.deployment import Deployment
from src.utils import err
from src.constants import CLOUD_PROVIDERS

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

    with open(project_name + '.glide.json', 'w') as f:
        f.write(json.dumps(template, indent=4))

@click.command()
@click.argument('directory')
def deploy(directory):
    """
    Deploys a directory to given cloud provider.
    """
    if not glob.glob("*.glide.json"):
        click.echo('\033[91m' + "ERROR: Glide file not found. Please run init command." + '\033[0m')
        sys.exit(1) 

    for file in glob.glob("*.glide.json"):
        with open(file, 'r') as f:
            glideJson = json.loads(f.read())

            if glideJson['project_name'] != f.name.replace('.glide.json', ''):
                err("ERROR: Project name does not match glide file name.")
                sys.exit(1)

            deployment = Deployment(glideJson['project_name'], directory)
            if glideJson['cloud_name'] == "netlify":
                deployment.deployToNetlify()

            elif glideJson['cloud_name'] == "vercel":
                deployment.deployToVercel()
            
            elif glideJson['cloud_name'] == "aws":
                deployment.deployToAWS()
            
            else:
                err("ERROR: Cloud name not specified in Glide file. Please add a value to 'cloud_name'.")

@click.command()
@click.argument('cloud')
def migrate(cloud):
    """
    Migrates current configuration to the given cloud provider.
    """
    if not glob.glob("*.glide.json"):
        err("ERROR: Glide file not found. Please run init command.")

    for file in glob.glob("*.glide.json"):
        # Read the glide file and close it
        with open(file, 'r+') as f:
            glideJson = json.loads(f.read())
            f.close()

        # Empty the contents of the file
        with open(file, 'r+') as f:
            f.close()

        with open(file, 'r+') as f:
            if glideJson['project_name'] != f.name.replace('.glide.json', ''):
                err("ERROR: Project name does not match glide file name.")
            
            if cloud not in CLOUD_PROVIDERS:
                err("ERROR: Given cloud provider is not recognised. Please provide a known cloud provider.")

            glideJson['cloud_name'] = cloud

            if cloud == "aws":
                if "region" not in glideJson:
                    glideJson['region'] = "us-east-1"
                
                if "access_secret" not in glideJson:
                    glideJson['access_secret'] = "<your_access_secret>"

            f.write(json.dumps(glideJson, indent=4))
            f.close()

@click.command()
def sites():
    """
    Shows all available user sites.
    """
    if not glob.glob("*.glide.json"):
        err("ERROR: Glide file not found. Please run init command.")

    for file in glob.glob("*.glide.json"):
        with open(file, 'rb') as f:
            glideJson = json.loads(f.read())

            api = Api(file.replace('.glide.json', ''))
            table = []
            if glideJson['cloud_name'] == "netlify":
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
cli.add_command(migrate)
cli.add_command(sites)

