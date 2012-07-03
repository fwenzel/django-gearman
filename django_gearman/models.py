from django.conf import settings
import gearman
import pickle


class PickleDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return pickle.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return pickle.loads(decodable_string)


class DjangoGearmanClient(gearman.GearmanClient):
    data_encoder = PickleDataEncoder
    """gearman client, automatically connecting to server"""

    def __call__(self, func, arg, uniq=None, **kwargs):
        raise NotImplementedError('Use do_task() or dispatch_background'\
                                  '_task() instead')

    def __init__(self, **kwargs):
        """instantiate Gearman client with servers from settings file"""
        return super(DjangoGearmanClient, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

    def dispatch_background_task(self, func, arg, uniq=None, high_priority=False):
        """
            Submit a background task and return its handle.
        """
        
        priority = None
        if high_priority:
            priority = gearman.PRIORITY_HIGH
        request = self.submit_job(func, arg, unique=uniq, wait_until_complete=False, priority=priority)
        return request

class DjangoGearmanWorker(gearman.GearmanWorker):
    """
    gearman worker, automatically connecting to server and discovering
    available jobs
    """
    data_encoder = PickleDataEncoder
    
    def __init__(self, **kwargs):
        """instantiate Gearman worker with servers from settings file"""
        return super(DjangoGearmanWorker, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)