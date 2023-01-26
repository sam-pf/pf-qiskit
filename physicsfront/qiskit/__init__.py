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

def backends (provider = None, hub = 'ibm-q', backend = None, ** kwargs): # <<<
    """
    Yields backends.

    If ``backend`` is already specified as a
    :class:`~qiskit.providers.backend.Backend` instance, or an interable of
    them, then they are yielded without having to use the provider
    information, defined by ``provider`` and ``hub`` (see
    :func:`~get_provider`).

    If ``backend`` is left unspecified, is a string, or an iterable that
    yields a string among others, then the provider is necessasry to identify
    and it will be obtained using ``provider`` and ``hub``.

    If and when the provider is needed and its ``backends`` method is called,
    ``kwargs`` will be passed to the method.  For example, kwargs can specify
    a ``filters`` function.

    :param backend:  A string (backend name),
        a :class:`~qiskit.providers.backend.Backend` instance, an iterable of
        them, or ``None``.

        The default value ``None`` means all backends for the provider,
        specified by ``provider`` and ``hub`` (see :func:`~get_provider`).
    """
    from qiskit.providers.backend import Backend # pylint: disable=E0401,E0611
    it_backends = None
    if type (backend) == str:
        it_backends = [backend]
    elif isinstance (backend, Backend):
        it_backends = [backend]
    elif backend is not None:
        it_backends = backend
    if it_backends is None:
        for b in get_provider (provider = provider, hub = hub).backends (** kwargs):
            yield b
    else:
        name2backend = None
        for b in it_backends:
            if type (b) == str:
                if name2backend is None:
                    name2backend = dict ((o.name (), o) for o in get_provider
                        (provider = provider, hub = hub).backends (** kwargs))
                yield name2backend [b]
            else:
                assert isinstance (b, Backend)
                yield b
# >>>
def get_provider (provider = None, hub = 'ibm-q'): # <<<
    if provider is None:
        from qiskit import IBMQ # pylint: disable=W0406,E0611
        provider = IBMQ.get_provider (hub = hub)
    return provider
# >>>>>
def jobs (provider = None, hub = 'ibm-q', backend = None, age = '1d', # <<<
          ** kwargs):
    """
    Yields jobs.

    The arguments ``provider``, ``hub``, and ``backend`` are used to get
    backends (see :func:`~backends`).  Then, for each backend, jobs are
    yielded with ``kwargs``.

    For details of what ``kwargs`` can be,
    `see here <https://qiskit.org/documentation/stubs/qiskit.providers.ibmq.IBMQBackend.jobs.html>`_.

    Note that by default ``limit = 10`` is, implicitly, part of ``kwargs``,
    which means, in this function, 10 jobs maximum yielded per backend.

    If none of ``kwargs`` is given, then by default

    :param age:  By default, the ``start_datetime`` argument in ``kwargs`` is
        automatically generated so that only jobs created within one day are
        yielded.

        To change this behavior, the value of this argument may be changed to
        any other string that ends with 'd' or 'h', or any false value (in
        which case, there will be no consideration of this argument).

        If ``start_datetime`` is specified in ``kwargs``, then this argument
        will not be considered at all.
    """
    if 'start_datetime' not in kwargs and age:
        import datetime, dateutil
        timedelta_o = None
        if type (age) == str:
            if age.endswith ('d'):
                timedelta_o = datetime.timedelta (days = float (age [:-1]))
            elif age.endswith ('h'):
                timedelta_o = datetime.timedelta (hours = float (age [:-1]))
        if timedelta_o is None:
            raise ValueError ("age must be a string that ends with 'd' or 'h'")
        kwargs ['start_datetime'] = (
                datetime.datetime.now (dateutil.tz.tzlocal ()) -
                timedelta_o)
    for b in backends (provider = provider, hub = hub, backend = backend):
        for j in b.jobs (** kwargs):
            yield j
# >>>
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
    n = qc.num_qubits
    bs = list (backends (hub = hub, backend = backend,
                         filters = lambda x:
                            x.configuration ().n_qubits >= n and
                            not x.configuration ().simulator and
                            x.status ().operational == True))
    if not len (bs):
        raise ValueError ("No operational backends found.")
    if len (bs) > 1:
        from qiskit.providers.ibmq import least_busy # pylint: disable=W0406,E0401,E0611
        b = least_busy (bs)
        if not quiet:
            print ("backend auto-determined as the least busy:", b)
    else:
        b = bs [0]
    from qiskit import transpile # pylint: disable=W0406,E0611
    kwargs = {}
    if qasm3:
        #from qiskit import qasm3 as q3 # pylint: disable=W0406,E0611
        qc_t = transpile (qc, b)
        #runnable = q3.Exporter (basis_gates =
        #        b.configuration ().basis_gates).dumps (qc_t)
        runnable = qc_t
        kwargs ['dynamic'] = True
    else:
        runnable = transpile (qc, b, optimization_level = 3)
    return b.run (runnable, shots = shots, memory = memory, ** kwargs)
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
