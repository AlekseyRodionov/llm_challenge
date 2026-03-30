"""CLI interface for RAG Chat Agent."""
import os
from rich.console import Console
from rich.table import Table
from app.agent import Agent
from app.evaluator import run_evaluation
from app.retriever import create_project_retriever
from app.generator import generate_dev_answer
from app.mcp.client import mcp_git_branch, mcp_project_files


console = Console()


def print_help():
    """Print available commands."""
    console.print("\n[bold]Available commands:[/bold]")
    console.print("  [cyan]rag_on[/cyan]    - Enable RAG mode")
    console.print("  [cyan]rag_off[/cyan]   - Disable RAG mode")
    console.print("  [cyan]eval[/cyan]     - Run evaluation (10 questions)")
    console.print("  [cyan]help[/cyan]     - Show this help")
    console.print("  [cyan]/help[/cyan]    - Dev Assistant (RAG + MCP)")
    console.print("  [cyan]/help branch[/cyan] - Show git branch")
    console.print("  [cyan]/help files[/cyan]  - Show project files")
    console.print("  [cyan]stats[/cyan]    - Show session statistics")
    console.print("  [cyan]reset[/cyan]    - Clear conversation history")
    console.print("  [cyan]history[/cyan]  - Show message history")
    console.print("  [cyan]exit[/cyan]     - Exit chat")
    console.print()


def filter_chunks_by_keywords(chunks: list, question: str, min_matches: int = 1) -> list:
    """Filter chunks that contain keywords from question."""
    keywords = question.lower().split()
    keywords = [w for w in keywords if len(w) > 2]
    
    if not keywords:
        return chunks
    
    filtered = []
    for chunk in chunks:
        text = chunk.get("text", "").lower()
        matches = sum(1 for kw in keywords if kw in text)
        if matches >= min_matches:
            filtered.append(chunk)
    
    return filtered if filtered else chunks


def handle_dev_help(question: str) -> dict:
    """Handle /help command with RAG + MCP."""
    branch = mcp_git_branch()
    files = mcp_project_files()
    
    retriever = create_project_retriever()
    chunks = retriever.retrieve(question, k=30)
    chunks = filter_chunks_by_keywords(chunks, question, min_matches=1)
    
    if not chunks:
        return {
            "text": "Не знаю",
            "sources": ["НЕТ"]
        }
    
    return generate_dev_answer(question, branch, files, chunks)


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
    console.print("[bold cyan]=== Dev Assistant ===[/bold cyan]")
    console.print("[bold cyan]RAG + MCP для документации проекта llm_challenge[/bold cyan]")
    console.print()
    console.print("[cyan]Индекс:[/cyan] llm_challenge (64 документа, 400 чанков)")
    console.print("[cyan]MCP:[/cyan] git branch + project files")
    console.print("[cyan]Embeddings:[/cyan] Ollama (nomic-embed-text)")
    console.print("[cyan]LLM:[/cyan] OpenAI (GPT-4o-mini)")
    console.print()
    console.print("[cyan]Команды:[/cyan] /help <вопрос>, /help branch, /help files, exit")
    console.print()
    
    model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    agent = Agent(model=model, rag_enabled=False)
    
    stats = {
        "requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0
    }
    
    while True:
        try:
            user_input = console.input(f"[bold blue]Dev:[/bold blue] ")
            
            command = user_input.strip().lower()
            
            if command in ("exit", "quit", "выход"):
                console.print("\n[bold]Session Statistics:[/bold]")
                print_stats(stats)
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            
            if command == "help" or command == "help":
                print_help()
                continue
            
            if user_input.startswith("/help"):
                parts = user_input.split(maxsplit=1)
                
                if len(parts) == 1:
                    console.print("[bold]Dev Assistant commands:[/bold]")
                    console.print("  /help <question> - Ask about the project")
                    console.print("  /help branch    - Show git branch")
                    console.print("  /help files     - Show project files")
                    console.print()
                    continue
                
                subcmd = parts[1].strip()
                
                if subcmd == "branch":
                    branch = mcp_git_branch()
                    console.print(f"[green]Branch: {branch}[/green]\n")
                    continue
                
                if subcmd == "files":
                    files = mcp_project_files()
                    console.print(f"[green]Files:[/green]\n{files}\n")
                    continue
                
                question = subcmd
                with console.status("[bold green]Ищу в документации...[/bold green]") as status:
                    result = handle_dev_help(question)
                
                sources = result.get("sources", ["НЕТ"])
                console.print(f"\n[bold]Ответ:[/bold] {result['text']}")
                console.print(f"[bold]Источники:[/bold] {', '.join(sources)}\n")
                continue
            
            if command == "rag_on":
                agent.enable_rag()
                console.print("[green]RAG mode enabled[/green]\n")
                continue
            
            if command == "rag_off":
                agent.disable_rag()
                console.print("[yellow]RAG mode disabled[/yellow]\n")
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
            stats["total_input_tokens"] += result["input_tokens"]
            stats["total_output_tokens"] += result["output_tokens"]
            stats["total_tokens"] += result["total_tokens"]
            stats["total_cost"] += result["cost"]
            
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
