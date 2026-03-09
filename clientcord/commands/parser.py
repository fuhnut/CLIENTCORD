from typing import Any

def default_prefix_parser(content: str, prefix_list: list[str]) -> tuple[str, dict[str, str]] | None:
    used_prefix = None
    for p in prefix_list:
        if content.startswith(p):
            used_prefix = p
            break
            
    if not used_prefix:
        return None
        
    content = content[len(used_prefix):].strip()
    if not content:
        return None
        
    parts = content.split()
    command_name = parts[0]
    
    args = {"__positional__": []}
    current_key = None
    current_value = []
    
    for part in parts[1:]:
        if part.startswith("-"):
            if current_key:
                args[current_key] = " ".join(current_value)
            elif current_value:
                args["__positional__"].extend(current_value)
                
            current_key = part[1:]
            current_value = []
        else:
            current_value.append(part)
                
    if current_key:
        args[current_key] = " ".join(current_value)
    elif current_value:
        args["__positional__"].extend(current_value)
        
    return command_name, args
