"""
Модуль для анализа и сравнения ответов LLM.
В данный момент не используется в основной логике, может пригодиться для расширения.
"""
from rich.table import Table, Console

console = Console()


def analyze_response(resp: str, stop_seq: str) -> dict:
    """
    Анализирует текстовый ответ LLM по базовым метрикам.
    
    Args:
        resp: Текст ответа LLM
        stop_seq: Последовательность для проверки завершения
    
    Returns:
        Словарь с метриками:
        - chars: количество символов
        - words: количество слов
        - bullets: количество пунктов
        - stop_ok: завершен ли стоп-последовательностью
    """
    length_chars = len(resp)
    length_words = len(resp.split())
    has_stop = resp.strip().endswith(stop_seq)

    # структура — считаем подпункты вида "- " или "1. "
    bullets = resp.count("\n- ") + resp.lower().count("\n1. ")

    return {
        "chars": length_chars,
        "words": length_words,
        "bullets": bullets,
        "stop_ok": has_stop
    }


def display_comparison(basic_data: dict, ctrl_data: dict, basic_str: str, ctrl_str: str):
    """
    Выводит таблицу сравнения двух ответов.
    
    Args:
        basic_data: Метрики первого ответа
        ctrl_data: Метрики второго ответа
        basic_str: Текст первого ответа
        ctrl_str: Текст второго ответа
    """
    table = Table(title="Сравнение ответов")

    table.add_column("Метрика", justify="left")
    table.add_column("Без ограничений", justify="center")
    table.add_column("С ограничениями", justify="center")

    table.add_row("Символы", str(basic_data["chars"]), str(ctrl_data["chars"]))
    table.add_row("Слова", str(basic_data["words"]), str(ctrl_data["words"]))
    table.add_row("Пункты (≈)", str(basic_data["bullets"]), str(ctrl_data["bullets"]))
    table.add_row("Завершение stop", str(basic_data["stop_ok"]), str(ctrl_data["stop_ok"]))

    console.print(table)

    console.print("\n[bold blue]Ответ без ограничений:[/]")
    console.print(basic_str, "\n")

    console.print("[bold green]Ответ с ограничениями:[/]")
    console.print(ctrl_str, "\n")
