"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет трёхслойной моделью памяти и FSM Task Mode.
"""
import json

from app.llm_client import ask_llm
from app.memory_manager import (
    init_db,
    add_long_term_memory,
    add_working_memory,
    get_long_term_memory,
    get_working_memory,
    clear_working_memory,
    clear_all_memory,
    get_active_profile
)
from app.router import route_message
from app.state_machine import transition, StateError, STATES
from app.task_manager import (
    create_task,
    get_task,
    update_task,
    delete_task,
    parse_plan,
    get_current_step_text
)
from app.prompts import PLANNING_PROMPT, EXECUTION_PROMPT, VALIDATION_PROMPT, build_invariants_prompt
from app.invariants import check_invariants, explain_violation, init_invariants_db


class Agent:
    """
    LLM агент с трёхслойной памятью и FSM Task Mode.
    """

    def __init__(self, model: str = None, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.short_term_memory = []
        self.execution_results = []
        init_db()
        init_invariants_db()

    def _build_system_prompt(self) -> str:
        """Формирует системный prompt на основе памяти, профиля и инвариантов."""
        profile = get_active_profile()
        
        parts = [
            "You are an AI assistant.",
            f"\nUSER PROFILE:\n{profile['description']}",
            "\nAdapt your answer automatically according to this profile."
        ]

        long_term = get_long_term_memory()
        if long_term:
            parts.append("\nДолговременная память (факты о пользователе):")
            for item in long_term:
                parts.append(f"- {item['content']}")

        working = get_working_memory()
        if working:
            parts.append("\nРабочая память (текущая задача):")
            for item in working:
                parts.append(f"- {item['content']}")

        parts.append("\n" + build_invariants_prompt())

        return "\n".join(parts)

    def _save_to_memory(self, user_message: str):
        """Сохраняет данные из сообщения в соответствующую память."""
        routes = route_message(user_message)

        for route in routes:
            text = route.get("text", "").strip()
            memory_type = route.get("memory_type", "")

            if not text:
                continue

            if memory_type == "long_term":
                add_long_term_memory(text)
            elif memory_type == "working":
                add_working_memory(text)

    def ask(self, user_message: str) -> dict:
        """
        Отправляет сообщение агенту и получает ответ.
        Использует FSM или legacy режим в зависимости от state.
        """
        task = get_task()
        
        if task and task["state"] != "IDLE":
            return self._handle_fsm(user_message)
        else:
            return self._handle_legacy(user_message)

    def _handle_legacy(self, user_message: str) -> dict:
        """Legacy режим - AI router + profiles."""
        self._save_to_memory(user_message)
        self.short_term_memory.append({"role": "user", "content": user_message})

        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.short_term_memory)

        result = ask_llm(
            prompt="",
            model=self.model,
            temperature=self.temperature,
            messages=messages
        )

        violations = check_invariants(result["text"])
        if violations:
            result["text"] = explain_violation(violations)

        self.short_term_memory.append({"role": "assistant", "content": result["text"]})
        return result

    def _handle_fsm(self, user_message: str) -> dict:
        """FSM режим - обрабатывает только команды."""
        task = get_task()
        state = task["state"] if task else "IDLE"
        
        state_hints = {
            "PLANNING": "План генерируется...",
            "WAITING_APPROVAL": "План готов. Используйте approve для подтверждения.",
            "EXECUTING": "Выполнение шага. Используйте next.",
            "VALIDATING": "Валидация результата...",
            "DONE": "Задача завершена. Используйте reset_task для новой.",
            "PAUSED": "Задача на паузе. Используйте resume."
        }
        
        hint = state_hints.get(state, "")
        msg = f"⚙️ FSM режим (состояние: {state})"
        if hint:
            msg += f"\n{hint}"
        msg += "\n\nКоманды: task_start, approve, next, pause, resume, reset_task, status"
        
        return {
            "text": msg,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost": 0,
            "model": self.model
        }

    def fsm_task_start(self, task_text: str) -> dict:
        """Запуск новой задачи. /task start"""
        task = get_task()
        
        if task and task["state"] not in ("IDLE", "DONE"):
            return {
                "text": f"⚠️ Задача уже существует (состояние: {task['state']}). Используйте reset_task для начала новой.",
                "state": task["state"]
            }
        
        if task and task["state"] == "DONE":
            delete_task()
        
        create_task(task_text)
        update_task("PLANNING", "", 0)
        
        result = self._fsm_planning(task_text)
        
        new_state = "WAITING_APPROVAL"
        update_task(new_state, json.dumps(result["plan"]), 0)
        
        return {
            "text": result["text"],
            "state": new_state,
            "plan": result["plan"]
        }

    def _fsm_planning(self, task_text: str) -> dict:
        """Генерирует план задачи."""
        prompt = PLANNING_PROMPT.format(task_text=task_text)
        
        messages = [{"role": "system", "content": "Ты - планировщик задач."}]
        messages.append({"role": "user", "content": prompt})
        
        result = ask_llm(
            prompt="",
            model=self.model,
            temperature=0.3,
            messages=messages
        )
        
        violations = check_invariants(result["text"])
        if violations:
            return {
                "text": explain_violation(violations),
                "plan": []
            }
        
        plan = parse_plan(result["text"])
        
        return {
            "text": "План:\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan)]),
            "plan": plan
        }

    def fsm_approve(self) -> dict:
        """Подтверждение плана. /approve"""
        task = get_task()
        
        if not task:
            return {"text": "❌ Нет активной задачи. Используйте task_start \"задача\"", "error": True}
        
        current_state = task["state"]
        
        if current_state == "IDLE":
            return {"text": "❌ Нет активной задачи. Используйте task_start \"задача\"", "error": True}
        
        if current_state == "DONE":
            return {"text": "❌ Задача уже завершена. Используйте reset_task для новой задачи.", "error": True}
        
        if current_state == "EXECUTING":
            return {"text": "⚠️ Задача уже выполняется. Используйте next для следующего шага.", "error": True}
        
        if current_state == "VALIDATING":
            return {"text": "❌ Задача на валидации. Ожидайте результат проверки.", "error": True}
        
        if current_state == "PAUSED":
            return {"text": "❌ Задача приостановлена. Используйте resume для продолжения.", "error": True}
        
        if current_state == "PLANNING":
            return {"text": "⏳ План ещё генерируется. Подождите.", "error": True}
        
        if current_state != "WAITING_APPROVAL":
            return {"text": f"❌ Недопустимое действие для состояния {current_state}. Ожидается WAITING_APPROVAL.", "error": True}
        
        try:
            new_state = transition(current_state, "EXECUTING")
            update_task(new_state)
            self.execution_results = []
            return {"text": "✅ План утверждён. Начинаю выполнение.", "state": new_state}
        except StateError as e:
            return {"text": f"❌ Недопустимый переход: {e}", "error": True}

    def fsm_next(self) -> dict:
        """Выполнение следующего шага. /next"""
        task = get_task()
        
        if not task:
            return {"text": "❌ Нет активной задачи. Используйте task_start \"задача\"", "error": True}
        
        current_state = task["state"]
        
        if current_state == "DONE":
            return {"text": "❌ Задача уже завершена. Используйте reset_task для новой задачи.", "error": True}
        
        if current_state == "PAUSED":
            return {"text": "❌ Задача приостановлена. Используйте resume для продолжения.", "error": True}
        
        if current_state == "PLANNING":
            return {"text": "❌ План ещё не утверждён. Используйте approve для подтверждения плана.", "error": True}
        
        if current_state == "WAITING_APPROVAL":
            return {"text": "❌ План требует подтверждения. Используйте approve для начала выполнения.", "error": True}
        
        if current_state != "EXECUTING":
            return {"text": f"❌ Команда /next доступна в состоянии EXECUTING. Текущее: {current_state}", "error": True}
        
        try:
            transition(current_state, "EXECUTING")
        except StateError as e:
            return {"text": f"❌ Недопустимый переход: {e}", "error": True}
        
        try:
            plan = json.loads(task["plan"]) if task["plan"] else []
            current_step = task["current_step"]
            
            # Если шаги уже закончились - сразу валидация
            if current_step >= len(plan):
                new_state = "VALIDATING"
                update_task(new_state)
                return self._fsm_validating(task, plan)
            
            step_text = plan[current_step]
            
            result = self._fsm_execute(task, plan, current_step, step_text)
            self.execution_results.append(result["text"])
            
            # Если это был последний шаг - переходим в валидацию
            if current_step + 1 >= len(plan):
                new_state = "VALIDATING"
                task_for_validate = dict(task)
                task_for_validate["current_step"] = current_step
                update_task(new_state, task["plan"], current_step)
                return self._fsm_validating(task_for_validate, plan)
            else:
                current_step += 1
                update_task("EXECUTING", task["plan"], current_step)
                return {
                    "text": f"Шаг {current_step} выполнен.\n\n{result['text']}",
                    "state": "EXECUTING",
                    "current_step": current_step,
                    "total_steps": len(plan),
                    "step_text": step_text
                }
                
        except StateError as e:
            return {"text": str(e), "error": True}

    def _fsm_execute(self, task: dict, plan: list, current_step: int, step_text: str) -> dict:
        """Выполняет один шаг плана."""
        prompt = EXECUTION_PROMPT.format(
            task_text=task["task_text"],
            plan="\n".join([f"{i+1}. {s}" for i, s in enumerate(plan)]),
            current_step=current_step + 1,
            current_step_text=step_text
        )
        
        messages = [{"role": "system", "content": "Ты - исполнитель задач."}]
        messages.append({"role": "user", "content": prompt})
        
        result = ask_llm(
            prompt="",
            model=self.model,
            temperature=0.5,
            messages=messages
        )
        
        violations = check_invariants(result["text"])
        if violations:
            return {"text": explain_violation(violations)}
        
        return {"text": result["text"]}

    def _fsm_validating(self, task: dict, plan: list) -> dict:
        """Валидация результата."""
        prompt = VALIDATION_PROMPT.format(
            task_text=task["task_text"],
            plan="\n".join([f"{i+1}. {s}" for i, s in enumerate(plan)]),
            results="\n\n".join([f"Шаг {i+1}:\n{r}" for i, r in enumerate(self.execution_results)])
        )
        
        messages = [{"role": "system", "content": "Ты - валидатор. Верни строго VALID или NEED_FIX: причина."}]
        messages.append({"role": "user", "content": prompt})
        
        result = ask_llm(
            prompt="",
            model=self.model,
            temperature=0.2,
            messages=messages
        )
        
        text = result["text"].strip()
        
        if text.startswith("VALID"):
            new_state = "DONE"
            update_task(new_state)
            return {
                "text": "Задача выполнена!",
                "state": new_state,
                "valid": True
            }
        elif text.startswith("NEED_FIX"):
            reason = text[9:].strip() if len(text) > 9 else ""
            task = get_task()
            
            if not task:
                return {"text": "Ошибка: задача не найдена", "error": True}
            
            plan_result = self._fsm_planning(task["task_text"] + " (исправленный вариант)")
            plan_json = json.dumps(plan_result["plan"])
            
            new_state = "WAITING_APPROVAL"
            update_task(new_state, plan_json, 0)
            self.execution_results = []
            
            return {
                "text": f"Требуется корректировка: {reason}\n\nНовый план:\n{plan_result['text']}",
                "state": new_state,
                "valid": False,
                "plan": plan_result["plan"]
            }
        else:
            new_state = "DONE"
            update_task(new_state)
            return {
                "text": "Задача выполнена (валидация не распознана).",
                "state": new_state
            }

    def fsm_pause(self) -> dict:
        """Пауза. /pause"""
        task = get_task()
        
        if not task:
            return {"text": "❌ Нет активной задачи. Используйте task_start \"задача\"", "error": True}
        
        current_state = task["state"]
        
        if current_state != "EXECUTING":
            return {"text": f"❌ Пауза доступна только в состоянии EXECUTING. Текущее: {current_state}", "error": True}
        
        try:
            new_state = transition(current_state, "PAUSED")
            update_task(new_state)
            return {"text": "✅ Задача приостановлена.", "state": new_state}
        except StateError as e:
            return {"text": f"❌ Недопустимый переход: {e}", "error": True}

    def fsm_resume(self) -> dict:
        """Возобновление. /resume"""
        task = get_task()
        
        if not task:
            return {"text": "❌ Нет активной задачи. Используйте task_start \"задача\"", "error": True}
        
        current_state = task["state"]
        
        if current_state != "PAUSED":
            return {"text": f"❌ Resume доступно только из состояния PAUSED. Текущее: {current_state}", "error": True}
        
        try:
            new_state = transition(current_state, "EXECUTING")
            update_task(new_state)
            return {"text": "✅ Задача возобновлена.", "state": new_state}
        except StateError as e:
            return {"text": f"❌ Недопустимый переход: {e}", "error": True}

    def fsm_reset(self) -> dict:
        """Сброс задачи. /reset"""
        task = get_task()
        
        if not task:
            return {"text": "ℹ️ Нет активной задачи.", "state": "IDLE"}
        
        delete_task()
        self.execution_results = []
        return {"text": "✅ Задача сброшена. Можете начать новую: task_start \"задача\"", "state": "IDLE"}

    def fsm_status(self) -> dict:
        """Статус задачи. /status"""
        task = get_task()
        
        if not task:
            return {"state": "IDLE", "text": "ℹ️ Нет активной задачи."}
        
        plan = json.loads(task["plan"]) if task["plan"] else []
        
        return {
            "state": task["state"],
            "task_text": task["task_text"],
            "current_step": task["current_step"],
            "total_steps": len(plan),
            "text": f"Задача: {task['task_text']}\nСостояние: {task['state']}\nШаг: {task['current_step'] + 1}/{len(plan)}"
        }

    def reset_history(self):
        """Очищает short-term память."""
        self.short_term_memory = []

    def clear_working(self):
        """Очищает рабочую память."""
        clear_working_memory()

    def clear_all(self):
        """Очищает всю память."""
        clear_all_memory()

    def get_short_term(self) -> list:
        return self.short_term_memory.copy()

    def get_long_term(self) -> list:
        return get_long_term_memory()

    def get_working(self) -> list:
        return get_working_memory()

    def get_all_memory(self) -> dict:
        return {
            "short_term": self.get_short_term(),
            "working": self.get_working(),
            "long_term": self.get_long_term()
        }
