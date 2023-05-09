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
    ##
    # If IBM qiskit is not available yet, then the patching won't work.  In
    # such a case, the patching must be done manually by importing patch
    # again after qiskit is installed.  For example, colab.init includes
    # importing patch.
    ##
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

def backends (backend = None, provider = None, instance = None, # <<<
              ** kwargs):
    """
    Yields backend instances given the information in the arguments.

    Any backend instance (of type
    :class:`~qiskit_ibm_provider.ibm_backend.IBMBackend` or
    :class:`~qiskit.providers.backend.Backend` instance), specified as the
    value of ``backend`` or as an iterated value of an iterable ``backend``,
    would be left untouched: such a backend instance would be yielded as is.

    The rest of arguments are used only if there are any backends left to be
    found.

    If ``backend`` is left unspecified, is a string, or an iterable that
    yields string, then arguments ``provider`` and ``instance`` are used
    together to identify the provider (see :func:`get_provider`).  Then the
    backends method of this provider is called with ``** kwargs`` to find
    backends.  For example, ``kwargs`` can specify a ``filters`` function.


    :param backend:  A string (backend name), a backend instance, an iterable
        of strings or backend instances, or ``None``.

        The default value ``None`` means all backends for the provider,
        specified by ``provider`` and ``instance``.
    """
    from qiskit_ibm_provider.ibm_backend import IBMBackend # new
    from qiskit.providers.backend import Backend # old (deprecated) # pylint: disable=E0611,E0401
    classes = (IBMBackend, Backend)
    it_backends = None
    if isinstance (backend, str):
        it_backends = [backend]
    elif isinstance (backend, classes):
        it_backends = [backend]
    elif backend is not None:
        it_backends = backend
    if it_backends is None:
        for b in (get_provider (provider = provider, instance = instance)
                  .backends (** kwargs)):
            yield b
    else:
        name2backend = None
        for b in it_backends:
            if isinstance (b, str):
                if name2backend is None:
                    ##
                    # name is a property/attribute for IBMBackend/BackendV2
                    # and is a method in BackendV1
                    ##
                    name2backend = dict (((s (), o) if callable (s) else
                                          (s, o))
                        for (s, o) in ((o.name, o) for o in get_provider
                        (provider = provider, instance = instance)
                        .backends (** kwargs)))
                yield name2backend [b]
            else:
                assert isinstance (b, classes)
                yield b
# >>>
def clbit_label_to_mii (r): # <<<
    """
    Given the job result ``r``, computes the mapping from the classical bit
    label to the memory item index.

    Each memory item (:meth:`~get_memory` of a job result) is a string, which
    is filled from the _back_ in the order of the classical bits defined,
    separated by a space whenever the register is changed.

    :returns:  A :func:`dict` with ``(classical_register_name, index)`` or
        ``classical_register_name `` as keys and the memory item index as
        value.

        There are two copies of keys ``index`` including negativer indices
        going from ``-N`` through ``-1`` where ``N`` is the size of the
        classical register for the name.

        For all registers of length 1 (``N = 1``), and only for them,
        ``classical_register_name`` will appear as key.
    """
    ans = {}
    size = {}
    i = 0
    for res in r.results:
        last_key = None
        for name, index in res.header.clbit_labels:
            if not index and i:
                # starting new register
                if last_key:
                    # pylint: disable=E1136
                    size [last_key [0]] = last_key [-1] + 1
                i += 1
            last_key = (name, index)
            ans [last_key] = i
            i += 1
        if last_key:
            size [last_key [0]] = last_key [-1] + 1
    N = i
    if N:
        N -= 1
        for key in ans:
            ans [key] = N - ans [key]
    toextend = {}
    for key in ans:
        name, index = key
        N = size [name]
        index -= N
        assert 0 < -index <= N
        toextend [(name, index)] = ans [key]
    ans.update (toextend)
    for name in size:
        if size [name] == 1:
            ans [name] = ans [(name, 0)]
    return ans
# >>>
# <<< def expand, tokenize (s, funcname = '_'):
def expand ():
    from io import StringIO
    import re, tokenize # pylint: disable=W0621
    TokenInfo = tokenize.TokenInfo
    generate_tokens = tokenize.generate_tokens
    untokenize = tokenize.untokenize
    NAME = tokenize.NAME
    NUMBER = tokenize.NUMBER
    OP = tokenize.OP
    magic_ops = frozenset (('|', '@'))
    STRING = tokenize.STRING
    pretypes = frozenset ((NAME, STRING))
    posttypes = frozenset ((NUMBER,))
    test_funcname = re.compile ('^[a-zA-Z_][a-z_A-Z0-9]*').match
    test_number = re.compile ('^[0-9]+$').match
    def getti (ti, offset):
        lnum_s, pos_s = ti.start
        lnum_e, pos_e = ti.end
        if lnum_s not in offset:
            assert lnum_e not in offset
            return ti
        start = lnum_s, pos_s + offset [lnum_s]
        if lnum_e in offset:
            end = lnum_e, pos_e + offset [lnum_e]
        else:
            end = lnum_e, pos_e
        return TokenInfo (ti.type, ti.string, start, end, ti.line)
    def _expand (s, funcname = '_'):
        """
        Expands string ``s`` using the 'classical bit info' notation.

        This notation is defined as follows.

            <name>|[<index>]
            <name>@[<index>]

        As indicated, <index> is optional.  The classical bit specification
        (as accepted by :func:`memory_item_index`) is defined from this
        notation as <name> if <index> is not given or (<name>, <index>) if
        <index> is given.

        Note that <name> can be a bare string or a quoted string (if name
        contains tricky characters).

        The symbols | and @ are completely equivalent, and there can be any
        spaces (but no line breaks) around either of them in the above
        notation.

        Lastly, the above notation must be contained in a single line, i.e.,
        it cannot be split into multiple lines.
        """
        return untokenize (_tokenize (s, funcname = funcname))
    def _tokenize (s, funcname = '_'):
        """
        Like :func:`expand`, but yields :class:`~tokenize.TokenInfo`
        instances.
        """
        if not test_funcname (funcname):
            raise ValueError (f"Not a valid funcname ({funcname:!r})")
        it = generate_tokens (StringIO (s).readline)
        returned = []
        def get_next ():
            if returned:
                return returned.pop (0)
            else:
                return next (it)
        def return_ti (ti):
            returned.insert (0, ti)
        offset = {}
        while True:
            try:
                ti = get_next ()
            except StopIteration:
                return
            ti = getti (ti, offset)
            # ti for regname must be confined in one line.
            if not (ti.type in pretypes and ti.start [0] == ti.end [0]):
                yield ti
                continue
            try:
                ti2 = get_next ()
            except StopIteration:
                ti2 = None
            # ti for regname and ti2 for magic marker must belong in one line.
            if not (ti2 and ti2.type == OP and ti2.string in magic_ops and
                    ti2.end [0] == ti.start [0]):
                return_ti (ti2)
                yield ti
                continue
            # found a ti to expand!
            if ti.type == STRING:
                regname = ti.string
            else:
                assert ti.type == NAME
                regname = repr (ti.string)
            ln, i_s = ti.start
            _, i_e = ti2.end
            ti2 = getti (ti2, offset)
            assert _ == ln
            len_funcname = len (funcname)
            i = i_s + len_funcname # i: new ending position
            yield TokenInfo (NAME, funcname, (ln, i_s), (ln, i), '')
            i_s, i = i, i + 1
            yield TokenInfo (OP, '(', (ln, i_s), (ln, i), '')
            i_s, i = i, i + len (regname)
            yield TokenInfo (STRING, regname, (ln, i_s), (ln, i), '')
            try:
                ti3 = get_next ()
            except StopIteration:
                ti3 = None
            doing_number = False
            # any number postfix must along belong in the same line
            ti4 = None
            if ti3:
                if ti3.end [0] == ln:
                    if ti3.type == OP and ti3.string == '-':
                        try:
                            ti4 = get_next ()
                        except StopIteration:
                            ti4 = None
                        doing_number = (ti4 and ti4.end [0] == ln and
                                        ti4.type in posttypes and
                                        test_number (ti4.string))
                        if not doing_number:
                            if ti4:
                                return_ti (ti4)
                            return_ti (ti3)
                    else:
                        doing_number = (ti3.type in posttypes and
                                        test_number (ti3.string))
                        if not doing_number:
                            return_ti (ti3)
                else:
                    return_ti (ti3)
            i_s, i = i, i + 1
            assert i > i_e + offset.get (ln, 0)
            offset [ln] = i - i_e
            if doing_number:
                yield TokenInfo (OP, ',', (ln, i_s), (ln, i), '')
            else:
                yield TokenInfo (OP, ')', (ln, i_s), (ln, i), '')
                continue
            assert ti3 or ti4
            _, i_e = (ti4 or ti3).end
            offset [ln] += 1
            if ti3:
                yield (ti3 := getti (ti3, offset))
            if ti4:
                yield (ti4 := getti (ti4, offset))
            _, i_s = (ti4 or ti3).end
            assert _ == ln
            i = i_s + 1
            yield TokenInfo (OP, ')', (ln, i_s), (ln, i), '')
            assert i > i_e
            offset [ln] = i - i_e
    return _expand, _tokenize
expand, tokenize = expand () # >>>
def gather_counts (r, * clbitspec, predicate = None, keys = None): # <<<
    """
    Gathers counts from a run result (``r``).

    With ``clbitspec`` unspecified, this function is just the same as
    ``r.get_counts ()``.

    With ``clbitspec`` specified, this function will retrieve the raw data
    (``r.get_memory ()``) first (and so the circuit/experiment must have been
    run with memory requested), reduce each memory item by applying
    index/indices defined by ``clbitspec`` (see :func:`memory_item_index`),
    and build the counter dictionary based on the reduced items.

    :param predicate:  If given, then this argument must pass a string value,
        which is expanded using :func:`expand` according to the classical bit
        info notation as accepted by that function and :func:`tokenize`.

    :param keys:  If given, then the :class:`~collections.Counter` instance
        will be updated with this argument as follows.

        If the value of this argument is a mapping, then the counter will be
        updated with this mapping at the end, i.e., with the counts cumulated
        while new keys will be added as necessary.

        Any other value must be an iterable of keys, in which case the keys
        will be made sure to exist (with zero count).  This is equivalent to
        passing a mapping argument with these keys and all values 0.
    """
    if not clbitspec and not predicate:
        return r.get_counts ()
    if predicate:
        assert isinstance (predicate, str)
        regname2index = {}
        namespace = {}
        def _taker (regname, index = None): # requires x to be a memory item
            if index is None:
                key = regname
            else:
                key = (regname, index)
            if key not in regname2index:
                regname2index [key] = memory_item_index (r, key)
            return take (namespace ['x'], regname2index [key])
        code = compile (expand (predicate), '<predicate>', 'eval')
        def predicate_f (x): 
            namespace ['x'] = x
            namespace ['_'] = _taker
            return eval (code, namespace, namespace)
    else:
        predicate_f = None
    def take (k, i):
        ans = k [i]
        assert ans != ' '
        return ans
    if clbitspec:
        indices = memory_item_index (r, * clbitspec)
        if len (clbitspec) == 1:
            assert isinstance (indices, int)
            indices = tuple (indices)
        assert isinstance (indices, tuple)
    else:
        indices = None
    m = r.get_memory ()
    from collections import Counter
    from collections.abc import Mapping
    joinstr = ''.join
    if predicate_f:
        if indices is None:
            it = (k for k in m if predicate_f (k))
        else:
            it = (joinstr (take (k, i) for i in indices) for k in m
                  if predicate_f (k))
    else:
        assert indices is not None
        it = (joinstr (take (k, i) for i in indices) for k in m)
    ans = Counter (it)
    if keys:
        if not isinstance (keys, Mapping):
            keys = dict ((k, 0) for k in keys)
        ans.update (keys)
    return ans
# >>>
def get_provider (): # <<<
    _cached = None
    def _get_provider (provider = None, token = None, instance = None):
        """
        Returns a provider instance based on the information given.

        1. If ``provider`` is given a provider instance (of type IBMProvider
           or AccountProvider, the latter of which is deprecated), then it is
           returned as is.

           In this case, no cache mechanism is used.

        2. If ``provider`` is any other value, it must be one of the
           following values.

                ``None``, ``"cached"``, ``"renew"``

           In this case, a cache mechanism will kick into action.

           First, even if the cache value exists, it is accepted only it is
           valid.  The cached value is valid if the values for ``token`` and
           ``instance`` of its active account are equal to the passed values,
           if any, of ``token`` and ``instance`` arguments.

           If ``provider`` is passed ``"cached"``, then any valid cached
           provider value or ``None`` will be returned immediately.  This is
           simply a check on the cached value.  The return value would be
           either ``None`` or an IBMProvider instance.

           If ``provider`` is passed ``"renew"``, then any cached value will
           be expunged first.

           If ``provider`` is ``None``, then any valid cached value will be
           kept.

           In the latter two cases, a new cache value will be provisioned if
           a valid cached value is not found or has just been expunged.  Then
           the new cached value, of type IBMProvider, will be returned.
        """
        ##
        # These import statements can't be put outside this function, since
        # colab.init must be loaded first to install these modules in the
        # first place!
        ##
        from qiskit_ibm_provider.ibm_provider import IBMProvider
        from qiskit.providers.ibmq.accountprovider import AccountProvider # pylint: disable=E0611,E0401
        classes = (IBMProvider, AccountProvider)
        from qiskit_ibm_provider import IBMProvider # pylint: disable=W0404
        if isinstance (provider, classes):
            return provider
        nonlocal _cached
        if provider == 'renew':
            provider = _cached = None
        has_cache_value = _cached is not None
        if has_cache_value:
            assert isinstance (_cached, classes [0])
        has_valid_cache_value = (has_cache_value and
            (token is None or
             _cached.active_account () ['token'] == token) and
            (instance is None or
             _cached.active_account () ['instance'] == instance))
        if provider == 'cached':
            return _cached if has_valid_cache_value else None
        if provider is not None:
            raise ValueError ("** Invalid value passed for provider "
                              f"argument: {provider}")
        if not has_valid_cache_value:
            _cached = IBMProvider (token = token, instance = instance)
        assert isinstance (_cached, classes [0])
        return _cached
    return _get_provider
get_provider = get_provider ()
# >>>
def jobs (provider = None, instance = None, age = '1d', ** kwargs): # <<<
    """
    Yields jobs meeting the given descriptions at selected backends.

    The arguments ``provider``, ``instance`` are used to get the provider
    (:func:`get_provider`).

    Then, ``provider.backend.jobs`` is invoked with ``kwargs`` passed to it
    to collect jobs.

    For possible keys for ``kwargs``, see the documentation for
    :func:`~qiskit_ibm_provider.ibm_backend_service.IBMBackendService.jobs`.
    The keys include ``"backend_name"`` (to filter for specific backend),
    ``"start_datetime"``, and ``"end_datetime"``. 

    Note that by default ``limit = 10`` is implied, meaning the maximum of 10
    jobs yielded.

    :param age:  By default, the ``start_datetime`` argument in ``kwargs`` is
        automatically generated so that only jobs created within one day are
        yielded.

        To change this behavior, the value of this argument may be changed to
        any other string that ends with 'd' or 'h', or any false value (in
        which case, there will be no consideration of this argument).

        If ``start_datetime`` is already specified in ``kwargs``, then that
        takes precedence and this argument will have no effect at all.
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
    p = get_provider (provider = provider, instance = instance)
    for j in p.backend.jobs (** kwargs):
        yield j
# >>>
def jobs_monitor (jobs, interval = None, # <<< # pylint: disable=W0621
                  quiet = False, job_id_minlen = 6,
                  line_discipline = "\r", output = None):
    """
    A bit like of qiskit.tools.monitor.job_monitor, but for an iterable of
    jobs, instead of a single job.
    """
    import datetime, sys, time
    if interval is None:
        interval = 5
    assert type (interval) is int and interval >= 1
    assert type (job_id_minlen) is int and job_id_minlen >= 4
    assert type (line_discipline) is str
    if output is None:
        output = sys.stderr
    #print (type (jobs), jobs)
    jobs = tuple (jobs)
    n_jobs = len (jobs)
    ended = frozenset (('DONE', 'CANCELLED', 'ERROR'))
    states = [None] * n_jobs
    job_ids = list (job.job_id () for job in jobs)
    while True:
        job_ids_short = list (j [:job_id_minlen] for j in job_ids)
        if len (set (job_ids_short)) == n_jobs:
            break
        job_id_minlen += 2
    all_ended = False
    msg_len = 0
    while True:
        all_ended = True
        for i, job in enumerate (jobs):
            if states [i] in ended:
                continue
            status = job.status ()
            state = status.name
            if state == 'QUEUED':
                queue_position = job.queue_position (refresh = True)
                if queue_position is not None:
                    state += f'({queue_position}' # )
                    ect = job.queue_info ().estimated_complete_time
                    if ect:
                        # add estimated time information
                        tz = ect.tzinfo
                        dt = ect - datetime.datetime.now (tz)
                        dt_s = str (dt)
                        dotpos = dt_s.rfind ('.')
                        if dotpos > 0:
                            dt_s = dt_s [: dotpos]
                        state += f'; {dt_s}' # (
                    state += ')'
            states [i] = state
            all_ended = False
        msg = (f'Status for {n_jobs} job{"s" if n_jobs > 1 else ""}: ' +
            ', '.join (':'.join ([job_id_short, state])
                for job_id_short, state in zip (job_ids_short, states)))
        lendiff = msg_len - len (msg)
        if lendiff > 0:
            msg += " " * lendiff
        msg_len = len (msg)
        if not quiet:
            print (line_discipline + msg, end = '', file = output)
        if all_ended:
            break
        if 'QUEUED' not in states:
            interval = 2
        time.sleep (interval)
    if not quiet:
        print ('', file = output)
# >>>
def memory_item_index (r, * clbitspec): # <<<
    """
    Given a job result ``r`` and classical bit spec(s) ``clbitspec``, returns
    the corresponding memory item index/indices.

    If only one ``clbitspec`` is given, then an index will be returned.  If
    more than one ``clbitspec`` are given, then a tuple of indices will be
    returned.

    :param clbitspec:  Either a 2-tuple ``(clreg_name, index)`` (where
        ``index`` may be negative) or just ``clreg_name`` (if the length of
        the register is 1).
    """
    if not clbitspec:
        raise ValueError ("At least one classical bit specification "
                          "(clbitspec) must be provided.")
    clabel2index = clbit_label_to_mii (r)
    regnames = set (key [0] if isinstance (key, tuple) else key
                    for key in clabel2index)
    ans = []
    for spec in clbitspec:
        if isinstance (spec, tuple):
            name, index = spec
            key_is_tuple = True
        else:
            name = spec
            key_is_tuple = False
        regname = None
        if name in regnames:
            regname = name
        else:
            cands = list (regname for regname in regnames if name in regname)
            if len (cands) != 1:
                raise ValueError (f'Name {name!r} does not complete a '
                                  'classical bit register name (uniquely).')
            regname = cands [0]
        ans.append (clabel2index [(regname, index) if key_is_tuple
                                  else regname])
    return ans [0] if len (ans) == 1 else tuple (ans)
# >>>
def run_quantum_computer (qc, instance = None, shots = 2000, # <<<
                          memory = True, qasm3 = False, backend = None,
                          quiet = False):
    """
    Runs quantum circuit ``qc`` on a real quantum computer.

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
    bs = list (backends (instance = instance, backend = backend,
                         filters = lambda x:
                            x.configuration ().n_qubits >= n and
                            not x.configuration ().simulator and
                            x.status ().operational == True))
    if not len (bs):
        raise ValueError ("No suitable backends found.")
    if len (bs) > 1:
        from qiskit_ibm_provider import least_busy
        b = least_busy (bs)
        if not quiet:
            print ("backend auto-determined as the least busy:", b)
    else:
        b = bs [0]
    from qiskit import transpile # pylint: disable=W0406,E0611
    kwargs = {}
    if qasm3: # WIP
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

    See :func:`run_quantum_computer` for how to process the run result.

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
