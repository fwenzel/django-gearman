from gearman import GearmanClient, GearmanWorker, Task

import settings


class DjangoGearmanClient(GearmanClient):
    """gearman client, automatically connecting to server"""

    def __init__(self, **kwargs):
        """instanciate Gearman client with servers from settings file"""
        return super(DjangoGearmanClient, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

class DjangoGearmanWorker(GearmanWorker):
    """
    gearman worker, automatically connecting to server and discovering
    available jobs
    """

    def __init__(self, **kwargs):
        """instanciate Gearman worker with servers from settings file"""
        return super(DjangoGearmanWorker, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

class DjangoGearmanTask(Task):
    """Gearman Task, namespacing jobs according to config file"""

    def __init__(self, func, arg, **kwargs):
        # get app and job name from function call, namespace as configured,
        # then execute
        parts = func.partition('.')
        if parts[2]:
            app = parts[0]
            job = parts[2]
        else:
            app = ''
            job = parts[0]

        try:
            func = settings.GEARMAN_JOB_NAME % {'app': app, 'job': job}
        except NameError:
            pass

        return super(DjangoGearmanTask, self).__init__(func, args, **kwargs)

