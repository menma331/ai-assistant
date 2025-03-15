import re


def extract_source(text: str) -> str:
    """Ищем подстроку вида "\nИсточник: [источник]" в конце строки"""
    match = re.search(r'\nИсточник: .*$', text, flags=re.MULTILINE)
    if match:
        return match.group(0).strip()  # Возвращаем найденный источник
    return ""  # Если источника нет, возвращаем пустую строку