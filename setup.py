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

name = "physicsfront-qiskit"
author = "Physics Front LLC"
author_email = "info@physicsfront.com"
url = "https://github.com/sam-pf/pf-qiskit"
project_urls = {
    'GitHub': url,
    # potential useful keys: 'Documentation', 'ChangeLog', 'Issues', ...
}
version = "0.1.6.2"
license_ = "Apache 2.0"
description = "Utility package for qiskit"
long_description = "This package provides modules such as physicsfront.qiskit and physicsfront.qiskit.colab.  These modules can be used to aid the usage of qiskit in various environments, e.g., in the Google Colab environment."

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = 'Development Status :: 3 - Alpha'

import io, os, setuptools, sys

# dependencies, extras, python_requires
exec (io.open (os.path.join (os.path.split (__file__)[0],
                             'physicsfront', 'qiskit', '_requires.py'),
               mode = 'r', encoding = 'utf-8').read (),
      globals ())

packages = setuptools.find_namespace_packages (include = ['physicsfront.*'])

namespaces = ["physicsfront"]
# any additional namespace as necessary (none so far)
#if "physicsfront.cloud" in packages:
#    namespaces.append("physicsfront.cloud")

# <<< pf dev cycle support: _do_setup, sys.argv
# only if var '_do_setup' is pre-defined or os.environ has 'PYARUNNING'

##
# The content of this file may be just read to extract the values of certain
# parameters, not to really run the setup.  In such a case, define _do_setup
# with a false value _before_ running the content of this file.
#
# Example: python3 -c '_do_setup = False; exec (open ("setup.py", "r").read ()); print (version)'
##
try:
    _do_setup # pylint: disable=E0601
except:
    _do_setup = __name__ == '__main__'

if _do_setup and __name__ == '__main__' and os.environ.get ('PYARUNNING'):
    # 'PYARUNNING' set with any non-empty value? take it as 'pdf dev cycle'.
    if sys.argv [-1] == 'setup.py' or sys.argv [-1].endswith ('/setup.py'):
        ##
        # Some (auto) pf dev cylce command may invoke this file with no
        # argument following this file name.  We allow such type of
        # invocation by falling back to 'check'.
        ##
        sys.argv.append ('check')
# >>>

if _do_setup:
    import pkg_resources
    for _ in namespaces:
        pkg_resources.declare_namespace (_)
    setuptools.setup (
        name = name,
        version = version,
        description = description,
        long_description = long_description,
        author = author,
        author_email = author_email,
        license = license_,
        url = url,
        project_urls = project_urls,
        classifiers = [
            release_status,
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Operating System :: OS Independent",
            "Topic :: Internet",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Security :: Cryptography",
        ],
        platforms = "Posix; MacOS X; Windows",
        packages = packages,
        install_requires = dependencies, # pylint: disable=E0602
        extras_require = extras, # pylint: disable=E0602
        python_requires = python_requires, # pylint: disable=E0602
    )
