import os
import sys

import paramiko


SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts') + '/'
CORES_DIR = '.more_cores/'

SETUP_SCRIPT = 'setup_pyenv'
RUN_SCRIPT = 'run_job'
RUN_SCRIPT_PY = 'run_job.py'
REQUIREMENTS = 'mc_requirements.txt'


class Job:
    def __init__(self, cores):
        self.cores = cores


class Cores:

    def __init__(self, server_dicts, requirements, quiet=False):
        if not quiet:
            print('Initializing environment... this may take a few minutes')
        self.server_dicts = server_dicts
        self.requirements = requirements
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.sftp = None
        self.active_server = None
        initialized_dfs = set()
        for i, sd in enumerate(server_dicts):
            dfs = sd['dfs']
            if dfs is not None and dfs in initialized_dfs:
                continue
            if dfs is not None:
                initialized_dfs.add(dfs)
            with open(SCRIPTS_DIR + REQUIREMENTS, 'w') as fp:
                fp.write('\n'.join(requirements['requirements']))
            self.connect(i)
            self.send_file(SCRIPTS_DIR + SETUP_SCRIPT, SETUP_SCRIPT, temp_dir=False)
            self.send_file(SCRIPTS_DIR + REQUIREMENTS, REQUIREMENTS, temp_dir=False)
            cmd_str = 'bash {} {} {}'.format(
                SETUP_SCRIPT, requirements['python'], REQUIREMENTS
            )
            ssh_stdin, ssh_stdout, ssh_stderr = self.send_command(cmd_str, temp_dir=False)
            if not quiet:
                for line in ssh_stdout.readlines():
                    print(line)
                for line in ssh_stderr.readlines():
                    print(line)
            self.sftp.remove(SETUP_SCRIPT)
            self.sftp.remove(REQUIREMENTS)
            self.send_file(SCRIPTS_DIR + RUN_SCRIPT, CORES_DIR + RUN_SCRIPT, temp_dir=False)
            self.send_file(SCRIPTS_DIR + RUN_SCRIPT_PY, CORES_DIR + RUN_SCRIPT_PY, temp_dir=False)
            self.disconnect()
        if not quiet:
            print('Initialization complete!')

    def send_file(self, src, dst, temp_dir=True):
        if temp_dir:
            dst = CORES_DIR + dst
        self.sftp.put(src, dst)

    def get_file(self, src, dst, temp_dir=True):
        if temp_dir:
            src = CORES_DIR + src
        self.sftp.get(src, dst)

    def send_command(self, cmd, temp_dir=True):
        if temp_dir:
            cmd = 'cd {}; {}'.format(CORES_DIR, cmd)
        return self.ssh.exec_command(cmd)

    def is_job_complete(self):
        try:
            self.sftp.lstat('{}indicator_{}'.format(CORES_DIR, self.active_server))
        except FileNotFoundError:
            return False
        return True

    def connect(self, server_index):
        # TODO: keep all computation and scripts in the temp folder, and
        #       clean up files properly
        self.active_server = server_index
        server_dict = self.server_dicts[server_index]
        self.ssh.connect(
            server_dict['host'],
            username=server_dict['username'],
            password=server_dict['password'],
            pkey=server_dict['pkey']
        )
        self.sftp = self.ssh.open_sftp()

    def disconnect(self):
        self.ssh.close()
        self.sftp.close()


def make_server_dict(host, user, password=None, pkey=None, cores=4, dfs=0):
    return {
        'host': host,
        'username': user,
        'password': password,
        'pkey': pkey,
        'cores': cores,
        'dfs': dfs
    }


def make_requirements(dependencies=None):
    python_version = '.'.join(str(v_i) for v_i in sys.version_info[:3])
    if dependencies is None:
        dependencies = []
    return {'python': python_version, 'requirements': dependencies}
