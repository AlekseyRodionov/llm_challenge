"""Evaluator module for comparing RAG modes with Sources and Quotes validation."""
import os
import sys
import re
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from rich.console import Console
from rich.panel import Panel

from agent import Agent


console = Console()


QUESTIONS = [
    # БАЗОВЫЕ (1-3) — RAG должен отвечать уверенно
    {
        "question": "Что такое Python Fire?",
        "category": "базовый",
        "expected_keywords": ["fire", "cli", "библиотек"]
    },
    {
        "question": "Как установить Python Fire?",
        "category": "базовый",
        "expected_keywords": ["pip", "install", "fire"]
    },
    {
        "question": "Что такое MkDocs?",
        "category": "базовый",
        "expected_keywords": ["mkdocs", "документац", "статич"]
    },
    # СЛОЖНЫЕ (4-6) — проверка retrieval + filter
    {
        "question": "Можно ли использовать Fire с классами Python?",
        "category": "сложный",
        "expected_keywords": ["класс", "python", "fire"]
    },
    {
        "question": "Какие настройки доступны в mkdocs.yml?",
        "category": "сложный",
        "expected_keywords": ["mkdocs.yml", "настройк", "конфиг"]
    },
    {
        "question": "Как Fire обрабатывает аргументы командной строки?",
        "category": "сложный",
        "expected_keywords": ["аргумент", "команд", "параметр"]
    },
    # TRICKY (7-8) — проверка rewrite
    {
        "question": "Как сделать CLI из функции?",
        "category": "tricky",
        "expected_keywords": ["cli", "функц", "fire"]
    },
    {
        "question": "Как поднять сайт локально?",
        "category": "tricky",
        "expected_keywords": ["serve", "локальн", "localhost"]
    },
    # НЕГАТИВНЫЕ (9-10) — анти-галлюцинации
    {
        "question": "Как работает Django ORM?",
        "category": "негативный",
        "expected_keywords": ["django", "orm", "баз"]
    },
    {
        "question": "Какие лучшие практики Kubernetes?",
        "category": "негативный",
        "expected_keywords": ["kubernetes", "docker", "контейнер"]
    }
]


def check_keywords(text: str, keywords: list) -> tuple[int, int]:
    """
    Check how many keywords appear in text.
    
    Returns:
        (hits, total) tuple
    """
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits, len(keywords)


def show_progress():
    """Show dots while processing."""
    for _ in range(20):
        sys.stdout.write("\033[90m.\033[0m")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.flush()


def run_evaluation(agent: Agent):
    """
    Run evaluation comparing 3 modes: RAG, RAG+filter, RAG+filter+rewrite.
    Validates Sources and Quotes presence.
    
    Args:
        agent: Agent instance
    """
    print("\n" + "=" * 80)
    console.print("[bold cyan]ОЦЕНКА: Сравнение 3 режимов RAG[/bold cyan]")
    print("=" * 80)
    
    modes = [
        {"name": "RAG", "filter": False, "rewrite": False, "short": "RAG"},
        {"name": "RAG+Filter", "filter": True, "rewrite": False, "short": "RAG+Filter"},
        {"name": "RAG+Filter+Rewrite", "filter": True, "rewrite": True, "short": "RAG+Rewrite"},
    ]
    
    totals = {m["name"]: {"hits": 0, "total": 0} for m in modes}
    
    # Новые метрики
    fallback_count = 0
    sources_ok = 0
    quotes_ok = 0
    total_questions = len(QUESTIONS)
    
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n\033[1m{q['question']}\033[0m", end=" ", flush=True)
        
        show_progress()
        
        results = {}
        
        for mode in modes:
            agent.use_filter = mode["filter"]
            agent.use_rewrite = mode["rewrite"]
            
            try:
                result = agent.ask(q["question"])
                hits, total = check_keywords(result["text"], q["expected_keywords"])
                results[mode["name"]] = {
                    "text": result["text"],
                    "hits": hits,
                    "total": total,
                    "fallback": result.get("fallback", False)
                }
                totals[mode["name"]]["hits"] += hits
                totals[mode["name"]]["total"] += total
            except Exception as e:
                results[mode["name"]] = {"error": str(e), "hits": 0, "total": 0, "text": "", "fallback": False}
        
        pct_rag = (results["RAG"]["hits"] / results["RAG"]["total"] * 100) if results["RAG"]["total"] > 0 else 0
        pct_filter = (results["RAG+Filter"]["hits"] / results["RAG+Filter"]["total"] * 100) if results["RAG+Filter"]["total"] > 0 else 0
        pct_rewrite = (results["RAG+Filter+Rewrite"]["hits"] / results["RAG+Filter+Rewrite"]["total"] * 100) if results["RAG+Filter+Rewrite"]["total"] > 0 else 0
        
        best_mode = max([("RAG", pct_rag), ("RAG+Filter", pct_filter), ("RAG+Filter+Rewrite", pct_rewrite)], key=lambda x: x[1])
        best_pct = best_mode[1]
        best_name = best_mode[0]
        best_text = results[best_name]["text"]
        
        # Проверка Sources и Quotes С СОДЕРЖИМЫМ
        has_sources = bool(re.search(r"Sources:\s*\S", best_text, re.IGNORECASE))
        has_quotes = bool(re.search(r"Quotes:\s*\d", best_text, re.IGNORECASE))
        is_fallback = "Не знаю" in best_text or "I don't know" in best_text
        
        # Обновление метрик
        if is_fallback:
            fallback_count += 1
        if has_sources:
            sources_ok += 1
        if has_quotes:
            quotes_ok += 1
        
        # Вывод с Rich
        category_color = {
            "базовый": "green",
            "сложный": "yellow", 
            "tricky": "cyan",
            "негативный": "red"
        }
        color = category_color.get(q.get("category", ""), "white")
        
        console.print(f"\n[{color}][{q.get('category', '').upper()}][/] ", end="")
        console.print(f"[bold cyan]Вопрос:[/bold cyan] {q['question']}")
        
        if is_fallback:
            console.print("[red]Отступление: ДА[/red]")
        else:
            console.print("[green]Отступление: НЕТ[/green]")
        
        if has_sources:
            console.print("[green]Есть источники: ДА[/green]")
        else:
            console.print("[red]Есть источники: НЕТ[/red]")
        
        if has_quotes:
            console.print("[green]Есть цитаты: ДА[/green]")
        else:
            console.print("[red]Есть цитаты: НЕТ[/red]")
        
        # Answer panel
        console.print(Panel(best_text, title=f"Лучший ответ ({best_name}, {best_pct:.0f}%)", border_style="blue"))
    
    # ИТОГОВАЯ СТАТИСТИКА
    print("\n" + "=" * 80)
    console.print("[bold]ИТОГОВАЯ СТАТИСТИКА[/bold]")
    print("=" * 80)
    
    # Правильный расчёт % (универсальный)
    fallback_pct = (fallback_count / total_questions) * 100
    sources_pct = (sources_ok / total_questions) * 100
    quotes_pct = (quotes_ok / total_questions) * 100
    
    console.print(f"Отступление: {fallback_count}/{total_questions} ({fallback_pct:.0f}%)")
    console.print(f"Покрытие источниками: {sources_ok}/{total_questions} ({sources_pct:.0f}%)")
    console.print(f"Покрытие цитатами: {quotes_ok}/{total_questions} ({quotes_pct:.0f}%)")
    
    console.print("\n[bold]Полнота ключевых слов:[/bold]")
    for mode in modes:
        name = mode["name"]
        hits = totals[name]["hits"]
        total = totals[name]["total"]
        pct = (hits / total * 100) if total > 0 else 0
        console.print(f"  {mode['short']:20s} {hits}/{total} ({pct:.0f}%)")
    
    print("=" * 80)
