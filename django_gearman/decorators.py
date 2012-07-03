def gearman_job(queue='default', name=None):
    """
    Decorator turning a function inside some_app/gearman_jobs.py into a
    Gearman job.
    """

    class gearman_job_cls(object):

        def __init__(self, f):
            self.f = f
            # set the custom task name
            self.__name__ = name
            # if it's null, set the import name as the task name
            # this also saves one line (no else clause) :)
            if not name:
                self.__name__ = '.'.join((f.__module__, f.__name__)) \
                                    .replace('gearman_jobs.', '')
            self.queue = queue

            # Store function in per-app job list (to be picked up by a
            # worker).
            gm_module = __import__(f.__module__)
            try:
                gm_module.gearman_job_list[queue].append(self)
            except KeyError:
                gm_module.gearman_job_list[queue] = [self]
            except AttributeError:
                gm_module.gearman_job_list = {self.queue: [self]}

        def __call__(self, worker, job, *args, **kwargs):
            # Call function with argument passed by the client only.
            try:
                arg = job.data
            except IndexError:
                arg = None
            return self.f(arg)

    return gearman_job_cls
