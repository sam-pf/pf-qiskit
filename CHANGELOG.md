# 0.1.3
> qiskit.patch of QuantumCircuit.initialize updated (tuple notation)

1. qiskit.WiringInstruction.prepare processes qubits first and then, only for
   unwired qubits, qregs
1. qiskit.patch updates the patch for QuantumCircuit.initialize: tuple
   notation for probability notation and no 'unit' argument

# 0.1.2
> wire,patch (of QuantumCircuit.initialize) added to physicsfront.qiskit

1. QuantumCircuit.initialize is patched to accept tuple (probability sequence
   with optional probability amplitude phase factors).
1. New classe and functions for physicsfront.qiskit:
   - WiringInstruction
   - wire
   - jobs
   - backends
   - get_provider
1. Functions removed from physicsfront.qiskit:
   - qc_entangled_two_qubits
   - qc_for_random_bits
1. Function run_quantum accepts a new parameter qasm3: WIP since IBM qiskit
   dynamic circuit examples do not seem to work...

# 0.1.1
> physicsfront.qiskit.colab.init improved

1. Changed to native namespace (physicsfront) package scheme.
1. physicsfront.qiskit.colab is made 'idempotent', and accepts filenames.
1. physicsfront.qiskit.run_quantum accepts string value for backend, as well
   as an instance value or None.

# 0.1.0
> init release; physicsfront.qiskit, physicsfront.qiskit.colap
