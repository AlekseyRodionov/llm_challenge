"""
CLI-интерфейс для Agent с трёхслойной памятью.
"""
import os
from rich.console import Console
from rich.table import Table
from app.agent import Agent

console = Console()


def print_help():
    """Выводит справку по доступным командам."""
    console.print("\n[bold]Доступные команды:[/bold]")
    console.print("  [cyan]help[/cyan]          - Показать эту справку")
    console.print("  [cyan]stats[/cyan]         - Показать статистику запросов")
    console.print("  [cyan]reset[/cyan]        - Очистить историю диалога (short-term)")
    console.print("  [cyan]clear_working[/cyan]- Очистить рабочую память")
    console.print("  [cyan]clear_all[/cyan]    - Очистить всю память из БД")
    console.print("  [cyan]history[/cyan]      - Показать short-term память")
    console.print("  [cyan]show_memory[/cyan]  - Показать все слои памяти")
    console.print("  [cyan]demo[/cyan]         - Запустить демонстрационный сценарий")
    console.print("  [cyan]exit[/cyan]         - Выйти из чата")
    console.print()


def print_stats(stats: dict):
    """Выводит статистику по запросам."""
    table = Table(title="Статистика сессии")
    table.add_column("Метрика")
    table.add_column("Значение")

    table.add_row("Запросов", str(stats["requests"]))
    table.add_row("Всего токенов (input)", str(stats["total_input_tokens"]))
    table.add_row("Всего токенов (output)", str(stats["total_output_tokens"]))
    table.add_row("Всего токенов", str(stats["total_tokens"]))
    table.add_row("Общая стоимость (₽)", str(stats["total_cost"]))

    console.print(table)


def print_memory(agent: Agent):
    """Выводит все слои памяти агента."""
    memory = agent.get_all_memory()

    console.print("\n[bold]Short-Term Memory (оперативная память):[/bold]")
    if memory["short_term"]:
        for i, msg in enumerate(memory["short_term"]):
            role = msg["role"]
            content = msg["content"]
            console.print(f"  [{i}] {role}: {content[:80]}{'...' if len(content) > 80 else ''}")
    else:
        console.print("  [dim]пусто[/dim]")

    console.print("\n[bold]Working Memory (SQLite):[/bold]")
    if memory["working"]:
        for item in memory["working"]:
            console.print(f"  [{item['id']}] {item['content']}")
    else:
        console.print("  [dim]пусто[/dim]")

    console.print("\n[bold]Long-Term Memory (SQLite):[/bold]")
    if memory["long_term"]:
        for item in memory["long_term"]:
            console.print(f"  [{item['id']}] {item['content']}")
    else:
        console.print("  [dim]пусто[/dim]")

    console.print()


DEMO_SCENARIO = [
    "Привет! Я backend-разработчик с 5-летним опытом, изучаю Python и AI.",
    "Хочу составить план изучения LLM для интеграции в свои проекты.",
    "Сколько времени займёт базовое освоение?",
    "Какие первые шаги ты посоветуешь для моего уровня?",
    "Отлично, спасибо! Учти, что я предпочитаю практические примеры.",
    "Можешь порекомендовать конкретные библиотеки для Python?",
    "А какие есть бесплатные ресурсы для тестирования LLM?",
]


def run_demo(agent: Agent, stats: dict):
    """Запускает демонстрационный сценарий."""
    console.print("\n[bold yellow]Запуск демонстрационного сценария...[/bold yellow]\n")

    for i, user_message in enumerate(DEMO_SCENARIO, 1):
        console.print(f"[bold blue]Шаг {i}:[/bold blue] {user_message}")

        with console.status("[bold green]Обрабатываю...[/bold green]") as status:
            result = agent.ask(user_message)

        stats["requests"] += 1
        stats["total_input_tokens"] += result["input_tokens"]
        stats["total_output_tokens"] += result["output_tokens"]
        stats["total_tokens"] += result["total_tokens"]
        stats["total_cost"] += result["cost"]

        console.print(f"[bold green]Агент:[/bold green] {result['text']}\n")
        console.print("[dim]" + "=" * 60 + "[/dim]\n")

    console.print("[bold yellow]Демонстрация завершена.[/bold yellow]")
    console.print("[bold]Текущее состояние памяти:[/bold]")
    print_memory(agent)


def main():
    """Главная функция - запускает CLI с агентом."""
    console.print("[bold green]Agent с трёхслойной памятью[/bold green]")
    console.print("Введите [bold]'help'[/bold] для списка команд\n")
    console.print("[dim]Команды: help, stats, reset, clear_working, clear_all, history, show_memory, demo, exit[/dim]\n")

    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(model=model)

    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }

    while True:
        try:
            user_input = console.input("[bold blue]Вы:[/bold blue] ")
            command = user_input.strip().lower()

            if command in ("exit", "quit", "выход"):
                console.print("\n[bold]Статистика сессии:[/bold]")
                print_stats(stats)
                console.print("\n[yellow]До свидания![/yellow]")
                break

            if command == "help":
                print_help()
                continue

            if command == "stats":
                print_stats(stats)
                console.print()
                continue

            if command == "reset":
                agent.reset_history()
                console.print("[yellow]История диалога очищена.[/yellow]\n")
                continue

            if command == "clear_working":
                agent.clear_working()
                console.print("[yellow]Рабочая память очищена.[/yellow]\n")
                continue

            if command == "clear_all":
                agent.clear_all()
                console.print("[yellow]Вся память из БД очищена.[/yellow]\n")
                continue

            if command == "history":
                short_term = agent.get_short_term()
                console.print(f"[dim]Сообщений в short-term: {len(short_term)}[/dim]\n")
                for i, msg in enumerate(short_term):
                    role = msg["role"]
                    content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                    console.print(f"  [{i}] {role}: {content}")
                console.print()
                continue

            if command == "show_memory":
                print_memory(agent)
                continue

            if command == "demo":
                run_demo(agent, stats)
                continue

            if not user_input.strip():
                continue

            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(user_input)

            stats["requests"] += 1
            stats["total_input_tokens"] += result["input_tokens"]
            stats["total_output_tokens"] += result["output_tokens"]
            stats["total_tokens"] += result["total_tokens"]
            stats["total_cost"] += result["cost"]

            console.print(f"\n[bold green]Агент:[/bold green] {result['text']}\n")

        except KeyboardInterrupt:
            console.print("\n[bold]Статистика сессии:[/bold]")
            print_stats(stats)
            console.print("\n[yellow]Выход (Ctrl+C)[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Ошибка:[/bold red] {e}")


if __name__ == "__main__":
    main()
