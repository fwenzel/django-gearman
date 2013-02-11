import pickle
from os import getcwd
from zlib import adler32

import gearman

from django.conf import settings


def default_taskname_decorator(task_name):
    return "%s.%s" % (str(adler32(getcwd()) & 0xffffffff), task_name)

task_name_decorator = getattr(settings, 'GEARMAN_JOB_NAME',
                              default_taskname_decorator)


class PickleDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return pickle.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return pickle.loads(decodable_string)


class DjangoGearmanClient(gearman.GearmanClient):
    """Gearman client, automatically connecting to server."""

    data_encoder = PickleDataEncoder

    def __call__(self, func, arg, uniq=None, **kwargs):
        raise NotImplementedError('Use do_task() or dispatch_background'
                                  '_task() instead')

    def __init__(self, **kwargs):
        """instantiate Gearman client with servers from settings file"""
        return super(DjangoGearmanClient, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

    def parse_data(self, arg, args=None, kwargs=None, *arguments, **karguments):
        data = {
            "args": [],
            "kwargs": {}
        }

        # The order is significant:
        # - First, use pythonic *args and/or **kwargs.
        # - If someone provided explicit declaration of args/kwargs, use those
        #   instead.
        if arg:
            data["args"] = [arg]
        elif arguments:
            data["args"] = arguments
        elif args:
            data["args"] = args

        data["kwargs"].update(karguments)
        # We must ensure if kwargs actually exist,
        # Otherwise 'NoneType' is not iterable is thrown
        if kwargs:
            data["kwargs"].update(kwargs)

        return data

    def submit_job(
        self, task, orig_data = None, unique=None, priority=None,
        background=False, wait_until_complete=True, max_retries=0,
        poll_timeout=None, args=None, kwargs=None, *arguments, **karguments):
        """
        Handle *args and **kwargs before passing it on to GearmanClient's
        submit_job function.
        """
        if callable(task_name_decorator):
            task = task_name_decorator(task)

        data = self.parse_data(orig_data, args, kwargs, *arguments, **karguments)

        return super(DjangoGearmanClient, self).submit_job(
            task, data, unique, priority, background, wait_until_complete,
            max_retries, poll_timeout)

    def dispatch_background_task(
        self, func, arg = None, uniq=None, high_priority=False, args=None,
        kwargs=None, *arguments, **karguments):
        """Submit a background task and return its handle."""

        priority = None
        if high_priority:
            priority = gearman.PRIORITY_HIGH

        request = self.submit_job(func, arg, unique=uniq,
            wait_until_complete=False, priority=priority, args=args,
            kwargs=kwargs, *arguments, **karguments)

        return request


class DjangoGearmanWorker(gearman.GearmanWorker):
    """
    Gearman worker, automatically connecting to server and discovering
    available jobs.
    """
    data_encoder = PickleDataEncoder

    def __init__(self, **kwargs):
        """Instantiate Gearman worker with servers from settings file."""
        return super(DjangoGearmanWorker, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

    def register_task(self, task_name, task):
        if callable(task_name_decorator):
            task_name = task_name_decorator(task_name)
        return super(DjangoGearmanWorker, self).register_task(task_name, task)
