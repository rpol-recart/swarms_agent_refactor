# Swarms Framework — Руководство с примерами

> Версия swarms: 9.x
> Дата: 2026-03-11

---

## Содержание

1. [Установка](#1-установка)
2. [Agent — базовый строительный блок](#2-agent--базовый-строительный-блок)
3. [Инструменты (Tools)](#3-инструменты-tools)
4. [MCP — удалённые инструменты](#4-mcp--удалённые-инструменты)
5. [SequentialWorkflow — последовательный конвейер](#5-sequentialworkflow--последовательный-конвейер)
6. [ConcurrentWorkflow — параллельное выполнение](#6-concurrentworkflow--параллельное-выполнение)
7. [MixtureOfAgents — эксперты + агрегатор](#7-mixtureofagents--эксперты--агрегатор)
8. [GroupChat — групповой чат агентов](#8-groupchat--групповой-чат-агентов)
9. [SpreadSheetSwarm — массовый параллелизм с CSV](#9-spreadsheetswarm--массовый-параллелизм-с-csv)
10. [SwarmRouter — единый роутер](#10-swarmrouter--единый-роутер)
11. [Подключение к локальным LLM](#11-подключение-к-локальным-llm)
12. [Выбор архитектуры](#12-выбор-архитектуры)
13. [Справочник импортов](#13-справочник-импортов)

---

## 1. Установка

```bash
pip install swarms
```

Для работы с конкретными провайдерами LLM задайте API-ключи:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 2. Agent — базовый строительный блок

`Agent` — центральный класс фреймворка. Инкапсулирует LLM, системный промпт, инструменты и логику выполнения.

### Ключевые параметры конструктора

| Параметр | Тип | Описание |
|---|---|---|
| `agent_name` | `str` | Имя агента |
| `agent_description` | `str` | Описание назначения |
| `system_prompt` | `str` | Системный промпт — инструкции для LLM |
| `model_name` | `str` | Идентификатор модели (`"gpt-4.1"`, `"anthropic/claude-sonnet-4-20250514"`, `"ollama/llama3"`) |
| `llm` | `Any` | Кастомный LLM-объект с методом `run(task: str) -> str` |
| `tools` | `List[Callable]` | Список Python-функций как инструментов |
| `max_loops` | `int` или `"auto"` | Количество итераций; `"auto"` — автономное планирование |
| `max_tokens` | `int` | Максимум токенов на запрос |
| `temperature` | `float` | Температура генерации |
| `dynamic_temperature_enabled` | `bool` | Динамическая температура |
| `output_type` | `str` | Формат вывода: `"str"`, `"all"` |
| `mcp_url` | `str` | URL MCP-сервера для удалённых инструментов |
| `autosave` | `bool` | Автосохранение истории диалога |
| `verbose` | `bool` | Подробный вывод |

### Минимальный пример

```python
from swarms import Agent

agent = Agent(
    agent_name="Помощник",
    system_prompt="Ты — полезный AI-ассистент.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

response = agent.run("Объясни что такое рефакторинг кода")
print(response)
```

### Автономный режим (auto)

Режим `max_loops="auto"` позволяет агенту самостоятельно планировать подзадачи:

```python
agent = Agent(
    agent_name="Исследователь",
    model_name="gpt-4.1",
    max_loops="auto",
    system_prompt="Ты — исследователь. Планируй и выполняй многошаговые задачи.",
)

response = agent.run("Проведи комплексный анализ применения AI в медицине")
```

---

## 3. Инструменты (Tools)

Инструменты — это обычные Python-функции, передаваемые в `tools=[]`. Фреймворк автоматически
генерирует JSON-схему для function calling на основе аннотаций типов и docstring.

### Требования к функциям-инструментам

1. Type hints на все параметры и возвращаемый тип
2. Docstring в формате Google (с секциями `Args:`, `Returns:`)
3. Обработка ошибок внутри функции
4. Возвращать `str` (предпочтительно JSON)

### Пример: агент с инструментами

```python
import json
import subprocess
from swarms import Agent


def execute_shell(command: str) -> str:
    """Выполняет shell-команду и возвращает вывод.

    Args:
        command (str): Команда для выполнения.

    Returns:
        str: Стандартный вывод команды.
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout or result.stderr
    except subprocess.TimeoutExpired:
        return "Команда превысила лимит времени"
    except Exception as e:
        return f"Ошибка: {e}"


def read_file(file_path: str) -> str:
    """Читает содержимое файла.

    Args:
        file_path (str): Путь к файлу.

    Returns:
        str: Содержимое файла или сообщение об ошибке.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Ошибка чтения: {e}"


def write_file(file_path: str, content: str) -> str:
    """Записывает содержимое в файл.

    Args:
        file_path (str): Путь к файлу.
        content (str): Содержимое для записи.

    Returns:
        str: Результат операции.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Файл {file_path} успешно записан"
    except Exception as e:
        return f"Ошибка записи: {e}"


agent = Agent(
    agent_name="DevOps-Agent",
    system_prompt="Ты — DevOps инженер. Используй инструменты для работы с системой.",
    model_name="gpt-4.1",
    max_loops=3,
    tools=[execute_shell, read_file, write_file],
)

response = agent.run("Проверь версию Python и установленные пакеты")
print(response)
```

### Пример: финансовый агент с API

```python
import json
import requests
from swarms import Agent


def get_coin_price(coin_id: str, vs_currency: str = "usd") -> str:
    """Получает текущую цену криптовалюты.

    Args:
        coin_id (str): ID монеты на CoinGecko (bitcoin, ethereum).
        vs_currency (str): Целевая валюта для конвертации.

    Returns:
        str: JSON с ценой монеты.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id.lower().strip(),
            "vs_currencies": vs_currency.lower(),
            "include_market_cap": True,
            "include_24hr_vol": True,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.RequestException as e:
        return json.dumps({"error": str(e)})


def get_top_cryptocurrencies(limit: int = 10) -> str:
    """Получает топ криптовалют по рыночной капитализации.

    Args:
        limit (int): Количество монет для возврата.

    Returns:
        str: JSON-список топ криптовалют.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return json.dumps(response.json(), indent=2)


agent = Agent(
    agent_name="Crypto-Analyst",
    system_prompt="Ты — криптоаналитик с доступом к реальным данным.",
    model_name="gpt-4.1",
    max_loops=1,
    tools=[get_coin_price, get_top_cryptocurrencies],
)

response = agent.run("Покажи текущие цены Bitcoin и Ethereum в USD и EUR")
print(response)
```

---

## 4. MCP — удалённые инструменты

Model Context Protocol позволяет выносить инструменты на отдельный HTTP-сервер и подключать их к агенту через URL.

### Сервер (отдельный процесс)

```python
from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("CryptoTools")
mcp.settings.port = 8001


@mcp.tool(
    name="get_crypto_price",
    description="Get cryptocurrency price from exchange",
)
def get_crypto_price(symbol: str) -> str:
    """Get cryptocurrency price.

    Args:
        symbol (str): Trading pair like 'BTC-USDT'.

    Returns:
        str: Formatted price data.
    """
    symbol = symbol.upper().strip()
    if not symbol.endswith("-USDT"):
        symbol = f"{symbol}-USDT"

    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    ticker = data.get("data", [{}])[0]
    price = float(ticker.get("last", 0))
    return f"Price {symbol}: ${price:,.2f}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### Клиент (агент, использующий MCP)

```python
from swarms import Agent

agent = Agent(
    agent_name="MCP-Crypto-Agent",
    system_prompt="Ты — финансовый аналитик с доступом к биржевым данным.",
    max_loops=1,
    mcp_url="http://0.0.0.0:8001/mcp",
    output_type="all",
)

response = agent.run("Получи цену Bitcoin и Ethereum")
print(response)
```

---

## 5. SequentialWorkflow — последовательный конвейер

Агенты выполняются один за другим. Выход предыдущего агента подаётся на вход следующему.

```
Задача → [Агент 1] → результат → [Агент 2] → результат → [Агент 3] → финал
```

### Пример: конвейер создания контента

```python
from swarms import Agent, SequentialWorkflow

researcher = Agent(
    agent_name="Researcher",
    system_prompt=(
        "Ты — исследователь. Собери факты и создай "
        "структурированный отчёт по заданной теме."
    ),
    model_name="gpt-4.1-mini",
    max_loops=1,
)

writer = Agent(
    agent_name="Writer",
    system_prompt=(
        "Ты — копирайтер. Преобразуй исследование "
        "в увлекательный и понятный текст статьи."
    ),
    model_name="gpt-4.1-mini",
    max_loops=1,
)

editor = Agent(
    agent_name="Editor",
    system_prompt=(
        "Ты — редактор. Проверь текст на ошибки, "
        "улучши стиль и подготовь к публикации."
    ),
    model_name="gpt-4.1-mini",
    max_loops=1,
)

workflow = SequentialWorkflow(agents=[researcher, writer, editor])
result = workflow.run("История и будущее искусственного интеллекта")
print(result)
```

### Дополнительные возможности

```python
# Командная осведомлённость — агенты знают свою позицию в цепочке
workflow = SequentialWorkflow(
    agents=[researcher, writer, editor],
    team_awareness=True,
)

# Пакетная обработка нескольких задач
results = workflow.run_batched([
    "Тема 1: Машинное обучение",
    "Тема 2: Квантовые вычисления",
    "Тема 3: Кибербезопасность",
])

# Асинхронное выполнение
result = workflow.run_async("Асинхронная задача")
```

---

## 6. ConcurrentWorkflow — параллельное выполнение

Все агенты получают одну и ту же задачу и работают параллельно. Каждый даёт свой независимый результат.

```
              ┌─ [Агент 1] → результат 1
Задача ──────┼─ [Агент 2] → результат 2
              └─ [Агент 3] → результат 3
```

### Пример: параллельный анализ

```python
from swarms import Agent, ConcurrentWorkflow

market_analyst = Agent(
    agent_name="Market-Analyst",
    system_prompt="Ты — рыночный аналитик. Анализируй тренды рынка.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

financial_analyst = Agent(
    agent_name="Financial-Analyst",
    system_prompt="Ты — финансовый аналитик. Проводи финансовый анализ.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

risk_analyst = Agent(
    agent_name="Risk-Analyst",
    system_prompt="Ты — риск-аналитик. Оцени риски и предложи митигации.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

workflow = ConcurrentWorkflow(
    agents=[market_analyst, financial_analyst, risk_analyst],
    max_loops=1,
)
results = workflow.run("Анализ влияния AI на индустрию здравоохранения")
print(results)
```

---

## 7. MixtureOfAgents — эксперты + агрегатор

Несколько экспертных агентов работают параллельно, затем агент-агрегатор синтезирует
их результаты в единый ответ.

```
              ┌─ [Эксперт 1] ─┐
Задача ──────┼─ [Эксперт 2] ──┼─→ [Агрегатор] → финальный результат
              └─ [Эксперт 3] ─┘
```

### Пример: экспертный совет

```python
from swarms import Agent, SwarmRouter

finance_expert = Agent(
    agent_name="Finance-Expert",
    system_prompt="Ты — финансовый эксперт. Дай детальный финансовый анализ.",
    model_name="gpt-4.1-mini",
)

market_expert = Agent(
    agent_name="Market-Expert",
    system_prompt="Ты — рыночный аналитик. Оцени рыночные тренды.",
    model_name="gpt-4.1-mini",
)

tech_expert = Agent(
    agent_name="Tech-Expert",
    system_prompt="Ты — технический эксперт. Проведи технический due diligence.",
    model_name="gpt-4.1-mini",
)

aggregator = Agent(
    agent_name="Aggregator",
    system_prompt=(
        "Ты — старший аналитик. Синтезируй выводы всех экспертов "
        "в единый структурированный отчёт."
    ),
    model_name="gpt-4.1",
)

router = SwarmRouter(
    swarm_type="MixtureOfAgents",
    agents=[finance_expert, market_expert, tech_expert],
    aggregator_agent=aggregator,
)

result = router.run("Оцени потенциал приобретения TechStartup Inc.")
print(result)
```

---

## 8. GroupChat — групповой чат агентов

Агенты общаются между собой в формате чата. Поддерживаются разные стратегии выбора
следующего говорящего.

### Стратегии выбора спикера

| Стратегия | Поведение |
|---|---|
| `"round-robin-speaker"` | Агенты говорят по очереди |
| `"random-speaker"` | Случайный выбор |
| `"priority-speaker"` | Взвешенная вероятность |
| `"random-dynamic-speaker"` | По @-упоминаниям в ответах |

### Пример: групповой чат по кругу

```python
from swarms import Agent, GroupChat

finance_agent = Agent(
    agent_name="Finance-Agent",
    system_prompt="Ты — финансовый консультант.",
    model_name="gpt-4.1",
)

tax_agent = Agent(
    agent_name="Tax-Agent",
    system_prompt="Ты — налоговый консультант.",
    model_name="gpt-4.1",
)

legal_agent = Agent(
    agent_name="Legal-Agent",
    system_prompt="Ты — юридический консультант.",
    model_name="gpt-4.1",
)

chat = GroupChat(
    name="Investment-Advisory",
    agents=[finance_agent, tax_agent, legal_agent],
    speaker_function="round-robin-speaker",
    max_loops=6,
)

history = chat.run("Как оптимизировать налоговую стратегию для IT-стартапа?")
print(history)
```

### Пример: приоритетный спикер

```python
chat = GroupChat(
    agents=[finance_agent, tax_agent, legal_agent],
    speaker_function="priority-speaker",
    speaker_state={
        "priorities": {
            "Finance-Agent": 0.5,
            "Tax-Agent": 0.3,
            "Legal-Agent": 0.2,
        }
    },
)
```

### Пакетный и конкурентный запуск

```python
# Несколько тем через один чат
histories = chat.batched_run([
    "Налоговая стратегия",
    "Инвестиционный портфель",
    "Юридический комплаенс",
])

# Параллельный запуск нескольких чатов
histories = chat.concurrent_run(["Задача 1", "Задача 2"])
```

---

## 9. SpreadSheetSwarm — массовый параллелизм с CSV

Управляет большим количеством агентов, запущенных параллельно, с логированием
результатов в CSV-файл.

```python
from swarms import Agent
from swarms.structs.spreadsheet_swarm import SpreadSheetSwarm

research_agent = Agent(
    agent_name="Research-Agent",
    system_prompt="Проведи детальное исследование.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

analysis_agent = Agent(
    agent_name="Analysis-Agent",
    system_prompt="Проведи аналитику на основе данных.",
    model_name="gpt-4.1-mini",
    max_loops=1,
)

swarm = SpreadSheetSwarm(
    name="Analysis-Swarm",
    agents=[research_agent, analysis_agent],
    max_loops=1,
    autosave=True,  # результаты сохраняются в CSV
)

result = swarm.run("Анализ трендов рынка AI в 2026 году")
print(result)
```

### Загрузка агентов из CSV

SpreadSheetSwarm может загружать конфигурации агентов из CSV-файла. Колонки:

| Колонка | Описание |
|---|---|
| `agent_name` | Имя агента |
| `description` | Описание |
| `system_prompt` | Системный промпт |
| `task` | Задача для выполнения |
| `model_name` | Модель LLM |
| `max_loops` | Количество итераций |

```python
swarm = SpreadSheetSwarm(
    name="CSV-Swarm",
    load_path="agents.csv",
    autosave=True,
)
result = swarm.run_from_config()
```

---

## 10. SwarmRouter — единый роутер

`SwarmRouter` — единая точка входа для всех архитектур. Переключение между стратегиями
через параметр `swarm_type`.

### Поддерживаемые типы

`SwarmType` — это `Literal`, а не Enum. Передавайте строки:

| Значение (строка) | Описание |
|---|---|
| `"SequentialWorkflow"` | Последовательное выполнение |
| `"ConcurrentWorkflow"` | Параллельное выполнение |
| `"MixtureOfAgents"` | Эксперты + агрегатор |
| `"AgentRearrange"` | Пользовательские паттерны потоков |
| `"GroupChat"` | Групповой чат |
| `"HierarchicalSwarm"` | Иерархическая делегация |
| `"HeavySwarm"` | Тяжёлая обработка |
| `"LLMCouncil"` | Совет LLM для принятия решений |
| `"DebateWithJudge"` | Дебаты агентов с арбитром |
| `"MajorityVoting"` | Голосование большинством |
| `"RoundRobin"` | Циклический обход |
| `"auto"` | Автовыбор лучшей стратегии |

### Пример: переключение архитектур

```python
from swarms import Agent, SwarmRouter

agents = [
    Agent(agent_name="Writer", system_prompt="Ты — писатель.", model_name="gpt-4.1-mini"),
    Agent(agent_name="Editor", system_prompt="Ты — редактор.", model_name="gpt-4.1-mini"),
    Agent(agent_name="Reviewer", system_prompt="Ты — рецензент.", model_name="gpt-4.1-mini"),
]

# Последовательное выполнение
seq = SwarmRouter(swarm_type="SequentialWorkflow", agents=agents)
result = seq.run("Напиши рассказ о роботе, открывшем музыку")

# Параллельное выполнение
par = SwarmRouter(swarm_type="ConcurrentWorkflow", agents=agents)
results = par.run("Напиши рассказ о роботе, открывшем музыку")

# Автоматический выбор стратегии
auto = SwarmRouter(name="AutoRouter", agents=agents, swarm_type="auto")
result = auto.run("Напиши рассказ о роботе, открывшем музыку")
```

---

## 11. Подключение к локальным LLM

### Ollama (простейший вариант)

```bash
# Запуск модели
ollama run llama3
```

```python
from swarms import Agent

agent = Agent(
    agent_name="Local-Agent",
    model_name="ollama/llama3",  # префикс ollama/
    system_prompt="Ты — полезный ассистент.",
    max_loops=1,
)
response = agent.run("Объясни машинное обучение простыми словами")
```

Другие модели: `"ollama/mistral"`, `"ollama/codellama"`, `"ollama/qwen2"`.

### vLLM / llama.cpp / LM Studio (OpenAI-совместимый API)

```bash
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=dummy
```

```python
from swarms import Agent

agent = Agent(
    agent_name="vLLM-Agent",
    model_name="openai/Qwen2.5-32B-Instruct",  # префикс openai/
    system_prompt="Ты — кодер-эксперт.",
    max_loops=1,
)
response = agent.run("Напиши функцию сортировки на Python")
```

### Кастомный LLM-обёртка

Любой объект с методом `run(task: str) -> str` можно передать в параметр `llm=`:

```python
import ollama
from swarms import Agent


class OllamaWrapper:
    """Обёртка для Ollama с полным контролем параметров."""

    def __init__(
        self,
        model_name: str = "llama3",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        num_predict: int = 2048,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.num_predict = num_predict
        self.client = ollama.Client(host=base_url)

    def run(self, task: str, **kwargs) -> str:
        options = {
            "temperature": self.temperature,
            "num_predict": self.num_predict,
        }
        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": task}],
            options=options,
        )
        return response["message"]["content"]


llm = OllamaWrapper(model_name="llama3", temperature=0.3)

agent = Agent(
    agent_name="Custom-LLM-Agent",
    llm=llm,
    system_prompt="Ты — ассистент для программистов.",
    max_loops=1,
)
response = agent.run("Напиши unit-тест для функции сортировки")
print(response)
```

### Поддерживаемые провайдеры через LiteLLM

Swarms использует LiteLLM под капотом. Формат `model_name`:

| Провайдер | Формат | Пример |
|---|---|---|
| OpenAI | `gpt-*` | `gpt-4.1`, `gpt-4.1-mini` |
| Anthropic | `anthropic/*` | `anthropic/claude-sonnet-4-20250514` |
| Ollama | `ollama/*` | `ollama/llama3` |
| vLLM/локальный | `openai/*` + `OPENAI_API_BASE` | `openai/Qwen2.5-32B` |
| Google | `gemini/*` | `gemini/gemini-2.5-pro` |
| Groq | `groq/*` | `groq/llama-3.3-70b-versatile` |
| Together AI | `together_ai/*` | `together_ai/meta-llama/Meta-Llama-3-70B` |
| Hugging Face | `huggingface/*` | `huggingface/bigcode/starcoder` |

---

## 12. Выбор архитектуры

| Задача | Рекомендуемая архитектура |
|---|---|
| Конвейер обработки (исследование → написание → редактура) | `SequentialWorkflow` |
| Независимый параллельный анализ | `ConcurrentWorkflow` |
| Синтез мнений экспертов | `MixtureOfAgents` |
| Мульти-агентная дискуссия | `GroupChat` |
| Массовая обработка с логированием | `SpreadSheetSwarm` |
| Иерархическая делегация | `HierarchicalSwarm` (через `SwarmRouter`) |
| Универсальный (автовыбор) | `SwarmRouter` с `swarm_type="auto"` |

### Схема принятия решения

```
Задача требует последовательных этапов?
├── Да → SequentialWorkflow
└── Нет
    ├── Нужен синтез от нескольких экспертов?
    │   ├── Да → MixtureOfAgents
    │   └── Нет → ConcurrentWorkflow
    ├── Нужна дискуссия между агентами?
    │   └── Да → GroupChat
    └── Массовый параллелизм с логами?
        └── Да → SpreadSheetSwarm
```

---

## 13. Справочник импортов

```python
# Ядро
from swarms import Agent

# Рабочие процессы
from swarms import SequentialWorkflow
from swarms import ConcurrentWorkflow

# Роутер (единый интерфейс ко всем типам)
from swarms import SwarmRouter, SwarmType  # SwarmType = Literal[...], SwarmType

# Групповой чат
from swarms import GroupChat

# Массовый параллелизм
from swarms.structs.spreadsheet_swarm import SpreadSheetSwarm

# Другие структуры
from swarms import MixtureOfAgents
from swarms import MajorityVoting
from swarms import AgentRearrange
from swarms import HierarchicalSwarm
from swarms import HeavySwarm
from swarms import DebateWithJudge
from swarms import LLMCouncil
```

---

## Источники

- [Swarms Quickstart](https://docs.swarms.world/en/latest/quickstart/)
- [Agent Reference](https://docs.swarms.world/en/latest/swarms/structs/agent/)
- [Tools & MCP Examples](https://docs.swarms.world/en/latest/swarms/tools/tools_examples/)
- [SpreadSheetSwarm](https://docs.swarms.world/en/latest/swarms/structs/spreadsheet_swarm/)
- [Ollama Integration](https://docs.swarms.world/en/latest/swarms/examples/ollama/)
- [vLLM Integration](https://docs.swarms.world/en/latest/swarms/examples/vllm_custom_wrapper/)
- [Model Providers](https://docs.swarms.world/en/latest/swarms/examples/model_providers/)
- [GitHub Repository](https://github.com/kyegomez/swarms)
