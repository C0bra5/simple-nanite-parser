from unreal_io import *
from typing import BinaryIO
import os

class FBitStreamReader:
	def __init__(self, AlignedByteAddress: uint, BitOffset: uint, CompileTimeMaxRemainingBits: uint):
		self.num_bits_read: uint = 0

		self.AlignedByteAddress: uint = AlignedByteAddress
		self.BitOffsetFromAddress: int = BitOffset

		self.BufferBits: FUIntVector4 = FUIntVector4(0,0,0,0)
		self.BufferOffset: int = 0

		self.CompileTimeMinBufferBits: int = 0
		self.CompileTimeMinDwordBits: int = 0
		self.CompileTimeMaxRemainingBits: int = CompileTimeMaxRemainingBits
	
	@staticmethod
	def Create_Aligned(ByteAddress: uint, BitOffset: uint, CompileTimeMaxRemainingBits: uint):
		return FBitStreamReader(ByteAddress, BitOffset, CompileTimeMaxRemainingBits)

	@staticmethod
	def Create(ByteAddress: uint, BitOffset: uint, CompileTimeMaxRemainingBits: uint):
		AlignedByteAddress: uint = ByteAddress & ~3
		BitOffset += u32_rshift((ByteAddress & 3), 3)
		return FBitStreamReader(AlignedByteAddress, BitOffset, CompileTimeMaxRemainingBits)
	
	def Read(State, InputBuffer: BinaryIO, NumBits: int, CompileTimeMaxBits: int) -> uint:
		if CompileTimeMaxBits > State.CompileTimeMinBufferBits:
			# BitBuffer could be out of bits: Reload.

			# Add cumulated offset since last refill. No need to update at every read.
			State.BitOffsetFromAddress += State.BufferOffset;	
			Address: uint = State.AlignedByteAddress + u32_rshift((State.BitOffsetFromAddress >> 5), 2)
			assert(0 <= Address <= 0xFFFFFFFF)

			# C5: You have to be a bit weird about it because it tries
			# to read from out of bounds, which is not great NGL
			InputBuffer.seek(Address, os.SEEK_SET)
			Data = FUIntVector4(
				read_u32(InputBuffer),
				read_u32(InputBuffer),
				read_u32(InputBuffer),
				read_u32(InputBuffer)
			)
			

			# Shift bits down to align
			State.BufferBits.x												= BitAlignU32(Data.y,	Data.x,	State.BitOffsetFromAddress); # BitOffsetFromAddress implicitly &31
			if State.CompileTimeMaxRemainingBits > 32: State.BufferBits.y	= BitAlignU32(Data.z,	Data.y,	State.BitOffsetFromAddress); # BitOffsetFromAddress implicitly &31
			if State.CompileTimeMaxRemainingBits > 64: State.BufferBits.z	= BitAlignU32(Data.w,	Data.z,	State.BitOffsetFromAddress); # BitOffsetFromAddress implicitly &31
			if State.CompileTimeMaxRemainingBits > 96: State.BufferBits.w	= BitAlignU32(0,		Data.w,	State.BitOffsetFromAddress); # BitOffsetFromAddress implicitly &31

			State.BufferOffset = 0

			State.CompileTimeMinDwordBits	= min(32, State.CompileTimeMaxRemainingBits)
			State.CompileTimeMinBufferBits	= min(97, State.CompileTimeMaxRemainingBits) # Up to 31 bits wasted to alignment
		
		elif CompileTimeMaxBits > State.CompileTimeMinDwordBits:
			# Bottom dword could be out of bits: Shift down.
			State.BitOffsetFromAddress += State.BufferOffset

			# Workaround for BitAlignU32(x, y, 32) returning x instead of y.
			# In the common case where State.CompileTimeMinDwordBits != 0, this will be optimized to just BitAlignU32.
			# sTODO: Can we get rid of this special case?
			bOffset32: bool = State.CompileTimeMinDwordBits == 0 and State.BufferOffset == 32

			State.BufferBits.x											= State.BufferBits.y if bOffset32 else BitAlignU32(State.BufferBits.y, State.BufferBits.x, State.BufferOffset)
			if State.CompileTimeMinBufferBits > 32: State.BufferBits.y	= State.BufferBits.z if bOffset32 else BitAlignU32(State.BufferBits.z, State.BufferBits.y, State.BufferOffset)
			if State.CompileTimeMinBufferBits > 64: State.BufferBits.z	= State.BufferBits.w if bOffset32 else BitAlignU32(State.BufferBits.w, State.BufferBits.z, State.BufferOffset)
			if State.CompileTimeMinBufferBits > 96: State.BufferBits.w	= 0                  if bOffset32 else BitAlignU32(0,                  State.BufferBits.w, State.BufferOffset)
		
			State.BufferOffset = 0

			State.CompileTimeMinDwordBits = min(32, State.CompileTimeMaxRemainingBits)

		Result: uint = BitFieldExtractU32(State.BufferBits.x, NumBits, State.BufferOffset); # BufferOffset implicitly &31
		
		# C5: readbits tracker
		State.num_bits_read += NumBits

		State.BufferOffset += NumBits
		State.CompileTimeMinBufferBits    -= CompileTimeMaxBits
		State.CompileTimeMinDwordBits     -= CompileTimeMaxBits
		State.CompileTimeMaxRemainingBits -= CompileTimeMaxBits

		return Result
	
	def Read2(State, InputBuffer: BinaryIO, NumBits: FIntVector2, CompileTimeMaxBits: FIntVector2) -> FUIntVector2:
		return FUIntVector2(
			State.Read(InputBuffer, NumBits.x, CompileTimeMaxBits.x),
			State.Read(InputBuffer, NumBits.y, CompileTimeMaxBits.y)
		)
	
	def Read3(State, InputBuffer: BinaryIO, NumBits: FIntVector3, CompileTimeMaxBits: FIntVector3) -> FUIntVector3:
		return FUIntVector3(
			State.Read(InputBuffer, NumBits.x, CompileTimeMaxBits.x),
			State.Read(InputBuffer, NumBits.y, CompileTimeMaxBits.y),
			State.Read(InputBuffer, NumBits.z, CompileTimeMaxBits.z)
		)
	
	def Read4(State, InputBuffer: BinaryIO, NumBits: FIntVector4, CompileTimeMaxBits: FIntVector4) -> FUIntVector4:
		return FUIntVector4(
			State.Read(InputBuffer, NumBits.x, CompileTimeMaxBits.x),
			State.Read(InputBuffer, NumBits.y, CompileTimeMaxBits.y),
			State.Read(InputBuffer, NumBits.z, CompileTimeMaxBits.z),
			State.Read(InputBuffer, NumBits.w, CompileTimeMaxBits.w)
		)