import logging

from celery import signals
from celery.signals import after_setup_logger

from config import get_celery
from gcpdac.solution_terraform import run_terraform

celery_app = get_celery()

logger = logging.getLogger('worker')
log_format = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.INFO,format=log_format)

@celery_app.task()
def add_together_two(a, b):
    logger.debug("ADD_TOGETHER_TWO IN WORKER")
    return a + b

@celery_app.task()
def deploy_solution_task(solutionDetails):
    run_terraform(solutionDetails, "apply")
    # just return call = True TODO
    return True


@celery_app.task()
def destroy_solution_task(solutionDetails):
    run_terraform(solutionDetails, "destroy")
    # just return call = True TODO
    return True

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # FileHandler
    fh = logging.FileHandler('logs.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # # SysLogHandler
    # slh = logging.handlers.SysLogHandler(address=('logsN.papertrailapp.com', '...'))
    # slh.setFormatter(formatter)
    # logger.addHandler(slh)

# DON'T REMOVE - added to fix celery logging error
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass

if __name__ == '__main__':
    celery_app.worker_main('worker')

