import argparse
from rich.console import Console
from rich.table import Table
from rich.status import Status

from app.llm_client import ask_llm
from app.comparator import (
    analyze_temperature_response,
    display_temperature_comparison
)

console = Console()


def print_metrics(data):
    table = Table(title="Метрики запроса")
    table.add_column("Метрика")
    table.add_column("Значение")

    table.add_row("Модель", data["model"])
    table.add_row("Input tokens", str(data["input_tokens"]))
    table.add_row("Output tokens", str(data["output_tokens"]))
    table.add_row("Total tokens", str(data["total_tokens"]))
    table.add_row("Оценка стоимости (₽)", str(data["cost"]))

    console.print(table)


def run_temperature_experiment(query, model=None):
    temperatures = [0, 0.7, 1.2]
    results = {}

    console.print("[bold green]LLM Temperature Experiment Tool[/bold green]\n")

    for index, temp in enumerate(temperatures, start=1):
        console.print(f"\n[bold blue]Temperature = {temp}[/bold blue]")

        # 🔄 Псевдоанимация ожидания ответа
        with console.status(
            f"[bold green]Выполнение {index}/{len(temperatures)} "
            f"(temperature={temp})...[/bold green]",
            spinner="dots"
        ):
            response = ask_llm(
                query,
                model=model,
                temperature=temp
            )

        console.print("[green]✓ Ответ получен[/green]\n")
        console.print(response["text"])
        console.print()

        print_metrics(response)

        analysis = analyze_temperature_response(response["text"])
        results[temp] = analysis

    console.print("\n[bold cyan]Сравнение temperature[/bold cyan]")
    display_temperature_comparison(results)

    console.print("\n[bold yellow]Вывод:[/bold yellow]")
    console.print(
        """
temperature = 0  
→ максимальная детерминированность  
→ высокая точность  
→ минимальная вариативность  

temperature = 0.7  
→ баланс точности и креативности  
→ естественный стиль  
→ подходит для большинства задач  

temperature = 1.2  
→ высокая креативность  
→ больше разнообразия  
→ возможна потеря строгости  
"""
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Запрос к LLM")
    parser.add_argument("--model", help="Переопределить модель")
    parser.add_argument(
        "--temp-experiment",
        action="store_true",
        help="Запустить эксперимент с temperature"
    )

    args = parser.parse_args()

    if args.temp_experiment:
        run_temperature_experiment(args.query, args.model)
    else:
        console.print(
            "[red]Укажите флаг --temp-experiment для запуска эксперимента[/red]"
        )


if __name__ == "__main__":
    main()
