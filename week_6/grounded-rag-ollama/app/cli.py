"""CLI interface for Grounded RAG Chat Agent."""
import os
from rich.console import Console
from rich.table import Table
from app.agent import Agent
from app.evaluator import run_evaluation


console = Console()


def print_help():
    """Print available commands."""
    console.print("\n[bold]Available commands:[/bold]")
    console.print("  [cyan]rag_on[/cyan]       - Enable RAG mode")
    console.print("  [cyan]rag_off[/cyan]      - Disable RAG mode")
    console.print("  [cyan]filter_on[/cyan]    - Enable distance filtering")
    console.print("  [cyan]filter_off[/cyan]   - Disable distance filtering")
    console.print("  [cyan]rewrite_on[/cyan]  - Enable query rewrite")
    console.print("  [cyan]rewrite_off[/cyan]  - Disable query rewrite")
    console.print("  [cyan]eval[/cyan]        - Run evaluation (3 modes)")
    console.print("  [cyan]help[/cyan]        - Show this help")
    console.print("  [cyan]stats[/cyan]       - Show session statistics")
    console.print("  [cyan]reset[/cyan]       - Clear conversation history")
    console.print("  [cyan]history[/cyan]     - Show message history")
    console.print("  [cyan]exit[/cyan]        - Exit chat")
    console.print()


def print_stats(stats: dict):
    """Print session statistics."""
    table = Table(title="Session Statistics")
    table.add_column("Metric")
    table.add_column("Value")
    
    table.add_row("Requests", str(stats["requests"]))
    table.add_row("Total tokens (input)", str(stats["total_input_tokens"]))
    table.add_row("Total tokens (output)", str(stats["total_output_tokens"]))
    table.add_row("Total tokens", str(stats["total_tokens"]))
    table.add_row("Total cost (₽)", str(stats["total_cost"]))
    
    console.print(table)


def main():
    """Main CLI entry point."""
    console.print("[bold cyan]=== Grounded RAG Chat Agent ===[/bold cyan]")
    console.print("[bold cyan]RAG с проверкой источников и цитат[/bold cyan]")
    console.print()
    console.print("[cyan]Индекс:[/cyan] Fire + MkDocs (fixed)")
    console.print("[cyan]Embeddings:[/cyan] Ollama (nomic-embed)")
    llm_label = "Ollama (mistral)" if os.getenv("LLM_MODE") == "local" else "OpenAI (GPT-4o-mini)"
    console.print(f"[cyan]LLM:[/cyan] {llm_label}")
    console.print()
    console.print("[cyan]Команды:[/cyan] rag_on/off, filter_on/off, rewrite_on/off, eval, help, stats, reset, history, exit")
    console.print()
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(model=model, rag_enabled=True, use_filter=False, use_rewrite=False)
    
    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }
    
    # SAFE MODE indicator
    if agent.rag_enabled:
        console.print("[bold green][SAFE MODE][/bold green]\n")
    
    while True:
        try:
            rag_status = "[RAG ON]" if agent.rag_enabled else "[RAG OFF]"
            filter_status = "[FILTER ON]" if agent.use_filter else "[FILTER OFF]"
            rewrite_status = "[REWRITE ON]" if agent.use_rewrite else "[REWRITE OFF]"
            user_input = console.input(f"[bold blue]Вы ({rag_status} {filter_status} {rewrite_status}):[/bold blue] ")
            
            command = user_input.strip().lower()
            
            if command in ("exit", "quit", "выход"):
                console.print("\n[bold]Session Statistics:[/bold]")
                print_stats(stats)
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            if command == "help" or command == "help":
                print_help()
                continue
            
            if command == "rag_on":
                agent.enable_rag()
                console.print("[green]RAG mode enabled[/green]")
                console.print("[bold green][SAFE MODE][/bold green]\n")
                continue
            
            if command == "rag_off":
                agent.disable_rag()
                console.print("[yellow]RAG mode disabled[/yellow]\n")
                continue
            
            if command == "filter_on":
                agent.enable_filter()
                console.print("[green]Filter enabled (MAX_DISTANCE=300.0)[/green]\n")
                continue
            
            if command == "filter_off":
                agent.disable_filter()
                console.print("[yellow]Filter disabled[/yellow]\n")
                continue
            
            if command == "rewrite_on":
                agent.enable_rewrite()
                console.print("[green]Query rewrite enabled[/green]\n")
                continue
            
            if command == "rewrite_off":
                agent.disable_rewrite()
                console.print("[yellow]Query rewrite disabled[/yellow]\n")
                continue
            
            if command == "eval":
                console.print("[bold]Запускаю оценку...[/bold]")
                run_evaluation(agent)
                continue
            
            if command == "stats":
                print_stats(stats)
                console.print()
                continue
            
            if command == "reset":
                agent.reset_history()
                console.print("[yellow]History cleared.[/yellow]\n")
                continue
            
            if command == "history":
                history = agent.get_history()
                console.print(f"[dim]Messages in history: {len(history)}[/dim]\n")
                for i, msg in enumerate(history):
                    role = msg["role"]
                    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    console.print(f"  [{i}] {role}: {content}")
                console.print()
                continue
            
            if not user_input.strip():
                continue
            
            with console.status("[bold green]Думаю...[/bold green]") as status:
                result = agent.ask(user_input)
            
            stats["requests"] += 1
            stats["total_input_tokens"] += result.get("input_tokens", 0)
            stats["total_output_tokens"] += result.get("output_tokens", 0)
            stats["total_tokens"] += result.get("total_tokens", 0)
            stats["total_cost"] += result.get("cost", 0)
            
            # Проверка fallback
            if result.get("fallback", False):
                console.print(f"\n[bold red]Агент:[/bold red] {result['text']}\n")
            else:
                console.print(f"\n[bold green]Агент:[/bold green] {result['text']}\n")
            
            if agent.rag_enabled and result.get("retrieved_chunks"):
                chunks = result["retrieved_chunks"]
                console.print(f"[dim]Найдено чанков: {len(chunks)}[/dim]")
        
        except KeyboardInterrupt:
            console.print("\n[bold]Session Statistics:[/bold]")
            print_stats(stats)
            console.print("\n[yellow]Exit (Ctrl+C)[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
