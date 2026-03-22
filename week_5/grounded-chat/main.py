"""Main entry point for Grounded Chat Agent."""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import argparse
from app.cli import main, run_demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grounded Chat Agent")
    parser.add_argument(
        "--demo", 
        choices=["mkdocs", "fire"], 
        help="Run demo scenario (mkdocs or fire)"
    )
    args = parser.parse_args()
    
    if args.demo:
        run_demo(args.demo)
    else:
        main()
