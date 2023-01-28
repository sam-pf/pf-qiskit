def _initialize (): # <<<
    import qiskit
    from math import isclose, sqrt
    from numpy import abs # pylint: disable=W0622
    # pylint: disable=E0401,E0611
    from qiskit.circuit.library.data_preparation import state_preparation
    # pylint: enable=E0401,E0611
    _EPS = state_preparation._EPS
    _initialize_orig = qiskit.QuantumCircuit.initialize # pylint: disable=E1101
    docstr = """
A patched version of :meth:`qiskit.QuantumCircuit.initialize` so
that ``params`` accepts a new type of value, a tuple.

    When ``params`` is a tuple, it is taken as a probability sequence
    (rather than a probability amplitude sequence, if ``params`` is a
     list).

    The probabilities may be given in unit of % or in no unit.  However,
    there is no need or way to specify the unit explicitly.

    The values of probabilities should sum up to 100 or 1.  If the sum is
    100, then the unit of probabilities is taken as %, and if the sum is
    1, then there is no unit.

    Any element of a tuple ``params`` can tiself be a tuple, in which
    case it must be a 2-tuple, consisting of a probability and a
    "probability amplitude phase factor," a (real or complex) number
    whose magnitude must be 1.

    For instance, all the following are valid inputs for ``params``.

            ``(100, 0)``
            ``(1, 0)``
            ``((100, -1), 0)``
            ``((50, 1j), (50, -1))``
            ``((0.5, 1j), (0.5, -1))``
            ``((70, np.exp(2j)), (30, -1j))``

    In the last expression, ``import numpy as np`` is assumed to have
    been executed already.

    When going from the probability to the probability amplitude, the
    probability will be squarer-rooted, and then the probability
    amplitude phase factor will be multiplied to it.

    Therefore, the probabiliy specification of ``params`` is as powerful
    as the probabiliy amplitude specification in terms of its
    expressiveness.
    """.strip ()
    if _initialize_orig.__doc__:
        docstr += """

--- The documentation for the unpatched version of this method follows. ---

""" + _initialize_orig.__doc__
    def initialize (self, params, qubits = None): # <<<
        if isinstance (params, tuple):
            params_new = []
            pr_sum = 0.
            for v in params:
                if isinstance (v, tuple):
                    pr, pf = v
                    if not isclose (abs (pf), 1., abs_tol = _EPS):
                        raise ValueError (f"Phase factor ({pf}) is not of "
                                          "unit magnitude.")
                else:
                    pr = v
                    pf = 1
                if pr < 0:
                    if isclose (pr, 1., abs_tol = _EPS):
                        pr = 0
                    else:
                        raise ValueError (f"Probability ({pf}) is not "
                                          "non-negative.")
                pr_sum += pr
                params_new.append (sqrt (pr) * pf)
            if isclose (pr_sum, 1., abs_tol = _EPS):
                pass
            elif isclose (pr_sum, 100., abs_tol = _EPS * 100):
                params_new = list (v / 10. for v in params_new)
            else:
                raise ValueError ("Sum of probabilities is not equal to 1 "
                                  "or 100 (%).")
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
