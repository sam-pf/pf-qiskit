def _initialize (): # <<<
    import qiskit
    from math import isclose, sqrt
    from numpy import exp, pi
    # pylint: disable=E0401,E0611
    from qiskit.circuit.library.data_preparation import state_preparation
    # pylint: enable=E0401,E0611
    _EPS = state_preparation._EPS
    _initialize_orig = qiskit.QuantumCircuit.initialize # pylint: disable=E1101
    docstr = """
A patched version of :meth:`qiskit.QuantumCircuit.initialize` so
that ``params`` accepts probability-centric expressions (in % unit).

    When ``params`` is an iterable of strings, and only strings, then the
    string expressions are parsed by this method as probability expressions
    (with optional probability amplitude phases) and then converted to the
    probability amplitudes for internal use.

    Additionally, ``params`` may be a string that includes all
    probability-centric expressions, separated by ',' and enclosed by '[' and
    ']'.

    Probability-centric string expression must be in the following format

    .. parsed-literal::

                    '<probability> %'
                    '<probability> % <phase>'

    where ``<probability>`` and ``<phase>`` must be expressions for real
    numbers (non-negative for ``<probability>``) and any white space before
    ``%`` or after ``%`` is optional.

    So, in addition to specifying the probability, the phase of the probability
    amplitude can also be optionally specified.  The phase here corresponds
    to the angle in the complex plane (as probability amplitude is complex
    number; see the conversion forma below), and so it may just be considered
    angle.  Its unit is (implicitly) fixed as degrees.

    Here are some basic phase values.  360 degrees, or any integer
    multiples of 360 degrees, is the same as 0 degrees (which means a
    positive amplitude), 180 degrees means a negative amplitude, 90 degrees
    means multiplying the amplitude by 1j, 270 degrees means multiplying the
    amplitude by -1j, etc.

    For instance, all the following examples are valid inputs for ``params``
    for a single qubit.  For refernece, corresponding numeric expressions for
    the probably amplitude are also given.

    .. code-block::

        ['100 %', '0 %']         : [1, 0]
        '[100 % 360, 0 %]'       : [1, 0]
        '[100 % 720.0, 0 %]'     : [1, 0]
        ['100 % -360', '0 %']    : [1, 0]
        '[100 % 180, 0 %]'       : [-1, 0]
        '[50 % 90, 50 % 180]'    : [sqrt(0.5)*1j, -sqrt(0.5)]
        '[70 % 2, 30 % 270]'     : [sqrt(0.7)*exp(2j*pi/180), -sqrt(0.3)*1j]
        ['70 % 2', '30 % 270']   : [sqrt(0.7)*exp(2j*pi/180), -sqrt(0.3)*1j]

    As these examples demonstrate, the formula going from the `<probability>`
    and `<phase>` to the probability amplitude is as follows:
    ``sqrt(<probability>) * exp(<phase> * 1j * pi/180)``.

    In this way, the probabiliy-centric specification of ``params`` using
    string is equal in terms of its expressive power as the probabiliy
    amplitude specification using (generally complex) numbers.

    For example the following two circuits ``c1`` and ``c2`` are initialized
    exactly the same way.

    .. code-block::

        import numpy as np
        from qiskit import QuantumCircuit

        c1 = QuantumCircuit (1)
        c1.initialize ([1/np.sqrt(2), -1/np.sqrt(2)])

        c2 = QuantumCircuit (1)
        c2.initialize (['50 %', '50 % 180'])
    """.strip ()
    if _initialize_orig.__doc__:
        docstr += """

--- The documentation for the unpatched version of this method follows. ---

""" + _initialize_orig.__doc__
    phase_arg_factor = 1j * pi / 180.
    from collections.abc import Iterable
    def initialize (self, params, qubits = None): # <<<
        if isinstance (params, str):
            s = params.strip ()
            if s.startswith ('[') and s.endswith (']'):
                s = s [1:-1]
                params = s.split (',')
        if isinstance (params, Iterable) and not isinstance (params, str):
            params = list (params)
            score = sum (1 if isinstance (v, str) else 0 for v in params)
            if score == len (params):
                params_new = []
                pr_sum = 0.
                for v in params:
                    if '%' not in v:
                        raise ValueError ("Any string iterated by params "
                                          "must contain %.")
                    pr, pf = v.split ('%', 1)
                    pr = float (pr)
                    pf = (exp (float (pf) * phase_arg_factor)
                          if pf.strip () else 1.)
                    if pr < 0:
                        if isclose (pr, 0., abs_tol = _EPS):
                            pr = 0.
                        else:
                            raise ValueError (f"Probability in {v!r} is not "
                                              "non-negative.")
                    params_new.append (sqrt (pr) * pf / 10.)
                    pr_sum += pr
                if not isclose (pr_sum, 100., abs_tol = _EPS * 100.):
                    raise ValueError ("Sum of probabilities must be equal to "
                                      "100 (%).")
                params = params_new
            elif score:
                raise TypeError ("If a string is an element of params then "
                                 "all elements must be strings.")
        return _initialize_orig (self, params, qubits = qubits)
    # >>>
    initialize.__doc__ = docstr
    return initialize
# >>>
_initialize = _initialize ()

def _ (): # <<<
    import qiskit
    if qiskit.QuantumCircuit.initialize is _initialize: # pylint: disable=E1101
        return
    qiskit.QuantumCircuit.initialize = _initialize # pylint: disable=E1101
# >>>
_ ()
