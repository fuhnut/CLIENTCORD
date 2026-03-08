class Option:
    def __init__(self, type: int, description: str = "", required: bool = False, choices: list = None, autocomplete: bool = False) -> None:
        self.type = type
        self.description = description
        self.required = required
        self.choices = choices or []
        self.autocomplete = autocomplete

def string(description: str = "", required: bool = False, choices: list = None, autocomplete: bool = False) -> Option:
    return Option(3, description, required, choices, autocomplete)

def integer(description: str = "", required: bool = False, choices: list = None, autocomplete: bool = False) -> Option:
    return Option(4, description, required, choices, autocomplete)

def boolean(description: str = "", required: bool = False) -> Option:
    return Option(5, description, required)

def user(description: str = "", required: bool = False) -> Option:
    return Option(6, description, required)

def channel(description: str = "", required: bool = False) -> Option:
    return Option(7, description, required)

def role(description: str = "", required: bool = False) -> Option:
    return Option(8, description, required)

def numeric(description: str = "", required: bool = False, choices: list = None, autocomplete: bool = False) -> Option:
    return Option(10, description, required, choices, autocomplete)

def attachment(description: str = "", required: bool = False) -> Option:
    return Option(11, description, required)
