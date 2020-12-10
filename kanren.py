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
class Neq:
	def __init__(self, a, b):
		self.vars = a, b
	def __repr__(self):
		return "Neq(%s, %s)" % self.vars
	def check(self, e):
		a, b = map(e.get, self.vars)
		return a != b
class TEq:
	def __init__(self, a, b):
		self.vars = a, b
	def __repr__(self):
		return "TEq(%s, %s)" % self.vars
	def check(self, e):
		a, b = map(e.get, self.vars)
		return isinstance(a, (b, Var))
class Var:
	def __init__(self, name):
		self.name = name
	def __repr__(self):
		return self.name
class Env:
	def __init__(self, vars=[], vals={}, conds=ddict(set)):
		self.vars = vars
		self.vals = vals
		self.conds = conds
	def get(self, var):
		#print var, id(var)
		if var in self.vals: return self.get(self.vals[var])
		if isinstance(var, tuple): return tuple(map(self.get, var))
		return var
	def set(self, var, val):
		var = self.get(var)
		vals = self.vals.copy()
		conds = self.conds.copy()
		vals[var] = val
		conds[var] = conds[var] | conds[val]
		self = Env(self.vars, vals, conds)
		if all(cond.check(self) for cond in self.conds[var]):
			return self
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
		return vars, Env(self.vars + vars, self.vals, self.conds)
	def cond(self, cond):
		if not cond.check(self):
			return None
		conds = self.conds.copy()
		for var in cond.vars:
			if isinstance(var, Var):
				conds[var] = conds[var] | {cond}
		return Env(self.vars, self.vals, conds)
reify = lambda r: iter([r]) if r else iter([])
fresh = lambda f: lambda e: (lambda(vars, e2): f(*vars)(e2))(e.fresh(args(f)))
or2 = lambda a, b: lambda e: combine(iter([a(e), b(e)]))
and2 = lambda a, b: lambda e: combine(b(e2) for e2 in a(e))
eq = lambda a, b: lambda e: reify(e.unify(a, b))
neq = lambda a, b: lambda e: reify(e.cond(Neq(a, b)))
eqt = lambda a, b: lambda e: reify(e.cond(TEq(a, b)))
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
goal = fresh(lambda a, b: and2(neq(a, b), append(a, b, ('a', ('b', ('a', ('b', ())))))))
for e in goal(Env()):
	print e.get(e.vars[0]), e.get(e.vars[1])
