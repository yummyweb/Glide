import click

@click.command()
@click.argument('project_name')
def init(project_name):
    """
    Creates a basic glide config file.
    """
    template = {
        "project_name": project_name
    } 

    with open(project_name + '.glide', 'w') as fp:
        fp.write(str(template))
    
if __name__ =="__main__":
    init()