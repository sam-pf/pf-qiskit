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

PIP_PKGS_TO_INSTALL = ('qiskit', 'qiskit_ibm_provider', 'matplotlib', 'pylatexenc')

def _check_setup_file (kind, fallback_filename = None): # <<<
    """
    Checks the qiskitrc or settings file and returns that file name.

    :returns:  ``(setup_filename, status)``

        ``setup_filename`` is the setup file name that will be read by
        qiskit.

        ``status`` is false if ``setup_filename`` does not exist.

        If ``status`` is true, it will be either ``setup_filename`` or
        ``fallback_filename``.

    :param kind:  'rc', 'conf', or 'json'

        The corresponding file names are respectively 'qiskitrc',
        'settings.conf', and 'qiskit-ibm.json'.

    :param fallback_filename:  If the file does not exist and this
        filename is given, then this file will be copied to the setup file,
        before fallback_filename is returned.

        If this name is given, then it will be replaced by the value returned
        by :func:`_correct_filename`.
    """
    import os.path, shutil
    setup_dir = os.path.join (os.path.expandvars ('$HOME'), '.qiskit')
    if kind == 'rc':
        filename = 'qiskitrc'
    elif kind == 'conf':
        filename = 'settings.conf'
    else:
        assert kind == 'json'
        filename = 'qiskit-ibm.json'
    setup_file = os.path.join (setup_dir, filename)
    if os.path.exists (setup_file):
        return (setup_file, setup_file)
    if fallback_filename:
        #print (fallback_filename, '...', end = ' ')
        fallback_filename = _correct_filename (fallback_filename)
        #print (fallback_filename)
        if not os.path.exists (setup_dir):
            os.mkdir (setup_dir)
        if shutil.copy2 (fallback_filename, setup_file):
            return (setup_file, fallback_filename)
    return (setup_file, False)
# >>>
def _correct_filename (filename): # <<<
    """
    Corrects ``filename`` in an edge case of a Google Drive access within
    Colab.

    The edge case is the following.

    #. The file (which is not a folder) has no extension in its name.

    #. Google Drive displays no extension.

    #. In Colab, when Google Drive is mounted, the file appears with a random
       extension (such as '.9f4Hb8').

    In order to deal with this edge case (which has been observed with a file
    copied from Ubuntu using googledrive-ocaml-fuse), this function will
    return a new filename if the following conditions apply.

    #. There is no file (or folder) with ``filename``.

    #. There is no extension in ``filename``.

    #. There is one unique file found with its name = ``filename`` +
       extension (which cannot have another '.').
    """
    import os.path
    if os.path.exists (filename):
        return filename
    dname, fname = os.path.split (filename)
    if '.' in fname:
        return filename
    cands = list (name for name in os.listdir (dname)
                  if name.split ('.') [0] == fname)
    if len (cands) != 1 or len (cands [0].split ('.')) != 2:
        return filename
    return os.path.join (dname, cands [0])
# >>>
def _install_pip_packages (reload = False, quiet = False): # <<<
    import subprocess, sys
    if 'qiskit' in sys.modules and not reload:
        if not quiet:
            print ("== Installing/checking needed pip packages: aborted since "
                   "qiskit has already been imported and reload was not "
                   "requested.\n"
                   "   Restart runtime if you wish to restart everything anew.")
        return
    pkgs = list (PIP_PKGS_TO_INSTALL)
    if not quiet:
        print ("== Installing/checking needed pip packages:", pkgs,
               '...', end = ' ', flush = True)
    r = subprocess.run ([sys.executable, "-m", "pip", "install"] + pkgs, # pylint: disable=W1510
                        capture_output = True)
    rv = r.returncode
    if not rv:
        if not quiet: print ("OK!")
        return
    if not quiet:
        print ("\r", end = '')
    print ("** Error while installing required pip packages:", pkgs)
    print (r.stderr.decode ('utf-8'))
    raise Exception ("pip returned error %d" % (rv,))
# >>>
def _setup_account (reload = False, quiet = False, filename = None): # <<<
    from qiskit import IBMQ # pylint: disable=E0611
    if not quiet:
        print ("== Account setup (you might be prompted for an API TOKEN) ...",
               end = ' ', flush = True)
    d = IBMQ.active_account ()
    if d and not reload:
        if not quiet:
            print ("OK! (account already active; reload not requested)\n"
                   "   Restart runtime if you wish to restart everything anew.")
        return
    _, rv = _check_setup_file ('rc', fallback_filename = filename)
    if reload: IBMQ.disable_account ()
    if rv:
        IBMQ.load_account ()
    else:
        old_token = d ['token'] if d else ''
        import IPython
        display = IPython.display.display
        from google.colab import output # pylint: disable=E0401,E0611
        display (IPython.display.Javascript (f'window._key = "{old_token}"'))
        display (IPython.display.Javascript ('''
window._key = prompt ("Please enter your IBMQ API TOKEN:", window._key)
        '''))
        token = output.eval_js ('_key')
        # for safety; even if javascript is sandboxed per cell
        output.eval_js ('delete window._key')
        IBMQ.enable_account (token)
    d = IBMQ.active_account ()
    if not d:
        raise Exception ("Failed to set up an IBMQ account.")
    jsonfilename, rv = _check_setup_file ('json')
    if not rv:
        jsonobj = {
            'default-ibm-quantum': {
                'channel': 'ibm_quantum',
                'token': d ['token'],
                'url': d.get ('url',
                              'https://auth.quantum-computing.ibm.com/api'),
            },
        }
        import json
        json.dump (jsonobj, open (jsonfilename, 'w', encoding = 'utf-8'))
    if not quiet:
        print ("OK!")
# >>>
def _setup_settings (reload = False, quiet = False, filename = None): # <<<
    import io
    if not quiet:
        print ("== Qiskit settings file check ...", end = ' ', flush = True)
    setupfname, rv = _check_setup_file ('conf', fallback_filename = filename)
    msg = ''
    if rv:
        if rv == setupfname:
            msg = 'file exists'
            if reload:
                msg += '; reload request received but reload unimplemented'
        else:
            msg = 'file was copied'
    else:
        with io.open (setupfname, 'w', encoding = 'utf-8') as f:
            f.write ('''[default]
circuit_drawer = mpl
''')
        msg = 'created with default content'
    assert msg
    if not quiet:
        print ("OK! (" + msg + ")")
# >>>

def init (reload = False, quiet = False, qiskitrc_filename = None,
          settings_filename = None):
    _install_pip_packages (reload = reload, quiet = quiet)
    _setup_settings (reload = reload, quiet = quiet,
                     filename = settings_filename)
    _setup_account (reload = reload, quiet = quiet,
                    filename = qiskitrc_filename)
    from . import patch as _
