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

import io, os, setuptools, sys


# Package metadata.

name = "physicsfront-qiskit"
description = "Utility package for qiskit"

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = 'Development Status :: 3 - Alpha'
##
# These dependencies and python_requires are rough values based on the
# limited testing in google colab (Jan 2023).
##
dependencies = [
    "matplotlib >= 3.2.2",
    "qiskit >= 0.39.4",
    "pylatexenc >= 2.10",
]
#extras = {}
python_requires = ">=3.8"

# Setup boilerplate below this line.

package_root = os.path.abspath (os.path.dirname (__file__))

version = "0.1.0"

readme_filename = os.path.join (package_root, "README.md")
with io.open (readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read ()

# Only include packages under the 'physicsfront' namespace. Do not include tests, benchmarks, etc.
packages = [
    package for package in setuptools.find_packages () if package.startswith("physicsfront")
]

# Determine which namespaces are needed.
namespaces = ["physicsfront"]
#if "physicsfront.cloud" in packages:
#    namespaces.append("physicsfront.cloud")

# for 'ap' dev cycle
if __name__ == '__main__' and len (sys.argv) == 1:
    sys.argv.append ('check')

setuptools.setup (
    name=name,
    version=version,
    description=description,
    long_description=readme,
    author="Physics Front LLC",
    author_email="info@physicsfront.com",
    license="Apache 2.0",
    url="https://github.com/sam-pf/pf-qiskit",
    classifiers=[
        release_status,
        "Intended Audience :: Developers Teachers Students",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Quantum Computing",
    ],
    platforms="Posix; MacOS X; Windows",
    packages=packages,
    namespace_packages=namespaces,
    install_requires=dependencies,
    #extras_require=extras,
    python_requires=python_requires,
    include_package_data=True,
    #zip_safe=False,
)
