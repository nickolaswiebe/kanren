def vars_of(func):
	return func.func_code.co_varnames[:func.func_code.co_argcount]

class Variable:
	def __init__(self, name):
		self.name = name
	def __repr__(self):
		return "Variable('%s')" % self.name

class State:
	def __init__(self, variables=None, values=None):
		self.variables = variables or []
		self.values = values or {}
	def create_variables(self, names):
		new_variables = [Variable(name) for name in names]
		st = State(self.variables + new_variables, self.values)
		return st, new_variables
	def assign_values(self, new_values):
		v = self.values.copy()
		v.update(new_values)
		return State(self.variables, v)
	def value_of(self, key):
		if key in self.values:
			return self.value_of(self.values[key])
		else:
			return key
	def unify(self, a, b):
		a = self.value_of(a)
		b = self.value_of(b)
		if a == b:
			return self
		elif isinstance(a, Variable):
			return self.assign_values({a: b})
		elif isinstance(b, Variable):
			return self.assign_values({b: a})
		elif isinstance(a, Pair) and isinstance(b, Pair):
			state = self.unify(a.left, b.left)
			if state:
				return state.unify(a.right, b.right)
	def value_of(self, key):
		if key in self.values:
			return self.value_of(self.values[key])
		elif isinstance(key, Pair):
			return Pair(
				self.value_of(key.left),
				self.value_of(key.right))
		else:
			return key

class Goal:
	def __init__(self, block):
		self.block = block
	def pursue_in(self, state):
		return self.block(state)
	def pursue_in_each(self, states):
		first = next(states)
		remaining = states
		first_stream = self.pursue_in(first)
		remaining_streams = self.pursue_in_each(remaining)
		for state in interleave_with(first_stream, remaining_streams):
			yield state

def Goal_equal(a, b):
	def do(state):
		state = state.unify(a, b)
		if state:
			yield state
	return Goal(do)

def Goal_with_variables(block):
	names = vars_of(block)
	def do(state):
		state, variables = state.create_variables(names)
		goal = block(*variables)
		return goal.pursue_in(state)
	return Goal(do)

def Goal_either(first_goal, second_goal):
	def do(state):
		for x in first_goal.pursue_in(state):
			yield x
		for x in second_goal.pursue_in(state):
			yield x
	return Goal(do)

def interleave_with(*enumerators):
	enumerators = list(enumerators)
	while enumerators != []:
		enumerator = enumerators.pop(0)
		yield next(enumerator)
		enumerators.append(enumerator)

def Goal_both(first_goal, second_goal):
	def do(state):
		for state in first_goal.pursue_in(state):
			for x in second_goal.pursue_in(state):
				yield x
	return Goal(do)

class Pair:
	def __init__(self, left, right):
		self.left = left
		self.right = right
	def __repr__(self):
		return "(%s, %s)" % (self.left, self.right)

goal = Goal_with_variables(lambda x, y, z:
	Goal_both(
		Goal_either(Goal_equal(x, 0), Goal_equal(x, 1)),
		Goal_both(
			Goal_either(Goal_equal(y, 0), Goal_equal(y, 1)),
			Goal_either(Goal_equal(z, 0), Goal_equal(z, 1)) )))
for state in goal.pursue_in(State()):
	print state.value_of(state.variables[0]), state.value_of(state.variables[1]), state.value_of(state.variables[2])
