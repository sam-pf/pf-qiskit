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

def define_qft_functions (namespace, output_endians = ('auto',), # <<<
                          inverses = (False, True), mfs = (True,),
                          include_examples = False, overwrite = False,
                          verbose = False):
    """
    Builds (when necessary) and binds various qft functions to ``namespace``.

    Calling this function is _not_ necessarily more powerful than just
    calling get_qft once, although this function can be useful for a testing
    purpose.

    This function implies three loops defined by three arguments
    ``output_endians``, ``inverses``, and ``mfs``.

    Perhaps very informative are the special attributes of any funtion newly
    bound to ``namespace``.

        __inverse__
        __opposite_endian__
        __opposite_mf__
        __other_mf__
        __example__

    (See :func:`get_qft` for explanation of these attributes.)

    Through these attributes, the full interconnectivity of all functions
    newly bound in ``namespace`` or any functions that are related to them is
    expressed starting from just one function.
    """
    assert isinstance (output_endians, (tuple, list))
    assert isinstance (inverses, (tuple, list))
    assert isinstance (mfs, (tuple, list))
    accepts = []
    rejects = []
    reject_map = {}
    def record (f):
        name = f.__name__
        if name not in namespace or overwrite:
            namespace [name] = f
            assert namespace [name] is f
            accepts.append (name)
        else:
            rejects.append (name)
            reject_map [name] = f
    for endian in output_endians:
        for inverse in inverses:
            for mf in mfs:
                f = get_qft (output_endian = endian, inverse = inverse,
                             mf = mf)
                record (f)
                assert f is get_qft (output_endian = endian, inverse = inverse,
                                     mf = mf)
                if include_examples:
                    f_ex = getattr (f, '__example__', None)
                    if f_ex:
                        record (f_ex)
    if verbose:
        import sys
        if accepts:
            print ("Number of QFT functions recorded: %d: %s" %
                   (len (accepts), accepts), file = sys.stderr)
        if rejects:
            print ("Number of QFT functions rejected: %d: %s" %
                   (len (rejects), rejects), file = sys.stderr)
            print ("Consider using optional argument 'overwrite'?",
                   file = sys.stderr)
    return accepts, rejects, reject_map
# >>>
def get_qft (): # <<<
    cache = {}
    def add2cache (funcname, f):
        assert funcname not in cache
        assert funcname == f.__name__
        cache [funcname] = f
    def _bind_one_other (f, attr, f_attr):
        assert not hasattr (f, attr)
        assert callable (f_attr)
        assert f is not f_attr
        setattr (f, attr, f_attr)
        assert getattr (f, attr) is f_attr
    def bind_inverse_and_others (f, output_endian, inverse, mf): # <<<
        # assert that all _get_qft args have been normalized (by _get_qft)
        assert output_endian == 'little' or output_endian == 'big'
        assert mf != 'measure'
        oppo_endian = 'big' if output_endian == 'little' else 'little'
        _bind_one_other (f, '__inverse__', _get_qft (
                            output_endian = oppo_endian,
                            mf = mf,
                            inverse = not inverse))
        _bind_one_other (f, '__opposite_endian__', _get_qft (
                            output_endian = oppo_endian,
                            mf = mf,
                            inverse = inverse))
        _bind_one_other (f, '__opposite_mf__', _get_qft (
                            output_endian = output_endian,
                            mf = not mf,
                            inverse = inverse))
        if not mf:
            return
        _bind_one_other (f, '__other_mf__', _get_qft (
                            output_endian = output_endian,
                            mf = True if mf == 'measured' else 'measured',
                            inverse = inverse))
    # >>>
    def _get_qft (output_endian = 'auto', inverse = False, mf = True): # <<<
        """
        Factory function for qft or inverse qft function that can be applied
        to a quantum circuit.

        The returned function has informative name as well as the following
        informative attrivbutes.

            __src__: the source code of the function
            __inverse__: the inverse of this (inverse) qft function
            __opposite_endian__: endian reversed
            __opposite_mf__: mf boolean negatiion
            __other_mf__: 'measured' (1-bit) or 'mf' ('n-bit)
            __example__: a use pattern example (only if mf == 'measured')

        The full connectivity provided by these attributes means that the
        full set of qft functions is accesssible starting from just one
        function returned by this factory function.

        :param output_endian:  'auto', 'opposite' (or 'auto_opposite'),
            'little', 'big'

        :param mf':  If this value is true, then a measurement friendly form
            of tranform function is returned.

            If the true value is 'measured', then it is treated specially and
            it will cause a one-qubit measurement protocol function to be
            returned.

            If the true value is 'measure', it is taken as the same meaning
            as 'measured'.
        """
        if mf == 'measure': mf = 'measured'
        if output_endian == 'auto':
            if mf == 'measured':
                output_endian = 'little'
            else:
                output_endian = 'little' if inverse else 'big'
        elif output_endian == 'opposite' or output_endian == 'auto_opposite':
            if mf == 'measured':
                output_endian = 'big'
            else:
                output_endian = 'big' if inverse else 'little'
        assert output_endian == 'big' or output_endian == 'little'
        little_endian_doc = 'the LSB at index 0 and the MSB at index n-1'
        big_endian_doc = 'the MSB at index 0 and the LSB at index n-1'
        qft_adj = 'Measurement friendly form of ' if mf else ''
        if mf == 'measured': qft_adj = 'Measured '
        qft_adj += ('i' if qft_adj else 'I') + 'nverse ' if inverse else ''
        if qft_adj:
            qft_adj_lc = qft_adj [0].lower () + qft_adj [1:]
        else:
            qft_adj_lc = ''
        input_info_line = "Input ({}): {}-endian: {}".format (
            "a_F" if inverse else "a",
            'little' if output_endian == 'big' else 'big',
            little_endian_doc if output_endian == 'big' else big_endian_doc)
        output_info_line = "Output ({}): {}-endian: {}".format (
            "a" if inverse else "a_F",
            output_endian,
            big_endian_doc if output_endian == 'big' else little_endian_doc)
        if output_endian == 'big':
            output_info_line_m = 'LSB = ``creg [n - 1]``, MSB = ``creg [0]``'
        else:
            output_info_line_m = 'LSB = ``creg [0]``, MSB = ``creg [n - 1]``'
        output_info_line_m = "Output ({}): {}-endian: {}".format (
            "a" if inverse else "a_F",
            output_endian,
            output_info_line_m)
        # pylint: disable=W0641
        from math import pi
        float_ = float
        # pylint: enable=W0641
        funcname = 'iqft' if inverse else 'qft'
        if mf:
            funcname += '_m' if mf == 'measured' else '_mf'
        if output_endian == 'little':
            funcname += '_leo'
        else:
            assert output_endian == 'big'
            funcname += '_beo'
        # <<< f_cached, fex_cached, funcname_example; return f_cached
        f_cached = cache.get (funcname, None)
        if mf == 'measured':
            funcname_example = '_' + funcname + '_example'
            fex_cached = cache.get (funcname_example, None)
        else:
            funcname_example = fex_cached = None
        if fex_cached:
            assert f_cached
        if not f_cached:
            assert not fex_cached
        if f_cached:
            if funcname_example:
                assert f_cached.__example__ is fex_cached
            else:
                assert not hasattr (f_cached, '__example__')
            return f_cached
        # >>>
        assert f_cached is None and fex_cached is None
        hfirst = hlast = ''
        if mf:
            hlast = 'qc.h (j)'
            if output_endian == 'big':
                iterj = 'reversed (range (n))'
                iterk = 'range (j + 1, n)'
            else:
                iterj = 'range (n)'
                iterk = 'range (0, j)'
        else:
            hfirst = 'qc.h (j)'
            if output_endian == 'big':
                iterj = 'reversed (range (n))'
                iterk = 'range (0, j)'
            else:
                iterj = 'range (n)'
                iterk = 'range (j + 1, n)'
        if iterk == 'range (j + 1, n)':
            jkdif = 'k - j'
        elif iterk == 'range (0, j)':
            jkdif = 'j - k'
        else:
            raise Exception ("Unexpected value for iterk = %r" % (iterk,)) # pylint: disable=W0719
        psign = '-' if inverse else ''
        if hfirst:
            assert not hlast
        else:
            assert hlast
        funcexampledef = None
        if mf == 'measured':
            assert not hfirst
            funcdef = f"""
def {funcname} (qc, i, creg, j, n = None):
    '''
    Uses the quantum circuit (``qc``)'s qubit at index ``i`` for 1-bit
    {qft_adj_lc}QFT whilst storing the measured outcome in the
    classical bit ``creg [j]``.

    This function allows to compute {qft_adj_lc}QFT with only a single
    qubit (``i`` of ``qc``), which must be prepared to carry the required
    input at each call.  The qubit will be used as a work qubit and then
    will be left in the state measured and recorded at ``creg [j]``.

    For this bit-by-bit {qft_adj_lc}QFT to work, the following
    underlying mechanism must be understood clearly for its use.

    #. This function must be called *repeatedly* (``n`` times, precisely
       speaking) for the full result.

    #. The output, which is recorded at ``creg [j]``, comes out the LSB
       first, while the input (``i`` of ``qc``) must be prepared the MSB
       first.

    {output_info_line_m}

    :param n:  If not given, then defaults to ``creg.size``.  This is the
        bit size of the full result.

        That is, this function must be called ``n`` times for the full
        result and ``j`` must range from zero through ``n - 1``.
    '''
    if n is None:
        n = creg.size
    assert n <= creg.size and 0 <= j < n
    for k in {iterk}:
        qc.p ({psign}pi / float_ (2 ** ({jkdif})), i).c_if (creg [k], 1)
    qc.h (i)
    qc.measure (i, creg [j])
""".strip ()
            funcexampledef = f"""
def {funcname_example} (qc, creg, n = None):
    '''
    Example that shows the pattern to use function {funcname}.

    The quantum circuit must consist of at least ``n + 1`` qubits and
    the qubit at index at ``n`` is used as the work-space qubit.

    However, due to entanglement, all qubits will be left in the state of
    the measurement, not just the work-space qubit.

    {input_info_line}
    {output_info_line_m}
    '''
    if n is None:
        n = creg.size
    for j in {iterj}:
        ##
        # This is a silly example since we got the full qubits, and all
        # we are doing is the QFT, or inv QFT, in a convoluted way.  But,
        # in some important algorithm (phase measurment), the loops can
        # use a single qubit for doing QFT-inv-QFT, while the other
        # qubits are used to generate phase information.
        #
        # In such a (real use) case, the following two changes are to be
        # noted.
        #
        # 1. The qubit index (the first j here) will be a fixed value
        #    regardless of j.
        # 2. Other non-trival computations must occur in this space
        #    just before calling {funcname}.
        ##
        {funcname} (qc, j, creg, j, n)
        # qc [j] will have been measured to creg [j] now
""".strip ()
        else:
            funcdef = f"""
def {funcname} (qc, n):
    '''
    {qft_adj}QFT

    {input_info_line}
    {output_info_line}
    '''
    for j in {iterj}:
        {hfirst}
        for k in {iterk}:
            qc.cp ({psign}pi / float_ (2 ** ({jkdif})), j, k)
        {hlast}
""".strip ()
            funcdef = '\n'.join (s for s in funcdef.strip ().split ('\n')
                                 if len (s) < 8 or s.strip ())
        exec (funcdef, locals ())
        f = eval (funcname, locals ())
        f.__src__ = funcdef
        n_cache = len (cache)
        add2cache (funcname, f)
        assert len (cache) == n_cache + 1
        n_cache += 1
        if funcexampledef:
            assert funcname_example
            exec (funcexampledef, locals ())
            fex = eval (funcname_example, locals ())
            fex.__src__ = funcexampledef
            add2cache (funcname_example, fex)
            assert len (cache) == n_cache + 1
            _bind_one_other (f, '__example__', fex)
        else:
            assert not funcname_example
        bind_inverse_and_others (f, output_endian, inverse, mf)
        assert len (cache) <= 16
        return f
# >>>
    return _get_qft
get_qft = get_qft ()
# >>>
