import difflib
from .utils.ansi import YELLOW, RESET, BOLD

class Suggestor:
    def __init__(self, items: list[str]) -> None:
        self.items = items

    def suggest(self, target: str, limit: int = 1) -> list[str]:
        return difflib.get_close_matches(target, self.items, n=limit, cutoff=0.6)

    def print_suggestion(self, target: str, context: str = "Command") -> None:
        matches = self.suggest(target)
        if matches:
            print(f"{BOLD}{YELLOW}CLIENTCORD WARN{RESET} {context} '{target}' not found. {BOLD}Did you mean: {matches[0]}?{RESET}")
