import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.meal_service import meal_service

async def test_kyk():
    result = await meal_service.get_kyk_meals()
    print(f'Toplam gün sayısı: {len(result)}')
    
    today_found = any(day.get('isToday', False) for day in result)
    print(f'Bugün için veri var mı: {today_found}')
    
    if result:
        print(f'İlk gün: {result[0].get("date", "N/A")}')
        print(f'Son gün: {result[-1].get("date", "N/A")}')
        
        # Bugünün verisini bul
        today_data = next((day for day in result if day.get('isToday', False)), None)
        if today_data:
            print(f'Bugünün menüsü bulundu: {today_data.get("date", "N/A")}')
        else:
            print('Bugünün menüsü bulunamadı!')
    
    return result

if __name__ == "__main__":
    asyncio.run(test_kyk())
