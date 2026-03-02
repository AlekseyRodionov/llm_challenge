"""
CLI-интерфейс для Agent с управлением контекстом.
Запускает интерактивный чат с LLM агентом с выбором стратегии.
"""
import os
import sys
import signal
from rich.console import Console
from rich.table import Table
from app.agent import Agent
from app.storage import MessageStorage

console = Console()

DEMO_SCENARIOS = {
    "sliding": {
        "name": "Проверка памяти (10 сообщений, N=5)",
        "check_facts": {
            "имя_кота": ["барсик"],
            "город": ["москв"],
            "последний_вопрос": ["python"]
        },
        "messages": [
            "Запомни: моего кота зовут Барсик",
            "Я живу в городе Москва",
            "Мне 25 лет",
            "Я работаю врачом",
            "Сколько будет 2+2?",
            "Какой сегодня день недели?",
            "Расскажи анекдот",
            "Что такое Python?",
            "О чем был последний вопрос?",
            "Как зовут моего кота и где я живу?",
        ]
    },
    "sticky": {
        "name": "Проверка памяти (10 сообщений, N=5)",
        "check_facts": {
            "имя_кота": ["барсик"],
            "город": ["москв"],
            "последний_вопрос": ["python"]
        },
        "messages": [
            "Запомни: моего кота зовут Барсик",
            "Я живу в городе Москва",
            "Мне 25 лет",
            "Я работаю врачом",
            "Сколько будет 2+2?",
            "Какой сегодня день недели?",
            "Расскажи анекдот",
            "Что такое Python?",
            "О чем был последний вопрос?",
            "Как зовут моего кота и где я живу?",
        ]
    },
    "branching": {
        "name": "Ветвление с переключениями",
        "messages": [
            ("main", "Делаем интернет-магазин одежды"),
            ("main", "Бюджет 100 тысяч, срок 2 месяца"),
            ("main", "Нужна корзина и оплата картой"),
            ("switch", None),
            ("alt", "А если добавить доставку дронами?"),
            ("alt", "Это легально в России?"),
            ("alt", "Сколько стоит?"),
            ("switch", None),
            ("main", "Продолжим про магазин, добавим акции"),
            ("main", "Про сроки доставки забыли"),
            ("switch", None),
            ("alt", "Сколько стоит внедрение дронов?"),
            ("alt", "Какие ограничения по весу?"),
            ("alt", "Реально сделать за 2 месяца?"),
            ("switch", None),
            ("main", "Подведи итог по магазину"),
            ("main", "Подведи итог по доставке дронами"),
        ]
    }
}


def print_help():
    """Выводит справку по доступным командам."""
    console.print("\n[bold]Доступные команды:[/bold]")
    console.print("  [cyan]help[/cyan]      - Показать эту справку")
    console.print("  [cyan]stats[/cyan]     - Показать статистику (текущая / общая)")
    console.print("  [cyan]reset[/cyan]     - Очистить историю разговора")
    console.print("  [cyan]history[/cyan]   - Показать историю сообщений")
    console.print("  [cyan]strategy[/cyan]  - Показать/изменить стратегию")
    console.print("  [cyan]switch[/cyan]    - Переключить ветку (для Branching)")
    console.print("  [cyan]facts[/cyan]     - Показать факты (для Sticky Facts)")
    console.print("  [cyan]branches[/cyan]  - Показать ветки (для Branching)")
    console.print("  [cyan]demo[/cyan]      - Запустить демо режим")
    console.print("  [cyan]exit[/cyan]      - Выйти из чата")
    console.print()


def print_stats(stats: dict, title: str = "Статистика сессии"):
    """Выводит статистику по запросам."""
    table = Table(title=title)
    table.add_column("Метрика")
    table.add_column("Значение")

    table.add_row("Запросов", str(stats["requests"]))
    table.add_row("Всего токенов (input)", str(stats["total_input_tokens"]))
    table.add_row("Всего токенов (output)", str(stats["total_output_tokens"]))
    table.add_row("Всего токенов", str(stats["total_tokens"]))
    table.add_row("Общая стоимость (₽)", str(round(stats["total_cost"], 4)))

    console.print(table)


def choose_strategy() -> str:
    """Предлагает выбрать стратегию управления контекстом."""
    console.print("\n[bold]Выберите стратегию управления контекстом:[/bold]")
    console.print("  [cyan]1[/cyan] - Sliding Window (последние N сообщений)")
    console.print("  [cyan]2[/cyan] - Sticky Facts (ключ-значение память)")
    console.print("  [cyan]3[/cyan] - Branching (ветвление диалога)")
    
    while True:
        choice = console.input("Выбор (1/2/3): ").strip()
        if choice == "1":
            return "sliding"
        elif choice == "2":
            return "sticky"
        elif choice == "3":
            return "branching"


def print_strategy_info(agent: Agent):
    """Выводит информацию о текущей стратегии."""
    console.print(f"\n[bold]Стратегия:[/bold] {agent.get_strategy_display()}")
    
    if agent.get_strategy_name() == "branching":
        branch = agent.get_current_branch()
        console.print(f"[bold]Текущая ветка:[/bold] {branch}")
        branches = agent.get_all_branches()
        console.print(f"[bold]Всего веток:[/bold] {len(branches)}")
        for name, msgs in branches.items():
            count = len([m for m in msgs if m.get("role") in ("user", "assistant")])
            console.print(f"  - {name}: {count} сообщений")


def analyze_memory(responses: list, check_facts: dict) -> dict:
    """Анализирует, запомнил ли LLM ключевые факты."""
    if not responses or not check_facts:
        return {"remembered": {}, "forgot": {}}
    
    last_response = responses[-1].get("response", "").lower() if responses else ""
    prev_response = responses[-2].get("response", "").lower() if len(responses) > 1 else ""
    
    remembered = {}
    forgot = {}
    
    for fact_name, keywords in check_facts.items():
        found_last = any(kw.lower() in last_response for kw in keywords)
        found_prev = any(kw.lower() in prev_response for kw in keywords)
        
        if found_last or found_prev:
            remembered[fact_name] = "✓"
        else:
            forgot[fact_name] = "✗"
    
    return {"remembered": remembered, "forgot": forgot}


def print_memory_analysis(memory_analysis: dict):
    """Выводит анализ памяти."""
    if not memory_analysis.get("remembered") and not memory_analysis.get("forgot"):
        return
    
    remembered = memory_analysis.get("remembered", {})
    forgot = memory_analysis.get("forgot", {})
    
    if remembered:
        console.print("\n[green]✓ Помнит:[/green]")
        for k in remembered.keys():
            console.print(f"  ✓ {k}")
    
    if forgot:
        console.print("\n[red]✗ Забыла:[/red]")
        for k in forgot.keys():
            console.print(f"  ✗ {k}")


def run_demo(agent: Agent, strategy_name: str, all_stats: dict) -> dict:
    """Запускает демо режим для выбранной стратегии."""
    scenario = DEMO_SCENARIOS[strategy_name]
    
    console.print("\n" + "="*60)
    console.print(f"[bold magenta]ДEMO: {scenario['name']}[/bold magenta]")
    console.print(f"[dim]Стратегия: {agent.get_strategy_display()}[/dim]")
    console.print("="*60)
    
    agent.reset_history()
    
    demo_stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "responses": []
    }
    
    if strategy_name == "branching":
        for i, msg_data in enumerate(scenario["messages"]):
            action, content = msg_data
            
            if action == "switch":
                agent.switch_branch()
                branch = agent.get_current_branch()
                console.print(f"\n[yellow]>>> Переключение на ветку: {branch}[/yellow]")
                continue
            
            console.print(f"\n[bold cyan]Сообщение {i+1} ({action}):[/bold cyan] {content}")
            
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(content)
            
            demo_stats["requests"] += 1
            demo_stats["total_input_tokens"] += result["input_tokens"]
            demo_stats["total_output_tokens"] += result["output_tokens"]
            demo_stats["total_tokens"] += result["total_tokens"]
            demo_stats["total_cost"] += result["cost"]
            
            response_preview = result["text"][:100] + "..." if len(result["text"]) > 100 else result["text"]
            console.print(f"[bold green]Агент:[/bold green] {response_preview}")
            console.print(f"[dim]Токены: in={result['input_tokens']}, out={result['output_tokens']}, всего={result['total_tokens']}[/dim]")
            
            demo_stats["responses"].append({
                "message": content,
                "response": result["text"],
                "tokens": result["total_tokens"]
            })
    else:
        for i, msg in enumerate(scenario["messages"]):
            console.print(f"\n[bold cyan]Сообщение {i+1}:[/bold cyan] {msg}")
            
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(msg)
            
            demo_stats["requests"] += 1
            demo_stats["total_input_tokens"] += result["input_tokens"]
            demo_stats["total_output_tokens"] += result["output_tokens"]
            demo_stats["total_tokens"] += result["total_tokens"]
            demo_stats["total_cost"] += result["cost"]
            
            response_preview = result["text"][:100] + "..." if len(result["text"]) > 100 else result["text"]
            console.print(f"[bold green]Агент:[/bold green] {response_preview}")
            console.print(f"[dim]Токены: in={result['input_tokens']}, out={result['output_tokens']}, всего={result['total_tokens']}[/dim]")
            
            demo_stats["responses"].append({
                "message": msg,
                "response": result["text"],
                "tokens": result["total_tokens"]
            })
    
    console.print("\n" + "="*60)
    console.print(f"[bold magenta]РЕЗУЛЬТАТ ДEMO[/bold magenta]")
    console.print("="*60)
    
    if strategy_name == "sticky":
        facts = agent.get_facts()
        if facts:
            console.print("\n[bold]Сохранённые факты:[/bold]")
            for key, value in facts.items():
                console.print(f"  - {key}: {value}")
    
    if strategy_name == "branching":
        branches = agent.get_all_branches()
        console.print("\n[bold]Итоговое состояние веток:[/bold]")
        branch_info = {}
        for name, msgs in branches.items():
            count = len([m for m in msgs if m.get("role") in ("user", "assistant")])
            console.print(f"  - {name}: {count} сообщений")
            branch_info[name] = count
        demo_stats["branches"] = branch_info
        
        responses = demo_stats.get("responses", [])
        if len(responses) >= 2:
            last_two = responses[-2:]
            console.print("\n[bold]Ответы на итоговые вопросы:[/bold]")
            for r in last_two:
                q = r.get("message", "")[:50]
                a = r.get("response", "")[:150] + "..." if len(r.get("response", "")) > 150 else r.get("response", "")
                console.print(f"  [cyan]В:[/cyan] {q}")
                console.print(f"  [green]О:[/green] {a}\n")
    
    print_stats(demo_stats, f"Статистика демо ({strategy_name})")
    
    if strategy_name in ("sliding", "sticky") and "check_facts" in scenario:
        check_facts = scenario["check_facts"]
        memory_analysis = analyze_memory(demo_stats["responses"], check_facts)
        print_memory_analysis(memory_analysis)
        demo_stats["memory_analysis"] = memory_analysis
    
    all_stats[strategy_name] = demo_stats
    
    return demo_stats


def main():
    """Главная функция - запускает интерактивный чат с агентом."""
    console.print("[bold green]Agent Managed Context CLI[/bold green] — Управление контекстом")
    console.print("Введите [bold]'help'[/bold] для списка команд\n")
    console.print("[dim]Команды: help, stats, reset, history, strategy, switch, facts, branches, demo, exit[/dim]\n")

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
    
    all_stats = {}
    agent = Agent(model=model, load_history=load_history, strategy="sliding")
    
    def signal_handler(sig, frame):
        agent.save_history()
        console.print("\n[yellow]История сохранена.[/yellow]")
        console.print("\n[bold]Статистика сессии:[/bold]")
        print_stats(stats)
        
        if all_stats:
            console.print("\n[bold]Общая статистика по стратегиям:[/bold]")
            for strat_name, strat_stats in all_stats.items():
                console.print(f"  {strat_name}: {strat_stats['total_tokens']} токенов, {strat_stats['requests']} запросов, {round(strat_stats['total_cost'], 4)} ₽")
        
        console.print("\n[yellow]Выход (Ctrl+C)[/yellow]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    print_strategy_info(agent)

    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }

    while True:
        try:
            prefix = f"[bold blue]Вы [{agent.get_strategy_display()}][/bold blue]"
            if agent.get_strategy_name() == "branching":
                prefix = f"[bold blue]Вы [{agent.get_current_branch()}][/bold blue]"
            user_input = console.input(f"{prefix}: ")

            command = user_input.strip().lower()

            if command in ("exit", "quit", "выход"):
                agent.save_history()
                console.print("\n[yellow]История сохранена.[/yellow]")
                
                if all_stats:
                    table = Table(title="Сравнение стратегий")
                    table.add_column("Стратегия", style="cyan")
                    table.add_column("Токены", justify="right")
                    table.add_column("Запросы", justify="right")
                    table.add_column("Стоимость", justify="right")
                    table.add_column("Память", justify="center")
                    table.add_column("Ветки", justify="center")
                    
                    for strat_name, strat_stats in all_stats.items():
                        tokens = strat_stats.get("total_tokens", 0)
                        requests = strat_stats.get("requests", 0)
                        cost = round(strat_stats.get("total_cost", 0), 4)
                        
                        memory = strat_stats.get("memory_analysis")
                        if memory:
                            remembered = memory.get("remembered", {})
                            forgot = memory.get("forgot", {})
                            total = len(remembered) + len(forgot)
                            mem_count = f"{len(remembered)}/{total}" if total > 0 else "-"
                        else:
                            mem_count = "-"
                        
                        branches = strat_stats.get("branches")
                        if branches:
                            branch_str = f"m:{branches.get('main', 0)},a:{branches.get('alt', 0)}"
                        else:
                            branch_str = "-"
                        
                        table.add_row(strat_name, str(tokens), str(requests), f"{cost} ₽", mem_count, branch_str)
                    
                    console.print(table)
                    
                    console.print("\n[bold]Анализ стратегий:[/bold]")
                    console.print("""
[bold cyan]Sliding Window:[/bold cyan]
  ✓ Плюсы: Простота, автоматически
  ✗ Минусы: Теряет ранний контекст, нет контроля над важными данными
  → Качество: ++ (зависит от N — при N=5 теряет данные за пределами окна)

[bold cyan]Sticky Facts:[/bold cyan]
  ✓ Плюсы: Сохраняет ключевые факты, прозрачность (/facts)
  ✗ Минусы: Ограниченный набор фактов, зависит от качества extraction
  → Качество: +++ (3/3 — все факты сохранены в memory)

[bold cyan]Branching:[/bold cyan]
  ✓ Плюсы: Полный контекст в каждой ветке, можно исследовать альтернативы
  ✗ Минусы: Сложнее управление
  → Качество: +++ (полный контекст сохранён в обеих ветках)
""")
                
                console.print("\n[yellow]До свидания![/yellow]")
                break

            if command == "help":
                print_help()
                continue

            if command == "stats":
                if all_stats:
                    table = Table(title="Сравнение стратегий")
                    table.add_column("Стратегия", style="cyan")
                    table.add_column("Токены", justify="right")
                    table.add_column("Запросы", justify="right")
                    table.add_column("Стоимость", justify="right")
                    table.add_column("Память", justify="center")
                    table.add_column("Качество", justify="center")
                    table.add_column("Ветки", justify="center")
                    
                    quality_map = {
                        "sliding": "++",
                        "sticky": "+++",
                        "branching": "+++"
                    }
                    
                    for strat_name, strat_stats in all_stats.items():
                        tokens = strat_stats.get("total_tokens", 0)
                        requests = strat_stats.get("requests", 0)
                        cost = round(strat_stats.get("total_cost", 0), 4)
                        
                        memory = strat_stats.get("memory_analysis")
                        if memory:
                            remembered = memory.get("remembered", {})
                            forgot = memory.get("forgot", {})
                            total = len(remembered) + len(forgot)
                            mem_count = f"{len(remembered)}/{total}" if total > 0 else "-"
                        else:
                            mem_count = "-"
                        
                        branches = strat_stats.get("branches")
                        if branches:
                            branch_str = f"m:{branches.get('main', 0)},a:{branches.get('alt', 0)}"
                        else:
                            branch_str = "-"
                        
                        quality = quality_map.get(strat_name, "-")
                        
                        table.add_row(strat_name, str(tokens), str(requests), f"{cost} ₽", mem_count, quality, branch_str)
                    
                    console.print(table)
                    
                    console.print("\n[bold]Анализ стратегий:[/bold]")
                    console.print("""
[bold cyan]Sliding Window:[/bold cyan]
  ✓ Плюсы: Простота, автоматически
  ✗ Минусы: Теряет ранний контекст, нет контроля над важными данными
  → Качество: ++ (зависит от N — при N=5 теряет данные за пределами окна)

[bold cyan]Sticky Facts:[/bold cyan]
  ✓ Плюсы: Сохраняет ключевые факты, прозрачность (/facts)
  ✗ Минусы: Ограниченный набор фактов, зависит от качества extraction
  → Качество: +++ (3/3 — все факты сохранены в memory)

[bold cyan]Branching:[/bold cyan]
  ✓ Плюсы: Полный контекст в каждой ветке, можно исследовать альтернативы
  ✗ Минусы: Сложнее управление
  → Качество: +++ (полный контекст сохранён в обеих ветках)
""")
                console.print()
                continue

            if command == "reset":
                agent.reset_history()
                console.print("[yellow]История очищена.[/yellow]\n")
                print_strategy_info(agent)
                continue

            if command == "history":
                history = agent.get_history()
                console.print(f"[dim]Сообщений в истории: {len(history)}[/dim]\n")
                for i, msg in enumerate(history):
                    role = msg["role"]
                    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    console.print(f"  [{i}] {role}: {content}")
                console.print()
                continue

            if command == "strategy":
                console.print(f"\n[bold]Текущая стратегия:[/bold] {agent.get_strategy_display()}")
                console.print("Изменить стратегию?")
                console.print("  [cyan]1[/cyan] - Sliding Window")
                console.print("  [cyan]2[/cyan] - Sticky Facts")
                console.print("  [cyan]3[/cyan] - Branching")
                console.print("  [cyan]n[/cyan]  - Не менять")
                
                choice = console.input("Выбор: ").strip().lower()
                if choice in ("1", "2", "3"):
                    strategy_map = {"1": "sliding", "2": "sticky", "3": "branching"}
                    agent.set_strategy(strategy_map[choice])
                    console.print(f"[green]Стратегия изменена на: {agent.get_strategy_display()}[/green]\n")
                print_strategy_info(agent)
                continue

            if command == "switch":
                if agent.get_strategy_name() != "branching":
                    console.print("[yellow]Переключение веток доступно только в стратегии Branching[/yellow]\n")
                    continue
                
                new_branch = agent.switch_branch()
                console.print(f"[green]Переключено на ветку: {new_branch}[/green]\n")
                print_strategy_info(agent)
                continue

            if command == "facts":
                facts = agent.get_facts()
                if facts:
                    console.print("\n[bold]Сохранённые факты:[/bold]")
                    for key, value in facts.items():
                        console.print(f"  - {key}: {value}")
                else:
                    console.print("[dim]Факты пока не сохранены[/dim]")
                console.print()
                continue

            if command == "branches":
                if agent.get_strategy_name() != "branching":
                    console.print("[yellow]Ветки доступны только в стратегии Branching[/yellow]\n")
                    continue
                
                branches = agent.get_all_branches()
                console.print("\n[bold]Ветки диалога:[/bold]")
                for name, msgs in branches.items():
                    count = len([m for m in msgs if m.get("role") in ("user", "assistant")])
                    marker = " ←" if name == agent.get_current_branch() else ""
                    console.print(f"  [cyan]{name}[/cyan]{marker}: {count} сообщений")
                console.print()
                continue

            if command == "demo":
                console.print("\n[bold]Выберите стратегию для демо:[/bold]")
                console.print("  [cyan]1[/cyan] - Sliding Window")
                console.print("  [cyan]2[/cyan] - Sticky Facts")
                console.print("  [cyan]3[/cyan] - Branching")
                
                choice = console.input("Выбор (1/2/3): ").strip()
                strategy_map = {"1": "sliding", "2": "sticky", "3": "branching"}
                
                if choice in strategy_map:
                    demo_strategy = strategy_map[choice]
                    agent.set_strategy(demo_strategy)
                    run_demo(agent, demo_strategy, all_stats)
                    console.print("\n[green]Демо завершено. Возврат в чат.[/green]\n")
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
            agent.save_history()
            console.print("\n[yellow]История сохранена.[/yellow]")
            console.print("\n[bold]Статистика сессии:[/bold]")
            print_stats(stats)
            
            if all_stats:
                console.print("\n[bold]Общая статистика по стратегиям:[/bold]")
                for strat_name, strat_stats in all_stats.items():
                    console.print(f"  {strat_name}: {strat_stats['total_tokens']} токенов, {strat_stats['requests']} запросов")
            
            console.print("\n[yellow]Выход (Ctrl+C)[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Ошибка:[/bold red] {e}")


if __name__ == "__main__":
    main()
