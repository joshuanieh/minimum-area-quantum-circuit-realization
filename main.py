import pandas as pd
from itertools import product
import collections
import math
from qiskit.circuit.library import MCXGate
from qiskit import QuantumCircuit
from qiskit.circuit import QuantumRegister, ClassicalRegister
#step 1 2: Construct original truth table plus the preservation bits
clasical_boolean_logic = []
inputs = ''
print("Please enter your clasical boolean logics, q to return: (ex, s (output) = ab' + a'b (input))")
while True:
	inputs = input("")
	if inputs == "q":
		break
	if inputs == "":
		continue
	clasical_boolean_logic += [inputs]
print("Please enter the variables you want to preserve, press enter if no bits to be preserved: (ex, a, b)")
p = input("").split(", ")
if p == ['']:
	p = []
output_variable_list = []
for i in p:
	output_variable_list.append(f'o_{i}')
input_variable_list = []
function_string = ["" for i in range(len(clasical_boolean_logic))]
for i, logic in enumerate(clasical_boolean_logic):
	left_braket_pos = 0
	function_string[i] = "("
	prev = ""
	outputs, inputs = logic.split("=")
	output_variable_list += [outputs]
	for alphabet in inputs:
		if alphabet == "(":
			if prev == ")" or prev.isalpha() or prev == "\'":
				function_string[i] += " and "
			function_string[i] += alphabet
			left_braket_pos = len(function_string[i]) - 1
		elif alphabet.isalpha():
			if prev == ")" or prev.isalpha() or prev == "\'":
				function_string[i] += " and "
			if alphabet not in input_variable_list:
				input_variable_list += [alphabet]
			function_string[i] += "arg[\'" + alphabet + "\']"
		elif alphabet == ")":
			function_string[i] += alphabet
		elif alphabet == "+":
			function_string[i] += ") or ("
		elif alphabet == '\'':
			if function_string[i][-1] == ")":
				function_string[i] = function_string[i][:left_braket_pos] + "not " + function_string[i][left_braket_pos:]
			else:
				function_string[i] = function_string[i][:-8] + "not " + function_string[i][-8:]
		else:
			pass

		prev = alphabet
	function_string[i] += ")"
	# print(function_string[i])

def evaluation(arg, function_string):
	return eval(function_string)

# print(output_variable_list)
# print(input_variable_list)
values = [[int(i) for i in x] + [" "] + [" "] + [int(x[input_variable_list.index(variable)]) for variable in p] + [int(evaluation(dict([(input_variable_list[i], x[i]) for i in range(len(input_variable_list))]), func)) for func in function_string] for x in product([False, True], repeat=len(input_variable_list))]
# print(values)
current_truth_table = pd.DataFrame(values,columns=(input_variable_list + [" "] + [" "] + output_variable_list))
print("\nClassical truth table:")
print(current_truth_table.to_string(index=False))

#step 3: Eliminate duplicate output
output_values = [tuple([int(x[input_variable_list.index(variable)]) for variable in p] + [int(evaluation(dict([(input_variable_list[i], x[i]) for i in range(len(input_variable_list))]), func)) for func in function_string]) for x in product([False, True], repeat=len(input_variable_list))]
item_count_dictionary = dict([(item, count) for item, count in collections.Counter(output_values).items() if count > 1])
z = max([count for item, count in collections.Counter(output_values).items()])
z = int(math.ceil(math.log(z, 2)))

def decimal_to_binary_string(decimal, z):
	binary = ""
	while decimal:
		if (decimal & 1):
			binary += "1"
		else:
			binary += "0"
		decimal >>= 1
	binary += "".join(['0' for i in range(z - len(binary))])
	return binary[::-1]

d = []
if z > 0:
	for i in output_values:
		if i in item_count_dictionary.keys():
			d.append([int(k) for k in decimal_to_binary_string(item_count_dictionary[i] - 1, z)])
			item_count_dictionary[i] -= 1
		else:
			d.append([0 for k in range(z)])
	values = [[int(i) for i in x] + [" "] + [" "] + list(output_values[j]) + d[j] for j, x in enumerate(product([False, True], repeat=len(input_variable_list)))]
output_variable_list += [f'd{i}' for i in range(z)]

# current_truth_table = pd.DataFrame(values,columns=(input_variable_list + [" "] + [" "] + output_variable_list))
# print("\nTruth table:")
# print(current_truth_table.to_string(index=False))
t = max(len(input_variable_list), len(output_variable_list))
new_output_values = [[] for i in range(len(values))]
if d != []:
	for i in range(len(values)):
		new_output_values[i] = list(output_values[i]) + d[i]
else:
	for i in range(len(values)):
		new_output_values[i] = list(output_values[i])
# print("n: ", new_output_values)

#step 4: Pad some bits in ouput or input to t and construct the whole transformation table
input_values = [[int(k) for k in decimal_to_binary_string(i, t)] for i in range(2**t)]
l = len(input_variable_list)
for i in range(t - l):
	input_variable_list.insert(0, f'x{t - l - i - 1}')
# print(input_values)
output_values = new_output_values[:]
output_values = [new_output_values[i] + [0 for j in range(t - len(output_variable_list))] for i in range(len(new_output_values))]
# print(output_values)

# print(input_variable_list)

output_slots = [0 for i in range(2**t)]
for i in output_values:
	# print(i)
	output_slots[int("".join([f'{j}' for j in i]), 2)] = 1
# print(output_slots)
# print(output_values)
current_pos = 0
while len(output_values) < 2**t:
	while output_slots[current_pos] == 1:
		# print(current_pos)
		current_pos += 1
	# print("---")
	output_values += [[int(i) for i in decimal_to_binary_string(current_pos, t)]]
	output_slots[current_pos] = 1

# print(output_values) 
values = [input_values[i] + [" "] + [" "] + output_values[i] for i in range(2**t)]
# print(values)
current_truth_table = pd.DataFrame(values,columns=(input_variable_list + [" "] + [" "] + output_variable_list))
print("\nTransformation table:")
print(current_truth_table.to_string(index=False))

#step 5: Permutation and cycle
permutation = dict([(int("".join([f'{j}' for j in input_values[i]]), 2), int("".join([f'{j}' for j in output_values[i]]), 2)) for i in range(2**t)])
print(permutation)
cycles = []
for i in range(2**t):
	l = []
	k = i
	while k in permutation.keys():
		# print(k)
		l += [k]
		k = permutation.pop(k)
	if len(l) >= 2:
		cycles.append(l)
new_cycles = []
for cycle in cycles:
	new_cycle = []
	for i, j in enumerate(cycle):
		if i == len(cycle) - 1:
			break
		new_cycles.append((j, cycle[i + 1]))
	# new_cycles.append(new_cycle)
print(new_cycles)

#step 6: T(S, R, I) gate
cycles = new_cycles
new_cycles = []
print(cycles)
power_list = [2**k for k in range(t)]
for cycle in cycles:
	print(cycle)
	j = cycle[0]
	k = cycle[1]
	if k ^ j in power_list:
		new_cycles += [(j, k)]
		continue
	else:
		tmp_cycles = []
		s = decimal_to_binary_string(j, t)
		s = list(s)
		diff = decimal_to_binary_string(k ^ j, t)
		for m, i in enumerate(diff):
			if i == '1':
				if s[m] == '0':
					s[m] = '1'
				else:
					s[m] = '0'
				tmp_cycles += [(j, int("".join(s), 2))]
				new_cycles += [(j, int("".join(s), 2))]
				j = int("".join(s), 2)
		new_cycles += tmp_cycles[-2::-1]
print(new_cycles)

#step 7: Draw
input_registers = []
for i in range(t):
	input_registers.append(QuantumRegister(1, name=input_variable_list[t - i - 1]))
output_registers = []
for i in range(t):
	output_registers.append(ClassicalRegister(1, name=output_variable_list[t - i - 1]))
circuit = QuantumCircuit(*input_registers, *output_registers)
for cycle in new_cycles[::-1]:
	n = cycle[0]
	j = cycle[1]
	current_state_binary = decimal_to_binary_string(n, t)
	diff = n ^ j
	diff_binary = decimal_to_binary_string(diff, t)
	ctrl_state = ""
	# print(diff_binary)
	for k, i in enumerate(diff_binary):
		if i == '0':
			ctrl_state += current_state_binary[k]
		else:
			X_pos = t - k - 1
	# print(ctrl_state)
	gate = MCXGate(t - 1, ctrl_state = ctrl_state)
	# print([m for m in range(t) if m != X_pos], [X_pos])
	circuit.append(gate, [m for m in range(t) if m != X_pos] + [X_pos])
for i in range(t):
	circuit.measure(input_registers[i], output_registers[i])
circuit.draw(output='mpl',filename='circuit.png')
print(circuit)