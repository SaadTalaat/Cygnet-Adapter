
from click.testing import CliRunner

from cygnet_adapter.__main__ import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    #assert result.output == '()\n'
    #assert result.exit_code == 0
