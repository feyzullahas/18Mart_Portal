import sys

with open('api/app/services/meal_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

with open('scratch_osem_out.py', 'r', encoding='utf-8') as f:
    oct_osem = f.read()

content = content.replace('    def _build_osem_month', oct_osem + '\n    def _build_osem_month')

content = content.replace(
    '        elif year == 2026 and month == 9:\n            menus = self._osem_menus_september_2026()',
    '        elif year == 2026 and month == 9:\n            menus = self._osem_menus_september_2026()\n        elif year == 2026 and month == 10:\n            menus = self._osem_menus_october_2026()'
)

with open('api/app/services/meal_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OSEM updated.')
