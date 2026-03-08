from .utils import ansi
from .utils.memory import get_ram_usage_mb

def log(level: str, message: str, color: str) -> None:
    ram = get_ram_usage_mb()
    print(f"[{ansi.BOLD}RAM: {ram}MB{ansi.RESET}] {color}CLIENTCORD {level}{ansi.RESET} {message}")

def info(message: str) -> None:
    log("INFO", message, ansi.CYAN)

def debug(message: str) -> None:
    log("DEBUG", message, ansi.BLUE)

def warn(message: str) -> None:
    log("WARN", message, ansi.YELLOW)

def error(message: str) -> None:
    log("ERROR", message, ansi.RED)
