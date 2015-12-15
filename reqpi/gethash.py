"""
hash command for the reqpi command-line

Input: path to a requirements.txt file
Output: the URL endpoint of a package server which includes the packages
        listed in requirements.txt
"""
from __future__ import print_function
import os
import requests
import json
import argparse

DEFAULT_SERVER = 'http://localhost:2000'

REQPI_MAIN_OK = True

PARSER = argparse.ArgumentParser()
PARSER.add_argument('requirements', type=str,
                    help="path to requirements.txt file listing package "
                         "versions to be served")
PARSER.add_argument('-u', '--url', default=DEFAULT_SERVER,
                    help="Base URL for reqpi server")


def main(clargs, session=requests.Session):
    args = PARSER.parse_args(clargs[1:])
    session = session()
    message = get_server_url(session, args.url, args.requirements)
    print(message)


def get_server_url(session, server, reqfile_path):
    '''
    Get the URL for a server of the packages in the given requirements.txt
    '''
    requirements = get_requirements(reqfile_path)
    sha = get_package_server_url(session, server, requirements)
    return sha


def get_requirements(reqs_path):
    with open(reqs_path, 'r') as rf:
        return rf.read()


def get_package_server_url(session, server, requirements):
    '''
    POST requirements to server and expect a 200 ok
    as well as a JSON response with a 'url' key.
    Returns the url of the server, or None if no server exists.
    '''
    post_url = os.path.join(server, 'robot', 'hash')
    r = session.post(post_url,
                     data=json.dumps(dict(requirements=requirements)))
    if r.status_code != 200:
        raise ValueError("Got bad HTTP status, expecting 200 OK",
                         r.status_code, post_url)
    else:
        return json.loads(r.text)['url']
