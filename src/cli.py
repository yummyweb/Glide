import click

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

    with open(project_name + '.glide', 'w') as fp:
        fp.write(str(template))
    
if __name__ =="__main__":
    init()