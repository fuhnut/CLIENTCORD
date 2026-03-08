import difflib

def get_suggestion(word: str, possibilities: list[str], n: int = 1, cutoff: float = 0.6) -> list[str]:
    return difflib.get_close_matches(word, possibilities, n=n, cutoff=cutoff)
