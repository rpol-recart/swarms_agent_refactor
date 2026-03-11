"""Tests for refactoring_agent module."""

import os
import json
import tempfile
import pytest

from refactoring_agent import (
    AgentRole,
    CodeArtifact,
    RefactoringProposal,
    ProjectContext,
    DatabaseTools,
    read_file,
    write_file,
    list_directory,
    search_code,
    analyze_python_file,
    check_syntax,
    create_agent,
    DEFAULT_MODEL_MAP,
    SYSTEM_PROMPTS,
    ROLE_TOOLS,
)


# ── Data classes ─────────────────────────────────────────────


class TestCodeArtifact:
    def test_creation(self):
        a = CodeArtifact(file_path="x.py", content="code", language="python")
        assert a.version == 1
        assert a.dependencies == []

    def test_to_dict_truncates_long_content(self):
        long = "x" * 600
        a = CodeArtifact(file_path="x.py", content=long, language="python")
        d = a.to_dict()
        assert d["content"].endswith("...")
        assert len(d["content"]) < 600

    def test_to_dict_short_content(self):
        a = CodeArtifact(file_path="x.py", content="short", language="python")
        d = a.to_dict()
        assert d["content"] == "short"


class TestProjectContext:
    def test_add_rule(self):
        ctx = ProjectContext(root_path="/tmp")
        ctx.add_rule("rule1")
        ctx.add_rule("rule2")
        assert len(ctx.rules) == 2

    def test_summary(self):
        ctx = ProjectContext(root_path="/tmp")
        ctx.python_files = ["a.py", "b.py"]
        summary = ctx.get_context_summary()
        assert "Python файлов: 2" in summary


class TestRefactoringProposal:
    def test_defaults(self):
        p = RefactoringProposal(
            id="REF-001",
            agent_role=AgentRole.CODER,
            description="test",
            affected_files=["a.py"],
            changes=[],
            rationale="reason",
            risks=["risk1"],
        )
        assert p.tests_required is True
        assert p.approved is None


# ── Tool functions ───────────────────────────────────────────


class TestReadFile:
    def test_read_existing(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world", encoding="utf-8")
        assert read_file(str(f)) == "hello world"

    def test_read_nonexistent(self):
        result = read_file("/nonexistent/path/file.txt")
        assert "Ошибка" in result


class TestWriteFile:
    def test_write_new_file(self, tmp_path):
        path = str(tmp_path / "out.txt")
        result = write_file(path, "content", backup=False)
        assert "успешно" in result
        assert open(path).read() == "content"

    def test_write_with_backup(self, tmp_path):
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("original")
        write_file(path, "updated", backup=True)
        assert open(path).read() == "updated"
        # Backup file should exist
        backups = [f for f in os.listdir(tmp_path) if "backup" in f]
        assert len(backups) == 1

    def test_write_creates_dirs(self, tmp_path):
        path = str(tmp_path / "sub" / "dir" / "file.txt")
        write_file(path, "nested", backup=False)
        assert open(path).read() == "nested"


class TestListDirectory:
    def test_lists_files(self, tmp_path):
        (tmp_path / "a.py").touch()
        (tmp_path / "b.txt").touch()
        result = list_directory(str(tmp_path))
        assert "a.py" in result
        assert "b.txt" in result


class TestCheckSyntax:
    def test_valid(self):
        assert check_syntax("x = 1") == "Синтаксис корректен"

    def test_invalid(self):
        result = check_syntax("def (")
        assert "ошибка" in result.lower()


class TestAnalyzePythonFile:
    def test_analyze(self, tmp_path):
        src = tmp_path / "sample.py"
        src.write_text(
            "import os\n\ndef foo(x: int) -> int:\n    return x + 1\n",
            encoding="utf-8",
        )
        result = analyze_python_file(str(src))
        data = json.loads(result)
        assert any("os" in imp for imp in data["imports"])
        assert any(f["name"] == "foo" for f in data["functions"])

    def test_analyze_nonexistent(self):
        result = analyze_python_file("/nonexistent.py")
        assert "Ошибка" in result


# ── DatabaseTools ────────────────────────────────────────────


class TestDatabaseTools:
    def test_no_connection(self):
        db = DatabaseTools()
        assert "Не настроено" in db.execute_query("SELECT 1")
        assert "Не настроено" in db.get_schema_info()

    def test_sql_injection_guard(self):
        db = DatabaseTools("sqlite:///:memory:")
        assert "ОТКАЗАНО" in db.execute_query("DROP TABLE users")
        assert "ОТКАЗАНО" in db.execute_query("DELETE FROM users")
        assert "ОТКАЗАНО" in db.execute_query("INSERT INTO t VALUES (1)")
        assert "ОТКАЗАНО" in db.execute_query("UPDATE t SET x=1")

    def test_schema_info_empty_db(self):
        db = DatabaseTools("sqlite:///:memory:")
        result = db.get_schema_info()
        assert "Таблицы в БД (0)" in result


# ── Agent creation ───────────────────────────────────────────


class TestCreateAgent:
    def test_creates_file_manager(self):
        agent = create_agent(AgentRole.FILE_MANAGER)
        assert agent.agent_name == "FileManager"
        assert len(agent.tools) == 4

    def test_creates_sql_analyst_with_db(self):
        db = DatabaseTools("sqlite:///:memory:")
        agent = create_agent(AgentRole.SQL_ANALYST, db_tools=db)
        assert len(agent.tools) == 4  # read_file, search_code + 2 db tools

    def test_creates_sql_analyst_without_db(self):
        agent = create_agent(AgentRole.SQL_ANALYST)
        assert len(agent.tools) == 2  # just read_file, search_code

    def test_all_roles_have_prompts(self):
        for role in SYSTEM_PROMPTS:
            assert len(SYSTEM_PROMPTS[role]) > 50

    def test_all_roles_have_tools(self):
        for role in ROLE_TOOLS:
            assert len(ROLE_TOOLS[role]) >= 2


# ── AgentRole enum ───────────────────────────────────────────


class TestAgentRole:
    def test_all_values(self):
        values = {r.value for r in AgentRole}
        assert "orchestrator" in values
        assert "coder" in values
        assert "sql_analyst" in values
