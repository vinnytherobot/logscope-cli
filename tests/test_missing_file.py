from typer.testing import CliRunner

from logscope.cli import app


runner = CliRunner()


def test_cli_missing_log_file_reports_clean_error():
    result = runner.invoke(app, ["no-such-file-xyz.log"])

    assert result.exit_code == 2
    assert "not found" in result.output.lower()
    assert "no-such-file-xyz.log" in result.output


def test_cli_directory_as_log_file_reports_clean_error(tmp_path):
    result = runner.invoke(app, [str(tmp_path)])

    assert result.exit_code == 2
    assert "error" in result.output.lower()
