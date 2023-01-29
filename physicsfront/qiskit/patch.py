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
that ``params`` accepts an additional type of value, a tuple.

    When ``params`` is a tuple, it is taken as a probability sequence
    (rather than a probability amplitude sequence expresssed as a list).

    The probabilities may be given in % unit or no unit.  However,
    there is no need or way to specify the unit explicitly.

    The values of probabilities should sum up to 100 or 1.  If the sum is
    100, then the unit of probabilities is taken as %, and if the sum is
    1, then there is no unit.

    Any element of tuple ``params`` can itself be a tuple, in which case it
    must be a 2-tuple, consisting of a probability and a "probability
    amplitude phase" or simply "phase."  The phase can be taken to mean
    angle and for this function the unit of angle is fixed as degrees.

    Here are some basic phase values.  360 degrees, or any integer
    multiples of 360 degrees, is the same as 0 degrees (which means a
    positive amplitude), 180 degrees means a negative amplitude, 90 degrees
    means multiplying the amplitude by 1j, 270 degrees means multiplying the
    amplitude by -1j, etc.

    For instance, all the following examples are valid inputs for ``params``
    for a single qubit.  For refernece, corresponding list expressions are
    also given.

    .. code-block::

        (100, 0)                 : [1, 0]
        (1, 0)                   : [1, 0]
        ((100, 0), 0)            : [1, 0]
        ((100, 360), 0)          : [1, 0]
        ((100, 720), 0)          : [1, 0]
        ((100, -360), 0)         : [1, 0]
        ((100, 180), 0)          : [-1, 0]
        ((50, 90), (50, 180))    : [sqrt(0.5)*1j, -sqrt(0.5)]
        ((0.5, 90), (0.5, 180))  : [sqrt(0.5)*1j, -sqrt(0.5)]
        ((70, 2), (30, 270))     : [sqrt(0.7)*exp(2j*pi/180), -sqrt(0.3)*1j]

    When going from the probability to the probability amplitude, the
    probability will be square-rooted, and, if the phase has been given,
    ``exp(phase * 1j * pi/180)`` will be multiplied to it.

    Thus, the probabiliy specification of ``params`` is equal in terms of its
    expressive power as the probabiliy amplitude specification.

    For example the following two circuits ``c1`` and ``c2`` are initialized
    exactly the same way.

    .. code-block::

        import numpy as np
        from qiskit import QuantumCircuit

        c1 = QuantumCircuit (1)
        c1.initialize ([1/np.sqrt(2), -1/np.sqrt(2)])

        c2 = QuantumCircuit (1)
        c2.initialize ((50, (50, 180)))
    """.strip ()
    if _initialize_orig.__doc__:
        docstr += """

--- The documentation for the unpatched version of this method follows. ---

""" + _initialize_orig.__doc__
    phase_arg_factor = 1j * pi / 180.
    def initialize (self, params, qubits = None): # <<<
        if isinstance (params, tuple):
            params_new = []
            pr_sum = 0.
            for v in params:
                if isinstance (v, tuple):
                    pr, pf = v
                    if not isinstance (pf, (int, float)):
                        raise TypeError (f"Phase ({pf}) is not a real number.")
                    pf = exp (pf * phase_arg_factor)
                else:
                    pr = v
                    pf = 1
                if pr < 0:
                    if isclose (pr, 0., abs_tol = _EPS):
                        pr = 0
                    else:
                        raise ValueError (f"Probability ({pf}) is not "
                                          "non-negative.")
                pr_sum += pr
                params_new.append (sqrt (pr) * pf)
            if isclose (pr_sum, 100., abs_tol = _EPS * 100.):
                params_new = list (v / 10. for v in params_new)
            elif not isclose (pr_sum, 1., abs_tol = _EPS):
                raise ValueError ("Sum of probabilities must be equal to 100 "
                                  "(%) or 1.")
            params = params_new
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
