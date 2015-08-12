__author__ = 'deathowl'

class BaseReporter(object):
    """
    Base implementation for a Reporter, all reporters should subclass
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

    def report_task_exection_time(self, queue_name, exection_time):
        """
        Report that the execution time of a job
        """
        raise NotImplementedError