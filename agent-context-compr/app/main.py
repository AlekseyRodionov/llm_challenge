"""
CLI-интерфейс для Agent Context Compression.
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
    console.print("  [cyan]compress[/cyan] - Запустить демо-диалог со сжатием контекста")
    console.print("  [cyan]context[/cyan]  - Показать контекст агентов (после compress)")
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
    global stats, agent_demo, agent_compressed
    
    agent_demo = None
    agent_compressed = None
    
    console.print("[bold green]Agent Context Compression CLI[/bold green] — Чат со сжатием контекста")
    console.print("Введите [bold]'help'[/bold] для списка команд\n")
    console.print("[dim]Команды: help, stats, reset, history, tokens, fill, compress, context, exit[/dim]\n")

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

            # Команда демо-диалога со сжатием
            if command == "compress":
                DEMO_MESSAGES = [
                    "Привет! Расскажи о себе.",
                    "Какие языки программирования ты знаешь?",
                    "Почему Python стал таким популярным?",
                    "Какие недостатки у Python?",
                    "Для каких задач лучше использовать другие языки?",
                    "Как начать изучать программирование?",
                    "Сколько времени нужно чтобы выучить Python?",
                    "Какие проекты можно сделать на Python новичку?",
                    "Что такое алгоритмы и структуры данных?",
                    "Какие книги по Python ты рекомендуешь?",
                    "Где можно практиковаться в программировании?",
                    "Что такое open source и как участвовать?",
                    "Какие технологии нужно изучить веб-разработчику?",
                    "Что лучше: frontend или backend?",
                    "Как подготовиться к собеседованию?",
                ]
                
                console.print("\n[bold]=== ДЕМО: СРАВНЕНИЕ БЕЗ СЖАТИЯ И СО СЖАТИЕМ ===[/bold]\n")
                
                # Прогон без сжатия
                console.print("[yellow]Этап 1: Прогон без сжатия...[/yellow]\n")
                agent_demo = Agent(model=model, load_history=False, compression_enabled=False)
                stats_no_compress = {
                    "requests": 0,
                    "total_request_tokens": 0,
                    "total_history_tokens": 0,
                    "total_response_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
                responses_no_compress = []
                
                for i, msg in enumerate(DEMO_MESSAGES):
                    console.print(f"[bold]Вопрос {i+1}:[/bold] {msg}")
                    with console.status("[bold green]Думаю...[/bold green]"):
                        result = agent_demo.ask(msg)
                    responses_no_compress.append(result["text"])
                    console.print(f"[green]Ответ:[/green] {result['text']}\n")
                    stats_no_compress["requests"] += 1
                    stats_no_compress["total_request_tokens"] += result["request_tokens"]
                    stats_no_compress["total_history_tokens"] += result["history_tokens"]
                    stats_no_compress["total_response_tokens"] += result["response_tokens"]
                    stats_no_compress["total_tokens"] += result["total_tokens"]
                    stats_no_compress["total_cost"] += result["cost"]
                
                console.print(f"[green]✓ Без сжатия завершено.[/green]")
                console.print(f"  Всего токенов: {stats_no_compress['total_tokens']}")
                console.print(f"  Стоимость: {stats_no_compress['total_cost']:.4f} ₽\n")
                
                # Прогон со сжатием
                console.print("[yellow]Этап 2: Прогон со сжатием...[/yellow]\n")
                agent_compressed = Agent(
                    model=model,
                    load_history=False,
                    compression_enabled=True,
                    keep_last=5,
                    compress_threshold=10
                )
                stats_compressed = {
                    "requests": 0,
                    "total_request_tokens": 0,
                    "total_history_tokens": 0,
                    "total_response_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
                responses_compressed = []
                comp_stats = {"compression_count": 0}
                
                for i, msg in enumerate(DEMO_MESSAGES):
                    console.print(f"[bold]Вопрос {i+1}:[/bold] {msg}")
                    with console.status("[bold green]Думаю...[/bold green]"):
                        result = agent_compressed.ask(msg)
                    responses_compressed.append(result["text"])
                    console.print(f"[green]Ответ:[/green] {result['text']}")
                    
                    comp_stats = agent_compressed.get_compression_stats()
                    if comp_stats.get("compression_count", 0) > 0:
                        console.print(f"[dim]→ Сжатие #{comp_stats['compression_count']} выполнено[/dim]")
                    console.print()
                    
                    stats_compressed["requests"] += 1
                    stats_compressed["total_request_tokens"] += result["request_tokens"]
                    stats_compressed["total_history_tokens"] += result["history_tokens"]
                    stats_compressed["total_response_tokens"] += result["response_tokens"]
                    stats_compressed["total_tokens"] += result["total_tokens"]
                    stats_compressed["total_cost"] += result["cost"]
                
                console.print(f"[green]✓ Со сжатием завершено.[/green]")
                console.print(f"  Всего токенов: {stats_compressed['total_tokens']}")
                console.print(f"  Стоимость: {stats_compressed['total_cost']:.4f} ₽")
                console.print(f"  Сжатий выполнено: {comp_stats.get('compression_count', 0)}\n")
                
                # Финальное сравнение
                console.print("\n[bold]=== ИТОГОВОЕ СРАВНЕНИЕ ===[/bold]\n")
                
                table = Table(title="Сравнение режимов")
                table.add_column("Метрика")
                table.add_column("Без сжатия")
                table.add_column("Со сжатием")
                
                tokens_diff = stats_no_compress['total_tokens'] - stats_compressed['total_tokens']
                percent_diff = (tokens_diff / stats_no_compress['total_tokens']) * 100 if stats_no_compress['total_tokens'] > 0 else 0
                
                table.add_row("Всего токенов", str(stats_no_compress['total_tokens']), str(stats_compressed['total_tokens']))
                table.add_row("Токенов ввода", str(stats_no_compress['total_request_tokens']), str(stats_compressed['total_request_tokens']))
                table.add_row("Токенов вывода", str(stats_no_compress['total_response_tokens']), str(stats_compressed['total_response_tokens']))
                table.add_row("Стоимость (₽)", f"{stats_no_compress['total_cost']:.4f}", f"{stats_compressed['total_cost']:.4f}")
                table.add_row("Экономия токенов", "-", f"{tokens_diff} ({percent_diff:.1f}%)")
                
                console.print(table)
                
                stats["requests"] += stats_no_compress["requests"] + stats_compressed["requests"]
                stats["total_request_tokens"] += stats_no_compress["total_request_tokens"] + stats_compressed["total_request_tokens"]
                stats["total_history_tokens"] += stats_no_compress["total_history_tokens"] + stats_compressed["total_history_tokens"]
                stats["total_response_tokens"] += stats_no_compress["total_response_tokens"] + stats_compressed["total_response_tokens"]
                stats["total_tokens"] += stats_no_compress["total_tokens"] + stats_compressed["total_tokens"]
                stats["total_cost"] += stats_no_compress["total_cost"] + stats_compressed["total_cost"]
                
                console.print(f"[green]Статистика демо добавлена в общую статистику.[/green]\n")
                continue

            # Команда показа контекста
            if command == "context":
                if agent_demo is None and agent_compressed is None:
                    console.print("[yellow]Контекст демо-агентов недоступен. Сначала запустите compress.[/yellow]\n")
                else:
                    if agent_demo is not None:
                        console.print("\n[bold]=== КОНТЕКСТ БЕЗ СЖАТИЯ ===[/bold]\n")
                        history = agent_demo.get_history()
                        for i, msg in enumerate(history):
                            role = msg["role"]
                            content = msg["content"]
                            if len(content) > 100:
                                content = content[:100] + "..."
                            console.print(f"[{i}] {role}: {content}")
                    
                    if agent_compressed is not None:
                        console.print("\n[bold]=== КОНТЕКСТ СО СЖАТИЕМ ===[/bold]\n")
                        history = agent_compressed.get_history()
                        for i, msg in enumerate(history):
                            role = msg["role"]
                            content = msg["content"]
                            if len(content) > 100:
                                content = content[:100] + "..."
                            console.print(f"[{i}] {role}: {content}")
                    
                    comp_stats = agent_compressed.get_compression_stats() if agent_compressed else {}
                    if comp_stats.get("summary"):
                        console.print(f"\n[bold]Summary:[/bold]")
                        console.print(f"  {comp_stats['summary']}")
                console.print()
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
