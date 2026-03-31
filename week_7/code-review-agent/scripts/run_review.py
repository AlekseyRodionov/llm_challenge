#!/usr/bin/env python3
"""
Скрипт для запуска AI Code Review с цветным выводом.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.reviewer import review_code_simple


console = Console()


def print_header():
    """Выводит заголовок приложения."""
    header = Text()
    header.append("AI Code Review Agent\n", style="bold cyan")
    header.append("Version: 1.0\n", style="dim")
    header.append("Model: gpt-4o-mini\n\n", style="dim")
    header.append("• Анализ кода\n", style="white")
    header.append("• Безопасность\n", style="white")
    header.append("• Архитектура\n", style="white")
    header.append("• Рекомендации", style="white")
    
    console.print(Panel(header, border_style="cyan", padding=(0, 2)))
    console.print()


def parse_review_output(text: str) -> dict:
    """Парсит вывод LLM на секции."""
    sections = {
        "Bugs": [],
        "Security": [],
        "Architecture": [],
        "Code Quality": [],
        "Suggestions": []
    }
    
    current_section = None
    
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Определяем секцию
        for section in sections.keys():
            if line.startswith(section):
                current_section = section
                break
        
        # Добавляем строку в текущую секцию
        if current_section and line.startswith("-"):
            sections[current_section].append(line)
    
    return sections


def get_severity_color(line: str) -> str:
    """Определяет цвет по уровню серьёзности."""
    line_upper = line.upper()
    if "[HIGH]" in line_upper:
        return "red"
    elif "[MEDIUM]" in line_upper:
        return "yellow"
    else:
        return "white"


def print_review_colored(review_text: str):
    """Выводит review с цветами и панелями."""
    sections = parse_review_output(review_text)
    
    # Заголовок
    console.print(Panel.fit(
        "[bold cyan]AI Code Review[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))
    console.print()
    
    # Bugs
    if sections["Bugs"]:
        console.print("[bold red]🐛 BUGS (ОШИБКИ)[/bold red]")
        for line in sections["Bugs"]:
            color = get_severity_color(line)
            console.print(f"  [{color}]{line}[/{color}]")
        console.print()
    
    # Security
    if sections["Security"]:
        console.print("[bold red]🔒 SECURITY (БЕЗОПАСНОСТЬ)[/bold red]")
        for line in sections["Security"]:
            color = get_severity_color(line)
            console.print(f"  [{color}]{line}[/{color}]")
        console.print()
    
    # Architecture
    if sections["Architecture"]:
        console.print("[bold yellow]🏗️ ARCHITECTURE (АРХИТЕКТУРА)[/bold yellow]")
        for line in sections["Architecture"]:
            color = get_severity_color(line)
            console.print(f"  [{color}]{line}[/{color}]")
        console.print()
    
    # Code Quality
    if sections["Code Quality"]:
        console.print("[bold blue]📝 CODE QUALITY (КАЧЕСТВО КОДА)[/bold blue]")
        for line in sections["Code Quality"]:
            color = get_severity_color(line)
            console.print(f"  [{color}]{line}[/{color}]")
        console.print()
    
    # Suggestions
    if sections["Suggestions"]:
        console.print("[bold green]💡 SUGGESTIONS (РЕКОМЕНДАЦИИ)[/bold green]")
        for line in sections["Suggestions"]:
            color = get_severity_color(line)
            console.print(f"  [{color}]{line}[/{color}]")
        console.print()
    
    # Если нет проблем
    if not any(sections.values()):
        console.print(Panel.fit(
            "[green]Проблем не обнаружено ✓[/green]",
            border_style="green"
        ))


def main():
    print_header()
    
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/bold red] python scripts/run_review.py <diff_file>")
        console.print("[dim]Example:[/dim] python scripts/run_review.py scripts/demo_diff.txt")
        sys.exit(1)
    
    diff_file = sys.argv[1]
    
    if not os.path.exists(diff_file):
        console.print(f"[bold red]Error:[/bold red] File not found: {diff_file}")
        sys.exit(1)
    
    console.print(f"[dim]Reading diff from:[/dim] {diff_file}")
    
    with open(diff_file, "r", encoding="utf-8") as f:
        diff_text = f.read()
    
    if not diff_text.strip():
        console.print("[bold red]Error:[/bold red] Empty diff file")
        sys.exit(1)
    
    console.print()
    console.print("[bold cyan]Running code review...[/bold cyan]")
    console.print()
    
    result = review_code_simple(diff_text)
    
    print_review_colored(result["review"])
    
    # Metrics
    console.print()
    table = Table(title="📊 Metrics", show_header=False)
    table.add_column("Key", style="dim")
    table.add_column("Value", style="cyan")
    
    metrics = result.get("metrics", {})
    table.add_row("Changed files", str(metrics.get("changed_files", 0)))
    table.add_row("Input tokens", str(metrics.get("input_tokens", 0)))
    table.add_row("Output tokens", str(metrics.get("output_tokens", 0)))
    table.add_row("Cost", f"{metrics.get('cost', 0):.6f} RUB")
    
    console.print(table)


if __name__ == "__main__":
    main()
