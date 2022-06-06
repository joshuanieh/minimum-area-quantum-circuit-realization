from qiskit.circuit.library import MCXGate
gate = MCXGate(4, ctrl_state = '1000')

from qiskit import QuantumCircuit
circuit = QuantumCircuit(5)
circuit.append(gate, [0, 1, 2, 4, 3])
circuit.draw(output='mpl',filename='circuit.png')
print(circuit)