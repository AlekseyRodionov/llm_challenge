"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет историей сообщений и взаимодействием с LLM.
"""
from app.llm_client import ask_llm, get_history_tokens, get_request_tokens, check_token_limit, get_max_tokens
from app.storage import MessageStorage
from app.summarizer import compress_context, get_context_stats


class Agent:
    """
    LLM агент с поддержкой истории сообщений.
    
    Агент хранит контекст диалога и позволяет поддерживать
    беседу с учетом предыдущих сообщений.
    """
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        load_history: bool = False,
        compression_enabled: bool = False,
        keep_last: int = 5,
        compress_threshold: int = 10
    ):
        """
        Инициализация агента.
        
        Args:
            model: Название модели для LLM (по умолчанию из .env)
            temperature: Параметр temperature (0-2)
            load_history: Загружать ли историю из БД
            compression_enabled: Включено ли сжатие контекста
            keep_last: Сколько последних сообщений хранить "как есть"
            compress_threshold: Порог для сжатия
        """
        self.model = model
        self.temperature = temperature
        self.storage = MessageStorage()
        self.messages = []
        self.compression_enabled = compression_enabled
        self.keep_last = keep_last
        self.compress_threshold = compress_threshold
        self.summary = ""
        self.compression_count = 0
        self.summary_tokens_spent = 0
        
        if load_history and self.storage.has_history():
            loaded = self.storage.load_messages()
            self._add_system_prompt()
            self.messages.extend(loaded)
            self.summary = self.storage.load_summary()
        else:
            self._add_system_prompt()

    def save_history(self):
        """Сохраняет историю сообщений и summary в БД."""
        if self.messages:
            messages_to_save = [m for m in self.messages if m.get("role") != "system"]
            self.storage.clear_history()
            self.storage.save_messages(messages_to_save)
            if self.summary:
                self.storage.save_summary(self.summary)

    def _add_system_prompt(self):
        """Добавляет системный промпт в начало истории."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник."
        })

    def check_limit(self, user_message: str = "") -> dict:
        """Проверяет лимит токенов перед запросом."""
        history_tokens = get_history_tokens(self.messages, self.model)
        request_tokens = get_request_tokens(user_message, self.model)
        return check_token_limit(history_tokens, request_tokens, self.model)

    def _maybe_compress(self):
        """Проверяет и выполняет сжатие если нужно."""
        if not self.compression_enabled:
            return
        
        user_messages = [m for m in self.messages if m.get("role") != "system"]
        
        if len(user_messages) <= self.compress_threshold:
            return
        
        self.messages, self.summary = compress_context(
            messages=self.messages,
            keep_last=self.keep_last,
            compress_threshold=self.compress_threshold,
            model=self.model,
            existing_summary=self.summary
        )
        
        self.compression_count += 1

    def ask(self, user_message: str) -> dict:
        """
        Отправляет сообщение агенту и получает ответ.
        
        Args:
            user_message: Сообщение от пользователя
        
        Returns:
            Словарь с ответом и метриками от LLM
        """
        self._maybe_compress()
        
        result = ask_llm(
            prompt=user_message,
            model=self.model,
            temperature=self.temperature,
            messages=self.messages
        )

        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": result["text"]})
        
        self.save_history()

        return result

    def reset_history(self):
        """Очищает историю сообщений, сбрасывая системный промпт."""
        self.messages = []
        self.summary = ""
        self.compression_count = 0
        self._add_system_prompt()
        self.storage.clear_history()
        self.storage.clear_summary()

    def enable_compression(self):
        """Включает режим сжатия контекста."""
        self.compression_enabled = True

    def disable_compression(self):
        """Выключает режим сжатия контекста."""
        self.compression_enabled = False

    def get_compression_stats(self) -> dict:
        """Возвращает статистику сжатия."""
        context_stats = get_context_stats(self.messages, self.model)
        return {
            "compression_enabled": self.compression_enabled,
            "compression_count": self.compression_count,
            "summary": self.summary[:100] + "..." if len(self.summary) > 100 else self.summary,
            "context_stats": context_stats
        }

    def get_history(self) -> list:
        """
        Возвращает копию истории сообщений.
        
        Returns:
            Список сообщений [{role, content}, ...]
        """
        return self.messages.copy()
