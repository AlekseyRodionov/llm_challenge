"""
CLI-интерфейс для MCP Pipeline Agent.
"""
import os
from rich.console import Console
from rich.table import Table
from app.agent import Agent
from app.memory_manager import (
    get_all_profiles,
    get_active_profile,
    set_active_profile
)
from app.invariants import (
    get_invariants_list,
    get_all_invariants_from_db,
    add_invariant_to_db,
    remove_invariant_from_db,
    generate_keywords_with_llm,
    get_next_invariant_id
)
from app.mcp_client import MCPClient

console = Console()


def print_help():
    """Выводит справку по доступным командам."""
    console.print("""
[bold]╔══════════════════════════════════════════════════════════╗[/bold]
[bold]║                        СПРАВКА                          ║[/bold]
[bold]╚══════════════════════════════════════════════════════════╝[/bold]

[bold]📋 ОСНОВНЫЕ[/bold]
  help       — показать справку
  stats      — показать статистику запросов
  exit       — выйти из программы

[bold]💾 ПАМЯТЬ[/bold]
  reset            — очистить историю
  clear_working    — очистить рабочую память
  clear_all        — очистить всю память
  history          — показать историю
  show_memory      — показать все слои памяти

[bold]👤 ПРОФИЛИ[/bold]
  profiles      — показать все профили
  profile_use   — сменить профиль (profile_use junior)
  profile_show  — показать активный профиль

[bold]🔒 ИНВАРИАНТЫ[/bold]
  show_invariants   — показать все инварианты
  add_invariant     — добавить инвариант (add_invariant "правило")
  remove_invariant  — удалить инвариант (remove_invariant INV_001)

[bold]⚙️ FSM[/bold]
  task_start   — начать задачу (task_start "создать калькулятор")
  approve      — подтвердить план
  next         — следующий шаг
  pause        — приостановить
  resume       — возобновить
  reset_task   — сбросить задачу
  status       — показать статус

[bold]🎬 ДЕМО[/bold]
  demo — запустить демонстрацию

[bold]🔌 MCP[/bold]
  mcp_start       — запустить MCP сервер
  mcp_list        — показать инструменты
  mcp_call        — вызвать инструмент (mcp_call <tool_name>)
  mcp_disconnect  — отключиться

[bold]📊 PIPELINE[/bold]
  schedule_report interval_seconds=N — запустить scheduler (mcp_call schedule_report 5)
  run_monitoring_pipeline           — запустить обработку (mcp_call run_monitoring_pipeline)
""")


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
    console.print("\n[bold green]╔══════════════════════════════════════════════════════════╗")
    console.print("[bold green]║           MCP Pipeline Agent                              ║")
    console.print("[bold green]╚══════════════════════════════════════════════════════════╝[/bold green]\n")
    
    console.print("\n[bold]📋 ОСНОВНЫЕ[/bold]")
    console.print("  help, stats, exit")
    
    console.print("[bold]💾 ПАМЯТЬ[/bold]")
    console.print("  reset, clear_working, clear_all, history, show_memory")
    
    console.print("[bold]👤 ПРОФИЛИ[/bold]")
    console.print("  profiles, profile_use, profile_show")
    
    console.print("[bold]🔒 ИНВАРИАНТЫ[/bold]")
    console.print("  show_invariants, add_invariant, remove_invariant")
    
    console.print("[bold]⚙️ FSM[/bold]")
    console.print("  task_start, approve, next, pause, resume, reset_task, status")
    
    console.print("[bold]🎬 ДЕМО[/bold]")
    console.print("  demo")
    
    console.print("[bold]🔌 MCP[/bold]")
    console.print("  mcp_start, mcp_list, mcp_call, mcp_disconnect")
    
    console.print("[bold]📊 PIPELINE[/bold]")
    console.print("  schedule_report, run_monitoring_pipeline")
    
    console.print("\n[bold]Введите команду:[/bold]\n")
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(model=model)

    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }
    
    mcp_client = None

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

            if command == "profiles":
                profiles = get_all_profiles()
                active = get_active_profile()
                console.print("\n[bold]Доступные профили:[/bold]")
                for p in profiles:
                    marker = " ✓" if p["name"] == active["name"] else ""
                    console.print(f"  {p['name']}{marker}: {p['description']}")
                console.print()
                continue

            if command == "show_invariants":
                invariants = get_all_invariants_from_db()
                console.print("\n[bold]Системные инварианты:[/bold]")
                for inv in invariants:
                    active_marker = "✓" if inv.get("is_active", True) else "✗"
                    console.print(f"  [cyan]{inv['id']}[/cyan] ({inv['type']}) {active_marker}: {inv['rule']}")
                console.print()
                continue

            if command.startswith("profile_use "):
                profile_name = user_input.strip()[12:].strip()
                if set_active_profile(profile_name):
                    active = get_active_profile()
                    console.print(f"[green]Профиль изменён на: {active['name']}[/green]\n")
                else:
                    console.print(f"[red]Профиль '{profile_name}' не найден[/red]\n")
                continue

            if command == "profile_show":
                active = get_active_profile()
                console.print(f"\n[bold]Активный профиль:[/bold] {active['name']}")
                console.print(f"[bold]Описание:[/bold] {active['description']}\n")
                continue

            # Команды для инвариантов
            if command.startswith("add_invariant "):
                rule_text = user_input[14:].strip().strip('"')
                if not rule_text:
                    console.print("[red]Укажите правило в кавычках: add_invariant \"правило\"[/red]\n")
                    continue
                
                with console.status("[bold green]Генерирую ключевые слова...[/bold green]") as status:
                    keywords = generate_keywords_with_llm(rule_text)
                
                inv_id = add_invariant_to_db("custom", rule_text, keywords)
                
                console.print(f"[green]✓ Инвариант добавлен[/green]")
                console.print(f"  ID: {inv_id}")
                console.print(f"  Type: custom")
                console.print(f"  Rule: {rule_text}")
                console.print(f"  Keywords: {', '.join(keywords[:5])}...")
                console.print()
                continue

            if command.startswith("remove_invariant "):
                inv_id = user_input[17:].strip()
                if not inv_id:
                    console.print("[red]Укажите ID инварианта: remove_invariant <id>[/red]\n")
                    continue
                
                if remove_invariant_from_db(inv_id):
                    console.print(f"[green]✓ Инвариант {inv_id} удалён[/green]\n")
                else:
                    console.print(f"[red]Инвариант {inv_id} не найден[/red]\n")
                continue

            if command == "demo":
                run_demo(agent, stats)
                continue

            # FSM команды
            if command.startswith("task_start "):
                task_text = user_input[11:].strip().strip('"')
                if not task_text:
                    console.print("[red]Укажите описание задачи[/red]\n")
                    continue
                with console.status("[bold green]Планирую...[/bold green]") as status:
                    result = agent.fsm_task_start(task_text)
                if "error" in result:
                    console.print(f"[red]{result['text']}[/red]\n")
                else:
                    console.print(f"\n[bold]Состояние:[/bold] {result.get('state', 'N/A')}")
                    console.print(f"[bold green]Агент:[/bold green] {result['text']}\n")
                continue

            if command == "approve":
                result = agent.fsm_approve()
                if "error" in result:
                    console.print(f"[red]{result['text']}[/red]\n")
                else:
                    console.print(f"[bold]Состояние:[/bold] {result.get('state', 'N/A')}")
                    console.print(f"[green]{result['text']}[/green]\n")
                continue

            if command == "next":
                with console.status("[bold green]Выполняю шаг...[/bold green]") as status:
                    result = agent.fsm_next()
                if "error" in result:
                    console.print(f"[red]{result['text']}[/red]\n")
                else:
                    if "step_text" in result:
                        console.print(f"[bold cyan]Выполняется шаг {result.get('current_step')}:[/bold cyan] {result['step_text']}\n")
                    console.print(f"[bold]Состояние:[/bold] {result.get('state', 'N/A')}")
                    if "current_step" in result:
                        console.print(f"[dim]Шаг {result['current_step']}/{result.get('total_steps', '?')}[/dim]")
                    console.print(f"[bold green]Агент:[/bold green] {result['text']}\n")
                continue

            if command == "pause":
                result = agent.fsm_pause()
                if "error" in result:
                    console.print(f"[red]{result['text']}[/red]\n")
                else:
                    console.print(f"[yellow]{result['text']}[/yellow]\n")
                continue

            if command == "resume":
                result = agent.fsm_resume()
                if "error" in result:
                    console.print(f"[red]{result['text']}[/red]\n")
                else:
                    console.print(f"[green]{result['text']}[/green]\n")
                continue

            if command == "reset_task":
                result = agent.fsm_reset()
                console.print(f"[yellow]{result['text']}[/yellow]\n")
                continue

            if command == "status":
                result = agent.fsm_status()
                console.print(f"\n{result['text']}\n")
                continue

            # MCP команды
            if command == "mcp_start":
                # Запускаем сервер как подпроцесс
                mcp_client = MCPClient()
                if mcp_client.connect():
                    console.print("[green]MCP server started[/green]\n")
                else:
                    console.print("[red]MCP server failed to start[/red]\n")
                    mcp_client = None
                continue

            if command == "mcp_list":
                if mcp_client:
                    tools = mcp_client.list_tools()
                    if tools:
                        console.print("\n[bold]Available MCP tools:[/bold]")
                        tool_descriptions = {
                            "current_time": "текущее время",
                            "get_mock_issues": "демо-задачи",
                            "mock_random_tip": "случайный совет",
                            "schedule_report": "запустить scheduler (interval_seconds=N)",
                            "stop_reports": "остановить scheduler",
                            "get_reports_summary": "статистика сборки",
                            "get_last_reports": "последние 5 отчётов"
                        }
                        for tool in tools:
                            desc = tool_descriptions.get(tool, "")
                            if desc:
                                console.print(f"  * {tool:<25} — {desc}")
                            else:
                                console.print(f"  * {tool}")
                        console.print()
                    else:
                        console.print("[yellow]No tools available[/yellow]\n")
                else:
                    console.print("[yellow]MCP not connected. Use mcp_connect first.[/yellow]\n")
                continue

            if command == "mcp_disconnect":
                if mcp_client:
                    mcp_client.close()
                    mcp_client = None
                    console.print("[yellow]MCP disconnected[/yellow]\n")
                else:
                    console.print("[yellow]MCP not connected[/yellow]\n")
                continue

            if command.startswith("mcp_call "):
                tool_input = user_input[9:].strip()
                if not tool_input:
                    console.print("[red]Укажите название инструмента: mcp_call <tool_name> [args][/red]\n")
                    continue
                if not mcp_client:
                    console.print("[yellow]MCP not connected. Use mcp_connect first.[/yellow]\n")
                    continue
                
                # Парсим имя инструмента и аргументы
                parts = tool_input.split()
                tool_name = parts[0]
                args = {}
                for part in parts[1:]:
                    if "=" in part:
                        key, value = part.split("=", 1)
                        try:
                            args[key] = int(value)
                        except ValueError:
                            args[key] = value
                
                try:
                    result = mcp_client.call_tool(tool_name, args if args else None)
                    if result is not None:
                        console.print(f"[bold]Result:[/bold] {result}\n")
                    else:
                        console.print("[red]Tool execution failed[/red]\n")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]\n")
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
