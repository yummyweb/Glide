from click.testing import CliRunner
from src.cli import init

def TestInit():
    runner = CliRunner()
    result = runner.invoke(init, 'project')
    assert result.exit_code == 0
    assert result.output == ''

TestInit()