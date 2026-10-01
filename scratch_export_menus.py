import json
from api.app.services.meal_service import meal_service
import asyncio

async def export():
    kyk_data = await meal_service.get_kyk_meals(year=2026, month=10)
    
    # We need to construct osem data for 2026-10 since meal_service logic relies on today's date sometimes,
    # wait, meal_service.get_osem_meals() uses get_tr_now() which is Oct 2026, so it's fine.
    
    # Actually wait, get_osem_meals() gets current month which is October 2026 because of the mock time,
    # but I can just call _build_osem_month(2026, 10) directly to be safe
    osem_data = meal_service._build_osem_month(2026, 10)
    
    ts_content = f"""export const octKykData = {json.dumps(kyk_data, ensure_ascii=False, indent=4)};

export const octOsemData = {json.dumps(osem_data, ensure_ascii=False, indent=4)};
"""
    with open("frontend/src/data/octoberMenus.ts", "w", encoding="utf-8") as f:
        f.write(ts_content)

asyncio.run(export())
