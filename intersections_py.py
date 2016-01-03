from math import sqrt

class vec:
	def __init__(self, x, y=None):
		if y is not None:
			self.x = x
			self.y = y
		else:
			try:
				self.x = x.x
				self.y = x.y
			except AttributeError:
				try:
					self.x = x[0]
					self.y = x[1]
				except TypeError:
					raise TypeError, "Invalid parameters"
	def copy(self):
		return vec(self.x, self.y)
	
	def set(self, x, y):
		self.x = x
		self.y = y
		return self
	
	def iadd(self, v):
		self.x += v.x
		self.y += v.y
		return self
	def __add__(self, v):
		return self.copy().iadd(v)
	def __iadd__(self, v):
		return self.iadd(v)
	
	def isub(self, v):
		self.x -= v.x
		self.y -= v.y
		return self
	def __sub__(self, v):
		return self.copy().isub(v)
	def __isub__(self, v):
		return self.isub(v)
	
	def imul(self, s):
		self.x *= s
		self.y *= s
		return self
	def __mul__(self, s):
		if not isinstance(self, vec):
			self, s = s, self
		return self.copy().imul(s)
	def __imul__(self, s):
		if not isinstance(self, vec):
			self, s = s, self
		return self.imul(s)
	
	def idiv(self, s):
		self.x /= s
		self.y /= s
		return self
	def __div__(self, s):
		return self.copy().idiv(s)
	def __idiv__(self, s):
		return self.idiv(s)
	
	def dot(self, v):
		return self.x*v.x + self.y*v.y
	
	def cross(self, v):
		return self.x*v.y - v.x*self.y
	
	def lensq(self):
		return self.dot(self)
	def len(self):
		return sqrt(self.lensq())
	
	def unit(self):
		lensq = self.lensq()
		if lensq == 1:
			return self
		return self.copy().idiv(sqrt(lensq))
	def iunit(self):
		lensq = self.lensq()
		if lensq == 1:
			return self
		return self.idiv(sqrt(lensq))
	
	def iperp(self):
		self.x, self.y = -self.y, self.x
		return self
	def perp(self):
		return self.copy().iperp()
	
	def proj(self, v):
		return self.dot(v.unit())
	def proj_vec(self, v):
		u = v.unit()
		return u.imul(self.dot(u))
	
	def ineg(self):
		return self.imul(-1)
	def __neg__(self):
		return self.neg()
	def neg(self):
		return self.copy().ineg()
	
	def __nonzero__(self):
		if self.x or self.y:
			return True
		return False
	
	def __len__(self):
		return 2
	def __getitem__(self, key):
		if key == 0 or key == "x":
			return self.x
		if key == 1 or key == "y":
			return self.y
		raise IndexError
	def __setitem__(self, key, value):
		if key == 0 or key == "x":
			self.x = value
		if key == 1 or key == "y":
			self.y = value
		raise IndexError
	
	def __str__(self):
		return "vec(%.3f,%.3f)"%tuple(self)

class Circle:
	def __init__(self, pos, rad, radsq=-1):
		self.pos = pos
		self.rad = rad
		if radsq == -1:
			self.radsq = rad*rad
		else:
			self.radsq = radsq

class Segment:
	def __init__(self, a, b):
		self.a = a
		self.b = b

class Capsule:
	def __init__(self, a, b, rad, radsq=-1):
		self.a = a
		self.b = b
		self.rad = rad
		if radsq == -1:
			self.radsq = rad*rad
		else:
			self.radsq = radsq

def closest_point_on_seg(seg, pt):
	seg_v = seg.b - seg.a
	pt_v = pt - seg.a
	seg_lensq = seg_v.lensq()
	
	if seg_lensq <= 0:
		raise ValueError, "Segment length is less than or equal to zero"
	
	if seg_lensq != 1:
		seg_len = sqrt(seg_lensq)
		seg_v_unit = seg_v.copy().idiv(seg_len)
	else:
		seg_len = 1
		seg_v_unit = seg_v
	
	proj = pt_v.dot(seg_v_unit)
	if proj <= 0:
		return seg.a.copy()
	if proj >= seg_len:
		return seg.b.copy()
	
	return seg_v_unit.imul(proj).iadd(seg.a)

def segment_circle(seg, circ):
	dist_v = closest_point_on_seg(seg, circ.pos).ineg().iadd(circ.pos)
	distsq = dist_v.lensq()
	
	if distsq >= circ.radsq:
		return dist_v.set(0, 0)
	if distsq <= 0:
		return dist_v.set(0, 0)
	
	dist = sqrt(distsq)
	overlap = circ.rad - dist
	return dist_v.idiv(dist).imul(overlap)
	
def capsule_point(cap, pt):
	seg = Segment(cap.a, cap.b)
	circ = Circle(pt, cap.rad, cap.radsq)
	return segment_circle(seg, circ)

def capsule_circle(cap, circ):
	seg = Segment(cap.a, cap.b)
	circ2 = Circle(circ.pos, cap.rad+circ.rad)
	return segment_circle(seg, circ2)
