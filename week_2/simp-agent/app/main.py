"""
CLI-интерфейс для SimpAgent.
Запускает интерактивный чат с LLM агентом.
"""
import os
from rich.console import Console
from rich.table import Table
from app.agent import Agent

console = Console()


def print_help():
    """Выводит справку по доступным командам."""
    console.print("\n[bold]Доступные команды:[/bold]")
    console.print("  [cyan]help[/cyan]    - Показать эту справку")
    console.print("  [cyan]stats[/cyan]   - Показать статистику запросов")
    console.print("  [cyan]reset[/cyan]   - Очистить историю разговора")
    console.print("  [cyan]history[/cyan] - Показать историю сообщений")
    console.print("  [cyan]exit[/cyan]    - Выйти из чата")
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


def main():
    """Главная функция - запускает интерактивный чат с агентом."""
    console.print("[bold green]SimpAgent CLI[/bold green] — Чат с LLM")
    console.print("Введите [bold]'help'[/bold] для списка команд\n")
    console.print("[dim]Команды: help, stats, reset, history, exit[/dim]\n")

    # Получение модели из переменных окружения
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    
    # Создание агента
    agent = Agent(model=model)

    # Статистика сессии
    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }

    while True:
        try:
            # Получение ввода от пользователя
            user_input = console.input("[bold blue]Вы:[/bold blue] ")

            # Нормализация ввода
            command = user_input.strip().lower()

            # Команда выхода
            if command in ("exit", "quit", "выход"):
                console.print("\n[bold]Статистика сессии:[/bold]")
                print_stats(stats)
                console.print("\n[yellow]До свидания![/yellow]")
                break

            # Команда справки
            if command == "help":
                print_help()
                continue

            # Команда статистики
            if command == "stats":
                print_stats(stats)
                console.print()
                continue

            # Команда очистки истории
            if command == "reset":
                agent.reset_history()
                console.print("[yellow]История очищена.[/yellow]\n")
                continue

            # Команда показа истории
            if command == "history":
                history = agent.get_history()
                console.print(f"[dim]Сообщений в истории: {len(history)}[/dim]\n")
                for i, msg in enumerate(history):
                    role = msg["role"]
                    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    console.print(f"  [{i}] {role}: {content}")
                console.print()
                continue

            # Проверка на пустой ввод
            if not user_input.strip():
                continue

            # Отправка запроса агенту с индикатором загрузки
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(user_input)

            # Обновление статистики
            stats["requests"] += 1
            stats["total_input_tokens"] += result["input_tokens"]
            stats["total_output_tokens"] += result["output_tokens"]
            stats["total_tokens"] += result["total_tokens"]
            stats["total_cost"] += result["cost"]

            # Вывод ответа агента
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
