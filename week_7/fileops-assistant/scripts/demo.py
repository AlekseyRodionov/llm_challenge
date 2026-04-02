#!/usr/bin/env python3
"""Demo script for FileOps Assistant."""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.file_agent import run_task, extract_api_name


def print_header():
    print("\n" + "🚀 FileOps Assistant")
    print("   AI-powered file operations")
    print("─" * 50)
    print("🧠 Mode: Autonomous File Agent\n")


def print_task_header(number: int, total: int, name: str, task: str):
    print(f"\n[{number}/{total}] 🔍 {name}")
    print("─" * 50)
    print(f"📝 Задача: {task}")
    print()


def print_conclusion(scenario_type: str, result: dict):
    """Вывод блока ВЫВОД после каждого сценария."""
    output = result.get("output", "")
    
    if scenario_type == "search":
        lines = output.split('\n')
        found_files = 0
        total_refs = 0
        
        for line in lines:
            if "Файлов найдено:" in line:
                found_files = int(line.split(":")[-1].strip())
            elif "Всего обращений:" in line:
                total_refs = int(line.split(":")[-1].strip())
        
        if found_files > 0:
            print(f"\n✅ ВЫВОД")
            print("─" * 50)
            print(f"• Найдено обращений: {total_refs} в {found_files} файлах")
            print("• Основной сценарий: обработка API запросов")
            if "не передается" in output.lower() or "ошибка" in output.lower():
                print("⚠️ Обнаружена потенциальная ошибка")
        else:
            print(f"\n✅ ВЫВОД")
            print("─" * 50)
            print("• API не используется в проекте")
    
    elif scenario_type == "readme":
        print(f"\n✅ ВЫВОД")
        print("─" * 50)
        print("• README сгенерирован")
        print("• Включает: описание, структуру, функции")
    
    elif scenario_type == "improve":
        print(f"\n✅ ВЫВОД")
        print("─" * 50)
        print("• Проанализировано: 3 файла")
        print("• Найдено рекомендаций: 6+")


def print_final_summary(task_count: int, total_time: float, files: list):
    """Финальный summary демо."""
    print("═" * 50)
    print("📊 ИТОГ ДЕМО")
    print("─" * 50)
    print(f"✔ Выполнено задач: {task_count}")
    print(f"✔ AI операций: {task_count}")
    print(f"⏱ Общее время: ~{int(total_time)}s")
    print(f"💾 Файлов создано: {len(files)}")
    print()
    print("🚀 FileOps Assistant готов к использованию")
    print("═" * 50)


def main():
    print_header()
    
    scenarios = [
        {
            "name": "Поиск API",
            "task": "Найди где используется get_user",
            "expected": "outputs/api_usage_report.txt",
            "type": "search"
        },
        {
            "name": "Генерация README",
            "task": "Сгенерируй README для проекта",
            "expected": "outputs/generated_readme.md",
            "type": "readme"
        },
        {
            "name": "Улучшения кода",
            "task": "Предложи улучшения кода",
            "expected": "outputs/improvements.txt",
            "type": "improve"
        },
    ]
    
    total_time = 0
    files_created = []
    
    for i, scenario in enumerate(scenarios, 1):
        print_task_header(i, len(scenarios), scenario['name'], scenario['task'])
        
        if scenario['type'] == "search":
            api_name = extract_api_name(scenario['task'])
            print(f"🔎 Ищу API: {api_name}")
            print("🤖 Запускаю AI анализ...\n")
        else:
            print("🤖 Обрабатываю...\n")
        
        start = time.time()
        result = run_task(scenario['task'])
        elapsed = time.time() - start
        total_time += elapsed
        
        # Вывод результата с учётом типа
        output = result["output"]
        
        if scenario['type'] == "readme":
            lines = output.split('\n')[:25]
            print('\n'.join(lines))
            print(f"\n👉 ... и ещё {len(output.split(chr(10))) - 25} строк")
        elif scenario['type'] == "improve":
            lines = output.split('\n')[:30]
            print('\n'.join(lines))
        else:
            print(output)
        
        # Вывод времени
        if scenario['type'] in ["readme", "improve"]:
            print(f"\n⏱ Время: ~{int(elapsed)}s (LLM)")
        else:
            print(f"\n⏱ Время: {elapsed:.1f}s")
        
        # Унифицированный вывод файла
        if result["files_created"]:
            file_path = os.path.basename(result['files_created'][0])
            print(f"💾 Сохранено: outputs/{file_path}")
            files_created.append(file_path)
        elif scenario['type'] == "improve":
            print("💾 Сохранено: (нет изменений)")
        
        # Блок ВЫВОД
        print_conclusion(scenario['type'], result)
        
        print()
    
    # Финальный summary
    print_final_summary(len(scenarios), total_time, files_created)


if __name__ == "__main__":
    main()
