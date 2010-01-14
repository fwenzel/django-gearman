"""
Django Gearman Interface
"""
import gearman

from models import DjangoGearmanClient as GearmanClient
from models import DjangoGearmanWorker as GearmanWorker
from models import DjangoGearmanTask as Task
from gearman.task import Taskset

