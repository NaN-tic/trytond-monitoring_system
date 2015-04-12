# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os
import psutil
import json
import tempfile
import socket
import subprocess
from datetime import datetime
from trytond.pool import PoolMeta

__all__ = ['CheckPlan']
__metaclass__ = PoolMeta


def check_output(*args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    process.wait()
    data = process.stdout.read()
    return data


def to_float(text):
    try:
        return float(text)
    except ValueError:
        return None


PROTOCOLS = {
    socket.SOCK_STREAM: 'TCP',
    socket.SOCK_DGRAM: 'UDP',
    }


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

    def check_process_count(self):
        return [{
                'result': 'process_count',
                'float_value': len(psutil.pids()),
                }]

    def check_uptime(self):
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.now() - boot_time).total_seconds()
        return [{
                'result': 'uptime',
                'float_value': uptime,
                }]

    def check_process_cpu_percent(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = [x.strip() for x in processes.split(',')]
        res = []
        for process in psutil.process_iter():
            try:
                label = process.name()
                if processes and name not in processes:
                    continue
                cpu = process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            res.append({
                    'result': 'process_cpu_percent',
                    'label': label,
                    'float_value': cpu,
                    })
        return res

    def check_process_open_files_count(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = [x.strip() for x in processes.split(',')]
        res = []
        for process in psutil.process_iter():
            try:
                label = process.name()
                if processes and name not in processes:
                    continue
                files = process.num_fds()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            res.append({
                    'result': 'process_open_files_count',
                    'label': label,
                    'float_value': files,
                    })
        return res

    def check_process_memory_percent(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = [x.strip() for x in processes.split(',')]
        res = []
        for process in psutil.process_iter():
            try:
                label = process.name()
                if processes and name not in processes:
                    continue
                memory = process.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            res.append({
                    'result': 'process_memory_percent',
                    'label': label,
                    'float_value': memory,
                    })
        return res

    def check_process_io_counters(self):
        processes = self.get_attribute('processes')
        if processes:
            processes = [x.strip() for x in processes.split(',')]
        res = []
        for process in psutil.process_iter():
            try:
                label = process.name()
                if processes and name not in processes:
                    continue
                counters = process.io_counters()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            for name in ('read_count', 'write_count', 'read_bytes',
                    'write_bytes'):
                res.append({
                        'result': 'process_io_counter_%s' % name,
                        'label': label,
                        'float_value': getattr(counters, name),
                        })
        return res

    def check_process_open_ports(self):
        '''
        Expected structure in ports attribute:

        protocol:ip:port

        Example:

        TCP:*:22
        TCP:*:8000
        '''
        valid_entries = set()
        entries = [x.strip() for x in
            self.get_attribute('process_open_ports').split()]
        for entry in entries:
            if len(entry.split(':')) != 3:
                continue
            protocol, ip, port = entry.split(':')
            if '*' in entry:
                valid_entries.add((protocol, entry.replace('*', '0.0.0.0'),
                        port))
                valid_entries.add((protocol, entry.replace('*', '::'), port))
            else:
                valid_entries.add((protocol, ip, port))
        invalids = []
        value = 'OK'
        for process in psutil.process_iter():
            try:
                connections = process.get_connections()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            for connection in connections:
                if connection.status != 'LISTEN':
                    continue
                if connection.type not in PROTOCOLS:
                    continue
                protocol = PROTOCOLS[connection.type]
                ip = connection.laddr[0]
                port = connection.laddr[1]
                entry = (protocol, ip, port)
                if entry not in valid_entries:
                    invalids.append(entry)
                    value = 'Error'
                    continue
        return [{
                'result': 'process_open_ports_status',
                'char_value': value,
                'payload': json.dumps({
                        'invalid_ports': invalids,
                        }),
                }]

    def check_load(self):
        one, five, fifteen = os.getloadavg()
        res = []
        res.append({
                'result': 'load_1',
                'float_value': one,
                })
        res.append({
                'result': 'load_5',
                'float_value': five,
                })
        res.append({
                'result': 'load_15',
                'float_value': fifteen,
                })
        return res

    def check_raid(self):
        """
        Expected values in raid_devices:
        md0, md1
        """
        devices = self.get_attribute('raid_devices')
        if devices:
            devices = [x.strip() for x in devices.split(',')]
        lines = open('/proc/mdstat', 'r').readlines()
        current_device = None
        current_payload = ''
        res = []
        for line in lines:
            if line.startswith('md'):
                current_device = line.split()[0]
                current_payload += line
                continue
            if current_device:
                if devices and current_device not in devices:
                    current_device = None
                    current_payload = ''
                    continue
                current_payload += line
                if '[UU]' in line:
                    state = 'OK'
                else:
                    state = 'Error'
                res.append({
                        'result': 'raid_status',
                        'label': current_device,
                        'char_value': state,
                        'payload': json.dumps({
                                'output': current_payload,
                                }),
                        })
                current_device = None
                current_payload = ''
        return res

    def check_ntp_status(self):
        output = check_output('/usr/sbin/ntpdate', '-q', 'pool.ntp.org')
        line = output.splitlines()[-1]
        sec = line.split()[-1]
        text = line.split()[-2]
        offset = line.split()[-3]
        res = []
        value = 999999
        if sec == 'sec' and offset == 'offset':
            try:
                value = float(text)
            except ValueError:
                pass
        res.append({
                'result': 'ntp_offset',
                'float_value': value,
                })
        return res

    def check_apt(self):
        output = check_output('apt-get', '-s', 'upgrade')
        upgrades = 0
        packages = []
        security_upgrades = 0
        security_packages = []
        error_items = []
        for line in output.splitlines():
            if not line.startswith('Inst'):
                continue

            upgrades += 1

            items = line.split()
            if len(items) != 5:
                error_items += items
                continue

            packages.append(items[1])

            release = items[3]
            if 'security' in release.lower():
                security_upgrades += 1
                security_packages.append(items[1])

        res = []
        res.append({
                'result': 'apt_status',
                'char_value': 'Error' if errors else 'OK',
                'payload': json.dumps({
                        'items': error_items,
                        }),
                })
        res.append({
                'result': 'apt_upgrades',
                'float_value': upgrades,
                'payload': json.dumps({
                        'packages': packages,
                        }),
                })
        res.append({
                'result': 'apt_security_upgrades',
                'float_value': security_upgrades,
                'payload': json.dumps({
                        'packages': security_packages,
                        }),
                })
        return res

    def check_disk_writable(self):
        path = self.get_attribute('writable_path')
        path = path.strip()
        if not path.endswith('/'):
            path += '/'
        try:
            with tempfile.TemporaryFile(prefix=path):
                pass
        except Exception, e:
            return [{
                    'result': 'disk_writable',
                    'label': path,
                    'char_value': 'Error',
                    'payload': str(e),
                    }]
        return [{
                'result': 'disk_writable',
                'label': path,
                'char_value': 'OK',
                }]
