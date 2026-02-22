from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from app.llm_client import ask_llm, BENCHMARK_MODELS

console = Console()


def analyze_response(resp: str, stop_seq: str):
    length_chars = len(resp)
    length_words = len(resp.split())
    has_stop = resp.strip().endswith(stop_seq)

    bullets = resp.count("\n- ") + resp.lower().count("\n1. ")

    return {
        "chars": length_chars,
        "words": length_words,
        "bullets": bullets,
        "stop_ok": has_stop
    }


def run_benchmark(prompt: str, models_dict: dict = None, max_tokens: int = None):
    if models_dict is None:
        models_dict = BENCHMARK_MODELS

    results = []
    model_items = list(models_dict.items())

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Выполнение запросов...", total=len(model_items))

        try:
            for level, model in model_items:
                tokens_limit = max_tokens if (max_tokens and level == "strong") else None
                progress.update(task, description=f"[yellow]{level}: {model[:30]}...")
                result = ask_llm(prompt, model=model, temperature=0.7, max_tokens=tokens_limit)
                results.append({
                    "level": level,
                    "model": model,
                    **result
                })
                progress.advance(task)
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем. Показаны результаты...[/yellow]")

    return results


def display_benchmark_results(results: list):
    total_cost_rub = sum(r["cost"] for r in results)

    table = Table(title="Результаты Benchmark")

    table.add_column("Модель", justify="left")
    table.add_column("Уровень", justify="center")
    table.add_column("Время (сек)", justify="center")
    table.add_column("Input", justify="center")
    table.add_column("Output", justify="center")
    table.add_column("Total", justify="center")
    table.add_column("Цена", justify="center")

    for r in results:
        cost_rub = round(r["cost"], 5)
        table.add_row(
            r["model"],
            r["level"],
            str(r["elapsed_time"]),
            str(r["input_tokens"]),
            str(r["output_tokens"]),
            str(r["total_tokens"]),
            str(cost_rub)
        )

    console.print(table)
    console.print(f"[bold]Итого: {round(total_cost_rub, 5)}[/bold]\n")
    console.print("\n[bold]Ответы:[/bold]")

    for r in results:
        console.print(f"\n[bold cyan]{r['level'].upper()} ({r['model']}):[/bold cyan]")
        console.print(r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"])