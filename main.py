import pandas as pd
from itertools import product
import collections
import math
from qiskit.circuit.library import MCXGate

#step 1 2
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

output_variable_list = p[:]
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

#step 3
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


#step 4
input_values = [[int(k) for k in decimal_to_binary_string(i, t)] for i in range(2**t)]
l = len(input_variable_list)
for i in range(t - l):
	input_variable_list.insert(0, f'x{t - l - i - 1}')
# print(input_values)
output_values = new_output_values[:]
output_values = [new_output_values[i] + [0 for j in range(t - len(output_variable_list))] for i in range(len(new_output_values))]
# print(new_output_values)

# print(input_variable_list)

output_slots = [0 for i in range(2**t)]
for i in output_values:
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
print("\nTransform table:")
print(current_truth_table.to_string(index=False))

#step 5
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
print(cycles)

#step 6
new_cycles = []
power_list = [2**k for k in range(t)]
for cycle in cycles:
	new_cycle = []
	for j, k in enumerate(cycle):
		if j == len(cycle) -1 or k ^ cycle[j + 1] in power_list:
			new_cycle += [k]
			continue
		else:
			s = decimal_to_binary_string(k, t)
			s = list(s)
			diff = decimal_to_binary_string(k ^ cycle[j + 1], t)
			for m, i in enumerate(diff):
				if i == '1':
					new_cycle += [int("".join(s), 2)]
					if s[m] == '0':
						s[m] = '1'
					else:
						s[m] = '0'
	new_cycles += new_cycle
# print(new_cycles)

#step 7
gate = MCXGate(4, ctrl_state = '1000')

from qiskit import QuantumCircuit
circuit = QuantumCircuit(5)
circuit.append(gate, [0, 1, 2, 4, 3])
circuit.draw(output='mpl',filename='circuit.png')
print(circuit)