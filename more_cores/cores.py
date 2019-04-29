import os
import sys

from paramiko import SSHClient


class Job:
    def __init__(self, cores):
        self.cores = cores


class Cores:

    def __init__(self, server_dict, requirements):
        self.server_dict = server_dict
        self.requirements = requirements
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(
            self.server_dict['host'],
            username=self.server_dict['username'],
            password=self.server_dict['password'],
            pkey=self.server_dict['pkey']
        )
        print('Connected to', self.server_dict['host'])
        sftp = ssh.open_sftp()
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        sftp.put(scripts_dir + '/setup_pyenv', 'setup_pyenv')
        print('Setting up python... this may take a few minutes')
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('bash setup_pyenv 3.7.3 requirements.txt')
        for line in ssh_stdout.readlines():
            print(line)
        for line in ssh_stderr.readlines():
            print(line)


def make_server_dict(host, user, password=None, pkey=None):
    return {'host': host, 'username': user, 'password': password, 'pkey': pkey}


def make_requirements(dependencies=None):
    python_version = '.'.join(str(v_i) for v_i in sys.version_info[:3])
    if dependencies is None:
        dependencies = []
    return {'python': python_version, 'requirements': dependencies}
