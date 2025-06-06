from typing import BinaryIO, Callable, TypeVar, TypeAlias, overload
import struct
import os
import io
import math

# syntactic sugar
uint: TypeAlias = int




# unreal parsing utils
def read_magic(f: BinaryIO, magic: bytes):
	assert(f.read(len(magic)) == magic)

def read_u8(f: BinaryIO) -> uint:
	return f.read(1)[0]
def read_u16(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(2), 'little', signed=False)
def read_u24(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(3), 'little', signed=False)
def read_u32(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(4), 'little', signed=False)
def read_u40(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(5), 'little', signed=False)
def read_u48(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(6), 'little', signed=False)
def read_u64(f: BinaryIO) -> uint:
	return int.from_bytes(f.read(8), 'little', signed=False)

def read_s8(f: BinaryIO) -> int:
	return int.from_bytes(f.read(1), 'little', signed=True)
def read_s16(f: BinaryIO) -> int:
	return int.from_bytes(f.read(2), 'little', signed=True)
def read_s24(f: BinaryIO) -> int:
	return int.from_bytes(f.read(3), 'little', signed=True)
def read_s32(f: BinaryIO) -> int:
	return int.from_bytes(f.read(4), 'little', signed=True)
def read_s40(f: BinaryIO) -> int:
	return int.from_bytes(f.read(5), 'little', signed=True)
def read_s48(f: BinaryIO) -> int:
	return int.from_bytes(f.read(6), 'little', signed=True)
def read_s64(f: BinaryIO) -> int:
	return int.from_bytes(f.read(8), 'little', signed=True)

def unpack(format: str, f: BinaryIO):
	return struct.unpack(format, f.read(struct.calcsize(format)))

def read_f16(f) -> float:
	return unpack('<e', f)[0]

class _VectorBase:
	format: str
	def check_args(self, *args):
		return
	def parse_arg(self, *args):
		return args
class _IntVector(_VectorBase):
	def check_args(self, *args):
		for arg in args:
			assert(isinstance(arg, int))
class _UIntVector(_VectorBase):
	def check_args(self, *args):
		for arg in args:
			assert (isinstance(arg, int) and arg >= 0)
class _FloatVector(_VectorBase):
	def check_args(self, *args):
		for arg in args:
			assert(isinstance(arg, int|float))
	def parse_args(self, *args):
		return (*[float(f) for f in args],)

class TVector2[T](_VectorBase):
	format: str

	def __init__(self, x: T|BinaryIO|'TVector2', y: T|None = None):
		self.x: T
		self.y: T
		if isinstance(x, io.IOBase):
			self.x, self.y = struct.unpack(self.format, x.read(struct.calcsize(self.format)))
		else:
			if isinstance(x, TVector2):
				x, y = x.xy()
			self.check_args(x,y)
			self.x, self.y = self.parse_arg(x,y)
	
	def __eq__(self, value):
		return \
			isinstance(value, self.__class__) \
			and self.x == value.x \
			and self.y == value.y
	
	@overload
	def __add__(self, other: 'float|FVector2d|FVector2f|FVector2h') -> 'FVector2f': ...
	@overload
	def __sub__(self, other: 'float|FVector2d|FVector2f|FVector2h') -> 'FVector2f': ...
	@overload
	def __mul__(self, other: 'float|FVector2d|FVector2f|FVector2h') -> 'FVector2f': ...
	@overload
	def __div__(self, other: 'float|FVector2d|FVector2f|FVector2h') -> 'FVector2f': ...

	def __add__(self, other):
		if isinstance(other, TVector2):
			if isinstance(self, FVector2d|FVector2f|FVector2h) or isinstance(other, FVector2d|FVector2f|FVector2h):
				ret_class = FVector2f
			elif isinstance(self, FIntVector2) or isinstance(other, FIntVector2):
				ret_class = FIntVector2
			else:
				ret_class = FUIntVector2
			return ret_class(
				self.x + other.x,
				self.y + other.y
			)
		elif isinstance(other, int):
			return self.__class__(
				self.x - other,
				self.y - other
			)
		elif isinstance(other, float):
			return FVector2f(
				self.x - other,
				self.y - other
			)
		
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __sub__(self, other):
		if isinstance(other, TVector2):
			if isinstance(self, FVector2d|FVector2f|FVector2h) or isinstance(other, FVector2d|FVector2f|FVector2h):
				ret_class = FVector2f
			elif isinstance(self, FIntVector2) or isinstance(other, FIntVector2):
				ret_class = FIntVector2
			else:
				ret_class = self.__class__
			return ret_class(
				self.x - other.x,
				self.y - other.y
			)
		elif isinstance(other, float):
			return FVector2f(
				self.x - other,
				self.y - other
			)
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __mul__(self, other):
		if isinstance(other, TVector2):
			if isinstance(self, FVector2d|FVector2f|FVector2h) or isinstance(other, FVector2d|FVector2f|FVector2h):
				ret_class = FVector2f
			elif isinstance(self, FIntVector2) or isinstance(other, FIntVector2):
				ret_class = FIntVector2
			else:
				ret_class = self.__class__
			return ret_class(
				self.x * other.x,
				self.y * other.y
			)
		elif isinstance(other, float):
			return FVector2f(
				self.x * other,
				self.y * other
			)
		elif isinstance(other, int):
			if isinstance(self, FVector2d|FVector2f|FVector2h) or isinstance(other, float):
				ret_class = FVector2f
			elif isinstance(self, FIntVector2):
				ret_class = FIntVector2
			else:
				ret_class = self.__class__
			return self.__class__(
				self.x * other,
				self.y * other
			)
		
		raise ValueError(f'tried to multiply vector with unknown type! {other.__class__}')

	def __truediv__(self, other):
		if isinstance(other, TVector2):
			FVector2f(
				self.x / other.x,
				self.y / other.y
			)
		elif isinstance(other, float|int):
			return FVector2f(
				self.x / other,
				self.y / other
			)
		
		raise ValueError(f'tried to divide vector with unknown type! {other.__class__}')
		
	def __floordiv__(self, other):
		if isinstance(other, TVector2):
			if isinstance(self, FUIntVector2) and isinstance(other, FUIntVector2):
				return FUIntVector2(
					self.x // other.x,
					self.y // other.y
				)
			elif isinstance(self, FIntVector2) and isinstance(other, FIntVector2):
				return FIntVector2(
					self.x // other.x,
					self.y // other.y
				) 
		elif isinstance(self, FUIntVector2) and isinstance(other, int):
			if other < 0: ret_class = FIntVector2
			else: ret_class = FUIntVector2
			return ret_class(
				self.x // other,
				self.y // other
			)
		elif isinstance(self, FIntVector2) and isinstance(other, int):
			return FIntVector2(
				self.x // other,
				self.y // other
			)
		
	def __len__(self):
		return 2
	
	def dot(self, other: 'TVector2') -> float:
		ret = self.x * other.x
		ret += self.y * other.y
		return ret

	def __repr__(self):
		return f'{self.__class__.__name__}({self.x}, {self.y})'
	
	def __getitem__(self, index: int):
		if not 0 <= index < 2:
			raise IndexError(f'0 < index:{index} < 2')
		match index:
			case 0: return self.x
			case 1: return self.y
			case _: assert(False)

	def __setitem__(self, index: int, value: T):
		if not 0 <= index < 2:
			raise IndexError(f'0 < index:{index} < 2')
		match index:
			case 0: self.x = value
			case 1: self.y = value
			case _: assert(False)
	
	def xy(s): return s.x, s.y
	def yx(s): return s.y, s.x

class TVector3[T](_VectorBase):
	
	def __init__(self, x: T|BinaryIO, y: T|None = None, z: T|None = None):
		self.x: T
		self.y: T
		self.z: T
		if isinstance(x, io.IOBase):
			self.x, self.y, self.z = struct.unpack(self.format, x.read(struct.calcsize(self.format)))
		else:
			if isinstance(x, TVector3):
				x, y, z = x.xyz()
			self.check_args(x,y,z)
			self.x, self.y, self.z = self.parse_arg(x,y,z)

	def __eq__(self, value):
		return \
			isinstance(value, self.__class__) \
			and self.x == value.x \
			and self.y == value.y \
			and self.z == value.z


	@overload
	def __add__(self, other: 'float|FVector3d|FVector3f|FVector3h') -> 'FVector3f': ...
	@overload
	def __sub__(self, other: 'float|FVector3d|FVector3f|FVector3h') -> 'FVector3f': ...
	@overload
	def __mul__(self, other: 'float|FVector3d|FVector3f|FVector3h') -> 'FVector3f': ...
	@overload
	def __div__(self, other: 'float|FVector3d|FVector3f|FVector3h') -> 'FVector3f': ...

	def __add__(self, other):
		if isinstance(other, TVector3):
			if isinstance(self, FVector3f|FVector3h) or isinstance(other, FVector3f|FVector3h):
				ret_class = FVector3f
			elif isinstance(self, FIntVector3) or isinstance(other, FIntVector3):
				ret_class = FIntVector3
			else:
				ret_class = FUIntVector3
			return ret_class(
				self.x + other.x,
				self.y + other.y,
				self.z + other.z
			)
		
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __sub__(self, other):
		if isinstance(other, TVector3):
			if isinstance(self, FVector3f|FVector3h) or isinstance(other, FVector3f|FVector3h):
				ret_class = FVector3f
			elif isinstance(self, FIntVector3) or isinstance(other, FIntVector3):
				ret_class = FIntVector3
			else:
				ret_class = self.__class__
			return ret_class(
				self.x - other.x,
				self.y - other.y,
				self.z - other.z
			)
		
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __mul__(self, other):
		if isinstance(other, TVector3):
			if isinstance(self, FVector3f|FVector3h) or isinstance(other, FVector3f|FVector3h):
				ret_class = FVector3f
			elif isinstance(self, FIntVector3) or isinstance(other, FIntVector3):
				ret_class = FIntVector3
			else:
				ret_class = self.__class__
			return ret_class(
				self.x * other.x,
				self.y * other.y,
				self.z * other.z
			)
		elif isinstance(other, float):
			return FVector3f(
				self.x * other,
				self.y * other,
				self.z * other
			)
		elif isinstance(other, int):
			if isinstance(self, FVector3f|FVector3h) or isinstance(other, float):
				ret_class = FVector3f
			elif isinstance(self, FIntVector3):
				ret_class = FIntVector3
			else:
				ret_class = self.__class__
			return self.__class__(
				self.x * other,
				self.y * other,
				self.z * other
			)
		
		raise ValueError(f'tried to multiply vector with unknown type! {other.__class__}')

	def __truediv__(self, other):
		if isinstance(other, TVector3):
			if isinstance(self, FIntVector3|FUIntVector3) and isinstance(other, FIntVector3|FUIntVector3):
				return self.__class__(
					self.x // other.x,
					self.y // other.y,
					self.z // other.z
				)
			elif isinstance(self, FIntVector3|FUIntVector3) and isinstance(other, int):
				return self.__class__(
					self.x // other,
					self.y // other,
					self.z // other
				)
			elif isinstance(self, FVector3f|FVector3h):
				FVector3f(
					self.x / other.x,
					self.y / other.y,
					self.z / other.z
				)
		elif isinstance(other, float|int):
			return FVector3f(
				self.x / other,
				self.y / other,
				self.z / other
			)
		
		raise ValueError(f'tried to divide vector with unknown type! {other.__class__}')
	
	def __len__(self):
		return 3
	
	def saturate(self):
		self.x = max(1, min(0, self.x))
		self.y = max(1, min(0, self.y))
		self.z = max(1, min(0, self.z))

	def magnitude(self) -> float:
		return math.sqrt(
			self.x * self.x
			+ self.y * self.y
			+ self.z * self.z
		)
	
	def normalize(self):
		return self / self.magnitude()

	def cross(self, other: 'TVector3'):
		return self.__class__(
			self[1] * other[2] - self[2] * other[1],
			self[2] * other[0] - self[0] * other[2],
			self[0] * other[1] - self[1] * other[0]
		)

	def copy(self):
		return self.__class__(*self.xyz())

	def __repr__(self):
		return f'{self.__class__.__name__}({self.x}, {self.y}, {self.z})'
	
	def __getitem__(self, index: int):
		if not 0 <= index < 3:
			raise IndexError(f'0 < index:{index} < 3')
		match index:
			case 0: return self.x
			case 1: return self.y
			case 2: return self.z
			case _: assert(False)

	def __setitem__(self, index: int, value: T):
		if not 0 <= index < 3:
			raise IndexError(f'0 < index:{index} < 3')
		match index:
			case 0: self.x = value
			case 1: self.y = value
			case 2: self.y = value
			case _: assert(False)

	def xy(s): return s.x, s.y
	def xz(s): return s.x, s.z
	
	def yx(s): return s.y, s.x
	def yz(s): return s.y, s.z
	
	def zx(s): return s.z, s.x
	def zy(s): return s.z, s.y
	
	def xyz(s): return s.x, s.y, s.z
	def xzy(s): return s.x, s.z, s.y

	def yxz(s): return s.y, s.x, s.z
	def yzx(s): return s.y, s.z, s.x

	def zxy(s): return s.z, s.x, s.y
	def zyx(s): return s.z, s.y, s.x

class TVector4[T](_VectorBase):
	
	@overload
	def __add__(self, other: 'float|FVector4d|FVector4f|FVector4h') -> 'FVector4f': ...
	@overload
	def __sub__(self, other: 'float|FVector4d|FVector4f|FVector4h') -> 'FVector4f': ...
	@overload
	def __mul__(self, other: 'float|FVector4d|FVector4f|FVector4h') -> 'FVector4f': ...
	@overload
	def __div__(self, other: 'float|FVector4d|FVector4f|FVector4h') -> 'FVector4f': ...

	def __init__(self, x: T|BinaryIO, y: T|None = None, z: T|None = None, w: T|None = None):
		self.x: T
		self.y: T
		self.z: T
		self.w: T
		if isinstance(x, io.IOBase):
			pos = x.tell()
			x.seek(0, os.SEEK_END)
			length = x.tell()
			x.seek(pos, os.SEEK_SET)
			data = x.read(struct.calcsize(self.format))
			self.x, self.y, self.z, self.w = struct.unpack(self.format, data)
		else:
			if isinstance(x, TVector4):
				x, y, z, w = x.xyzw()
			self.check_args(x,y,z,w)
			self.x, self.y, self.z, self.w = self.parse_arg(x,y,z,w)

	def __add__(self, other):
		if isinstance(other, TVector4):
			if isinstance(self, FVector4d|FVector4f|FVector4h) or isinstance(other, FVector4d|FVector4f|FVector4h):
				ret_class = FVector4f
			elif isinstance(self, FIntVector4) or isinstance(other, FIntVector4):
				ret_class = FIntVector4
			else:
				ret_class = FUIntVector4
			return ret_class(
				self.x + other.x,
				self.y + other.y,
				self.z + other.z,
				self.w + other.w
			)
		elif isinstance(other, int):
			return self.__class__(
				self.x - other,
				self.y - other,
				self.z - other,
				self.w - other
			)
		elif isinstance(other, float):
			return FVector4f(
				self.x - other,
				self.y - other,
				self.z - other,
				self.w - other
			)
		
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __sub__(self, other):
		if isinstance(other, TVector4):
			if isinstance(self, FVector4d|FVector4f|FVector4h) or isinstance(other, FVector4d|FVector4f|FVector4h):
				ret_class = FVector4f
			elif isinstance(self, FIntVector4) or isinstance(other, FIntVector4):
				ret_class = FIntVector4
			else:
				ret_class = self.__class__
			return ret_class(
				self.x - other.x,
				self.y - other.y,
				self.z - other.z,
				self.w - other.w
			)
		elif isinstance(other, float):
			return FVector4f(
				self.x - other,
				self.y - other,
				self.z - other,
				self.w - other
			)
		raise ValueError(f'tried to add vector with unknown type! {other.__class__}')

	def __mul__(self, other):
		if isinstance(other, TVector4):
			if isinstance(self, FVector4d|FVector4f|FVector4h) or isinstance(other, FVector4d|FVector4f|FVector4h):
				ret_class = FVector4f
			elif isinstance(self, FIntVector4) or isinstance(other, FIntVector4):
				ret_class = FIntVector4
			else:
				ret_class = self.__class__
			return ret_class(
				self.x * other.x,
				self.y * other.y,
				self.z * other.z,
				self.w * other.w
			)
		elif isinstance(other, float):
			return FVector4f(
				self.x * other,
				self.y * other,
				self.z * other,
				self.w * other
			)
		elif isinstance(other, int):
			if isinstance(self, FVector4d|FVector4f|FVector4h) or isinstance(other, float):
				ret_class = FVector4f
			elif isinstance(self, FIntVector4):
				ret_class = FIntVector4
			else:
				ret_class = self.__class__
			return self.__class__(
				self.x * other,
				self.y * other,
				self.z * other,
				self.w * other
			)
		
		raise ValueError(f'tried to multiply vector with unknown type! {other.__class__}')

	def __truediv__(self, other):
		if isinstance(other, TVector4):
			FVector4f(
				self.x / other.x,
				self.y / other.y,
				self.z / other.z,
				self.w / other.w
			)
		elif isinstance(other, float|int):
			return FVector4f(
				self.x / other,
				self.y / other,
				self.z / other,
				self.w / other
			)
		
		raise ValueError(f'tried to divide vector with unknown type! {other.__class__}')
		
	def __floordiv__(self, other):
		if isinstance(other, TVector4):
			if isinstance(self, FUIntVector4) and isinstance(other, FUIntVector4):
				return FUIntVector4(
					self.x // other.x,
					self.y // other.y,
					self.z // other.z,
					self.w // other.w
				)
			elif isinstance(self, FIntVector4) and isinstance(other, FIntVector4):
				return FIntVector4(
					self.x // other.x,
					self.y // other.y,
					self.z // other.z,
					self.w // other.w
				) 
		elif isinstance(self, FUIntVector4) and isinstance(other, int):
			if other < 0: ret_class = FIntVector4
			else: ret_class = FUIntVector4
			return ret_class(
				self.x // other,
				self.y // other,
				self.z // other,
				self.w // other
			)
		elif isinstance(self, FIntVector4) and isinstance(other, int):
			return FIntVector4(
				self.x // other,
				self.y // other,
				self.z // other,
				self.w // other
			)
		

	def __len__(self):
		return 4

	def __eq__(self, value):
		return \
			isinstance(value, self.__class__) \
			and self.x == value.x \
			and self.y == value.y

	def __repr__(self):
		return f'{self.__class__.__name__}({self.x}, {self.y}, {self.z}, {self.w})'

	def __getitem__(self, index: int):
		if not 0 <= index < 4:
			raise IndexError(f'0 < index:{index} < 4')
		match index:
			case 0: return self.x
			case 1: return self.y
			case 2: return self.z
			case _: assert(False)

	def __setitem__(self, index: int, value: T):
		if not 0 <= index < 4:
			raise IndexError(f'0 < index:{index} < 4')
		match index:
			case 0: self.x = value
			case 1: self.y = value
			case 2: self.y = value
			case _: assert(False)
		
	def xy(s): return s.x, s.y
	def xz(s): return s.x, s.z
	def xw(s): return s.x, s.w
	
	def yx(s): return s.y, s.x
	def yz(s): return s.y, s.z
	def yw(s): return s.y, s.w
	
	def zx(s): return s.z, s.x
	def zy(s): return s.z, s.y
	def zw(s): return s.z, s.w
	
	def wx(s): return s.w, s.x
	def wy(s): return s.w, s.y
	def wz(s): return s.w, s.z
	
	def xyz(s): return s.x, s.y, s.z
	def xyw(s): return s.x, s.y, s.w
	def xzy(s): return s.x, s.z, s.y
	def xzw(s): return s.x, s.z, s.w
	def xwy(s): return s.x, s.w, s.y
	def xwz(s): return s.x, s.w, s.z
	
	def yxz(s): return s.y, s.x, s.z
	def yxw(s): return s.y, s.x, s.w
	def yzx(s): return s.y, s.z, s.x
	def yzw(s): return s.y, s.z, s.w
	def ywx(s): return s.y, s.w, s.x
	def ywz(s): return s.y, s.w, s.z
	
	def zxy(s): return s.z, s.x, s.y
	def zxw(s): return s.z, s.x, s.w
	def zyx(s): return s.z, s.y, s.x
	def zyw(s): return s.z, s.y, s.w
	def zwx(s): return s.z, s.w, s.x
	def zwy(s): return s.z, s.w, s.y
	
	def wxy(s): return s.w, s.x, s.y
	def wxz(s): return s.w, s.x, s.z
	def wyx(s): return s.w, s.y, s.x
	def wyz(s): return s.w, s.y, s.z
	def wzx(s): return s.w, s.z, s.x
	def wzy(s): return s.w, s.z, s.y

	def xyzw(s): return s.x, s.y, s.z, s.w
	def xywz(s): return s.x, s.y, s.w, s.z
	def xzyw(s): return s.x, s.z, s.y, s.w
	def xzwy(s): return s.x, s.z, s.w, s.y
	def xwyz(s): return s.x, s.w, s.y, s.z
	def xwzy(s): return s.x, s.w, s.z, s.y

	def yxzw(s): return s.y, s.x, s.z, s.w
	def yxwz(s): return s.y, s.x, s.w, s.z
	def yzxw(s): return s.y, s.z, s.x, s.w
	def yzwx(s): return s.y, s.z, s.w, s.x
	def ywxz(s): return s.y, s.w, s.x, s.z
	def ywzx(s): return s.y, s.w, s.z, s.x

	def zxyw(s): return s.z, s.x, s.y, s.w
	def zxwy(s): return s.z, s.x, s.w, s.y
	def zyxw(s): return s.z, s.y, s.x, s.w
	def zywx(s): return s.z, s.y, s.w, s.x
	def zwxy(s): return s.z, s.w, s.x, s.y
	def zwyx(s): return s.z, s.w, s.y, s.x

	def wxyz(s): return s.w, s.x, s.y, s.z
	def wxzy(s): return s.w, s.x, s.z, s.y
	def wyxz(s): return s.w, s.y, s.x, s.z
	def wyzx(s): return s.w, s.y, s.z, s.x
	def wzxy(s): return s.w, s.z, s.x, s.y
	def wzyx(s): return s.w, s.z, s.y, s.x

class FVector2h(TVector2[float], _FloatVector): format = '<ee'
class FVector3h(TVector3[float], _FloatVector): format = '<eee'
class FVector4h(TVector4[float], _FloatVector): format = '<eeee'

class FVector2f(TVector2[float], _FloatVector): format = '<ff'
class FVector3f(TVector3[float], _FloatVector): format = '<fff'
class FVector4f(TVector4[float], _FloatVector): format = '<ffff'

class FVector2d(TVector2[float], _FloatVector): format = '<dd'
class FVector3d(TVector3[float], _FloatVector): format = '<ddd'
class FVector4d(TVector4[float], _FloatVector): format = '<dddd'

class FUIntVector2(TVector2[uint], _UIntVector): format = '<II'
class FUIntVector3(TVector3[uint], _UIntVector): format = '<III'
class FUIntVector4(TVector4[uint], _UIntVector): format = '<IIII'

class FIntVector2(TVector2[int], _IntVector): format = '<ii'
class FIntVector3(TVector3[int], _IntVector): format = '<iii'
class FIntVector4(TVector4[int], _IntVector): format = '<iiii'

class FULongVector2(TVector2[uint], _UIntVector): format = '<QQ'
class FULongVector3(TVector3[uint], _UIntVector): format = '<QQQ'
class FULongVector4(TVector4[uint], _UIntVector): format = '<QQQQ'

class FLongVector2(TVector2[int], _IntVector): format = '<qq'
class FLongVector3(TVector3[int], _IntVector): format = '<qqq'
class FLongVector4(TVector4[int], _IntVector): format = '<qqqq'

class FVertex(FVector3f):
	def __init__(self, x, y, z):
		super().__init__(x, y, z)
		self.index:int|None = None
		self.is_ref:bool = False
		self.raw_pos: FIntVector3 = None

	def __repr__(self):
		return super().__repr__() + " | "+ (self.raw_pos.__repr__() if self.raw_pos else "None")


# shader types recreation
uint2: TypeAlias = FUIntVector2
uint3: TypeAlias = FUIntVector3
uint4: TypeAlias = FUIntVector4

int2: TypeAlias = FIntVector2
int3: TypeAlias = FIntVector3
int4: TypeAlias = FIntVector4

float2: TypeAlias = FVector2f
float3: TypeAlias = FVector3f
float4: TypeAlias = FVector4f

def u32_rshift(val:uint, shift: uint):
	return (val << shift) & 0xFFFFFFFF

def uint_to_int(val: uint, bit_len: uint) -> int:
	assert(isinstance(val, uint))
	assert(isinstance(bit_len, uint))
	assert(0 < bit_len)
	assert(0 <= val < (1 << bit_len))
	if (val >> (bit_len - 1) & 1):
		return (val - (1 << bit_len))
	else:
		return val
	
	
def int_to_uint(val: int, bit_len: uint) -> uint:
	assert(isinstance(val, uint))
	assert(isinstance(bit_len, uint))
	assert(0 < bit_len)
	bitmask = (1 << bit_len) - 1
	return ((val + (1 << bit_len)) & bitmask) if val < 0 else val

_T = TypeVar('T')
def read_list_with_len(f: BinaryIO, len: int, func: Callable[[BinaryIO],_T]) -> list[_T]:
	return [func(f) for _ in range(len)]

def read_list(f: BinaryIO, func:  Callable[[BinaryIO],_T]) -> list[_T]:
	return read_list_with_len(f, read_u32(f),func)

def read_bitfield_value(data: uint, num_bits: int, bit_offset: uint) -> int:
	assert(0 <= bit_offset < 32)
	assert(0 <= abs(num_bits) < 32)
	assert(abs(num_bits)+bit_offset <= 32)
	ret = (data >> bit_offset) & ((1 << (abs(num_bits))) - 1)
	if num_bits < 0:
		ret = uint_to_int(ret, abs(num_bits))
	return ret

def read_bitfield(Data: uint, *NumBits: int) -> tuple[int, ...]:
	start = 0
	ret = []
	for num in NumBits:
		ret.append(read_bitfield_value(Data, num, start))
		start += num
	return (*ret,)

def BitAlignU32(High: uint, Low: uint, Shift: uint):
	assert(0 <= High <= 0xFFFFFFFF)
	assert(0 <= Low <= 0xFFFFFFFF)
	assert(0 <= Shift)
	Shift &= 31
	Result = Low >> Shift
	Result |= u32_rshift(High, (32 - Shift)) if Shift > 0 else 0
	return Result

def ReadUnalignedDword(f: BinaryIO, BaseAddressInBytes: uint, BitOffset: int) -> uint:
	ByteAddress = BaseAddressInBytes + (BitOffset >> 3)
	AlignedByteAddress = ByteAddress & ~3
	BitOffset = u32_rshift((ByteAddress - AlignedByteAddress), 3) | (BitOffset & 7)
	f.seek(AlignedByteAddress, os.SEEK_SET)
	Data = FUIntVector2(f)
	return BitAlignU32(Data.y, Data.x, BitOffset)

def ReadUnalignedDwordFromAlignedBase(SrcBuffer: BinaryIO, AlignedBaseAddress: uint, BitOffset: uint) -> uint:
	SrcBuffer.seek(AlignedBaseAddress, os.SEEK_SET)
	Low: uint = read_u32(SrcBuffer)
	High: uint = read_u32(SrcBuffer)
	return BitAlignU32(High, Low, BitOffset)

def BitFieldExtractI32(Data:uint, Size: uint, Offset: uint) -> uint:
	assert (0 <= Data <= 0xFFFFFFFF)
	assert (0 <= Size)
	assert (0 <= Offset)
	Size &= 31
	Offset &= 31
	return read_bitfield_value(Data, -Size, Offset)

def BitFieldExtractU32(Data:uint, Size: uint, Offset: uint) -> uint:
	assert (0 <= Data <= 0xFFFFFFFF)
	assert (0 <= Size)
	if 0 > Offset:
		Offset = int_to_uint(Offset, 32)
	Size &= 31
	Offset &= 31
	return read_bitfield_value(Data, Size, Offset)

def BitFieldMaskU32(MaskWidth: uint, MaskLocation: uint) -> uint:
	assert(0 <= MaskWidth)
	assert(0 <= MaskLocation)
	MaskWidth &= 31
	MaskLocation &= 31
	return u32_rshift(((1 << MaskWidth) - 1), MaskLocation)

def firstbithigh(x: uint) -> uint:
	# this mimics the behaviour of the hlsl implementation
	# usually 0 would be returned for a 0 value but HLSL shaders output -1 so y'know
	return 0xffffffff if x == 0 else math.floor(math.log2(x))

def bytes_to_hex(bytes: bytes) -> str:
	return ''.join([f'{b:02x}' for b in bytes])

def ReadByte(InputBuffer: BinaryIO,	Address: uint) -> uint:
	InputBuffer.seek(Address & ~3, os.SEEK_SET)
	return (read_u32(InputBuffer) >> ((Address & 3)*8)) & 0xFF

def UnpackByte0(v: uint) -> uint: return v & 0xff
def UnpackByte1(v: uint) -> uint: return (v >> 8) & 0xff
def UnpackByte2(v: uint) -> uint: return (v >> 16) & 0xff
def UnpackByte3(v: uint) -> uint: return v >> 24

def UnpackToUint4(Value: uint, NumComponentBits: FUIntVector4):
	return FUIntVector4(BitFieldExtractU32(Value, NumComponentBits.x, 0),
				 BitFieldExtractU32(Value, NumComponentBits.y, NumComponentBits.x),
				 BitFieldExtractU32(Value, NumComponentBits.z, NumComponentBits.x + NumComponentBits.y),
				 BitFieldExtractU32(Value, NumComponentBits.w, NumComponentBits.x + NumComponentBits.y + NumComponentBits.z))

# tests
assert(firstbithigh(00000000) == 4294967295)
assert(False not in [firstbithigh((1 << i + 1) - 1) == i for i in range(32)])

assert(int_to_uint(0xFF00FF00 ^ 0, 32) == 4278255360)
assert(int_to_uint(0xFF00FF00 ^ -1, 32) == 16711935)
assert(int_to_uint(0x12345678 ^ -1, 32) == 3989547399)
assert(int_to_uint(0x9abcdef0 | (0x12345678 ^ -1), 32) == 4294967287)
assert(int_to_uint(0 - 1, 32) == 4294967295)

assert(BitFieldExtractI32(0b0111_1111, 8, 0) == 127)
assert(BitFieldExtractI32(0b1001_1111, 5, 0) == -1)
assert(BitFieldExtractI32(0b1111_1100, 8, 0) == -4)
assert(BitFieldExtractI32(0b1100_1100, 6, 2) == -13)

assert(BitAlignU32(0x12345678, 0x9abcdef0, 0) == 0x9abcdef0)
assert(BitAlignU32(0x12345678, 0x9abcdef0, 32) == 0x9abcdef0)
assert(BitAlignU32(0x12345678, 0x9abcdef0, 31) == 0x2468acf1)

assert(BitFieldMaskU32(5, 32-4) == 0xF0000000)

assert(u32_rshift(0xFFFFFFFF, 8) == 0xFFFFFF00)

assert(FIntVector3(1,2,3) == FIntVector3(1,2,3))
assert(FIntVector3(1,2,4) != FIntVector3(1,2,3))
