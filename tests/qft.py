# pylint: disable=E0401

def _test_suite (): # <<<
    from pf6.defs import UNITTEST_ASSERT_SHORTCUTS_DICT
    import unittest

    class Test_QFT_factory (unittest.TestCase): # <<< pylint: disable=W0641

        def test__inverse__ (self): # <<<
            a_ = UNITTEST_ASSERT_SHORTCUTS_DICT (self)
            from physicsfront.qiskit.qft import get_qft
            from qiskit import (BasicAer, execute, QuantumCircuit,
                                ClassicalRegister, QuantumRegister)
            from random import randint
            def random_x (qc, n): # <<<
                from random import random
                random_bits = []
                for i in range (n):
                    if random () > 0.5:
                        random_bits.append ('1')
                        qc.x (i)
                    else:
                        random_bits.append ('0')
                return ''.join (reversed (random_bits))
            # >>>
            def qft_demo_qc_0 (n, ** dargs): # <<< plain types
                q = QuantumRegister (n, 'q')
                qc = QuantumCircuit (q)
                input_in_creg_format = random_x (qc, n)
                #print ("input in creg format = %r" % (input_in_creg_format,))
                qft = get_qft (** dargs)
                assert '_m_' not in qft.__name__
                iqft = qft.__inverse__
                qft (qc, n)
                qc.barrier ()
                iqft (qc, n)
                qc.measure_all ()
                qc.__input_in_creg_format__ = input_in_creg_format
                return qc
            # >>>
            def qft_demo_qc_1 (n, ** dargs): # <<< _mf_ kind with _m_ inverse
                q = QuantumRegister (n, 'q')
                c = ClassicalRegister (n, 'c')
                qc = QuantumCircuit (q, c)
                input_in_creg_format = random_x (qc, n)
                #print ("input in creg format = %r" % (input_in_creg_format,))
                qft = get_qft (** dargs)
                assert '_mf_' in qft.__name__
                iqft = qft.__inverse__.__other_mf__.__example__
                qft (qc, n)
                qc.barrier ()
                iqft (qc, c, n)
                qc.__input_in_creg_format__ = input_in_creg_format
                return qc
            # >>>
            n = randint (3, 5)
            qcs = []
            for inverse in (False, True):
                for mf in (True, False):
                    for output_endian in ('auto', 'opposite'):
                        qcs.append (qft_demo_qc_0 (
                            n, inverse = inverse, mf = mf,
                            output_endian = output_endian))
            ##
            # This one takes much longer than the plain one, when run
            # through the simulator.  Why?
            #
            # Anyway, the total time for this method can be close to 10 s if
            # n is 6 or 7.
            ##
            for inverse in (False, True):
                for mf in (True,):
                    for output_endian in ('auto', 'opposite'):
                        qcs.append (qft_demo_qc_1 (
                            n, inverse = inverse, mf = mf,
                            output_endian = output_endian))
            # To run through this simulator backend, no account needed.
            sim_backend = BasicAer.get_backend ("qasm_simulator")
            job = execute (qcs, sim_backend, shots = 1024)
            result = job.result ()
            for qc in qcs:
                counts = result.get_counts (qc)
                #print (repr (qc.__input_in_creg_format__), counts)
                a_.eq ([qc.__input_in_creg_format__], list (counts))
        # >>>
        def test__names_and_connections (self): # <<<
            a_ = UNITTEST_ASSERT_SHORTCUTS_DICT (self)
            from physicsfront.qiskit.qft import define_qft_functions
            m = {}
            t = define_qft_functions (m, mfs = [True, False, 'measure'],
                                      output_endians = ['auto', 'opposite'],
                                      include_examples = True)
            a, b, c = t
            a_.tr (not b and not c)
            # 16: maximum possible number (get_qft cache won't grow beyond it)
            a_.eq (len (a), 16)
            for name in a:
                f = m [name]
                assert name == f.__name__
                #print ('== name:', name)
                if name.endswith ('_example'):
                    continue
                oppe_name = name
                if oppe_name.endswith ('_beo'):
                    oppe_name = oppe_name [:-3] + 'leo'
                else:
                    a_.tr (oppe_name.endswith ('_leo'))
                    oppe_name = oppe_name [:-3] + 'beo'
                a_._is (f.__opposite_endian__, m [oppe_name])
                otherm_name = None
                oppm_name = name
                if '_m_' in oppm_name or '_mf_' in oppm_name:
                    if '_m_' in oppm_name:
                        otherm_name = oppm_name.replace ('_m_', '_mf_')
                    else:
                        otherm_name = oppm_name.replace ('_mf_', '_m_')
                    oppm_name = oppm_name.replace ('_mf_', '_')
                    oppm_name = oppm_name.replace ('_m_', '_')

                else:
                    words = oppm_name.split ('_')
                    words.insert (1, 'mf')
                    oppm_name = '_'.join (words)
                a_._is (f.__opposite_mf__, m [oppm_name])
                if otherm_name:
                    a_._is (f.__other_mf__, m [otherm_name])
                inv_name = oppe_name
                if inv_name.startswith ('qft_'):
                    inv_name = 'i' + inv_name
                else:
                    a_.tr (inv_name.startswith ('iqft_'))
                    inv_name = inv_name [1:]
                a_._is (f.__inverse__, m [inv_name])
                if '_m_' not in oppe_name:
                    continue
                example_name = '_' + name + '_example'
                a_._is (f.__example__, m [example_name])
                #print ('-' * len (f.__src__.split ('\n')[0]))
                #print (f.__src__)
        # >>>

    # >>>

    suite = unittest.TestSuite ()
    for name in list (locals ()):
        if name.startswith ('Test_'):
            cls = eval (name)
            if issubclass (cls, unittest.TestCase):
                suite.addTests (unittest.TestLoader ()
                        .loadTestsFromTestCase (cls))
    r = unittest.TextTestRunner (verbosity = 2).run (suite)
    return len (r.errors) + len (r.failures)

# >>>
if __name__ == '__main__': # <<<
    with __import__ ('pf6.CG').CG.CurrentScriptPathIncluded (relpath = '..'):
        __import__ ('sys').exit (_test_suite ())
# >>>
