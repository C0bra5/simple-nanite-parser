from typing import BinaryIO, Callable, TypeVar, TypeAlias
import struct
import os
import io
import math

# syntactic sugar
uint: TypeAlias = int


# shader types recreation
uint2: TypeAlias = tuple[uint,uint]
uint3: TypeAlias = tuple[uint,uint,uint]
uint4: TypeAlias = tuple[uint,uint,uint,uint]

int2: TypeAlias = tuple[int,int]
int3: TypeAlias = tuple[int,int,int]
int4: TypeAlias = tuple[int,int,int,int]

float2: TypeAlias = tuple[float,float]
float3: TypeAlias = tuple[float,float,float]
float4: TypeAlias = tuple[float,float,float,float]

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




class TVector2[T]:
	
	def __init__(self,x: T,y: T):
		self.x: T = x
		self.y: T = y
	
	def __eq__(self, value):
		return \
			isinstance(value, self.__class__) \
			and self.x == value.x \
			and self.y == value.y
	
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

class TVector3[T]:
	
	def __init__(self,x: T,y: T,z: T):
		self.x: T = x
		self.y: T = y
		self.z: T = z

	def __eq__(self, value):
		return \
			isinstance(value, self.__class__) \
			and self.x == value.x \
			and self.y == value.y \
			and self.z == value.z

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


class TVector4[T]:
	
	def __init__(self,x: T,y: T,z: T,w: T):
		self.x: T = x
		self.y: T = y
		self.z: T = z
		self.w: T = w

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

class FVector2h(TVector2[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int):
			super().__init__(float(x),float(y))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<ee', x))
		else:
			raise ValueError("bad arg types")
class FVector3h(TVector3[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int):
			super().__init__(float(x),float(y),float(z))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<eee', x))
		else:
			raise ValueError("bad arg types")
class FVector4h(TVector4[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None, w: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int) and isinstance(w, float|int):
			super().__init__(float(x),float(y),float(z),float(w))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<eeee', x))
		else:
			raise ValueError("bad arg types")

class FVector2f(TVector2[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int):
			super().__init__(float(x),float(y))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<ff', x))
		else:
			raise ValueError("bad arg types")
class FVector3f(TVector3[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int):
			super().__init__(float(x),float(y),float(z))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<fff', x))
		else:
			raise ValueError("bad arg types")
class FVector4f(TVector4[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None, w: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int) and isinstance(w, float|int):
			super().__init__(float(x),float(y),float(z),float(w))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<ffff', x))
		else:
			raise ValueError("bad arg types")

class FVector2d(TVector2[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int):
			super().__init__(float(x),float(y))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<dd', x))
		else:
			raise ValueError("bad arg types")
class FVector3d(TVector3[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int):
			super().__init__(float(x),float(y),float(z))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<ddd', x))
		else:
			raise ValueError("bad arg types")
class FVector4d(TVector4[float]):
	def __init__(self, x: BinaryIO|float|int, y: float|int|None = None, z: float|int|None = None, w: float|int|None = None):
		if isinstance(x, float|int) and isinstance(y, float|int) and isinstance(z, float|int) and isinstance(w, float|int):
			super().__init__(float(x),float(y),float(z),float(w))
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<dddd', x))
		else:
			raise ValueError("bad arg types")

class FUIntVector2(TVector2[uint]):
	def __init__(self, x: BinaryIO|uint, y: uint|None = None):
		if isinstance(x, uint) and isinstance(y, uint):
			assert(x >= 0 and y >= 0)
			super().__init__(x,y)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<II', x))
		else:
			raise ValueError("bad arg types")
class FUIntVector3(TVector3[uint]):
	def __init__(self, x: BinaryIO|uint, y: uint|None = None, z: uint|None = None):
		if isinstance(x, uint) and isinstance(y, uint) and isinstance(z, uint):
			assert(x >= 0 and y >= 0 and z >= 0)
			super().__init__(x,y,z)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<III', x))
		else:
			raise ValueError("bad arg types")
class FUIntVector4(TVector4[uint]):
	def __init__(self, x: BinaryIO|uint, y: uint|None = None, z: uint|None = None, w: uint|None = None):
		if isinstance(x, uint) and isinstance(y, uint) and isinstance(z, uint) and isinstance(w, uint):
			assert(x >= 0 and y >= 0 and z >= 0 and w >= 0)
			super().__init__(x,y,z,w)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<IIII', x))
		else:
			raise ValueError("bad arg types")


class FIntVector2(TVector2[int]):
	def __init__(self, x: BinaryIO|int, y: int|None = None):
		if isinstance(x, int) and isinstance(y, int):
			super().__init__(x,y)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<ii', x))
		else:
			raise ValueError("bad arg types")
class FIntVector3(TVector3[int]):
	def __init__(self, x: BinaryIO|int, y: int|None = None, z: int|None = None):
		if isinstance(x, int) and isinstance(y, int) and isinstance(z, int):
			super().__init__(x,y,z)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<iii', x))
		else:
			raise ValueError("bad arg types")
class FIntVector4(TVector4[int]):
	def __init__(self, x: BinaryIO|int, y: int|None = None, z: int|None = None, w: int|None = None):
		if isinstance(x, int) and isinstance(y, int) and isinstance(z, int) and isinstance(w, int):
			super().__init__(x,y,z,w)
		elif isinstance(x, io.IOBase):
			super().__init__(*unpack('<iiii', x))
		else:
			raise ValueError("bad arg types")


class FVertex(FVector3f):
	def __init__(self, *args):
		super().__init__(*args)
		self.index:int|None = None
		self.is_ref:bool = False
	
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