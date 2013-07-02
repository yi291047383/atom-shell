#!/usr/bin/env python

import argparse
import errno
import os
import subprocess
import sys

from lib.util import *


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
VENDOR_DIR = os.path.join(SOURCE_ROOT, 'vendor')
BASE_URL = 'https://gh-contractor-zcbenz.s3.amazonaws.com/libchromiumcontent'
PYTHON_26_URL = 'https://chromium.googlesource.com/chromium/deps/python_26'


def main():
  os.chdir(SOURCE_ROOT)

  args = parse_args()
  if not args.skip_network:
    update_submodules()
    update_node_modules()
    bootstrap_brightray(args.url)
    if sys.platform == 'cygwin':
      update_win32_python()

  touch_config_gypi()
  update_atom_shell()


def parse_args():
  parser = argparse.ArgumentParser(description='Bootstrap this project')
  parser.add_argument('-u', '--url',
                      help='The base URL from which to download '
                      'libchromiumcontent (i.e., the URL you passed to '
                      'libchromiumcontent\'s script/upload script',
                      default=BASE_URL,
                      required=False)
  parser.add_argument('-s', '--skip-network',
                      help='Skip operations require networking',
                      action='store_true')
  return parser.parse_args()


def update_submodules():
  subprocess.check_call(['git', 'submodule', 'sync', '--quiet'])
  subprocess.check_call(['git', 'submodule', 'update', '--init',
                         '--recursive'])


def bootstrap_brightray(url):
  bootstrap = os.path.join(VENDOR_DIR, 'brightray', 'script', 'bootstrap')
  subprocess.check_call([sys.executable, bootstrap, url])


def update_node_modules():
  subprocess.check_call(['npm', 'install', '--silent'])


def update_win32_python():
  with scoped_cwd(VENDOR_DIR):
    if not os.path.exists('python_26'):
      subprocess.check_call(['git', 'clone', PYTHON_26_URL])
    else:
      with scoped_cwd('python_26'):
        subprocess.check_call(['git', 'pull', '--rebase'])


def touch_config_gypi():
  config_gypi = os.path.join(SOURCE_ROOT, 'vendor', 'node', 'config.gypi')
  with open(config_gypi, 'w+') as f:
    f.truncate(0)


def update_atom_shell():
  update = os.path.join(SOURCE_ROOT, 'script', 'update.py')
  subprocess.check_call([sys.executable, update])


if __name__ == '__main__':
  sys.exit(main())