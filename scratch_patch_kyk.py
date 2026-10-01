import sys

with open('api/app/data/kyk_manual_menus.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('def _day(date_raw: str, date_tr: str, breakfast: list, dinner: list) -> dict:', 'def _day(date_raw: str, date_tr: str, breakfast: list, dinner: list, total_calories_breakfast: int = None, total_calories_dinner: int = None) -> dict:')
content = content.replace('"total_calories_breakfast": None,', '"total_calories_breakfast": total_calories_breakfast,')
content = content.replace('"total_calories_dinner": None,', '"total_calories_dinner": total_calories_dinner,')

with open('scratch_out.py', 'r', encoding='utf-8') as f:
    oct_kyk = f.read()

content = content.replace('MANUAL_MENUS = {', oct_kyk + '\nMANUAL_MENUS = {\n    "2026-10": _OCTOBER_2026,')

with open('api/app/data/kyk_manual_menus.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('KYK updated.')
