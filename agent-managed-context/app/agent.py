"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет контекстом диалога с помощью различных стратегий:
- Sliding Window: хранит последние N сообщений
- Sticky Facts: key-value память + последние N сообщений
- Branching: ветвление диалога с переключением между ветками
"""
from app.llm_client import ask_llm
from app.storage import MessageStorage


class ContextStrategy:
    """Базовый класс для стратегий управления контекстом."""
    
    def get_context_messages(self, all_messages: list) -> list:
        """Вернуть список сообщений для отправки в LLM."""
        raise NotImplementedError
    
    def after_user_message(self, user_message: str, assistant_response: str = None):
        """Вызывается после сообщения пользователя."""
        pass
    
    def get_prompt_suffix(self) -> str:
        """Дополнительный промпт для LLM (например, facts)."""
        return ""


class SlidingWindowStrategy(ContextStrategy):
    """Стратегия Sliding Window - хранит последние N сообщений."""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
    
    def get_context_messages(self, all_messages: list) -> list:
        if len(all_messages) <= self.window_size:
            return all_messages
        return all_messages[-self.window_size:]
    
    def get_name(self) -> str:
        return f"Sliding Window (N={self.window_size})"


class StickyFactsStrategy(ContextStrategy):
    """Стратегия Sticky Facts - key-value память + последние N сообщений."""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.facts = {}
    
    def get_context_messages(self, all_messages: list) -> list:
        result = []
        
        recent = all_messages[-self.window_size:] if len(all_messages) > self.window_size else all_messages
        
        if self.facts:
            facts_text = self._format_facts()
            recent = [{"role": "system", "content": f"Запомни эти факты: {facts_text}"}] + recent
        
        result.extend(recent)
        
        return result
    
    def _format_facts(self) -> str:
        if not self.facts:
            return "(нет фактов)"
        lines = [f"- {k}: {v}" for k, v in self.facts.items()]
        return "\n".join(lines)
    
    def after_user_message(self, user_message: str, assistant_response: str = None):
        """Анализирует сообщение и обновляет факты."""
        self._extract_facts(user_message)
    
    def _extract_facts(self, text: str):
        """Простое извлечение фактов из текста."""
        text_lower = text.lower()
        
        if "кота" in text_lower or "кош" in text_lower:
            import re
            match = re.search(r'зовут\s+(\w+)', text_lower)
            if match:
                self.facts["имя_кота"] = match.group(1)
        
        if "живу" in text_lower and "город" in text_lower:
            import re
            match = re.search(r'город[аеу]?\s+(\w+)', text_lower)
            if match:
                self.facts["город"] = match.group(1)
        
        if "мне" in text_lower and "лет" in text_lower:
            import re
            match = re.search(r'(\d+)\s*лет', text_lower)
            if match:
                self.facts["возраст"] = match.group(1)
        
        if "работаю" in text_lower:
            import re
            match = re.search(r'работаю\s+(\w+)', text_lower)
            if match:
                self.facts["профессия"] = match.group(1)
        
        if "интернет-магазин" in text_lower or "магазин" in text_lower:
            self.facts["проект"] = "интернет-магазин"
        
        if "одежда" in text_lower:
            self.facts["товары"] = "одежда"
        
        if "корзина" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", корзина"
        
        if "оплата" in text_lower or "карт" in text_lower:
            self.facts["оплата"] = "карта"
        
        if "доставка" in text_lower:
            self.facts["доставка"] = "нужна"
        
        if "бюджет" in text_lower:
            import re
            match = re.search(r'(\d+)\s*(тыс|тысяч|руб)', text_lower)
            if match:
                self.facts["бюджет"] = match.group(1) + " тыс руб"
        
        if "срок" in text_lower or "месяц" in text_lower:
            import re
            match = re.search(r'(\d+)\s*месяц', text_lower)
            if match:
                self.facts["срок"] = match.group(1) + " месяцев"
        
        if "регистрация" in text_lower or "регистрир" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", регистрация"
        
        if "админка" in text_lower or "админ" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", админка"
        
        if "аналитика" in text_lower or "анализ" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", аналитика"
        
        if "акци" in text_lower or "скидк" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", акции/скидки"
        
        if "возврат" in text_lower:
            self.facts["функция"] = self.facts.get("функция", "") + ", возврат"
        
        if "мобильн" in text_lower or "приложение" in text_lower:
            self.facts["дополнительно"] = "мобильное приложение"
    
    def get_prompt_suffix(self) -> str:
        return self._format_facts()
    
    def get_name(self) -> str:
        return f"Sticky Facts (N={self.window_size})"
    
    def get_facts(self) -> dict:
        return self.facts.copy()


class BranchingStrategy(ContextStrategy):
    """Стратегия Branching - ветвление диалога."""
    
    def __init__(self):
        self.branches = {"main": [], "alt": []}
        self.current_branch = "main"
    
    def get_context_messages(self, all_messages: list) -> list:
        messages = self.branches.get(self.current_branch, [])
        
        if not messages:
            system_msg = {"role": "system", "content": "Ты полезный AI помощник."}
            return [system_msg]
        
        return messages
    
    def after_user_message(self, user_message: str, assistant_response: str = None):
        branch = self.branches[self.current_branch]
        branch.append({"role": "user", "content": user_message})
        if assistant_response:
            branch.append({"role": "assistant", "content": assistant_response})
    
    def switch_branch(self):
        """Переключает на другую ветку."""
        self.current_branch = "alt" if self.current_branch == "main" else "main"
        
        if not self.branches[self.current_branch]:
            self.branches[self.current_branch] = [{"role": "system", "content": "Ты полезный AI помощник."}]
        
        return self.current_branch
    
    def get_current_branch(self) -> str:
        return self.current_branch
    
    def get_all_branches(self) -> dict:
        return self.branches.copy()
    
    def get_name(self) -> str:
        return f"Branching (ветка: {self.current_branch})"


class Agent:
    """
    LLM агент с поддержкой различных стратегий управления контекстом.
    """
    
    STRATEGY_SLIDING = "sliding"
    STRATEGY_STICKY = "sticky"
    STRATEGY_BRANCHING = "branching"
    
    def __init__(self, model: str = None, temperature: float = 0.7, 
                 load_history: bool = False, strategy: str = "sliding",
                 window_size: int = 5):
        self.model = model
        self.temperature = temperature
        self.storage = MessageStorage()
        self.messages = []
        self.strategy_name = strategy
        self.window_size = window_size
        
        self._init_strategy(strategy)
        
        if load_history and self.storage.has_history():
            loaded = self.storage.load_messages()
            self._add_system_prompt()
            self.messages.extend(loaded)
        else:
            self._add_system_prompt()
    
    def _init_strategy(self, strategy: str):
        if strategy == self.STRATEGY_SLIDING:
            self.strategy = SlidingWindowStrategy(self.window_size)
        elif strategy == self.STRATEGY_STICKY:
            self.strategy = StickyFactsStrategy(self.window_size)
        elif strategy == self.STRATEGY_BRANCHING:
            self.strategy = BranchingStrategy()
        else:
            self.strategy = SlidingWindowStrategy(self.window_size)
    
    def set_strategy(self, strategy: str):
        """Изменить стратегию управления контекстом."""
        self.strategy_name = strategy
        self._init_strategy(strategy)
    
    def get_strategy_name(self) -> str:
        return self.strategy_name
    
    def get_strategy_display(self) -> str:
        return self.strategy.get_name()
    
    def switch_branch(self) -> str:
        """Переключить ветку (для Branching стратегии)."""
        if isinstance(self.strategy, BranchingStrategy):
            return self.strategy.switch_branch()
        return None
    
    def get_current_branch(self) -> str:
        if isinstance(self.strategy, BranchingStrategy):
            return self.strategy.get_current_branch()
        return None
    
    def get_all_branches(self) -> dict:
        if isinstance(self.strategy, BranchingStrategy):
            return self.strategy.get_all_branches()
        return {}
    
    def get_facts(self) -> dict:
        if isinstance(self.strategy, StickyFactsStrategy):
            return self.strategy.get_facts()
        return {}

    def save_history(self):
        """Сохраняет историю сообщений в БД."""
        if self.messages:
            messages_to_save = [m for m in self.messages if m.get("role") != "system"]
            self.storage.clear_history()
            self.storage.save_messages(messages_to_save)

    def _add_system_prompt(self):
        """Добавляет системный промпт в начало истории."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник."
        })

    def ask(self, user_message: str) -> dict:
        """Отправляет сообщение агенту и получает ответ."""
        if isinstance(self.strategy, BranchingStrategy):
            context = self.strategy.get_context_messages([])
        else:
            context = self.strategy.get_context_messages(self.messages)
        
        result = ask_llm(
            prompt=user_message,
            model=self.model,
            temperature=self.temperature,
            messages=context
        )

        if isinstance(self.strategy, BranchingStrategy):
            self.strategy.after_user_message(user_message, result["text"])
        else:
            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": result["text"]})
            self.strategy.after_user_message(user_message, result["text"])
        
        self.save_history()

        return result

    def reset_history(self):
        """Очищает историю сообщений."""
        self.messages = []
        self._add_system_prompt()
        self.storage.clear_history()
        
        if isinstance(self.strategy, BranchingStrategy):
            self.strategy.branches = {"main": [], "alt": []}
            self.strategy.current_branch = "main"
            if self.messages:
                self.strategy.branches["main"] = self.messages.copy()
        
        if isinstance(self.strategy, StickyFactsStrategy):
            self.strategy.facts = {}

    def get_history(self) -> list:
        """Возвращает историю сообщений."""
        if isinstance(self.strategy, BranchingStrategy):
            return self.strategy.get_context_messages([])
        return self.messages.copy()
