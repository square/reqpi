from __future__ import print_function

import contextlib
import os
import requests
import subprocess
import sys
import time

REQPI_MAIN_OK = True

REQUIREMENTS = """\
CleverCSS==0.1
docutils==0.12
Logbook==0.12.3
progressbar==2.3
py==1.4.31
swsg==0.3.0
texttable==0.8.4
wheel==0.24.0
"""


@contextlib.contextmanager
def server(tmp, *args):
    log = os.path.join(tmp, 'twistd.log')
    cmd = ['python', '-m', 'reqpi', 'server'] + map(str, args)
    with open(log, 'a') as stdout:
        p = subprocess.Popen(cmd, stdout=stdout)
        for i in range(30):
            try:
                requests.get('http://localhost:2000/')
            except Exception:
                print("Could not connect, retrying: "
                      "attempt {} of 30".format(i))
                time.sleep(1)
        try:
            yield
        finally:
            p.terminate()


def main(args):
    tmp = args[1]
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    requirementsTxt = os.path.join(tmp, 'requirements.txt')
    with open(requirementsTxt, 'w') as fp:
        fp.write(REQUIREMENTS)
    print("Wrote", requirementsTxt)
    with server(tmp, '--http', 2000,
                     '--url', 'http://localhost:2000'):
        # TODO(moshez): Currently disable human approval
        # requests.post('http://localhost:2000/human/grab',
        #               data=json.dumps(dict(requirements=REQUIREMENTS)))
        hash = subprocess.check_output(['python', '-m', 'reqpi', 'gethash',
                                        '--url', 'http://localhost:2000/',
                                        requirementsTxt])
        env = os.path.join(tmp, 'venv')
        subprocess.check_output(['virtualenv', env])
        envpip = os.path.join(env, 'bin', 'pip')
        subprocess.check_call([envpip, 'install', '--no-cache',
                               '--index-url', hash.strip(),
                               '--requirement', requirementsTxt])
        envcmd = os.path.join(env, 'bin', 'swsg-cli')
        p = subprocess.Popen([envcmd, '--version'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stderr.strip() != 'swsg-cli 0.3.0':
            sys.exit('Unexpected output %r' % stderr)
