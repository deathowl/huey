# -*- coding: utf-8 -*-
from huey.reporters.base import BaseReporter

__author__ = 'deathowl'

class StatsdReporter(BaseReporter):
    """
    Implementation for the StatsdReporter
    """

    def __init__(self, **connection):
        """
        Initialize the Queue - this happens once when the module is loaded

        :param name: A string representation of the name for this queue
        :param connection: Connection parameters for the queue
        """
        self.connection = connection

    def report_task_enqueued(self, queue_name):
        """
        Report that a job has been enqueued
        """
        raise NotImplementedError

    def report_task_started(self, queue_name):
        """
        Report that the execution of a job has been started
        """
        raise NotImplementedError

    def report_task_finished(self, queue_name):
        """
        Report that the execution of a job has been finished

        """
        raise NotImplementedError

    def report_task_failed(self, queue_name):
        """
        Report that the execution of a job has failed
        """
        raise NotImplementedError
