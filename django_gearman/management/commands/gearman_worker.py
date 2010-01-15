import sys

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django_gearman import GearmanWorker


class Command(NoArgsCommand):
    help = "Start a Gearman worker serving all registered Gearman jobs"
    __doc__ = help

    def handle_noargs(self, **options):
        # find gearman modules
        gm_modules = []
        for app in settings.INSTALLED_APPS:
            try:
                gm_modules.append(__import__("%s.gearman" % app))
            except ImportError:
                pass
        if not gm_modules:
            print "No gearman modules found!"
            return

        # instantiate a new worker and register all jobs
        worker = GearmanWorker()
        for gm_module in gm_modules:
            try:
                gm_module.gearman_jobs
            except NameError:
                continue
            for job in gm_module.gearman_jobs:
                # determine right name to register function with
                app = job.app
                jobname = job.__name__
                try:
                    func = settings.GEARMAN_JOB_NAME % {'app': app,
                                                        'job': jobname}
                except NameError:
                    func = '%s.%s' % (app, jobname)
                print "Registering job '%s'" % func
                worker.register_function(func, job)

        # start working
        print "Starting to work... (press ^C to exit)"
        try:
            worker.work()
        except KeyboardInterrupt:
            sys.exit(0)

