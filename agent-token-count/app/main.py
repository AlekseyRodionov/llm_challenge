"""
CLI-интерфейс для Agent Token Count.
Запускает интерактивный чат с LLM агентом и подсчетом токенов.
"""
import os
import sys
import signal
from rich.console import Console
from rich.table import Table
from app.agent import Agent
from app.storage import MessageStorage

console = Console()


def print_help():
    """Выводит справку по доступным командам."""
    console.print("\n[bold]Доступные команды:[/bold]")
    console.print("  [cyan]help[/cyan]      - Показать эту справку")
    console.print("  [cyan]stats[/cyan]     - Показать статистику запросов")
    console.print("  [cyan]reset[/cyan]     - Очистить историю разговора")
    console.print("  [cyan]history[/cyan]  - Показать историю сообщений")
    console.print("  [cyan]tokens[/cyan]   - Показать текущие токены")
    console.print("  [cyan]fill[/cyan]      - Добавить 10000 токенов для симуляции")
    console.print("  [cyan]exit[/cyan]      - Выйти из чата")
    console.print()


def print_stats(stats: dict):
    """Выводит статистику по запросам."""
    table = Table(title="Статистика сессии")
    table.add_column("Метрика")
    table.add_column("Значение")

    table.add_row("Запросов", str(stats["requests"]))
    table.add_row("Токенов запроса (сумма)", str(stats["total_request_tokens"]))
    table.add_row("Токенов истории (сумма)", str(stats["total_history_tokens"]))
    table.add_row("Токенов ответа (сумма)", str(stats["total_response_tokens"]))
    table.add_row("Всего токенов", str(stats["total_tokens"]))
    table.add_row("Общая стоимость (₽)", str(stats["total_cost"]))

    console.print(table)


def print_token_info(result: dict):
    """Выводит информацию о токенах последнего запроса."""
    limit = result["limit_info"]
    
    console.print("\n[bold]Токены:[/bold]")
    console.print(f"  Запрос: {result['request_tokens']}")
    console.print(f"  История: {result['history_tokens']}")
    console.print(f"  Ответ:   {result['response_tokens']}")
    console.print(f"  ─────────────")
    console.print(f"  Всего:   {result['total_tokens']}")
    
    console.print(f"\n[bold]Лимит:[/bold]")
    console.print(f"  Использовано: {limit['total']} / {limit['max']} ({limit['percent']}%)")
    console.print(f"  Осталось: {limit['remaining']}")
    
    if limit["overflow"]:
        console.print(f"\n[bold red]⚠ ПРЕВЫШЕН ЛИМИТ![/bold red]")
    elif limit["percent"] > 90:
        console.print(f"\n[bold yellow]⚠ Внимание: осталось менее 10% лимита![/bold yellow]")
    elif limit["percent"] > 75:
        console.print(f"\n[yellow]⚠ Приближаемся к лимиту (>75%)[/yellow]")
    
    console.print(f"  Стоимость: {result['cost']} ₽\n")


def main():
    """Главная функция - запускает интерактивный чат с агентом."""
    console.print("[bold green]Agent Token Count CLI[/bold green] — Чат с подсчетом токенов")
    console.print("Введите [bold]'help'[/bold] для списка команд\n")
    console.print("[dim]Команды: help, stats, reset, history, tokens, fill, exit[/dim]\n")

    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    
    storage = MessageStorage()
    load_history = False
    
    if storage.has_history():
        msg_count = storage.get_message_count()
        console.print(f"[yellow]Найдена сохраненная история ({msg_count} сообщений).[/yellow]")
        while True:
            answer = console.input("Загрузить историю? (y/n): ").strip().lower()
            if answer in ("y", "да", "yes"):
                load_history = True
                console.print("[green]История загружена.[/green]\n")
                break
            elif answer in ("n", "нет", "no"):
                console.print("[yellow]Начинаем с чистого листа.[/yellow]\n")
                break
    
    agent = Agent(model=model, load_history=load_history)
    
    def signal_handler(sig, frame):
        agent.save_history()
        console.print("\n[yellow]История сохранена.[/yellow]")
        console.print("\n[bold]Статистика сессии:[/bold]")
        print_stats(stats)
        console.print("\n[yellow]Выход (Ctrl+C)[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    stats = {
        "requests": 0,
        "total_request_tokens": 0,
        "total_history_tokens": 0,
        "total_response_tokens": 0,
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
                agent.save_history()
                console.print("\n[yellow]История сохранена.[/yellow]")
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

            # Команда показа токенов
            if command == "tokens":
                from app.llm_client import get_history_tokens, check_token_limit
                history = agent.get_history()
                model = agent.model
                history_tokens = get_history_tokens(history, model)
                limit = check_token_limit(history_tokens, 0, model)
                console.print(f"\n[bold]Текущее состояние:[/bold]")
                console.print(f"  Сообщений в истории: {len(history)}")
                console.print(f"  Токенов истории: {history_tokens} → {limit['total']} (LLM)")
                console.print(f"  Лимит: {limit['total']} / {limit['max']} ({limit['percent']}%)\n")
                continue

            # Команда симуляции переполнения
            if command == "fill":
                fill_tokens = 80000
                dummy_text = "Lorem ipsum dolor sit amet consectetur adipiscing elit. " * 4500
                agent.messages.append({"role": "user", "content": dummy_text})
                agent.messages.append({"role": "assistant", "content": "Dummy response for simulation. " * 4500})
                
                from app.llm_client import get_history_tokens, check_token_limit
                history_tokens = get_history_tokens(agent.messages, agent.model)
                limit = check_token_limit(history_tokens, 0, agent.model)
                
                console.print(f"[yellow]⚠ Добавлено ~{fill_tokens} мусорных токенов в историю.[/yellow]")
                console.print(f"  Сообщений в истории: {len(agent.messages)}")
                console.print(f"  Токенов истории: {history_tokens} → {limit['total']} (LLM)")
                console.print(f"  Лимит: {limit['total']} / {limit['max']} ({limit['percent']}%)\n")
                continue

            # Проверка на пустой ввод
            if not user_input.strip():
                continue

            # Отправка запроса агенту с индикатором загрузки
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(user_input)

            stats["requests"] += 1
            stats["total_request_tokens"] += result["request_tokens"]
            stats["total_history_tokens"] += result["history_tokens"]
            stats["total_response_tokens"] += result["response_tokens"]
            stats["total_tokens"] += result["total_tokens"]
            stats["total_cost"] += result["cost"]

            console.print(f"\n[bold green]Агент:[/bold green] {result['text']}\n")
            
            print_token_info(result)

        except KeyboardInterrupt:
            agent.save_history()
            console.print("\n[yellow]История сохранена.[/yellow]")
            console.print("\n[bold]Статистика сессии:[/bold]")
            print_stats(stats)
            console.print("\n[yellow]Выход (Ctrl+C)[/yellow]")
            break
        except Exception as e:
            error_msg = str(e)
            if "maximum context length" in error_msg.lower() or "context_length" in error_msg.lower():
                console.print(f"\n[bold red]⚠ ПРЕВЫШЕН ЛИМИТ![/bold red]")
                console.print(f"[yellow]Ошибка от LLM:[/yellow] {error_msg}\n")
                console.print("[yellow]Введите 'reset' чтобы очистить историю.[/yellow]\n")
            else:
                console.print(f"[bold red]Ошибка:[/bold red] {e}")


if __name__ == "__main__":
    main()
