from app.celery_config import celery
#from celery.beat import Scheduler

if __name__ == "__main__":
    celery.start(argv=["celery", "beat", "--loglevel=info"])