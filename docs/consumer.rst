.. _consuming-tasks:

Consuming Tasks
===============

To run the consumer, simply point it at the "import path" to your application's
:py:class:`Huey` instance.  For example, here is how I run it on my blog:

.. code-block:: bash

    huey_consumer.py blog.main.huey --logfile=../logs/huey.log

The concept of the "import path" has been the source of a few questions, but its
actually quite simple.  It is simply the dotted-path you might use if you were
to try and import the "huey" object in the interactive interpreter:

.. code-block:: pycon

    >>> from blog.main import huey

You may run into trouble though when "blog" is not on your python-path. To
work around this:

1. Manually specify your pythonpath: ``PYTHONPATH=/some/dir/:$PYTHONPATH huey_consumer.py blog.main.huey``.
2. Run ``huey_consumer.py`` from the directory your config module is in.  I use
   supervisord to manage my huey process, so I set the ``directory`` to the root
   of my site.
3. Create a wrapper and hack ``sys.path``.

.. warning::
    If you plan to use `supervisord <http://supervisord.org/>`_ to manage your consumer process, be sure that you are running the consumer directly and without any intermediary shell scripts. Shell script wrappers interfere with supervisor's ability to terminate and restart the consumer Python process. For discussion see `GitHub issue 88 <https://github.com/coleifer/huey/issues/88>`_.

Options for the consumer
------------------------

The following table lists the options available for the consumer as well as
their default values.

``-l``, ``--logfile``
    Path to file used for logging.  When a file is specified, by default Huey
    will use a rotating file handler (1MB / chunk) with a maximum of 3 backups.
    You can attach your own handler (``huey.logger``) as well.  The default
    loglevel is ``INFO``.

``-v``, ``--verbose``
    Verbose logging (equates to ``DEBUG`` level).  If no logfile is specified
    and verbose is set, then the consumer will log to the console.  **This is
    very useful for testing/debugging.**

``-q``, ``--quiet``
    Only log errors. The default loglevel for the consumer is ``INFO``.

``-w``, ``--workers``
    Number of worker threads/processes/greenlets, the default is ``1`` but
    some applications may want to increase this number for greater throughput.

``-k``, ``--worker-type``
    Choose the worker type, ``thread``, ``process`` or ``greenlet``. The default
    is ``thread``.

``-n``, ``--no-periodic``
    Indicate that this consumer process should *not* enqueue periodic tasks.

``-d``, ``--delay``
    When using a "polling"-type queue backend, the amount of time to wait
    between polling the backend.  Default is 0.1 seconds.

``-m``, ``--max-delay``
    The maximum amount of time to wait between polling, if using weighted
    backoff.  Default is 10 seconds.

``-b``, ``--backoff``
    The amount to back-off when polling for results.  Must be greater than
    one.  Default is 1.15.

``-s``, ``--scheduler-interval``
    The frequency with which the scheduler should run. By default this will run
    every second, but you can increase the interval to as much as 60 seconds.

``-u``, ``--utc``
    Indicates that the consumer should use UTC time for all tasks, crontabs
    and scheduling.  Default is True, so in practice you should not need to
    specify this option.

``--localtime``
    Indicates that the consumer should use localtime for all tasks, crontabs
    and scheduling.  Default is False.

Examples
^^^^^^^^

Running the consumer with 8 threads, a logfile for errors only, and a very
short polling interval:

.. code-block:: bash

  huey_consumer.py my.app.huey -l /var/log/app.huey.log -w 8 -b 1.1 -m 1.0

Running single-threaded without a crontab and logging to stdout:

.. code-block:: bash

    huey_consumer.py my.app.huey -v -n

Using multi-processing to run 4 worker processes:

.. code-block:: bash

    huey_consumer.py my.app.huey -w 4 -k process


Consumer Internals
------------------

The consumer is composed of a master process, the scheduler, and the worker(s). Depending on the worker type chosen, these will be either threads, processes or greenlets.

These threads coordinate the receipt, execution and scheduling of various
tasks.  What happens when you call a decorated function in your application?

1. You call a function -- huey has decorated it, which triggers a message being
   put into the queue.  At this point your application returns.  If you are using
   a "data store", then you will be return an :py:class:`AsyncData` object.
2. In a separate process, a worker will be listening for new messages --
   one of the workers will pull down the message.
3. The worker looks at the message and checks to see if it can be
   run (i.e., was this message "revoked"?  Is it scheduled to actually run
   later?).  If it is revoked, the message is thrown out.  If it is scheduled
   to run later, it gets added to the schedule.  Otherwise, it is executed.
4. The worker thread executes the task.  If the task finishes, any results are
   published to the result store (if one is configured).  If the task fails and
   can be retried, it is either enqueued or added to the schedule (which happens
   if a delay is specified between retries).

While all this is going on, the Scheduler is looking at its schedule to see
if any tasks are ready to be executed.  If a task is ready to run, it is
enqueued and will be processed by a worker.

If you are using the Periodic Task feature (cron), then every minute, the
scheduler will check through the various periodic tasks to see if any should
be run. If so, these tasks are enqueued.

When the consumer is shut-down cleanly (SIGTERM), any workers still involved in the execution of a task will complete their work.

Consumer Event Emitter
----------------------

If you specify a :py:class:`RedisEventEmitter` when setting up your :py:class:`Huey`
instance (or if you choose to use :py:class:`RedisHuey`), the consumer will publish
real-time events about the status of various tasks.  You can subscribe to these
events in your own application.

When an event is emitted, the following information is provided (serialized as
JSON):

* ``status``: a String indicating what type of event this is.
* ``id``: the UUID of the task.
* ``task``: a user-friendly name indicating what type of task this is.
* ``retries``: how many retries the task has remaining.
* ``retry_delay``: how long to sleep before retrying the task in event of failure.
* ``execute_time``: A unix timestamp indicating when the task is scheduled to
    execute (this may be ``None``).
* ``error``: A boolean value indicating if there was an error.
* ``traceback``: A string traceback of the error, if one occurred.

The following events are emitted by the consumer:

* ``enqueued``: sent when a task is enqueued, i.e., you call a ``task()`` decorated function.
* ``scheduled``: sent when a task is added to the schedule for execution in the future. For instance the worker pops off a task, sees that it should be run in an hour, and therefore schedules it.
* ``revoked``: sent when a task is not executed because it has been revoked.
* ``started``: sent when a worker begins executing a task.
* ``finished``: sent when a worker finishes executing a task and has stored the result.
* ``error``: sent when an exception occurs while executing a task.
* ``retrying``: sent when task that failed will be retried.
