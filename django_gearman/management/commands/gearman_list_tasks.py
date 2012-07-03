from django.core.management.base import NoArgsCommand
from gearman_worker import Command as Worker

class Command(NoArgsCommand):
    help = "List all available gearman jobs with queues they belong to"
    __doc__ = help

    def handle_noargs(self, **options):
        gm_modules = Worker.get_gearman_enabled_modules()
        if not gm_modules:
            self.stderr.write("No gearman modules found!\n")
            return

        for gm_module in gm_modules:
            try:
                gm_module.gearman_job_list
            except AttributeError:
                continue
            for queue, jobs in gm_module.gearman_job_list.items():
                self.stdout.write("Queue: %s\n" % queue)
                for job in jobs:
                    self.stdout.write("* %s\n" % job.__name__)
