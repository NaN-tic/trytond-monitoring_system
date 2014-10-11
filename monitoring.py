# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
import psutil

__all__ = ['CheckPlan']
__metaclass__ = PoolMeta


class CheckPlan:
    __name__ = 'monitoring.check.plan'

    def check_cpu_times_percent(self):
        usage = psutil.cpu_times_percent(interval=1)
        res = []
        for name in ('user', 'nice', 'system', 'idle', 'iowait', 'irq',
                'softirq', 'steal', 'guest', 'nice'):
            res.append({
                    'result': 'cpu_percent_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_cpu_percent(self):
        usage = psutil.cpu_percent(interval=1)
        return {
            'result': 'cpu_percent',
            'float_value': usage,
            }

    def check_disk(self):
        path = self.asset.get_attribute('path')
        usage = psutil.disk_usage(path)
        res = []
        for name in ('total', 'used', 'free', 'percent'):
            res.append({
                    'result': 'disk_usage_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_disk_io_counters(self):
        usage = psutil.disk_io_counters(perdisk=False)
        res = []
        for name in ('read_count', 'write_count', 'read_bytes', 'write_bytes',
                'read_time', 'write_time'):
            res.append({
                    'result': 'disk_io_counter_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_swap(self):
        usage = psutil.swap_memory()
        res = []
        for name in ('total', 'used', 'free', 'percent', 'sin', 'sout'):
            res.append({
                    'result': 'swap_usage_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_physical_memory(self):
        usage = psutil.phymem_usage()
        res = []
        for name in ('total', 'available', 'percent', 'used', 'free', 'active',
                'inactive', 'buffers', 'cached'):
            res.append({
                    'result': 'physical_memory_usage_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_net_io_counters(self):
        interface = self.asset.get_attribute('interface')
        pernic = bool(interface)
        usage = psutil.net_io_counters(pernic=pernic)
        if interface:
            usage = usage[interface]
        res = []
        for name in ('bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
                'errin', 'errout', 'dropin', 'dropout'):
            res.append({
                    'result': 'net_io_counter_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res
