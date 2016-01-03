cdef extern from "math.h":
	double sqrt(double x)

cdef class vec:
	cdef public double x
	cdef public double y
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
	cpdef vec copy(self):
		return vec(self.x, self.y)
	
	cpdef vec set(self, double x, double y):
		self.x = x
		self.y = y
		return self
	
	cdef vec iadd(self, vec v):
		self.x += v.x
		self.y += v.y
		return self
	def __add__(vec self, vec v):
		return self.copy().iadd(v)
	def __iadd__(vec self, vec v):
		return self.iadd(v)
	
	cdef vec isub(self, vec v):
		self.x -= v.x
		self.y -= v.y
		return self
	def __sub__(vec self, vec v):
		return self.copy().isub(v)
	def __isub__(vec self, vec v):
		return self.isub(v)
	
	cdef vec imul(self, double s):
		self.x *= s
		self.y *= s
		return self
	def __mul__(vec self, double s):
		if not isinstance(self, vec):
			self, s = s, self
		return self.copy().imul(s)
	def __imul__(vec self, double s):
		if not isinstance(self, vec):
			self, s = s, self
		return self.imul(s)
	
	cdef vec idiv(self, double s):
		self.x /= s
		self.y /= s
		return self
	def __div__(vec self, double s):
		return self.copy().idiv(s)
	def __idiv__(vec self, double s):
		return self.idiv(s)
	
	cpdef double dot(self, vec v):
		return self.x*v.x + self.y*v.y
	
	cpdef double cross(self, vec v):
		return self.x*v.y - v.x*self.y
	
	cpdef double lensq(self):
		return self.dot(self)
	cpdef double len(self):
		return sqrt(self.lensq())
	
	cpdef vec unit(self):
		cdef double lensq = self.lensq()
		if lensq == 1:
			return self
		return self.copy().idiv(sqrt(lensq))
	cpdef vec iunit(self):
		cdef double lensq = self.lensq()
		if lensq == 1:
			return self
		return self.idiv(sqrt(lensq))
	
	cpdef vec iperp(self):
		self.x, self.y = -self.y, self.x
		return self
	cpdef vec perp(self):
		return self.copy().iperp()
	
	cpdef double proj(self, vec v):
		return self.dot(v.unit())
	cpdef vec proj_vec(self, vec v):
		u = v.unit()
		return u.imul(self.dot(u))
	
	cpdef vec ineg(self):
		return self.imul(-1)
	def __neg__(self):
		return self.neg()
	cpdef vec neg(self):
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

cdef class Circle:
	cdef public vec pos
	cdef readonly double rad
	cdef readonly double radsq
	def __init__(self, vec pos, double rad, double radsq=-1):
		self.pos = pos
		self.rad = rad
		if radsq == -1:
			self.radsq = rad*rad
		else:
			self.radsq = radsq

cdef class Segment:
	cdef public vec a
	cdef public vec b
	def __init__(self, vec a, vec b):
		self.a = a
		self.b = b

cdef class Capsule:
	cdef public vec a
	cdef public vec b
	cdef readonly double rad
	cdef readonly double radsq
	def __init__(self, vec a, vec b, double rad, double radsq=-1):
		self.a = a
		self.b = b
		self.rad = rad
		if radsq == -1:
			self.radsq = rad*rad
		else:
			self.radsq = radsq

cpdef vec closest_point_on_seg(Segment seg, vec pt):
	cdef vec seg_v = seg.b - seg.a
	cdef vec pt_v = pt - seg.a
	cdef double seg_lensq = seg_v.lensq()
	
	if seg_lensq <= 0:
		raise ValueError, "Segment length is less than or equal to zero"
	
	cdef vec seg_v_unit
	cdef double seg_len
	if seg_lensq != 1:
		seg_len = sqrt(seg_lensq)
		seg_v_unit = seg_v.copy().idiv(seg_len)
	else:
		seg_len = 1
		seg_v_unit = seg_v
	
	cdef double proj = pt_v.dot(seg_v_unit)
	if proj <= 0:
		return seg.a.copy()
	if proj >= seg_len:
		return seg.b.copy()
	
	return seg_v_unit.imul(proj).iadd(seg.a)

cpdef vec segment_circle(Segment seg, Circle circ):
	cdef vec dist_v = closest_point_on_seg(seg, circ.pos).ineg().iadd(circ.pos)
	cdef double distsq = dist_v.lensq()
	
	if distsq >= circ.radsq:
		return dist_v.set(0, 0)
	if distsq <= 0:
		return dist_v.set(0, 0)
	
	cdef double dist = sqrt(distsq)
	cdef double overlap = circ.rad - dist
	return dist_v.idiv(dist).imul(overlap)
	
cpdef vec capsule_point(Capsule cap, vec pt):
	cdef Segment seg = Segment(cap.a, cap.b)
	cdef Circle circ = Circle(pt, cap.rad, cap.radsq)
	return segment_circle(seg, circ)

cpdef vec capsule_circle(Capsule cap, Circle circ):
	cdef Segment seg = Segment(cap.a, cap.b)
	cdef Circle circ2 = Circle(circ.pos, cap.rad+circ.rad)
	return segment_circle(seg, circ2)
