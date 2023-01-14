##
# Copyright 2023 Physics Front LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

def _install_pip_packages (reload = False, quiet = False):
    import subprocess, sys
    if 'qiskit' in sys.modules and not reload:
        raise Exception ("The initializtion function is called with the "
                         "qiskit module already imported, while reload "
                         "is false.")
    pkgs = ["qiskit", "pylatexenc"]
    if not quiet:
        print ("== Installing/chekcing required pip packages:", pkgs,
               '...', end = '', flush = True)
    r = subprocess.run ([sys.executable, "-m", "pip", "install"] + pkgs, # pylint: disable=W1510
                        capture_output = True)
    rv = r.returncode
    if not rv:
        if not quiet:
            print ("OK!")
        return
    if not quiet:
        print ("\r", end = '')
    print ("** Error while installing required pip packages:", pkgs)
    print (r.stderr.decode ('utf-8'))
    raise Exception ("pip returned error %d" % (rv,))

def _setup_account (reload = False, quiet = False):
    from qiskit import IBMQ
    if not quiet:
        print ("== Account setup (you may be prompted for an API TOKEN) ...")
    d = IBMQ.active_account ()
    old_token = ''
    if d:
        if reload:
            old_token = d ['token'] if d else ''
            IBMQ.disable_account ()
        else:
            raise Exception ("The initializtion fucntion is called with an "
                             "active IBMQ account, while reload is false.")
    import IPython
    from IPython.core.display import display # pylint: disable=E0611
    from google.colab import output # pylint: disable=E0401,E0611
    display (IPython.display.Javascript (f'window._key = "{old_token}"'))
    display (IPython.display.Javascript ('''
        window._key = prompt ("Please enter your IBMQ API TOKEN:", window._key)
    '''))
    token = output.eval_js ('_key')
    # for safety; even if javascript is sandboxed per cell
    output.eval_js ('delete window._key')
    IBMQ.enable_account (token)
    if not IBMQ.active_account ():
        raise Exception ("Failed to set up an IBMQ account.")
    if not quiet:
        print ("== Account setup ... OK!")

def _setup_settings (reload = False, quiet = False):
    import os.path
    settings_dir = os.path.join (os.path.expandvars ('$HOME'), '.qiskit')
    if not os.path.exists (settings_dir):
        os.mkdir (settings_dir)
    settings_file = os.path.join (settings_dir, 'settings.conf')
    if os.path.exists (settings_file):
        if not quiet:
            print ("== qiskit settings.conf exists---no action done to it")
        if reload:
            print ("== qiskit settings.conf: reload action unimplemented yet")
        return
    import io
    with io.open (settings_file, 'w', encoding = 'utf-8') as f:
        f.write ('''[default]
circuit_drawer = mpl
''')
    if not quiet:
        print ("== qiskit settings.conf was created with default content.")

def init (reload = False, quiet = False):
    _install_pip_packages (reload = reload, quiet = quiet)
    _setup_account (reload = reload, quiet = quiet)
    _setup_settings (reload = reload, quiet = quiet)
