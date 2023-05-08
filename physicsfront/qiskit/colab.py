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

import os, io

##
# PIP_PKGS_TO_INSTALL: collect all packages from _requires.py (including
#   extras; as colab needs all) into a tuple.
##
with io.open (os.path.join (os.path.split (__file__) [0], '_requires.py'),
              'r', encoding = 'utf-8') as _:
    PIP_PKGS_TO_INSTALL = {}
    exec (_.read (), PIP_PKGS_TO_INSTALL)
    PIP_PKGS_TO_INSTALL = (list (PIP_PKGS_TO_INSTALL ['dependencies']) +
        sum ((list (l) for l
              in PIP_PKGS_TO_INSTALL.get ('extras', {}).values ()), []))
    PIP_PKGS_TO_INSTALL = tuple (w.replace (' ', '')
                                for w in PIP_PKGS_TO_INSTALL)

def _check_setup_file (kind, fallback_filename = None): # <<<
    """
    Checks, or creates, a qiskit setup file of the given kind.

    If the file does not exist and if ``fallback_filename`` has been given,
    then the file is created by copying ``fallback_filename``.

    :returns:  ``(setup_filename, status)``

        ``setup_filename`` is the name of the setup file that qiskit will
        read.

        ``status`` would be false if checking or creating the setup file
        failed.

        If ``status`` is true, it will be either ``setup_filename`` (if it
        existed already) or ``fallback_filename`` (it it was copied from
        fallback).

    :param kind:  'json', 'conf', or 'rc'

        The corresponding file name is respectively  'qiskit-ibm.json',
        'settings.conf', and 'qiskitrc'.

        Consider the 'rc' kind as deprecated since the 'rc' setup file is
        read by qiskit.providers or qiskit.IBMQ, both of which are deprecated
        modules.  The new module to use is qiskit_ibm_provider, which uses
        the 'json' kind for account information.

    :param fallback_filename:  If the file does not exist and this
        filename is given, then this file will be copied to the setup file.

        The name may be subject to a correction by :func:`_correct_filename`
        (for internal technical reasons related to file system matters,
        basically).

        When this name was utilized, then the ``status`` value in the return
        tuple will be this name (possibly corrected).
    """
    import shutil
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
    if not os.path.exists (setup_dir):
        os.mkdir (setup_dir)
    if fallback_filename:
        #print (fallback_filename, '...', end = ' ')
        fallback_filename = _correct_filename (fallback_filename)
        #print (fallback_filename)
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
def _install_pip_packages (reload = False, quiet = False): # <<< # pylint: disable=W0613
    import subprocess, sys
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
    raise SystemError ("pip returned error %d" % (rv,))
# >>>
def _setup_account (reload = False, instance = None, quiet = False, # <<<
                    filename = None):
    """
    :param filename:  Used as ``fallback_filename`` when checking the account
        setup file.
    """
    ##
    # The method that involves
    # qiskit.IBMQ.{active_account,disable_account,load_account} has been
    # deprecated.  As of 2023-05-07, it has been noted that the jobs executed
    # in the last couple of days do not show up, if the job query is made
    # from the deprecated provider.  They do show up if the job query is made
    # from a provider of new type, which is recommended for use.  So, it is
    # time to move on to the new style.
    ##
    if not quiet:
        print ("== Account setup (you might be prompted for an API TOKEN) ...",
               end = ' ', flush = True)
    from . import get_provider
    provider = get_provider (provider = 'cached', instance = instance)
    if provider and not reload:
        if not quiet:
            print ("OK! (account already active; reload not requested)\n"
                "   Restart runtime if you wish to restart everything anew.")
        return
    _, rv = _check_setup_file ('json', fallback_filename = filename)
    if rv:
        provider = get_provider (provider = 'renew' if reload else None,
                                 instance = instance)
    else:
        old_token = '' # d ['token'] if d else ''
        import IPython # pylint: disable=E0401
        display = IPython.display.display
        from google.colab import output # pylint: disable=E0401,E0611
        display (IPython.display.Javascript (f'window._key = "{old_token}"'))
        display (IPython.display.Javascript ('''
window._key = prompt ("Please enter your IBM Quantum API TOKEN:", window._key)
        '''))
        token = output.eval_js ('_key')
        # for safety; even if javascript is sandboxed per cell
        output.eval_js ('delete window._key')
        provider = get_provider (token = token, instance = instance)
    if not provider:
        raise Exception ("Failed to set up an IBM Quantum provider.") # pylint: disable=W0719
    if not rv:
        dargs = provider.active_account ()
        dargs.pop ('channel', None)
        provider.save_account (** dargs)
    if not quiet:
        print ("OK!")
# >>>
def _setup_settings (reload = False, quiet = False, filename = None): # <<<
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

def init (reload = False, quiet = False, json_filename = None,
          conf_filename = None):
    _install_pip_packages (reload = reload, quiet = quiet)
    _setup_settings (reload = reload, quiet = quiet,
                     filename = conf_filename)
    _setup_account (reload = reload, quiet = quiet,
                    filename = json_filename)
    from . import patch as _
