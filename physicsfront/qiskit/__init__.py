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

#from qiskit.tools.monitor import job_monitor # pylint: disable=W0611
#from qiskit.visualization import plot_histogram # pylint: disable=W0611

def qc_entangled_two_qbits (kind = 1, statevector = False, measure = True):
    """
    :param statevector:  Only for simulator run.
    """
    from qiskit import QuantumCircuit # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    qc = QuantumCircuit (2)
    if kind == 0: # symmetric Bell sate: |00> + |11>
        iv0 = [1, 0]
        iv1 = [1, 0]
    elif kind == 1: # EPR: -|01> + |10>
        iv0 = [0, 1]
        iv1 = [0, 1]
    elif kind == 2: # |00> - |11>
        iv0 = [0, 1]
        iv1 = [1, 0]
    elif kind == 3: # |01> + |10>
        iv0 = [1, 0]
        iv1 = [0, 1]
    else:
        iv0, iv1 = kind
    qc.initialize (iv0, 0) # pylint: disable=E1101
    qc.initialize (iv1, 1) # pylint: disable=E1101
    qc.h (0)
    qc.cx (0, 1)
    if statevector:
        qc.save_statevector () # pylint: disable=E1101
        ##
        # Later, do 'j.result ().get_statevector ()' where j is job (returned
        # by run_quantum_simulator)
        ##
    if measure:
        qc.measure_all ()
    return qc

def qc_for_random_bits (statevector = False, measure = True):
    """
    :param statevector:  Only for simulator run.
    """
    from qiskit import QuantumCircuit # pylint: disable=W0406,E0611
    if statevector:
        # This is for 'qc.save_statevector'.
        from qiskit.providers.aer import Aer # pylint: disable=E0401,E0611,W0611
    qc = QuantumCircuit (1)
    qc.initialize ([1, 0], 0) # pylint: disable=E1101
    qc.h (0)
    if statevector:
        qc.save_statevector () # pylint: disable=E1101
    if measure:
        qc.measure_all ()
    return qc

def run_quantum (qc, hub = 'ibm-q', shots = 2000, memory = True,
                 backend = None, quiet = False):
    """
    Runs a real quantum computer.  This is how the run result can be processed.

    ```
    qc.draw ()
    j = run_quantum (qc)
    job_monitor (j, interval = 2)
    r = j.result ()
    plot_histogram (r.get_counts ())
    m = r.get_memory ()
    ```
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
        backend = least_busy (provider.backends
                (filters = lambda x: x.configuration().n_qubits >= n and
                                     not x.configuration().simulator and
                                     x.status().operational == True))
        if not quiet:
            print ("backend auto-determined with least_busy:", backend)
    transpiled_qc = transpile (qc, backend, optimization_level=3)
    return backend.run (transpiled_qc, shots = shots, memory = memory)

def run_quantum_simulator (qc, shots = 2000, memory = True, seed = 100):
    """
    Runs a quantum simulator.

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
