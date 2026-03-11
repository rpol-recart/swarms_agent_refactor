"""
Мультиагентная система для рефакторинга кода на базе Swarms Framework
Версия: 1.0.0

Архитектура:
    Orchestrator -> FileManager, Coder, Tester, Debugger, SQLAnalyst, Reviewer, Documenter

Каждый агент имеет свои инструменты (tools) и специализацию.
Все операции записи требуют подтверждения пользователя.
SQL-агент работает строго в режиме read-only.
"""

import os
import json
import subprocess
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import shutil
import logging

# Swarms Framework imports
from swarms import Agent

# Для работы с БД (опционально)
try:
    from sqlalchemy import create_engine, text, inspect as sa_inspect
    from sqlalchemy.engine import Engine

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    Engine = None  # type: ignore[assignment,misc]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("refactoring_agent")


# =============================================================================
# КОНФИГУРАЦИЯ И ТИПЫ ДАННЫХ
# =============================================================================


class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    FILE_MANAGER = "file_manager"
    CODER = "coder"
    TESTER = "tester"
    DEBUGGER = "debugger"
    SQL_ANALYST = "sql_analyst"
    REVIEWER = "reviewer"
    DOCUMENTER = "documenter"


@dataclass
class CodeArtifact:
    """Артефакт кода для передачи между агентами."""

    file_path: str
    content: str
    language: str
    dependencies: List[str] = field(default_factory=list)
    ast_tree: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "content": (
                self.content[:500] + "..."
                if len(self.content) > 500
                else self.content
            ),
            "language": self.language,
            "dependencies": self.dependencies,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass
class RefactoringProposal:
    """Предложение по рефакторингу."""

    id: str
    agent_role: AgentRole
    description: str
    affected_files: List[str]
    changes: List[Dict[str, Any]]
    rationale: str
    risks: List[str]
    tests_required: bool = True
    approved: Optional[bool] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProjectContext:
    """Контекст проекта для агентов."""

    root_path: str
    python_files: List[str] = field(default_factory=list)
    sql_files: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    database_schema: Dict[str, Any] = field(default_factory=dict)
    architecture_graph: Dict[str, List[str]] = field(default_factory=dict)
    rules: List[str] = field(default_factory=list)

    def add_rule(self, rule: str) -> None:
        self.rules.append(rule)

    def get_context_summary(self) -> str:
        return (
            f"Проект: {self.root_path}\n"
            f"Python файлов: {len(self.python_files)}\n"
            f"SQL файлов: {len(self.sql_files)}\n"
            f"Зависимостей: {len(self.dependencies)}\n"
            f"Правил: {len(self.rules)}"
        )


# =============================================================================
# ИНСТРУМЕНТЫ ДЛЯ АГЕНТОВ (обычные функции — swarms принимает List[Callable])
# =============================================================================


def read_file(file_path: str) -> str:
    """Читает содержимое файла.

    Args:
        file_path: Путь к файлу.

    Returns:
        Содержимое файла или сообщение об ошибке.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Ошибка чтения файла: {e}"


def write_file(file_path: str, content: str, backup: bool = True) -> str:
    """Записывает содержимое в файл с опциональным бэкапом.

    Args:
        file_path: Путь к файлу.
        content: Содержимое для записи.
        backup: Создать ли резервную копию.

    Returns:
        Результат операции.
    """
    try:
        if backup and os.path.exists(file_path):
            backup_path = (
                f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(file_path, backup_path)

        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Файл {file_path} успешно записан"
    except Exception as e:
        return f"Ошибка записи файла: {e}"


def list_directory(dir_path: str = ".") -> str:
    """Выводит структуру директории в виде дерева.

    Args:
        dir_path: Путь к директории.

    Returns:
        Строковое представление дерева файлов.
    """
    try:
        result: List[str] = []
        for root, dirs, files in os.walk(dir_path):
            # Пропускаем скрытые директории и __pycache__
            dirs[:] = [
                d for d in dirs if not d.startswith(".") and d != "__pycache__"
            ]
            level = root.replace(dir_path, "").count(os.sep)
            indent = "  " * level
            result.append(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                result.append(f"{subindent}{file}")
        return "\n".join(result)
    except Exception as e:
        return f"Ошибка: {e}"


def search_code(pattern: str, file_extension: str = ".py") -> str:
    """Поиск по кодовой базе с использованием регулярных выражений.

    Args:
        pattern: Регулярное выражение для поиска.
        file_extension: Расширение файлов для поиска.

    Returns:
        Найденные совпадения с номерами строк.
    """
    matches: List[str] = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for i, line in enumerate(content.split("\n"), 1):
                            if re.search(pattern, line):
                                matches.append(
                                    f"{file_path}:{i}: {line.strip()}"
                                )
                except (OSError, UnicodeDecodeError):
                    continue
    return "\n".join(matches[:50]) if matches else "Совпадений не найдено"


def analyze_python_file(file_path: str) -> str:
    """Анализирует Python файл с помощью AST.

    Args:
        file_path: Путь к Python файлу.

    Returns:
        JSON с информацией о структуре файла (классы, функции, импорты).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        analysis: Dict[str, Any] = {
            "imports": [],
            "classes": [],
            "functions": [],
        }

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                analysis["imports"].append(ast.unparse(node))
            elif isinstance(node, ast.ClassDef):
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                analysis["classes"].append(
                    {
                        "name": node.name,
                        "methods": methods,
                        "bases": [ast.unparse(base) for base in node.bases],
                    }
                )
            elif isinstance(node, ast.FunctionDef):
                end = getattr(node, "end_lineno", None)
                analysis["functions"].append(
                    {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line_count": (end - node.lineno) if end else 0,
                    }
                )

        return json.dumps(analysis, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Ошибка анализа: {e}"


def run_tests(test_path: str = ".", verbose: bool = True) -> str:
    """Запускает pytest для указанного пути.

    Args:
        test_path: Путь к тестам или файлу.
        verbose: Подробный вывод.

    Returns:
        Результат выполнения тестов.
    """
    try:
        cmd = ["pytest", test_path]
        if verbose:
            cmd.append("-v")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return (
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}\n\n"
            f"Return code: {result.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "Тесты превысили лимит времени (120 сек)"
    except Exception as e:
        return f"Ошибка запуска тестов: {e}"


def run_linter(file_path: str, linter: str = "pylint") -> str:
    """Запускает линтер для проверки качества кода.

    Args:
        file_path: Путь к файлу.
        linter: Название линтера (pylint, flake8, black, mypy).

    Returns:
        Результат проверки.
    """
    linter_commands: Dict[str, List[str]] = {
        "pylint": ["pylint", file_path, "--output-format=json"],
        "flake8": ["flake8", file_path, "--max-line-length=100"],
        "black": ["black", "--check", "--diff", file_path],
        "mypy": ["mypy", file_path],
    }
    cmd = linter_commands.get(linter)
    if cmd is None:
        return f"Неизвестный линтер: {linter}"
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr or "Проверка завершена без замечаний"
    except Exception as e:
        return f"Ошибка запуска линтера: {e}"


def check_syntax(code: str) -> str:
    """Проверяет синтаксис Python кода.

    Args:
        code: Python код для проверки.

    Returns:
        Результат проверки синтаксиса.
    """
    try:
        ast.parse(code)
        return "Синтаксис корректен"
    except SyntaxError as e:
        return (
            f"Синтаксическая ошибка: {e.msg} "
            f"(строка {e.lineno}, колонка {e.offset})"
        )


def install_dependency(package_name: str, version: Optional[str] = None) -> str:
    """Устанавливает Python пакет.

    Args:
        package_name: Название пакета.
        version: Версия пакета (опционально).

    Returns:
        Результат установки.
    """
    try:
        pkg = f"{package_name}=={version}" if version else package_name
        result = subprocess.run(
            ["pip", "install", pkg],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return f"Установка {pkg}:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        return f"Ошибка установки: {e}"


# =============================================================================
# ИНСТРУМЕНТЫ ДЛЯ РАБОТЫ С БД (только чтение)
# =============================================================================


class DatabaseTools:
    """Инструменты для работы с БД (только чтение)."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        self._engine: Optional[Any] = None

    def _get_engine(self) -> Optional[Any]:
        if not HAS_SQLALCHEMY:
            return None
        if self._engine is None and self.connection_string:
            self._engine = create_engine(self.connection_string, echo=False)
        return self._engine

    def execute_query(self, query: str, limit: int = 100) -> str:
        """Выполняет SQL запрос ТОЛЬКО ДЛЯ ЧТЕНИЯ.

        Args:
            query: SQL запрос (SELECT только).
            limit: Лимит строк.

        Returns:
            Результат запроса.
        """
        if not HAS_SQLALCHEMY:
            return "SQLAlchemy не установлена"

        forbidden_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "TRUNCATE",
            "MERGE",
        ]
        query_upper = query.upper()

        for keyword in forbidden_keywords:
            if keyword in query_upper:
                return (
                    f"ОТКАЗАНО: Обнаружена запрещенная операция '{keyword}'. "
                    "Только SELECT разрешен."
                )

        try:
            engine = self._get_engine()
            if not engine:
                return "Не настроено подключение к БД"

            with engine.connect() as conn:
                if "LIMIT" not in query_upper and "ROWNUM" not in query_upper:
                    query = f"SELECT * FROM ({query}) sub_q LIMIT {limit}"

                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = list(result.keys())

                output: List[str] = []
                output.append(" | ".join(columns))
                output.append("-" * 50)
                for row in rows[:limit]:
                    output.append(" | ".join(str(cell) for cell in row))

                return "\n".join(output)
        except Exception as e:
            return f"Ошибка выполнения запроса: {e}"

    def get_schema_info(self, table_name: Optional[str] = None) -> str:
        """Получает информацию о схеме БД.

        Args:
            table_name: Имя таблицы (если None — список всех таблиц).

        Returns:
            Информация о схеме.
        """
        if not HAS_SQLALCHEMY:
            return "SQLAlchemy не установлена"

        try:
            engine = self._get_engine()
            if not engine:
                return "Не настроено подключение к БД"

            inspector = sa_inspect(engine)

            if table_name:
                columns = inspector.get_columns(table_name)
                pk = inspector.get_pk_constraint(table_name)
                fk = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)

                info = {
                    "table": table_name,
                    "columns": [
                        {k: str(v) for k, v in col.items()} for col in columns
                    ],
                    "primary_key": pk,
                    "foreign_keys": fk,
                    "indexes": indexes,
                }
                return json.dumps(info, indent=2, ensure_ascii=False)
            else:
                tables = inspector.get_table_names()
                return (
                    f"Таблицы в БД ({len(tables)}):\n" + "\n".join(tables)
                )
        except Exception as e:
            return f"Ошибка получения схемы: {e}"


# =============================================================================
# ФАБРИКА АГЕНТОВ
# =============================================================================

# Модели по умолчанию для каждой роли
DEFAULT_MODEL_MAP: Dict[str, str] = {
    "orchestrator": "gpt-4.1",
    "file_manager": "gpt-4.1-mini",
    "coder": "gpt-4.1",
    "tester": "gpt-4.1-mini",
    "debugger": "gpt-4.1",
    "sql_analyst": "gpt-4.1-mini",
    "reviewer": "gpt-4.1",
    "documenter": "gpt-4.1-mini",
}

# Системные промпты для каждой роли
SYSTEM_PROMPTS: Dict[AgentRole, str] = {
    AgentRole.FILE_MANAGER: """Вы - FileManager агент. Ваша задача - исследовать кодовую базу проекта.

Обязанности:
1. Анализ структуры директорий и файлов
2. Поиск кода по шаблонам и зависимостям
3. Построение карты зависимостей между модулями
4. Анализ AST Python файлов для понимания структуры
5. Выявление циклических импортов и архитектурных проблем

Правила работы:
- Всегда начинайте с обзора структуры проекта
- Используйте AST анализ для понимания связей
- Создавайте индекс файлов и их зависимостей
- Отмечайте файлы с высокой цикломатической сложностью

При анализе учитывайте:
- FastAPI роутеры и зависимости
- SQLAlchemy модели и миграции
- Конфигурационные файлы
- Тестовые файлы""",
    AgentRole.CODER: """Вы - Coder агент. Ваша задача - рефакторинг и написание Python кода.

Ключевые навыки:
- FastAPI: роутеры, зависимости, middleware, Pydantic модели
- SQLAlchemy: ORM, миграции Alembic, оптимизация запросов
- Асинхронное программирование (async/await)
- Чистая архитектура, SOLID принципы
- Типизация (type hints)

Правила рефакторинга:
1. Сохраняйте поведение кода (backward compatibility)
2. Добавляйте type hints ко всем функциям
3. Используйте Pydantic v2 для валидации
4. Оптимизируйте SQLAlchemy запросы (selectinload, lazy/eager loading)
5. Разделяйте бизнес-логику от инфраструктуры
6. Используйте Dependency Injection для FastAPI

Запрещено:
- Менять поведение без согласования
- Удалять тесты без замены
- Игнорировать обработку ошибок

Всегда предоставляйте полный код измененных файлов.""",
    AgentRole.TESTER: """Вы - Tester агент. Ваша задача - обеспечение качества через тестирование.

Обязанности:
1. Написание unit-тестов (pytest)
2. Интеграционное тестирование API (FastAPI TestClient)
3. Тестирование SQLAlchemy моделей (in-memory SQLite)
4. Покрытие кода (coverage)
5. Property-based testing (hypothesis)

Стандарты тестов:
- Используйте pytest fixtures для зависимостей
- Мокируйте внешние сервисы (unittest.mock)
- Тестируйте граничные случаи и ошибки
- Используйте параметризацию для множества сценариев
- Покрытие не менее 80% для нового кода

Структура теста:
    def test_function_name_scenario():
        # Arrange
        # Act
        # Assert

Всегда запускайте тесты перед отправкой!""",
    AgentRole.DEBUGGER: """Вы - Debugger агент. Эксперт по поиску и устранению ошибок.

Методологии отладки:
1. Репродукция ошибки
2. Бинарный поиск по коду (comment out)
3. Логирование состояния (breakpoint debugging)
4. Анализ stack trace
5. Проверка гонок данных (race conditions)

Типичные проблемы FastAPI/SQLAlchemy:
- Сессии БД без правильного закрытия
- Циклические импорты
- Неправильное использование async/await
- N+1 проблема в SQLAlchemy
- Утечки памяти в генераторах

Стратегия:
1. Локализуйте проблему (модуль/функция)
2. Определите входные данные, вызывающие ошибку
3. Проверьте предусловия и постусловия
4. Исправьте корневую причину, не симптом
5. Добавьте регрессионный тест""",
    AgentRole.SQL_ANALYST: """Вы - SQLAnalyst агент. Эксперт по SQL и SQLAlchemy.

Компетенции:
- Оптимизация SQL запросов (execution plan)
- Индексы (B-tree, bitmap, composite)
- SQLAlchemy Core и ORM оптимизации
- Партиционирование таблиц
- Аналитические функции (Window functions)

Задачи:
1. Ревью SQL запросов на производительность
2. Рекомендации по индексам
3. Оптимизация JOIN операций
4. Конвертация сложных SQL в SQLAlchemy
5. Анализ медленных запросов

ВАЖНО: Только чтение из БД! Запрещены модификации данных.

Best Practices:
- Используйте EXPLAIN PLAN для анализа
- Избегайте SELECT *
- Используйте bind variables
- Рассмотрите materialized views для сложных агрегаций""",
    AgentRole.REVIEWER: """Вы - Reviewer агент. Критическая оценка кода и архитектуры.

Аспекты ревью:
1. Архитектура: SOLID, DRY, KISS, YAGNI
2. Безопасность: SQL injection, XSS, CSRF
3. Производительность: алгоритмическая сложность, I/O
4. Читаемость: именование, комментарии, структура
5. Тестируемость: зависимости, побочные эффекты
6. FastAPI: правильность статус-кодов, валидация
7. SQLAlchemy: утечки сессий, N+1, транзакции

Шкала оценки:
- КРИТИЧНО: Баги, уязвимости, ошибки логики
- ВАЖНО: Производительность, maintainability
- РЕКОМЕНДАЦИЯ: Стиль, оптимизации

Чеклист:
- Обработка исключений
- Логирование ошибок
- Валидация входных данных
- Типизация
- Документация сложных мест
- Тесты на граничные случаи

Выводите структурированный отчет с приоритетами.""",
    AgentRole.DOCUMENTER: """Вы - Documenter агент. Создание технической документации.

Типы документации:
1. README.md - обзор проекта, установка, запуск
2. API docs - OpenAPI/Swagger описания (FastAPI auto)
3. Architecture Decision Records (ADR)
4. Docstrings (Google style)
5. Диаграммы архитектуры (Mermaid)
6. CHANGELOG.md

Стандарт docstring:
    def function_name(param: type) -> return_type:
        \"\"\"Краткое описание.

        Args:
            param: Описание параметра.

        Returns:
            Описание возвращаемого значения.

        Raises:
            ExceptionType: Когда вызывается.
        \"\"\"

Требования:
- Документируйте публичные API
- Описывайте бизнес-логику
- Включайте примеры использования
- Обновляйте документацию при изменениях""",
}

# Инструменты для каждой роли
ROLE_TOOLS: Dict[AgentRole, List[Callable]] = {
    AgentRole.FILE_MANAGER: [
        read_file,
        list_directory,
        search_code,
        analyze_python_file,
    ],
    AgentRole.CODER: [read_file, write_file, check_syntax],
    AgentRole.TESTER: [read_file, write_file, run_tests, check_syntax],
    AgentRole.DEBUGGER: [
        read_file,
        search_code,
        run_tests,
        check_syntax,
        run_linter,
    ],
    AgentRole.REVIEWER: [read_file, analyze_python_file, run_linter],
    AgentRole.DOCUMENTER: [read_file, write_file, list_directory],
}


def create_agent(
    role: AgentRole,
    model_name: Optional[str] = None,
    temperature: float = 0.1,
    db_tools: Optional[DatabaseTools] = None,
    api_base: Optional[str] = None,
) -> Agent:
    """Создает агента по роли с правильной конфигурацией.

    Args:
        role: Роль агента.
        model_name: Имя модели LLM (если None — берётся из DEFAULT_MODEL_MAP).
            Для локальных LLM используйте формат ``openai/<model>`` (vLLM,
            llama.cpp, LM Studio) или ``ollama/<model>`` (Ollama).
        temperature: Температура генерации.
        db_tools: Инструменты БД для SQL-агента.
        api_base: URL локального LLM-сервера, например
            ``http://localhost:8000/v1``.  Если задан, будет установлен через
            переменную окружения ``OPENAI_API_BASE`` (для провайдера ``openai/``).

    Returns:
        Сконфигурированный объект Agent.
    """
    resolved_model = model_name or DEFAULT_MODEL_MAP.get(role.value, "gpt-4.1-mini")

    # Настройка локального LLM-сервера через переменные окружения
    if api_base:
        os.environ.setdefault("OPENAI_API_BASE", api_base)
        os.environ.setdefault("OPENAI_API_KEY", "local-dummy-key")

    # Для SQL агента добавляем инструменты БД
    if role == AgentRole.SQL_ANALYST:
        tools: List[Callable] = [read_file, search_code]
        if db_tools:
            tools.extend([db_tools.execute_query, db_tools.get_schema_info])
    else:
        tools = list(ROLE_TOOLS.get(role, []))

    agent = Agent(
        agent_name=role.value.title().replace("_", ""),
        system_prompt=SYSTEM_PROMPTS.get(role, "You are a helpful assistant."),
        model_name=resolved_model,
        max_loops=1,
        autosave=False,
        dashboard=False,
        tools=tools,
        temperature=temperature,
        max_tokens=4096,
        verbose=True,
    )
    return agent


# =============================================================================
# ОРКЕСТРАТОР
# =============================================================================


class RefactoringOrchestrator:
    """Оркестратор мультиагентной системы рефакторинга."""

    def __init__(
        self,
        project_path: str,
        db_connection: Optional[str] = None,
        model_configs: Optional[Dict[str, str]] = None,
        api_base: Optional[str] = None,
    ):
        self.project_path = os.path.abspath(project_path)
        self.context = ProjectContext(root_path=self.project_path)
        self.proposals: List[RefactoringProposal] = []
        self.approved_changes: List[Dict[str, Any]] = []
        self.api_base = api_base

        self.model_configs: Dict[str, str] = {
            **DEFAULT_MODEL_MAP,
            **(model_configs or {}),
        }

        # БД инструменты
        self.db_tools: Optional[DatabaseTools] = None
        if db_connection:
            self.db_tools = DatabaseTools(db_connection)

        # Инициализация агентов
        self.agents: Dict[AgentRole, Agent] = {}
        self._init_agents()

        # Рабочая директория
        os.chdir(self.project_path)
        logger.info("Оркестратор инициализирован для %s", self.project_path)

    def _init_agents(self) -> None:
        """Инициализирует всех агентов."""
        for role in [
            AgentRole.FILE_MANAGER,
            AgentRole.CODER,
            AgentRole.TESTER,
            AgentRole.DEBUGGER,
            AgentRole.SQL_ANALYST,
            AgentRole.REVIEWER,
            AgentRole.DOCUMENTER,
        ]:
            model = self.model_configs.get(role.value)
            self.agents[role] = create_agent(
                role=role,
                model_name=model,
                db_tools=self.db_tools,
                api_base=self.api_base,
            )
        logger.info("Агенты инициализированы: %s", list(self.agents.keys()))

    def add_project_rule(self, rule: str) -> None:
        """Добавляет правило работы с проектом."""
        self.context.add_rule(rule)
        logger.info("Добавлено правило: %s", rule)

    def initial_analysis(self) -> str:
        """Первоначальный анализ проекта."""
        logger.info("Начинаю анализ кодовой базы...")

        file_manager = self.agents[AgentRole.FILE_MANAGER]

        # Анализ структуры
        structure = file_manager.run(
            "Проанализируй структуру проекта. Используй list_directory и дай обзор."
        )

        # Поиск Python файлов
        py_files: List[str] = []
        for root, _, files in os.walk(self.project_path):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
        self.context.python_files = py_files

        # Анализ зависимостей
        deps: Dict[str, str] = {}
        req_file = os.path.join(self.project_path, "requirements.txt")
        if os.path.exists(req_file):
            with open(req_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "==" in line:
                        pkg, ver = line.split("==", 1)
                        deps[pkg.strip()] = ver.strip()
        self.context.dependencies = deps

        # Анализ ключевых файлов
        analyzed_count = 0
        for file_path in py_files[:10]:
            file_manager.run(
                f"Проанализируй файл {file_path} с помощью analyze_python_file"
            )
            analyzed_count += 1

        summary = (
            f"Результаты анализа:\n"
            f"- Python файлов: {len(py_files)}\n"
            f"- Зависимостей: {len(deps)}\n"
            f"- Ключевых компонентов проанализировано: {analyzed_count}\n\n"
            f"{structure}"
        )

        self.context.architecture_graph = self._build_dependency_graph()
        return summary

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Строит граф зависимостей между модулями."""
        graph: Dict[str, List[str]] = {}
        for file_path in self.context.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                imports: List[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        imports.append(module)

                rel_path = os.path.relpath(file_path, self.project_path)
                graph[rel_path] = list(set(imports))
            except (SyntaxError, OSError):
                continue
        return graph

    def create_refactoring_proposal(
        self,
        target_files: List[str],
        goal: str,
        agent_roles: Optional[List[AgentRole]] = None,
    ) -> RefactoringProposal:
        """Создает предложение по рефакторингу через анализ агентов."""
        if agent_roles is None:
            agent_roles = [
                AgentRole.FILE_MANAGER,
                AgentRole.REVIEWER,
                AgentRole.CODER,
            ]

        proposal_id = f"REF-{len(self.proposals) + 1:03d}"

        analyses: Dict[str, str] = {}
        for role in agent_roles:
            agent = self.agents[role]
            if role == AgentRole.FILE_MANAGER:
                result = agent.run(
                    f"Проанализируй файлы {target_files} для цели: {goal}"
                )
            elif role == AgentRole.REVIEWER:
                result = agent.run(
                    f"Проведи код-ревью файлов {target_files}. "
                    "Выяви проблемы и возможности улучшения."
                )
            elif role == AgentRole.CODER:
                result = agent.run(
                    f"Предложи конкретные изменения для {target_files} "
                    f"чтобы достичь: {goal}"
                )
            else:
                result = agent.run(
                    f"Проанализируй {target_files} в контексте: {goal}"
                )

            analyses[role.value] = result

        proposal = RefactoringProposal(
            id=proposal_id,
            agent_role=AgentRole.CODER,
            description=goal,
            affected_files=target_files,
            changes=[{"analysis": analyses}],
            rationale=(
                f"На основе анализа агентов: "
                f"{', '.join([r.value for r in agent_roles])}"
            ),
            risks=[
                "Возможные breaking changes",
                "Необходимость обновления тестов",
            ],
        )

        self.proposals.append(proposal)
        return proposal

    def present_proposal(self, proposal: RefactoringProposal) -> bool:
        """Представляет предложение пользователю и запрашивает подтверждение."""
        print(f"\n{'=' * 60}")
        print(f"ПРЕДЛОЖЕНИЕ ПО РЕФАКТОРИНГУ: {proposal.id}")
        print(f"{'=' * 60}")
        print(f"Цель: {proposal.description}")
        print(f"Затронутые файлы: {', '.join(proposal.affected_files)}")
        print(f"Обоснование: {proposal.rationale}")
        print(f"Риски: {', '.join(proposal.risks)}")
        print(f"\nДетальный анализ:")
        print(json.dumps(proposal.changes, indent=2, ensure_ascii=False)[:2000])

        while True:
            choice = input("\nОдобрить это изменение? (yes/no/modify): ").lower().strip()
            if choice in ("yes", "y"):
                proposal.approved = True
                return True
            elif choice in ("no", "n"):
                proposal.approved = False
                print("Изменение отклонено")
                return False
            elif choice == "modify":
                new_desc = input("Введите уточненное описание: ")
                proposal.description = new_desc
                print("Предложение обновлено")
            else:
                print("Пожалуйста, введите yes, no или modify")

    def execute_refactoring(self, proposal: RefactoringProposal) -> None:
        """Выполняет одобренное изменение с тестированием."""
        if not proposal.approved:
            print("Предложение не одобрено")
            return

        logger.info("Выполнение рефакторинга %s", proposal.id)

        coder = self.agents[AgentRole.CODER]
        tester = self.agents[AgentRole.TESTER]
        debugger = self.agents[AgentRole.DEBUGGER]

        for file_path in proposal.affected_files:
            print(f"\nОбработка файла: {file_path}")

            original_code = read_file(file_path)

            # Генерация изменений
            task = (
                f"Внеси изменения в файл {file_path} согласно цели: "
                f"{proposal.description}\n\n"
                f"Текущий код:\n{original_code[:3000]}\n\n"
                "Требования:\n"
                "1. Сохранить сигнатуры публичных функций (backward compatibility)\n"
                "2. Добавить type hints\n"
                "3. Улучшить обработку ошибок\n"
                "4. Оптимизировать SQLAlchemy запросы если есть\n"
                "5. Вернуть ПОЛНЫЙ код файла, без сокращений"
            )

            refactored_code = coder.run(task)

            # Извлечение кода из ответа (markdown code block)
            code_match = re.search(
                r"```python\n(.*?)```", refactored_code, re.DOTALL
            )
            clean_code = code_match.group(1) if code_match else refactored_code

            # Проверка синтаксиса
            syntax_check = check_syntax(clean_code)
            if "Ошибка" in syntax_check:
                logger.warning("Синтаксическая ошибка, запускаю Debugger...")
                fix_task = (
                    f"Исправь синтаксическую ошибку в коде:\n{clean_code}\n"
                    f"Ошибка: {syntax_check}"
                )
                fixed = debugger.run(fix_task)
                code_match = re.search(
                    r"```python\n(.*?)```", fixed, re.DOTALL
                )
                clean_code = code_match.group(1) if code_match else fixed

            # Создание тестов
            print("Создание тестов...")
            test_task = (
                f"Создай pytest тесты для следующего кода:\n\n"
                f"Файл: {file_path}\nКод:\n{clean_code[:2000]}\n\n"
                "Требования:\n"
                "1. Тесты должны проверять новую функциональность\n"
                "2. Использовать fixtures для зависимостей\n"
                "3. Покрыть граничные случаи\n"
                f"4. Сохранить тесты в tests/test_{os.path.basename(file_path)}"
            )

            test_code = tester.run(test_task)

            # Предпросмотр
            print(f"\nПодготовлены изменения для {file_path}")
            print("--- Оригинал (первые 10 строк) ---")
            print("\n".join(original_code.split("\n")[:10]))
            print("--- Новый код (первые 10 строк) ---")
            print("\n".join(clean_code.split("\n")[:10]))

            confirm = input("\nЗаписать изменения? (yes/no): ")
            if confirm.lower() in ("yes", "y"):
                write_file(file_path, clean_code, backup=True)

                # Запись тестов
                test_dir = os.path.join(self.project_path, "tests")
                os.makedirs(test_dir, exist_ok=True)
                test_file = os.path.join(
                    test_dir, f"test_{os.path.basename(file_path)}"
                )

                # Извлекаем код тестов из markdown
                test_match = re.search(
                    r"```python\n(.*?)```", test_code, re.DOTALL
                )
                clean_test = test_match.group(1) if test_match else test_code
                write_file(test_file, clean_test, backup=True)

                # Запуск тестов
                print("Запуск тестов...")
                test_result = run_tests(test_file)
                print(test_result)

                if "passed" in test_result.lower():
                    print("Тесты пройдены успешно")
                    self.approved_changes.append(
                        {
                            "proposal_id": proposal.id,
                            "file": file_path,
                            "test_file": test_file,
                            "status": "success",
                        }
                    )
                else:
                    print("Тесты не пройдены, запускаю Debugger...")
                    debug_result = debugger.run(
                        f"Исправь ошибки в тестах:\n{test_result}\n\n"
                        f"Код тестов:\n{clean_test}"
                    )
                    print(debug_result)
            else:
                print("Изменения отменены")

    def run_interactive_session(self) -> None:
        """Запускает интерактивную сессию рефакторинга."""
        print("МУЛЬТИАГЕНТНАЯ СИСТЕМА РЕФАКТОРИНГА КОДА")
        print("=" * 60)

        analysis = self.initial_analysis()
        print(analysis)

        while True:
            print(f"\n{'=' * 60}")
            print("Доступные команды:")
            print("  analyze [file/path] - Глубокий анализ файла")
            print("  refactor [goal] [files...] - Создать предложение рефакторинга")
            print("  test [path] - Запустить тесты")
            print("  lint [file] - Проверить линтером")
            print("  sql [query] - Выполнить SQL запрос (только чтение)")
            print("  docs - Обновить документацию")
            print("  rules - Показать правила проекта")
            print("  exit - Выход")

            raw_input = input("\nВведите команду: ").strip()
            if not raw_input:
                continue

            command = raw_input.split()
            cmd = command[0].lower()

            if cmd == "exit":
                print("До свидания!")
                break

            elif cmd == "analyze":
                if len(command) > 1:
                    target = command[1]
                    agent = self.agents[AgentRole.FILE_MANAGER]
                    result = agent.run(
                        f"Проведи детальный анализ файла {target}. "
                        "Используй analyze_python_file и объясни архитектуру."
                    )
                    print(result)
                else:
                    print("Укажите путь к файлу")

            elif cmd == "refactor":
                if len(command) >= 3:
                    goal = command[1]
                    files = command[2:]
                    proposal = self.create_refactoring_proposal(files, goal)
                    if self.present_proposal(proposal):
                        self.execute_refactoring(proposal)
                else:
                    print("Использование: refactor 'цель' file1.py file2.py")

            elif cmd == "test":
                path = command[1] if len(command) > 1 else "."
                result = run_tests(path)
                print(result)

            elif cmd == "lint":
                if len(command) > 1:
                    file_path = command[1]
                    for linter_name in ("pylint", "flake8", "mypy"):
                        print(f"\n{linter_name}:")
                        result = run_linter(file_path, linter_name)
                        print(result)
                else:
                    print("Укажите путь к файлу")

            elif cmd == "sql":
                if len(command) > 1:
                    query = " ".join(command[1:])
                    agent = self.agents[AgentRole.SQL_ANALYST]
                    result = agent.run(
                        f"Выполни и проанализируй запрос: {query}"
                    )
                    print(result)
                else:
                    print("Укажите SQL запрос")

            elif cmd == "docs":
                agent = self.agents[AgentRole.DOCUMENTER]
                result = agent.run(
                    "Создай полную документацию проекта. Используй read_file "
                    "для ключевых файлов и сгенерируй README.md с архитектурой."
                )
                print(result)

            elif cmd == "rules":
                print("Правила проекта:")
                for i, rule in enumerate(self.context.rules, 1):
                    print(f"  {i}. {rule}")
                if not self.context.rules:
                    print("  Правила не заданы. Используйте add_project_rule()")

            else:
                print(f"Неизвестная команда: {cmd}")


# =============================================================================
# ЗАПУСК СИСТЕМЫ
# =============================================================================


def main() -> None:
    """Точка входа."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Мультиагентная система рефакторинга кода"
    )
    parser.add_argument("--path", "-p", default=".", help="Путь к проекту")
    parser.add_argument(
        "--db", "-d", help="Строка подключения к БД (только чтение)"
    )
    parser.add_argument(
        "--model-config", "-m", help="JSON файл с конфигурацией моделей"
    )
    parser.add_argument(
        "--api-base",
        help="URL локального LLM-сервера (например http://localhost:8000/v1)",
    )

    args = parser.parse_args()

    # Загрузка конфигурации моделей
    model_configs = None
    if args.model_config and os.path.exists(args.model_config):
        with open(args.model_config, encoding="utf-8") as f:
            model_configs = json.load(f)

    # Инициализация оркестратора
    orchestrator = RefactoringOrchestrator(
        project_path=args.path,
        db_connection=args.db,
        model_configs=model_configs,
        api_base=args.api_base,
    )

    # Базовые правила
    orchestrator.add_project_rule("Все новые функции должны иметь type hints")
    orchestrator.add_project_rule(
        "SQLAlchemy сессии должны использоваться в контекстных менеджерах"
    )
    orchestrator.add_project_rule("Все изменения требуют unit-тестов")
    orchestrator.add_project_rule("Использовать Pydantic v2 для валидации")

    # Запуск интерактивной сессии
    orchestrator.run_interactive_session()


if __name__ == "__main__":
    main()
