"""
Scheduler to run the main pipeline on a schedule.

Uses cron time from config.ini to schedule when the job runs.
"""
import sys
import time
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Add shared to path
project_root = Path(__file__).parent.parent.parent.parent
shared_path = project_root / 'shared'
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from logger.logger import get_logger
from config.config import Config

log_path = Path("./logs/scheduler.log")
logger = get_logger("scheduler", str(log_path))


def run_job():
    """Run the main pipeline and track execution time."""
    start_time = time.time()
    
    print("Job started")
    logger.info("Job started")
    
    try:
        from main import main
        exit_code = main()
        
        execution_time = time.time() - start_time
        print(f"Job completed successfully. Time: {execution_time:.2f} seconds")
        logger.info(f"Job completed successfully. Time: {execution_time:.2f} seconds")
        
        return exit_code
        
    except KeyboardInterrupt:
        execution_time = time.time() - start_time
        print(f"Job interrupted. Time: {execution_time:.2f} seconds")
        logger.warning(f"Job interrupted. Time: {execution_time:.2f} seconds")
        return 1
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Job failed: {str(e)}. Time: {execution_time:.2f} seconds"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        return 1


def start_scheduler():
    """Start the scheduler using cron time from config."""
    try:
        config = Config()
        cron_time = config.get_cron_time()
        
        # Parse cron expression: minute hour day month day_of_week
        parts = cron_time.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_time}")
        
        minute, hour, day, month, day_of_week = parts
        
        logger.info(f"Starting scheduler with cron: {cron_time}")
        print(f"Scheduler started. Job will run at: {cron_time}")
        
        scheduler = BlockingScheduler()
        
        scheduler.add_job(
            run_job,
            trigger=CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            ),
            id='main_job',
            name='LoRaWAN Pipeline Job'
        )
        
        print("Scheduler is running. Press Ctrl+C to exit.")
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        print("\nScheduler stopped")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(start_scheduler())

