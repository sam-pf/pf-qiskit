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

##
# These requirements, expressed in the format suitable for use in setup.py,
# are rough values determined from limited test runs in google colab as well
# as terminal based ipython.
##
dependencies = [
    "qiskit >= 0.39.2",
    "qiskit_ibm_provider >= 0.1.0",
]
extras = {
    "mpl": [
        "matplotlib >= 3.2.2",
        "pylatexenc >= 2.10",
    ],
}
python_requires = ">=3.8"
