"""Evaluator module for comparing RAG vs non-RAG answers."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from agent import Agent


QUESTIONS = [
    {
        "question": "Что такое Fire?",
        "expected": "fire",
        "sources": ["fire"]
    },
    {
        "question": "Как использовать Fire в Python?",
        "expected": "@fire",
        "sources": ["fire"]
    },
    {
        "question": "Какова основная цель Fire?",
        "expected": "cli",
        "sources": ["fire"]
    },
    {
        "question": "Как установить Fire?",
        "expected": "pip install",
        "sources": ["fire"]
    },
    {
        "question": "Что такое MkDocs?",
        "expected": "документация",
        "sources": ["mkdocs"]
    },
    {
        "question": "Как создать документацию с помощью MkDocs?",
        "expected": "mkdocs",
        "sources": ["mkdocs"]
    },
    {
        "question": "Что делает команда mkdocs serve?",
        "expected": "serve",
        "sources": ["mkdocs"]
    },
    {
        "question": "Как задеплоить MkDocs на GitHub Pages?",
        "expected": "github",
        "sources": ["mkdocs"]
    },
    {
        "question": "В чем разница между Fire и Click?",
        "expected": "fire",
        "sources": []
    },
    {
        "question": "Какие лучшие практики документации?",
        "expected": "документация",
        "sources": []
    }
]


def run_evaluation(agent: Agent):
    """
    Run evaluation comparing RAG vs non-RAG answers.
    
    Args:
        agent: Agent instance
    """
    print("\n" + "=" * 60)
    print("\033[31m" + "ОЦЕНКА: RAG vs Без RAG" + "\033[0m")
    print("=" * 60)
    
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n{'='*60}")
        print(f"\033[31m" + f"Вопрос {i}/10: {q['question']}" + "\033[0m")
        print(f"{'='*60}")
        
        agent.disable_rag()
        result_no_rag = agent.ask(q["question"])
        
        print(f"\n\033[32mБез RAG:\033[0m")
        print(f"  {result_no_rag['text'][:200]}...")
        
        try:
            agent.enable_rag()
            result_with_rag = agent.ask(q["question"])
            
            print(f"\n\033[32mС RAG:\033[0m")
            print(f"  {result_with_rag['text'][:200]}...")
            
            if result_with_rag.get("retrieved_chunks"):
                chunks_count = len(result_with_rag['retrieved_chunks'])
                print(f"\nНайдено чанков: {chunks_count}")
        
        except Exception as e:
            print(f"\nRAG Error: {e}")
        
        print(f"\n\033[32mОжидаемые ключевые слова: {q['expected']}\033[0m")
    
    print("\n" + "=" * 60)
    print("Оценка завершена!")
    print("=" * 60)
