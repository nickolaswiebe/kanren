class Var:
	def __init__(self, num):
		self.num = num
	def __eq__(self, other):
		return isinstance(other, Var) and self.num == other.num
	def __repr__(self):
		return "V%i" % self.num
class Ref:
	def __init__(self, num):
		self.num = num
class State:
	def __init__(self, nvars=0, vals=[]):
		self.nvars = nvars
		self.vals = vals
	def get(self, var):
		#print var
		if isinstance(var, Var):
			if self.vals[var.num] is None:
				return var
			return self.get(self.vals[var.num])
		if isinstance(var, tuple):
			return tuple(map(self.get, var))
		return var
	def set(self, k, v):
		vals = self.vals[:]
		vals[k] = v
		return State(self.nvars, vals)
	def unify(self, a, b):
		a = self.get(a)
		b = self.get(b)
		if a == b:
			return self
		if isinstance(a, Var):
			return self.set(a.num, b)
		if isinstance(b, Var):
			return self.set(b.num, a)
		if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
			st = self.unify(a[0], b[0])
			if st is None: return None
			return st.unify(a[1:], b[1:])
		return None
def fresh(f):
	n = f.func_code.co_argcount
	def goal(st):
		return f(*[Var(i + st.nvars) for i in xrange(n)])(State(st.nvars + n, st.vals + [None] * n))
	return goal
def eq(a, b):
	def goal(st):
		r = st.unify(a, b)
		if r is not None:
			yield r
	return goal
def combine(xss):
	for xs in xss:
		for x in xs:
			yield x
def or2(a, b):
	def goal(st):
		return combine(iter([a(st), b(st)]))
	return goal
def and2(a, b):
	def goal(st):
		return combine(b(st2) for st2 in a(st))
	return goal
goal = fresh(lambda x, y, z:
	and2(
		or2(eq(x, 0), eq(x, 1)),
		and2(
			or2(eq(y, 0), eq(y, 1)),
			or2(eq(z, 0), eq(z, 1)) )))
def append(a, b, c):
	return or2(
		and2(
			eq(a, ()),
			eq(b, c)
		),
		fresh(lambda first, rest_of_a, rest_of_c:
			and2(
				and2(
					eq(a, (first, rest_of_a)),
					eq(c, (first, rest_of_c))
				),
				append(rest_of_a, b, rest_of_c)
			)
		)
	)
goal = fresh(lambda a, b: append(a, b, ('h', ('e', ('l', ('l', ('o', ())))))))
for st in goal(State()):
	print st.get(Var(0)), st.get(Var(1))
