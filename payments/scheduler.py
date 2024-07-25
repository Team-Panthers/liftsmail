from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .services import check_and_update_subscriptions  # Adjust the import path as needed

def start_scheduler():
    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    
    # Add job with IntervalTrigger to run every 12 hours
    scheduler.add_job(
        check_and_update_subscriptions,
        IntervalTrigger(hours=12, start_date=timezone.now()),  # Runs every 12 hours
        id='subscription_update_job',
        name='Update subscriptions to free plan after end date',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
