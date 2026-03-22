"""CLI interface for Grounded Chat Agent."""
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.agent import Agent


console = Console()


def print_help():
    """Print available commands."""
    console.print("\n[bold]Команды:[/bold]")
    console.print("  [cyan]help[/cyan]     - Показать справку")
    console.print("  [cyan]reset[/cyan]    - Очистить историю и состояние")
    console.print("  [cyan]state[/cyan]    - Показать состояние задачи")
    console.print("  [cyan]logs[/cyan]     - Включить/выключить debug")
    console.print("  [cyan]history[/cyan]  - Показать историю")
    console.print("  [cyan]exit[/cyan]     - Выйти")
    console.print()


def print_task_state(task_state: dict):
    """Print current task state."""
    console.print("\n[bold]TASK STATE:[/bold]")
    
    goal = task_state.get("goal", "")
    console.print(f"[cyan]Goal:[/cyan] {goal if goal else 'Не установлен'}")
    
    constraints = task_state.get("constraints", [])
    console.print(f"[cyan]Constraints ({len(constraints)}):[/cyan]")
    if constraints:
        for c in constraints:
            console.print(f"  - {c}")
    else:
        console.print("  (нет)")
    
    known_facts = task_state.get("known_facts", [])
    console.print(f"[cyan]Known facts ({len(known_facts)}):[/cyan]")
    if known_facts:
        for f in known_facts:
            console.print(f"  - {f}")
    else:
        console.print("  (нет)")
    console.print()


def print_history(history: list):
    """Print dialog history."""
    console.print(f"\n[bold]HISTORY ({len(history)} messages):[/bold]")
    if not history:
        console.print("(пустая история)")
    else:
        for i, entry in enumerate(history):
            role = entry.get("role", "user")
            content = entry.get("content", "")
            display = content[:80] + "..." if len(content) > 80 else content
            console.print(f"  [{i}] [cyan]{role}[/cyan]: {display}")
    console.print()


def main():
    """Main chat CLI entry point."""
    console.print("[bold cyan]=== Grounded Chat Agent ===[/bold cyan]")
    console.print("[cyan]RAG + Память задачи + Диалог + Логи[/cyan]")
    console.print()
    console.print("[dim]Команды: help, reset, state, logs, history, exit[/dim]\n")
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(
        model=model,
        rag_enabled=True,
        use_filter=True,
        use_rewrite=True,
        debug_mode=False
    )
    
    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }
    
    console.print("[bold green]Готов к чату![/bold green] Напишите вопрос или help\n")
    
    while True:
        try:
            user_input = console.input("[bold blue]>> [/bold blue] ").strip()
            
            if not user_input:
                continue
            
            command = user_input.lower()
            
            if command in ("exit", "quit", "выход"):
                console.print("\n[bold]Статистика сессии:[/bold]")
                _print_stats(stats)
                console.print("\n[yellow]До свидания![/yellow]\n")
                break
            
            if command == "help":
                print_help()
                continue
            
            if command == "reset":
                agent.reset()
                console.print("[yellow]История и состояние очищены.[/yellow]\n")
                continue
            
            if command == "state":
                task_state = agent.get_task_state()
                print_task_state(task_state)
                continue
            
            if command == "logs":
                debug_status = agent.toggle_debug()
                status = "включен" if debug_status else "выключен"
                console.print(f"[cyan]Debug логи: {status}[/cyan]\n")
                continue
            
            if command == "history":
                history = agent.get_history()
                print_history(history)
                continue
            
            stats["requests"] += 1
            
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(user_input)
            
            stats["total_input_tokens"] += result.get("input_tokens", 0)
            stats["total_output_tokens"] += result.get("output_tokens", 0)
            stats["total_tokens"] += result.get("total_tokens", 0)
            stats["total_cost"] += result.get("cost", 0)
            
            answer = result.get("text", "Не знаю. Уточните вопрос.")
            
            is_fallback = result.get("fallback", False)
            has_sources = "sources" in result
            has_quotes = "quotes" in result
            
            status_indicator = ""
            if is_fallback:
                status_indicator = "[red]❌ Отступление[/red]"
            elif has_sources and has_quotes:
                status_indicator = "[green]✓ Источники + Цитаты[/green]"
            else:
                status_indicator = "[yellow]⚠ Частично[/yellow]"
            
            console.print(Panel(
                answer,
                title=f"Ответ {status_indicator}",
                border_style="green" if not is_fallback else "red"
            ))
            
            if agent.debug_mode:
                chunks = result.get("retrieved_chunks", [])
                console.print(f"[dim]Чанков использовано: {len(chunks)}[/dim]")
            
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n\n[bold]Статистика сессии:[/bold]")
            _print_stats(stats)
            console.print("\n[yellow]Выход (Ctrl+C)[/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[bold red]Ошибка:[/bold red] {e}\n")


def _print_stats(stats: dict):
    """Print session statistics."""
    table = Table(title="Статистика")
    table.add_column("Метрика")
    table.add_column("Значение")
    
    table.add_row("Запросов", str(stats["requests"]))
    table.add_row("Токенов (ввод)", str(stats["total_input_tokens"]))
    table.add_row("Токенов (вывод)", str(stats["total_output_tokens"]))
    table.add_row("Всего токенов", str(stats["total_tokens"]))
    table.add_row("Стоимость", f"{stats['total_cost']:.4f}")
    
    console.print(table)


SCENARIOS = {
    "mkdocs": {
        "name": "MkDocs Deployment",
        "description": "Сценарий настройки и деплоя MkDocs на GitHub Pages",
        "questions": [
            "Хочу задеплоить MkDocs",
            "На GitHub Pages",
            "Проект уже есть",
            "Как настроить?",
            "Как обновлять?",
            "Где хранится конфиг?",
            "Как добавить поиск?",
            "Как изменить тему?",
            "Как собрать сайт?",
            "Как проверить локально?",
            "state"
        ]
    },
    "fire": {
        "name": "Fire CLI",
        "description": "Сценарий создания CLI с Python Fire",
        "questions": [
            "Хочу CLI",
            "На Python",
            "Без argparse",
            "Как проще?",
            "Как передавать аргументы?",
            "Как вызвать функцию?",
            "Как обработать типы?",
            "Можно ли использовать классы?",
            "Как запускать из консоли?",
            "state"
        ]
    }
}


def run_demo(scenario_name: str):
    """
    Run a demo scenario.
    
    Args:
        scenario_name: "mkdocs" or "fire"
    """
    if scenario_name not in SCENARIOS:
        console.print(f"[red]Неизвестный сценарий: {scenario_name}[/red]")
        console.print(f"Доступные: {', '.join(SCENARIOS.keys())}")
        return
    
    scenario = SCENARIOS[scenario_name]
    
    console.print("\n" + "=" * 60)
    console.print(f"[bold cyan]ДЕМО: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]{scenario['description']}[/dim]")
    console.print("=" * 60 + "\n")
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(
        model=model,
        rag_enabled=True,
        use_filter=True,
        use_rewrite=True,
        debug_mode=False
    )
    
    stats = {
        "requests": 0,
        "fallback": 0,
        "sources": 0,
        "quotes": 0
    }
    
    for i, question in enumerate(scenario["questions"], 1):
        console.print(f"\n[bold cyan]>> {question}[/bold cyan]")
        
        result = agent.ask(question)
        
        stats["requests"] += 1
        if result.get("fallback"):
            stats["fallback"] += 1
        if "sources" in result:
            stats["sources"] += 1
        if "quotes" in result:
            stats["quotes"] += 1
        
        answer = result.get("text", "Не знаю. Уточните вопрос.")
        is_fallback = result.get("fallback", False)
        has_sources = "sources" in result
        has_quotes = "quotes" in result
        
        if question == "state":
            print_task_state(agent.get_task_state())
        else:
            status_indicator = ""
            if is_fallback:
                status_indicator = "[red]❌ Отступление[/red]"
            elif has_sources and has_quotes:
                status_indicator = "[green]✓ Источники + Цитаты[/green]"
            else:
                status_indicator = "[yellow]⚠ Частично[/yellow]"
            
            console.print(Panel(
                answer[:500] + ("..." if len(answer) > 500 else ""),
                title=f"Ответ {status_indicator}",
                border_style="green" if not is_fallback else "red"
            ))
    
    console.print("\n" + "=" * 60)
    console.print("[bold]ИТОГИ ДЕМО:[/bold]")
    console.print(f"  Запросов: {stats['requests']}")
    console.print(f"  Отступлений: {stats['fallback']} ({stats['fallback']/stats['requests']*100:.0f}%)")
    console.print(f"  С источниками: {stats['sources']} ({stats['sources']/stats['requests']*100:.0f}%)")
    console.print(f"  С цитатами: {stats['quotes']} ({stats['quotes']/stats['requests']*100:.0f}%)")
    console.print("=" * 60 + "\n")
    
    console.print("[dim]Логи сохранены в logs/rag_debug.log[/dim]\n")


if __name__ == "__main__":
    main()
