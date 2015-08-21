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
        self.connection.incr("%s.enqueued" % queue_name)

    def report_task_started(self, queue_name):
        """
        Report that the execution of a job has been started
        """
        self.connection.incr("%s.started" % queue_name)

    def report_task_finished(self, queue_name):
        """
        Report that the execution of a job has been finished

        """
        self.connection.incr("%s.finished" % queue_name)

    def report_task_failed(self, queue_name):
        """
        Report that the execution of a job has failed
        """
        self.connection.incr("%s.failed" % queue_name)

    def report_task_queued_time(self, queue_name, runtime):
        """
        Report that the time spent in queue
        """
        self.connection.timing("%s.time.execution" % queue_name, runtime)

    def report_task_execution_time(self, queue_name, runtime):
        """
        Report that the execution time of a job
        """
        self.connection.timing("%s.time.execution" % queue_name, runtime)
