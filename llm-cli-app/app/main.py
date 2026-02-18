import argparse
from rich.console import Console
from rich.table import Table
from app.llm_client import ask_llm

console = Console()

def build_controlled_prompt(query: str):
    return f"""
{query}

Формат ответа:
- 4 пункта
- максимум 20 слов в пункте
- без примеров

Ограничение:
- максимум 100 слов
Заверши ответ строкой: END
"""

def print_metrics(title, data):
    table = Table(title=title)
    table.add_column("Метрика")
    table.add_column("Значение")

    table.add_row("Модель", data["model"])
    table.add_row("Input tokens", str(data["input_tokens"]))
    table.add_row("Output tokens", str(data["output_tokens"]))
    table.add_row("Total tokens", str(data["total_tokens"]))
    table.add_row("Оценка стоимости ($)", str(data["cost"]))

    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Запрос к LLM")
    parser.add_argument("--model", help="Переопределить модель")
    parser.add_argument("--compare", action="store_true", help="Сравнить с контролируемым режимом")

    args = parser.parse_args()

    console.print("[bold green]LLM CLI Compare Tool[/bold green]\n")

    # Без ограничений
    basic = ask_llm(
        args.query,
        model=args.model,
        temperature=0.7
    )

    console.print("[bold blue]Ответ без ограничений:[/bold blue]")
    console.print(basic["text"])
    print_metrics("Метрики (без ограничений)", basic)

    if args.compare:
        controlled_prompt = build_controlled_prompt(args.query)

        controlled = ask_llm(
            controlled_prompt,
            model=args.model,
            temperature=0.2,
            max_tokens=150,
            stop=["END"]
        )

        console.print("\n[bold green]Ответ с ограничениями:[/bold green]")
        console.print(controlled["text"])
        print_metrics("Метрики (с ограничениями)", controlled)


if __name__ == "__main__":
    main()