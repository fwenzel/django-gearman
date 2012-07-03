def gearman_job(queue='default'):
    """
    Decorator turning a function inside some_app/gearman_jobs.py into a
    Gearman job.
    """

    class gearman_job_cls(object):

        def __init__(self, f):
            self.f = f
            self.__name__ = f.__name__
            self.queue = queue

            # Determine app name.
            parts = f.__module__.split('.')
            if len(parts) > 1:
                self.app = parts[-2]
            else:
                self.app = ''

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
