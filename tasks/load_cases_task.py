import sys
import os
import subprocess

from qgis.core import Qgis

from util.redirect_stdout import redirect_stdout
from dycast_qgis.services.logging_service import log_message, log_exception

MESSAGE_CATEGORY = 'Messages'


def get_current_directory():
    return os.path.dirname(os.path.realpath(__file__))


def run(task, file_path):
    log_message("Started load_cases task", Qgis.Info)
    with redirect_stdout():
        from dycast_app.dycast import main as dycast_main

        dycast_main(["load_cases", "--srid-cases",
                     "3857", "--file", file_path])
        return "Success!"


def finished(exception, result=None, ):
    if result:
        log_message("Succesfully finished the load_cases task", Qgis.Success)
    else:
        if exception:
            log_message("Failed to run the load_cases task.", Qgis.Critical)
            log_exception(exception)
            raise exception

        log_message(
            "Failed to run the load_cases task. No exception was raised", Qgis.Warning)
