from collections import defaultdict as ddict
args = lambda f: f.func_code.co_varnames[:f.func_code.co_argcount]
def combine(xss):
	run = [next(xss)]
	while run != []:
		for _ in xrange(len(run)):
			xs = run.pop(0)
			try:
				x = next(xs)
				yield x
				run.append(xs)
			except StopIteration:
				pass
		try:
			run.append(next(xss))
		except StopIteration:
			pass
class Var:
	def __init__(self, name):
		self.name = name
	def __repr__(self):
		return self.name
class Env:
	def __init__(self, vars=[], vals={}):
		self.vars = vars
		self.vals = vals
	def get(self, var):
		if var in self.vals: return self.get(self.vals[var])
		if isinstance(var, tuple): return tuple(map(self.get, var))
		return var
	def set(self, var, val):
		var = self.get(var)
		vals = self.vals.copy()
		vals[var] = val
		return Env(self.vars, vals)
	def unify(self, a, b):
		a = self.get(a)
		b = self.get(b)
		if a == b: return self
		if isinstance(a, Var): return self.set(a, b)
		if isinstance(b, Var): return self.set(b, a)
		if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
			for x, y in zip(a, b):
				self = self.unify(x, y)
				if self is None: return None
			return self
		return None
	def fresh(self, names):
		vars = map(Var, names)
		return vars, Env(self.vars + vars, self.vals)
reify = lambda r: iter([r]) if r else iter([])
fresh = lambda f: lambda e: (lambda(vars, e2): f(*vars)(e2))(e.fresh(args(f)))
or2 = lambda a, b: lambda e: combine(iter([a(e), b(e)]))
and2 = lambda a, b: lambda e: combine(b(e2) for e2 in a(e))
eq = lambda a, b: lambda e: reify(e.unify(a, b))
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
goal = fresh(lambda a, b: append(a, b, ('a', ('b', ('c', ())))))
for e in goal(Env()):
	print e.get(e.vars[0]), e.get(e.vars[1])
