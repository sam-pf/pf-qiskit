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

from . import colab

def run_quantum (qc, hub = 'ibm-q', shots = 2000, memory = True, # <<<
                 qasm3 = False, backend = None, quiet = False):
    """
    Runs a real quantum computer on quantum circuit ``qc``.

    :param qasm3:  WIP.  Does not seem to work if this option is turned on,
        as of 01-25-2023.  Nor do the dynamic code examples in the IBM qiskit
        tutorial, when they are run in IBM Quantum Jupyter lab.

        When this argument is turned on, passing ``backend`` as a backend
        instance might be preferred.  And, ``memory`` might not work (I get a
        warning).

    :param backend:  If given, then it can be a backend instance or a backend
        name.
    """
    from qiskit import IBMQ, transpile # pylint: disable=W0406,E0611
    from qiskit.providers.ibmq import least_busy # pylint: disable=W0406,E0401,E0611
    if not IBMQ.active_account ():
        raise Exception ("No IBMQ acount is active.")
    provider = IBMQ.get_provider (hub = hub)
    n = qc.num_qubits
    if backend:
        if type (backend) == str:
            found = None
            for b in provider.backends ():
                if b.name () == backend:
                    found = b
                    break
            if found is None:
                raise ValueError (f"No backend found with name '{backend}'.")
            backend = found
        # In all other cases, backend must be a real backend (or simulator).
    else:
        # it'd be nice to check if backend is qasm3, but don't know how yet...
        assert not qasm3
        backend = least_busy (provider.backends
                (filters = lambda x: x.configuration().n_qubits >= n and
                                     not x.configuration().simulator and
                                     x.status().operational == True))
        if not quiet:
            print ("backend auto-determined with least_busy:", backend)
    kwargs = {}
    if qasm3:
        #from qiskit import qasm3 as q3 # pylint: disable=W0406,E0611
        qc_t = transpile (qc, backend)
        #runnable = q3.Exporter (basis_gates =
        #        backend.configuration ().basis_gates).dumps (qc_t)
        runnable = qc_t
        kwargs ['dynamic'] = True
    else:
        runnable = transpile (qc, backend, optimization_level = 3)
    return backend.run (runnable, shots = shots, memory = memory, ** kwargs)
# >>>
def run_quantum_simulator (qc, shots = 2000, memory = True, seed = 100): # <<<
    """
    Runs an Aer quantum simulator on the quantum circuit ``qc``.

    See :func:`run_quantum` for how to process the run result.

    In a simulator run, it is also possible to do

        `r.get_statevector ()`

    assuming that the statevector was saved in the qc.

    :param seed:  The seed value is intentionally fixed at an integer value
        to emphasize the deterministic nature of the simulator. If seed is
        set to None, then a seed will be reset for each run by the system.
    """
    from qiskit import Aer, assemble # pylint: disable=W0406,E0611
    o = assemble (qc)
    sim = Aer.get_backend ('aer_simulator')
    sim.set_option ('seed_simulator', seed)
    return sim.run (o, shots = shots, memory = memory)
# >>>
