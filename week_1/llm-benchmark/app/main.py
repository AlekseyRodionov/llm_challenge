import argparse
from rich.console import Console
from rich.table import Table
from app.llm_client import ask_llm, BENCHMARK_MODELS
from app.comparator import run_benchmark, display_benchmark_results

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

    cost_kopecks = round(data["cost"], 5)

    table.add_row("Модель", data["model"])
    table.add_row("Input tokens", str(data["input_tokens"]))
    table.add_row("Output tokens", str(data["output_tokens"]))
    table.add_row("Total tokens", str(data["total_tokens"]))
    table.add_row("Время (сек)", str(data.get("elapsed_time", "N/A")))
    table.add_row("Цена (руб)", str(cost_kopecks))

    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Запрос к LLM")
    parser.add_argument("--model", help="Переопределить модель")
    parser.add_argument("--compare", action="store_true", help="Сравнить с контролируемым режимом")
    parser.add_argument("--benchmark", action="store_true", help="Запустить benchmark на 3 моделях")
    parser.add_argument(
        "--levels",
        nargs="+",
        choices=["weak", "medium", "strong"],
        default=["weak", "medium", "strong"],
        help="Какие модели использовать для benchmark"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Максимальное количество токенов в ответе"
    )

    args = parser.parse_args()

    console.print("[bold green]LLM CLI Benchmark Tool[/bold green]")
    console.print("[dim]Сравнение LLM моделей по времени, токенам и стоимости[/dim]\n")

    if args.benchmark:
        models_dict = {level: BENCHMARK_MODELS[level] for level in args.levels}
        console.print(f"[bold]Benchmark с моделями:[/bold] {', '.join(models_dict.values())}\n")
        console.print("[dim]Запрос можно прервать: Ctrl+C | Таймаут по умолчанию: 300 сек[/dim]\n")
        
        results = run_benchmark(args.query, models_dict, args.max_tokens)
        display_benchmark_results(results)
        return

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
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Прервано пользователем[/bold red]")