# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .monitoring import *

def register():
    Pool.register(
        CheckPlan,
        module='monitoring_system', type_='model')
