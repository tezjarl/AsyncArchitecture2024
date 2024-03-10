from apscheduler.schedulers.background import BackgroundScheduler
from event_processors import process_payments


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_payments, 'cron', hour=0, minute=0, second=1)
    scheduler.start()