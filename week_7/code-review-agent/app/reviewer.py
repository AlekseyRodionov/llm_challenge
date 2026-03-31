"""
Главный модуль AI Code Review Agent.
Выполняет автоматический ревью кода для Pull Request.
"""
from app.diff_parser import parse_diff
from app.rag_context import load_project_docs, load_code_files, build_context
from app.llm_client import ask_llm


REVIEW_PROMPT = """Ты — senior software engineer. Проанализируй изменения в коде.

Используй формат с уровнями серьёзности:
- [HIGH] для критических проблем (безопасность, баги)
- [MEDIUM] для средних проблем

Формат:

Bugs (ОШИБКИ):
- [LEVEL] описание

Security (БЕЗОПАСНОСТЬ):
- [LEVEL] описание

Architecture (АРХИТЕКТУРА):
- [LEVEL] описание

Code Quality (КАЧЕСТВО КОДА):
- [LEVEL] описание

Suggestions (РЕКОМЕНДАЦИИ):
- [LEVEL] описание

Если проблем нет — напиши: "Проблем не обнаружено"

КОНТЕКСТ:
{context}

DIFF:
{diff_text}

Review:"""


def review_code(diff_text: str) -> str:
    """
    Выполняет AI review кода.
    
    Args:
        diff_text: Текст git diff
        
    Returns:
        str: Результат ревью
    """
    # 1. Парсим diff
    parsed_diff = parse_diff(diff_text)
    
    if not parsed_diff.get("files"):
        return "No changes detected in diff."
    
    # 2. Загружаем документацию
    docs = load_project_docs()
    
    # 3. Загружаем код проекта
    code = load_code_files()
    
    # 4. Собираем контекст
    context = build_context(parsed_diff, docs, code)
    
    # 5. Формируем prompt
    prompt = REVIEW_PROMPT.format(
        context=context,
        diff_text=diff_text[:5000]  # Ограничиваем diff
    )
    
    # 6. Отправляем в LLM
    result = ask_llm(
        prompt=prompt,
        max_tokens=2000,
        temperature=0.3
    )
    
    return result.get("text", "Error: No response from LLM")


def review_code_simple(diff_text: str) -> dict:
    """
    Выполняет review и возвращает полный результат с метриками.
    
    Args:
        diff_text: Текст git diff
        
    Returns:
        dict: {"review": "...", "metrics": {...}}
    """
    # 1. Парсим diff
    parsed_diff = parse_diff(diff_text)
    
    if not parsed_diff.get("files"):
        return {
            "review": "No changes detected in diff.",
            "metrics": {"changed_files": 0}
        }
    
    # 2. Загружаем документацию
    docs = load_project_docs()
    
    # 3. Загружаем код проекта
    code = load_code_files()
    
    # 4. Собираем контекст
    context = build_context(parsed_diff, docs, code)
    
    # 5. Формируем prompt
    prompt = REVIEW_PROMPT.format(
        context=context,
        diff_text=diff_text[:5000]
    )
    
    # 6. Отправляем в LLM
    result = ask_llm(
        prompt=prompt,
        max_tokens=2000,
        temperature=0.3
    )
    
    return {
        "review": result.get("text", "Error: No response from LLM"),
        "metrics": {
            "changed_files": len(parsed_diff.get("files", [])),
            "docs_count": len(docs),
            "code_files_count": len(code),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "cost": result.get("cost", 0)
        }
    }


if __name__ == "__main__":
    # Простой тест
    test_diff = """diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -1,5 +1,8 @@
+import new_module
+
 def main():
     print("Hello")
+    print("New feature")

"""
    result = review_code(test_diff)
    print(result)
