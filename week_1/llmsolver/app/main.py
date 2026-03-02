from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.llm_client import ask_llm
from app.comparator import compare_responses

console = Console()

# Новый список промтов
PROMPTS = [
    """
Реши задачу 
В кафе сидят три друга: Алекс, Боб и Карл.

Алекс: «Боб заказал кофе».
Боб: «Я не заказывал».
Карл: «Алекс лжёт».

Известно, что только один из них лжёт.

выведи ответ строго в формате:
1. Кто лжёт
2. Кто заказал кофе
3. Краткое логическое объяснение (до 80 слов)
""",
    """
Решай задачу пошагово. Сначала проанализируй каждое утверждение, сделай логические выводы, а потом дай окончательный ответ строго в формате ниже.

В кафе сидят три друга: Алекс, Боб и Карл.

Алекс: «Боб заказал кофе».
Боб: «Я не заказывал».
Карл: «Алекс лжёт».

Известно, что только один из них лжёт.

Сначала распиши свои рассуждения шаг за шагом, затем выведи ответ строго в формате:
1. Кто лжёт
2. Кто заказал кофе
3. Краткое логическое объяснение (до 80 слов)
""",
    """
Вы — три эксперта: философ, математик, аналитик. 
Дайте краткое (2–3 предложения) пошаговое рассуждение каждого эксперта.

Задача:
Алекс: «Боб заказал кофе».
Боб: «Я не заказывал».
Карл: «Алекс лжёт».
Известно, что только один из них лжёт.

выведи ответ строго в формате для каждого эксперта:
1. Кто лжёт
2. Кто заказал кофе
3. Краткое логическое объяснение (до 80 слов)
"""
]

def run_prompts(prompts):
    results = []
    for i, prompt in enumerate(prompts, 1):
        console.rule(f"Промт {i} — запрос к LLM", style="cyan")
        console.print(Panel(prompt.strip(), title=f"Промт {i}", style="magenta"))
        
        result = ask_llm(prompt)
        console.print(Panel(result['text'], title=f"Ответ модели для промта {i}", style="green"))
        
        results.append(result)
    return results

def generate_and_use_prompt(base_task):
    console.rule("Генерация улучшенного промпта через LLM", style="cyan")

    instruction = f"""
Твоя задача: создать улучшенный и более чёткий промт для LLM, чтобы решить задачу логики.
НЕ КОПИРУЙ исходный текст напрямую! Переформулируй его так, чтобы LLM дала пошаговое решение и итоговый вывод строго в формате 1-2-3.
Добавь указание выводить только нужный результат без лишних рассуждений.
Исходная задача для промта:
{base_task}
"""

    # Генерация улучшенного промта
    prompt_result = ask_llm(instruction)
    generated_prompt = prompt_result["text"]

    console.print(Panel(generated_prompt, title="Сгенерированный улучшенный промт", style="magenta"))

    console.rule("Использование сгенерированного промта", style="cyan")
    solution_result = ask_llm(generated_prompt)
    console.print(Panel(solution_result["text"], title="Ответ модели по улучшенному сгенерированному промту", style="green"))

    return solution_result

def comparative_analysis(all_results):
    analysis_results = compare_responses(all_results)

    table = Table(title="Анализ всех ответов", show_lines=True)
    table.add_column("Промт")
    table.add_column("Структура 1-2-3")
    table.add_column("Лжец указан")
    table.add_column("Кофе указан")
    table.add_column("Кол-во слов")
    table.add_column("Токены (входные)")
    table.add_column("Токены (выходные)")
    table.add_column("Токены (всего)")

    for res in analysis_results:
        table.add_row(
            res["Промт"],
            str(res["Есть структура 1-2-3"]),
            str(res["Указан лжец"]),
            str(res["Указан заказчик кофе"]),
            str(res["Количество слов"]),
            str(res["Токены (входные)"]),
            str(res["Токены (выходные)"]),
            str(res["Токены (всего)"])
        )

    console.print(table)

def main():
    # 1. Выполнение трёх исходных промтов
    results = run_prompts(PROMPTS)

    # 2. Генерация улучшенного промта для первого запроса
    generated_result = generate_and_use_prompt(PROMPTS[0])

    # 3. Сравнительный анализ всех ответов
    all_results = results + [generated_result]
    comparative_analysis(all_results)

if __name__ == "__main__":
    main()
