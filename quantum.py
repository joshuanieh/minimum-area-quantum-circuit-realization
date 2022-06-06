from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from math import pi
qc = QuantumCircuit(2)
c = 0
t = 1
# also a controlled-Z
qc.h(t)
qc.cx(c,t)
qc.h(t)
qc.draw(output='mpl',filename='circuit.png')
print(qc)