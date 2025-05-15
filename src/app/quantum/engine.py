from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

def run_simple_circuit():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)

    backend = Aer.get_backend("qasm_simulator")
    transpiled = transpile(qc, backend)

    result = backend.run(transpiled).result()
    return result.get_counts()
