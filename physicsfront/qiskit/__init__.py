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
try:
    from . import patch
except ModuleNotFoundError:
    # e.g., if qiskit is not available yet (in colab)
    pass

class WiringInstruction (object): # <<<

    """
    A helper class to ease composing quantum circuits.

    This class currently limits a possible wiring to attaching a quantum
    circuit (``qc``) to an existing one (``qc0``).  For this to be able to
    occur, ``qc`` must be a register oriented quantum circuit in the
    following sense.

    1. All qubits must be accountable through _its_ quantum registers, and
       vice versa.
    2. The wiring instruction (the ``wiring`` argument) should either exhaust
       a quantum register or leave it untouched.  That is, it is not allowed
       to wire only some qubits in a register.
    3. All unwired registers (which include any classical registers in ``qc``)
       will be added to ``qc0``.

    The per-instruction actions occur through
    :meth:`~WiringInstruction.prepare` and :meth:`~WiringInstruction.apply`.

    The static method :meth:`~WiringInstruction.wire` is a convenience method
    to wire multiple quantum circuits to an initial quantum circuit.
    """

    def __init__ (self, qc, wiring, barrier = False): # <<<
        """
        :param wiring:  Must be an iterable of 2-tuples, consisting of
            integers.  The 2-tuples are the wiring map from the qubits of a
            prepared preceding quantum circuit (``qc0``) to the qubits of
            ``qc``.

            Indices can be negative (reverse index).

            Note that as a quantum circuit is prepared for wiring, its qubit
            registers will become more numerous.  Negative indexes are
            interpreted when preparing (:meth:`~WiringInstruction.prepare`)
            the preceding  quantum circuit, rather than applying to it.
        """
        self._qc = qc
        self._wiring = wiring = tuple (wiring)
        for t in wiring:
            if not isinstance (t, tuple):
                raise TypeError ("'wiring' must consist of tuples.")
            i, j = t
            if not isinstance (i, int) or not isinstance (j, int):
                raise TypeError ("'wiring' must consist of 2-tuples of int's.")
        self._barrier = barrier
    # >>>

    # <<< def wire (qc0, * instruction):
    @staticmethod
    def wire (qc0, * instruction):
        """
        Wires ``qc0`` with other subsequent quantum circuits according to
        ``instruction``.

        Each instruction must be either a tuple, a dict, or a
        :class:`WiringInstruction` instance.  A tuple or dict is used as
        arguments to pass to :class:`WiringInstruction` in order to create an
        instance on the fly.

        A dict is used as keyword arguments.

        A tuple is used as positional arguments, with one exception.  If the
        tuple is a 2-tuple consisting of a tuple and a dict, then it is
        interpreted as positional arguments and keyword arguments.

        Once all :class:`WiringInstruction` instances are identified or created,
        then they are used to prepare ``qc0`` and then applied to ``qc0``.

        In this method, ``qc0`` is deep-copied first, and then, all
        subsequent operations are applied in-place.
        """
        assert (instruction)
        instructions = []
        for instr in instruction:
            if not isinstance (instr, WiringInstruction):
                assert instr
                if isinstance (instr, tuple):
                    if (len (instr) == 2 and isinstance (instr [0], tuple) and
                            isinstance (instr [1], dict)):
                        instr = WiringInstruction (* instr [0], ** instr [1])
                    else:
                        instr = WiringInstruction (* instr)
                elif isinstance (instr, dict):
                    instr = WiringInstruction (** instr)
            instructions.append (instr)
        ans = qc0 = qc0.copy ()
        iks = list ((instr, instr.prepare (qc0))
                    for instr in instructions)
        for instr, kwargs in iks:
            kwargs ['inplace'] = True
            ans = instr.apply (ans, kwargs)
            assert ans is not None and ans is qc0
        return ans
    # >>>

    def apply (self, qc0, kwargs): # <<<
        """
        Wires ``qc0`` and the quantum circuit registered with this object.

        ``kwargs`` must be the one that has been prepared through the method
        :meth:`~WiringInstruction.prepare`.

        When applyling multiple instructions, they must be applied exactly in
        the same order as they have been used to prepare ``qc0``.

        :returns: ``qc0`` (if 'inplace' is turned on in ``kwargs``) or a new
            quantum circuit (if not in place).
        """
        inplace = kwargs.get ('inplace', None)
        if self._barrier:
            if inplace:
                qc0.barrier ()
            else:
                qc0 = qc0.copy ()
                qc0.barrier ()
        assert set (kwargs.keys ()) <= set (['qubits', 'clbits', 'inplace'])
        ans = qc0.compose (self._qc, ** kwargs)
        if ans is None:
            assert inplace
            return qc0
        return ans
    # >>>
    def prepare (self, qc0): # <<<
        """
        Prepares the quantum circuit ``qc0`` in order to wire it to the
        subsequent quantum circuit, which is the one registered in this
        instruction object.

        The preparation can fail with error.

        If an error occurs or not, ``qc0`` may have been modified, having
        acquired any new quantum and classical registers, which correspond to
        the all unwired registers of the quantum circuit in this instruction.

        If an error occurs during the addition of those registers, then
        ``qc0`` may be in a partially modified state.  In all other cases,
        ``qc0`` will be in either a completely untouched state (if there are
        no registers to add, while this method returns normally, or if an
        error occurs prior to any attempt to add registers) or
        a fully modified state (all registers added and no errors).

        :returns:  ``kwargs`` that can, and must, be used with
            :func:`~WiringInstruction.apply` to do the actual wiring.
        """
        n0 = len (qc0.qubits)
        qc1 = self._qc
        n1 = len (qc1.qubits)
        qubitsmap = {}
        qubitsmap_forward = {} # this is just to check wiring integrity
        for i, j in self._wiring:
            i_orig = i
            j_orig = j
            if i < 0:
                i += n0
            if j < 0:
                j += n1
            if i < 0 or i >= n0:
                raise ValueError ("Index out of range for qubit for the first"
                                  " circuit: %d" % (i_orig,))
            if j < 0 or j >= n1:
                raise ValueError ("Index out of range for qubit for the second"
                                  " circuit: %d" % (j_orig,))
            # no merging or splitting allowed in wiring; always 1-to-1
            assert j not in qubitsmap
            qubitsmap [j] = i
            assert i not in qubitsmap_forward
            qubitsmap_forward [i] = j
        ##
        # The requirements for qc1 to be wireable to qc0.
        #
        # (In sum: Any unwired qubits/clbits must belong in qc1's registers,
        #          in which no wired qubits/clbits are allowed.)
        #
        # 1. After all qubits with indices as registered in qubitsmap are
        #    taken into account, any remaining qubits must belong in quantum
        #    registers.
        # 2. In any of those remaining registers, there should not exist any
        #    wired qubit.  Namely, those registers should consist of purely
        #    unwired qubits.
        # 3. At the moment, no classical bits are allowed to be wired, and
        #    all classical bits must be accounted for precisely by all
        #    classical registers of qc1.
        ##
        unwired_qbits_map = dict ((qb, i) for i, qb in enumerate (qc1.qubits)
                                   if i not in qubitsmap)
        qregs2add = []
        for r in qc1.qregs:
            test = sum (b in unwired_qbits_map for b in r)
            if test == r.size:
                qregs2add.append (r)
            elif test:
                raise TypeError ("Wiring is implemented only if unwired "
                                 "qubits are not mixed with wired qubits "
                                 "in their common register.")
        for r in qregs2add:
            n = r.size
            ioffset = unwired_qbits_map [r [0]]
            # anticipate that qregs will be added to qc0
            for i in range (n):
                assert i + ioffset not in qubitsmap
                qubitsmap [i + ioffset] = n0 + i
            n0 += n
        if len (qubitsmap) != n1:
            raise TypeError ("Wiring is limited to a circuit whose unwired "
                             "qubits are totally accounted for by its qregs.")
        ##
        # At this point, qbitsmap is complete and it contains wired and
        # non-wired indices of qc1 as its keys, and no other keys.  Namely,
        # its keys must be exactly a set equivalent to range (n1).
        #
        # The following will fail should this not be true (so it doubles
        # as an assertion).
        ##
        qubits_arg = list (qubitsmap [i] for i in range (n1))
        n0_cl = len (qc0.clbits)
        n1_cl = len (qc1.clbits)
        if n1_cl != sum (r.size for r in qc1.cregs):
            raise TypeError ("Wiring is limited to a circuit whose clbits "
                             "are completely accounted for by its cregs.")
        clbits_arg = list (range (n0_cl, n0_cl + n1_cl))
        ##
        # We add registers only after making sure that there are no errors.
        #
        # Adding registers can fail, if name conflict exists.  We leave it to
        # user to avoid any name collision.
        ##
        for r in qregs2add:
            qc0.add_register (r)
        for r in qc1.cregs:
            qc0.add_register (r)
        return {'qubits': qubits_arg, 'clbits': clbits_arg}
    # >>>

# >>>

def backends (provider = None, hub = 'ibm-q', backend = None, ** kwargs): # <<<
    """
    Yields backends.

    Any :class:`~qiskit.providers.backend.Backend` instance, as specified as
    the value of ``backend`` or any part of iterated values of ``backend``
    will be left untouched and be yielded as is.  None of the arguments are
    used in this case.

    If ``backend`` is left unspecified, is a string, or an iterable that
    yields a string among others, then the provider is necessasry to identify
    and it will be obtained using ``provider`` and ``hub``.  Then, its
    ``backends`` method is called with ``kwargs`` passed to it.  For example,
    kwargs can specify a ``filters`` function.

    :param backend:  A string (backend name),
        a :class:`~qiskit.providers.backend.Backend` instance, an iterable of
        them, or ``None``.

        The default value ``None`` means all backends for the provider,
        specified by ``provider`` and ``hub`` (see :func:`~get_provider`).
    """
    from qiskit.providers.backend import Backend # pylint: disable=E0401,E0611
    it_backends = None
    if isinstance (backend, str):
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
            if isinstance (b, str):
                if name2backend is None:
                    # name is method in BackendV1 and property in BackendV2
                    name2backend = dict (((s (), o) if callable (s) else (s, o))
                        for (s, o) in ((o.name, o) for o in get_provider
                        (provider = provider, hub = hub).backends (** kwargs)))
                yield name2backend [b]
            else:
                assert isinstance (b, Backend)
                yield b
# >>>
def gather_counts (r, converter = None): # <<<
    """
    Gathers counts from a run result (``r``).

    With ``converter`` unspecified, this function is just the same as
    ``r.get_counts ()``.

    With ``converter`` specified, in which case it must be a callable, this
    function will retrieve the raw data (``r.get_memory ()``) first (and so
    the circuit/experiment must have been run with memory requested), apply
    ``converter`` to each element of the raw data, and build the counter
    dictionary based on the converted values.
    """
    if converter is None:
        return r.get_counts ()
    m = r.get_memory ()
    from collections import Counter
    return Counter (e for e in (converter (k) for k in m) if e is not None)
# >>>
def get_provider (provider = None, hub = 'ibm-q'): # <<<
    """
    If ``provider`` is not ``None``, then this function just returns it.
    Otherwise, it will provision the provider based on ``hub``.
    """
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
        if isinstance (age, str):
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
    if qasm3:
        from qiskit_ibm_provider import IBMProvider
        provider = IBMProvider ()
    else:
        provider = None
    bs = list (backends (provider = provider, hub = hub, backend = backend,
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
wire = WiringInstruction.wire
