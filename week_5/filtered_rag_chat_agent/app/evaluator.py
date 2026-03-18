"""Evaluator module for comparing RAG modes."""
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from agent import Agent


QUESTIONS = [
    {
        "question": "Какие способы вызова fire.Fire() существуют?",
        "expected_keywords": ["fire.Fire", "вызов", "объект"]
    },
    {
        "question": "Какие встроенные плагины есть в MkDocs?",
        "expected_keywords": ["plugins", "search", "встроен"]
    },
    {
        "question": "Как использовать mkdocs serve --dev-addr?",
        "expected_keywords": ["serve", "localhost", "адрес"]
    },
    {
        "question": "Как настроить поиск в MkDocs?",
        "expected_keywords": ["search", "индекс", "настройк"]
    },
    {
        "question": "Можно ли в Fire указать значение по умолчанию?",
        "expected_keywords": ["default", "аргумент", "значение"]
    },
    {
        "question": "Как сделать навигацию в MkDocs?",
        "expected_keywords": ["nav", "страниц", "документ"]
    },
    {
        "question": "Как в Fire получить справку?",
        "expected_keywords": ["help", "справк", "--help"]
    },
    {
        "question": "Можно ли задеплоить MkDocs на Netlify?",
        "expected_keywords": ["netlify", "альтернатива", "статик"]
    },
    {
        "question": "Какие темы есть в MkDocs?",
        "expected_keywords": ["theme", "material", "оформлен"]
    },
    {
        "question": "Почему fire.Fire возвращает пустой CLI?",
        "expected_keywords": ["пустой", "debug", "трассировк"]
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
    
    Args:
        agent: Agent instance
    """
    print("\n" + "=" * 80)
    print("\033[1m\033[34mОЦЕНКА: Сравнение 3 режимов RAG\033[0m")
    print("=" * 80)
    
    modes = [
        {"name": "RAG", "filter": False, "rewrite": False, "short": "RAG"},
        {"name": "RAG+Filter", "filter": True, "rewrite": False, "short": "RAG+Filter"},
        {"name": "RAG+Filter+Rewrite", "filter": True, "rewrite": True, "short": "RAG+Rewrite"},
    ]
    
    totals = {m["name"]: {"hits": 0, "total": 0} for m in modes}
    
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
                    "total": total
                }
                totals[mode["name"]]["hits"] += hits
                totals[mode["name"]]["total"] += total
            except Exception as e:
                results[mode["name"]] = {"error": str(e), "hits": 0, "total": 0, "text": ""}
        
        pct_rag = (results["RAG"]["hits"] / results["RAG"]["total"] * 100) if results["RAG"]["total"] > 0 else 0
        pct_filter = (results["RAG+Filter"]["hits"] / results["RAG+Filter"]["total"] * 100) if results["RAG+Filter"]["total"] > 0 else 0
        pct_rewrite = (results["RAG+Filter+Rewrite"]["hits"] / results["RAG+Filter+Rewrite"]["total"] * 100) if results["RAG+Filter+Rewrite"]["total"] > 0 else 0
        
        best_mode = max([("RAG", pct_rag), ("RAG+Filter", pct_filter), ("RAG+Filter+Rewrite", pct_rewrite)], key=lambda x: x[1])
        best_pct = best_mode[1]
        best_name = best_mode[0]
        best_text = results[best_name]["text"]
        
        print(f"\nПолнота ключевых слов [RAG] {pct_rag:.0f}% | [RAG+Filter] {pct_filter:.0f}% | [RAG+Rewrite] {pct_rewrite:.0f}%")
        
        best_preview = best_text[:300].replace("\n", " ") + ("..." if len(best_text) > 300 else "")
        print(f"\n  \033[1mЛучший ответ ({best_name}, {best_pct:.0f}%):\033[0m")
        print(f"  {best_preview}")
    
    print("\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Полнота ключевых слов:")
    
    for mode in modes:
        name = mode["name"]
        hits = totals[name]["hits"]
        total = totals[name]["total"]
        pct = (hits / total * 100) if total > 0 else 0
        print(f"  {mode['short']:20s} {hits}/{total} ({pct:.0f}%)")
    
    print("=" * 80)
