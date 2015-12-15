import subprocess
import sys

import yaml

REQPI_MAIN_OK = True


def main(args):
    with open('.travis.yml') as fp:
        travis = yaml.load(fp)
    travis_envs = set(x.split('=')[1] for x in travis['env'])
    tox_envs = set(subprocess.check_output(['tox', '--listenvs']).splitlines())
    print tox_envs, travis_envs
    if tox_envs != travis_envs:
        sys.exit("Travis/Tox mismatch: {} != {}".format(tox_envs, travis_envs))
