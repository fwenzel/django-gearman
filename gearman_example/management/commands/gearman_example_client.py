from django.core.management.base import NoArgsCommand
from django_gearman import GearmanClient, Task


class Command(NoArgsCommand):
    help = "Execute an example command with the django_gearman interface"
    __doc__ = help

    def handle_noargs(self, **options):
        sentence = "The quick brown fox jumps over the lazy dog."

        print "Reversing example sentence: '%s'" % sentence
        # call "reverse" job defined in gearman_example app (i.e., this app)
        client = GearmanClient()
        res = client.do_task(Task("gearman_example.reverse", sentence))

        print "Result: '%s'" % res

