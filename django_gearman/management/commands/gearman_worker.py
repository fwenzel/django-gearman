from optparse import make_option
import os
import sys

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django_gearman import GearmanWorker


class Command(NoArgsCommand):
    ALL_QUEUES = '*'
    help = "Start a Gearman worker serving all registered Gearman jobs"
    __doc__ = help
    option_list = NoArgsCommand.option_list + (
        make_option('-w', '--workers', action='store', dest='worker_count',
                    default='1', help='Number of workers to spawn.'),
        make_option('-q', '--queue', action='store', dest='queue',
                    default=ALL_QUEUES, help='Queue to register tasks from'),
    )

    children = [] # List of worker processes

    @staticmethod
    def get_gearman_enabled_modules():
        gm_modules = []
        for app in settings.INSTALLED_APPS:
            try:
                gm_modules.append(__import__("%s.gearman_jobs" % app))
            except ImportError:
                pass
        if not gm_modules:
            return None
        return gm_modules


    def handle_noargs(self, **options):
        queue = options["queue"]
        # find gearman modules
        gm_modules = Command.get_gearman_enabled_modules()
        if not gm_modules:
            self.stderr.write("No gearman modules found!\n")
            return
        # find all jobs
        jobs = []
        for gm_module in gm_modules:
            try:
                gm_module.gearman_job_list
            except AttributeError:
                continue
            if queue == Command.ALL_QUEUES:
                for _jobs in gm_module.gearman_job_list.itervalues():
                    jobs += _jobs
            else:
                jobs += gm_module.gearman_job_list.get(queue, [])
        if not jobs:
            self.stderr.write("No gearman jobs found!\n")
            return
        self.stdout.write("Available jobs:\n")
        for job in jobs:
            # determine right name to register function with
            self.stdout.write("* %s\n" % job.__name__)

        # spawn all workers and register all jobs
        try:
            worker_count = int(options['worker_count'])
            assert(worker_count > 0)
        except (ValueError, AssertionError):
            worker_count = 1
        self.spawn_workers(worker_count, jobs)

        # start working
        self.stdout.write("Starting to work... (press ^C to exit)\n")
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

        self.stdout.write("Spawning %s worker(s)\n" % worker_count)
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
        """Children only: register all jobs, start working."""
        worker = GearmanWorker()
        for job in jobs:
            worker.register_task(job.__name__, job)
        try:
            worker.work()
        except KeyboardInterrupt:
            sys.exit(0)

