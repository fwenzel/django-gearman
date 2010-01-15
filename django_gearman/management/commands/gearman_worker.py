from optparse import make_option
import os
import sys

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django_gearman import GearmanWorker


class Command(NoArgsCommand):
    help = "Start a Gearman worker serving all registered Gearman jobs"
    __doc__ = help
    option_list = NoArgsCommand.option_list + (
        make_option('-w', '--workers', action='store', dest='worker_count',
                    default='1', help='Number of workers to spawn.'),
    )
    children = [] # list of worker processes

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

        # find all jobs
        jobs = []
        for gm_module in gm_modules:
            try:
                gm_module.gearman_jobs
            except AttributeError:
                continue
            jobs += gm_module.gearman_jobs
        if not jobs:
            print "No gearman jobs found!"
            return
        print "Available jobs:"
        for job in jobs:
            # determine right name to register function with
            app = job.app
            jobname = job.__name__
            try:
                func = settings.GEARMAN_JOB_NAME % {'app': app,
                                                    'job': jobname}
            except NameError:
                func = '%s.%s' % (app, jobname)
            job.register_as = func
            print "* %s" % func

        # spawn all workers and register all jobs
        try:
            worker_count = int(options['worker_count'])
            assert(worker_count > 0)
        except (ValueError, AssertionError):
            worker_count = 1
        self.spawn_workers(worker_count, jobs)

        # start working
        print "Starting to work... (press ^C to exit)"
        try:
            for child in self.children:
                os.waitpid(child, 0)
        except KeyboardInterrupt:
            sys.exit(0)

    def spawn_workers(self, worker_count, jobs):
        """
        Spawn as many workers as desired (at least 1).
        Accepts:
        - worker_count, positive int
        - jobs: list of gearman jobs
        """
        # no need for forking if there's only one worker
        if worker_count == 1:
            return self.work(jobs)

        print "Spawning %s worker(s)" % worker_count
        # spawn children and make them work (hello, 19th century!)
        for i in range(worker_count):
            child = os.fork()
            if child:
                self.children.append(child)
                continue
            else:
                self.work(jobs)
                break

    def work(self, jobs):
        """children only: register all jobs, start working"""
        worker = GearmanWorker()
        for job in jobs:
            worker.register_function(job.register_as, job)
        try:
            worker.work()
        except KeyboardInterrupt:
            sys.exit(0)

