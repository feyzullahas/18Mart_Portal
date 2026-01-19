from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.bus_service import bus_service
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Scheduler'ı başlat ve görevleri ekle"""
        
        # Her gün saat 03:00'da PDF'leri güncelle
        self.scheduler.add_job(
            bus_service.update_pdfs,
            CronTrigger(hour=3, minute=0),
            id='update_bus_pdfs',
            name='Otobüs Saatleri PDF Güncelleme',
            replace_existing=True
        )
        
        logger.info("Scheduler başlatıldı - PDF güncellemeleri her gün 03:00'da çalışacak")
        self.scheduler.start()
    
    def shutdown(self):
        """Scheduler'ı kapat"""
        self.scheduler.shutdown()
        logger.info("Scheduler kapatıldı")

scheduler_service = SchedulerService()
