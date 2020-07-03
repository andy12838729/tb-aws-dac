# Supports all actions concerning applications
import json
from pprint import pformat

from celery import states
from celery.result import AsyncResult
from flask import abort

import config
from gcpdac.application_ci import create_application, delete_application
from gcpdac.celery_tasks import deploy_application_task, destroy_application_task

logger = config.logger


def create(applicationDetails):
    logger.debug(pformat(applicationDetails))

    result = create_application(applicationDetails)
    if result.get("tf_return_code") == 0:
        return result, 201
    else:
        abort(500, "Failed to deploy your application")


def delete(oid):
    logger.debug("Id is {}".format(oid))

    applicationDetails = {"id": oid}
    result = delete_application(applicationDetails)
    if result.get("tf_return_code") == 0:
        return {}, 200
    else:
        abort(500, "Failed to delete  your application")


def create_async(applicationDetails):
    logger.debug(pformat(applicationDetails))

    result = deploy_application_task.delay(applicationDetails=applicationDetails)

    logger.info("Task ID %s", result.task_id)

    context = {"taskid": result.task_id}

    # TODO handle celery failure
    success = True
    if success == True:
        return context, 201
    else:
        abort(500, "Failed to create your application")


def delete_async(oid):
    logger.debug("Id is {}".format(oid))

    applicationDetails = {"id": oid}

    result = destroy_application_task.delay(applicationDetails=applicationDetails)

    logger.info("Task ID %s", result.task_id)

    context = {"taskid": result.task_id}

    # TODO handle celery failure
    success = True
    if success == True:
        return context, 201
    else:
        abort(500, "Failed to delete your application")


def create_application_result(taskid):
    logger.info("CREATE application RESULT %s", format(taskid))
    status = AsyncResult(taskid).status
    if status == states.SUCCESS or status == states.FAILURE:
        retval = AsyncResult(taskid).get(timeout=1.0)
        return_code = retval["return_code"]
        # tf_outputs = retval["tf_outputs"]
        if return_code > 0:
            status = states.FAILURE
            payload = {}
        else:
            payload = {}

        return {'status': status, "payload": json.dumps(payload)}
    else:
        return {'status': status}


def delete_application_result(taskid):
    logger.info("DELETE application RESULT %s", format(taskid))
    status = AsyncResult(taskid).status
    if status == states.SUCCESS or status == states.FAILURE:
        retval = AsyncResult(taskid).get(timeout=1.0)
        return_code = retval["return_code"]
        if return_code > 0:
            status = states.FAILURE
        return {'status': status, "return_code": return_code}
    else:
        return {'status': status}


