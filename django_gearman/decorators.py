class gearman_job(object):
    """
    Decorator marking a function inside some_app/gearman.py as a gearman job
    """

    def __init__(self, f):
        self.f = f
        self.__name__ = f.__name__
        
        # determine app name
        parts = f.__module__.rpartition('.')
        if parts[2]:
            self.app = parts[0]
        else:
            self.app = ''

        # store function in per-app job list (to be picked up by a worker)
        gm_module = __import__(f.__module__)
        try:
            gm_module.gearman_jobs.append(self)
        except AttributeError:
            gm_module.gearman_jobs = [self]

    def __call__(self, *args, **kwargs):
        # call function with argument passed by the client only
        try:
            arg = args[0].arg
        except IndexError:
            arg = None
        return self.f(arg)

