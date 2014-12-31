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
        for name in ('guest', 'idle', 'iowait', 'irq', 'nice', 'softirq',
                'steal', 'system', 'user'):
            res.append({
                    'result': 'cpu_percent_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_cpu_percent(self):
        usage = psutil.cpu_percent(interval=1)
        return [{
                'result': 'cpu_percent',
                'float_value': usage,
                }]

    def check_disk(self):
        path = self.get_attribute('path')
        usage = psutil.disk_usage(path)
        res = []
        for name in ('free', 'percent', 'total', 'used'):
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
        for name in ('free', 'percent', 'sin', 'sout', 'total', 'used'):
            res.append({
                    'result': 'swap_usage_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_physical_memory(self):
        usage = psutil.virtual_memory()
        res = []
        for name in ('active', 'available', 'buffers', 'cached', 'free',
                'inactive', 'percent', 'total', 'used'):
            res.append({
                    'result': 'physical_memory_usage_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_net_io_counters(self):
        interface = self.get_attribute('interface')
        pernic = bool(interface)
        usage = psutil.net_io_counters(pernic=pernic)
        if interface:
            usage = usage[interface]
        res = []
        for name in ('bytes_recv', 'bytes_sent', 'dropin', 'dropout', 'errin',
                'errout', 'packets_recv', 'packets_sent'):
            res.append({
                    'result': 'net_io_counter_%s' % name,
                    'float_value': getattr(usage, name),
                    })
        return res

    def check_process_cpu_percent(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = processes.split(',')
        res = []
        for process in psutil.process_iter():
            try:
                name = process.name()
                if processes and name not in processes:
                    continue
                cpu = process.cpu_percent()
            except psutil.NoSuchProcess:
                continue
            res.append({
                    'result': 'process_cpu_percent',
                    'label': name,
                    'float_value': cpu,
                    })
        return res

    def check_process_open_files_count(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = processes.split(',')
        res = []
        for process in psutil.process_iter():
            try:
                name = process.name()
                if processes and name not in processes:
                    continue
                files = process.num_fds()
            except psutil.NoSuchProcess:
                continue
            res.append({
                    'result': 'process_open_files_count',
                    'label': name,
                    'float_value': files,
                    })
        return res

    def check_process_memory_percent(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = processes.split(',')
        res = []
        for process in psutil.process_iter():
            try:
                name = process.name()
                if processes and name not in processes:
                    continue
                memory = process.memory_percent()
            except psutil.NoSuchProcess:
                continue
            res.append({
                    'result': 'process_memory_percent',
                    'label': name,
                    'float_value': memory,
                    })
        return res

    def check_process_io_counters(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = processes.split(',')
        res = []
        for process in psutil.process_iter():
            try:
                label = process.name()
                if processes and name not in processes:
                    continue
                counters = process.io_counters()
            except psutil.NoSuchProcess:
                continue
            for name in ('read_count', 'write_count', 'read_bytes',
                    'write_bytes'):
                res.append({
                        'result': 'process_io_counter_%s' % name,
                        'label': label,
                        'float_value': getattr(counters, name),
                        })
        return res
