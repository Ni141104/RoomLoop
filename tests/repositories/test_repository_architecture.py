from pathlib import Path


REPOSITORY_DIR = Path("app/repositories")


def test_repositories_do_not_commit_transactions():
    for repository_file in REPOSITORY_DIR.glob("*.py"):

        source = repository_file.read_text()

        assert ".commit(" not in source
        assert ".rollback(" not in source


def test_repositories_do_not_import_fastapi():
    for repository_file in REPOSITORY_DIR.glob("*.py"):

        source = repository_file.read_text()

        assert "fastapi" not in source.lower()


def test_repositories_do_not_raise_http_exceptions():
    for repository_file in REPOSITORY_DIR.glob("*.py"):

        source = repository_file.read_text()

        assert "HTTPException" not in source