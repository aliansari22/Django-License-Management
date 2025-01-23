from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

def backup_and_send():
    call_command('backup_and_send')

def start_scheduler():
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(minute='0')  # This triggers the job at the start of every hour
    scheduler.add_job(backup_and_send, trigger)
    scheduler.start()
