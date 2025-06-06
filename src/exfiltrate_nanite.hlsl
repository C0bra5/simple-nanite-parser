
#define DEFINE_SELECT(TYPE) \
	TYPE    select(bool    c, TYPE    a, TYPE    b) { return TYPE   (c   ? a.x : b.x); } \
	\
	TYPE##2 select_internal(bool    c, TYPE    a, TYPE##2 b) { return TYPE##2(c   ? a   : b.x, c   ? a   : b.y); } \
	TYPE##2 select_internal(bool    c, TYPE##2 a, TYPE    b) { return TYPE##2(c   ? a.x : b  , c   ? a.y : b  ); } \
	TYPE##2 select_internal(bool    c, TYPE##2 a, TYPE##2 b) { return TYPE##2(c   ? a.x : b.x, c   ? a.y : b.y); } \
	TYPE##2 select_internal(bool2   c, TYPE    a, TYPE    b) { return TYPE##2(c.x ? a   : b  , c.y ? a   : b  ); } \
	TYPE##2 select_internal(bool2   c, TYPE    a, TYPE##2 b) { return TYPE##2(c.x ? a   : b.x, c.y ? a   : b.y); } \
	TYPE##2 select_internal(bool2   c, TYPE##2 a, TYPE    b) { return TYPE##2(c.x ? a.x : b  , c.y ? a.y : b  ); } \
	TYPE##2 select_internal(bool2   c, TYPE##2 a, TYPE##2 b) { return TYPE##2(c.x ? a.x : b.x, c.y ? a.y : b.y); } \
	\
	TYPE##3 select_internal(bool    c, TYPE    a, TYPE##3 b) { return TYPE##3(c   ? a   : b.x, c   ? a   : b.y, c   ? a   : b.z); } \
	TYPE##3 select_internal(bool    c, TYPE##3 a, TYPE    b) { return TYPE##3(c   ? a.x : b  , c   ? a.y : b  , c   ? a.z : b  ); } \
	TYPE##3 select_internal(bool    c, TYPE##3 a, TYPE##3 b) { return TYPE##3(c   ? a.x : b.x, c   ? a.y : b.y, c   ? a.z : b.z); } \
	TYPE##3 select_internal(bool3   c, TYPE    a, TYPE    b) { return TYPE##3(c.x ? a   : b  , c.y ? a   : b  , c.z ? a   : b  ); } \
	TYPE##3 select_internal(bool3   c, TYPE    a, TYPE##3 b) { return TYPE##3(c.x ? a   : b.x, c.y ? a   : b.y, c.z ? a   : b.z); } \
	TYPE##3 select_internal(bool3   c, TYPE##3 a, TYPE    b) { return TYPE##3(c.x ? a.x : b  , c.y ? a.y : b  , c.z ? a.z : b  ); } \
	TYPE##3 select_internal(bool3   c, TYPE##3 a, TYPE##3 b) { return TYPE##3(c.x ? a.x : b.x, c.y ? a.y : b.y, c.z ? a.z : b.z); } \
	\
	TYPE##4 select_internal(bool    c, TYPE    a, TYPE##4 b) { return TYPE##4(c   ? a   : b.x, c   ? a   : b.y, c   ? a   : b.z, c   ? a   : b.w); } \
	TYPE##4 select_internal(bool    c, TYPE##4 a, TYPE    b) { return TYPE##4(c   ? a.x : b  , c   ? a.y : b  , c   ? a.z : b  , c   ? a.w : b  ); } \
	TYPE##4 select_internal(bool    c, TYPE##4 a, TYPE##4 b) { return TYPE##4(c   ? a.x : b.x, c   ? a.y : b.y, c   ? a.z : b.z, c   ? a.w : b.w); } \
	TYPE##4 select_internal(bool4   c, TYPE    a, TYPE    b) { return TYPE##4(c.x ? a   : b  , c.y ? a   : b  , c.z ? a   : b  , c.w ? a   : b  ); } \
	TYPE##4 select_internal(bool4   c, TYPE    a, TYPE##4 b) { return TYPE##4(c.x ? a   : b.x, c.y ? a   : b.y, c.z ? a   : b.z, c.w ? a   : b.w); } \
	TYPE##4 select_internal(bool4   c, TYPE##4 a, TYPE    b) { return TYPE##4(c.x ? a.x : b  , c.y ? a.y : b  , c.z ? a.z : b  , c.w ? a.w : b  ); } \
	TYPE##4 select_internal(bool4   c, TYPE##4 a, TYPE##4 b) { return TYPE##4(c.x ? a.x : b.x, c.y ? a.y : b.y, c.z ? a.z : b.z, c.w ? a.w : b.w); } \

DEFINE_SELECT(bool)
DEFINE_SELECT(uint)
DEFINE_SELECT(int)
DEFINE_SELECT(float)
DEFINE_SELECT(half)

#define select(cond,a,b) select_internal(cond,a,b)
#undef DEFINE_SELECT




float UnpackByte0(uint v) { return float(v & 0xff); }
float UnpackByte1(uint v) { return float((v >> 8) & 0xff); }
float UnpackByte2(uint v) { return float((v >> 16) & 0xff); }
float UnpackByte3(uint v) { return float(v >> 24); }

uint BitFieldExtractU32(uint Data, uint Size, uint Offset)
{
	// Shift amounts are implicitly &31 in HLSL, so they should be optimized away on most platforms
	// In GLSL shift amounts < 0 or >= word_size are undefined, so we better be explicit
	Size &= 31;
	Offset &= 31;
	return (Data >> Offset) & ((1u << Size) - 1u);
}

int BitFieldExtractI32(int Data, uint Size, uint Offset)
{
	Size &= 31u;
	Offset &= 31u;
	const uint Shift = (32u - Size) & 31u;
	const int Value = (Data >> Offset) & int((1u << Size) - 1u);
	return (Value << Shift) >> Shift;
}

uint BitFieldMaskU32(uint MaskWidth, uint MaskLocation)
{
	MaskWidth &= 31u;
	MaskLocation &= 31u;

	return ((1u << MaskWidth) - 1u) << MaskLocation;
}

uint BitAlignU32(uint High, uint Low, uint Shift)
{
	Shift &= 31u;

	uint Result = Low >> Shift;
	Result |= Shift > 0u ? (High << (32u - Shift)) : 0u;
	return Result;
}

const static float PI = 3.1415926535897932f;

#define fastClamp(x, Min, Max) clamp(x, Min, Max)

float Pow2( float x )
{
	return x*x;
}


uint4 UnpackToUint4(uint Value, int4 NumComponentBits)
{
	return uint4(BitFieldExtractU32(Value, NumComponentBits.x, 0),
				 BitFieldExtractU32(Value, NumComponentBits.y, NumComponentBits.x),
				 BitFieldExtractU32(Value, NumComponentBits.z, NumComponentBits.x + NumComponentBits.y),
				 BitFieldExtractU32(Value, NumComponentBits.w, NumComponentBits.x + NumComponentBits.y + NumComponentBits.z));
}


// Implement BitStreamReader for ByteAddressBuffer (RO), RWByteAddressBuffer (RW) and dynamic choice (RORW).
struct FBitStreamReaderState
{
	uint AlignedByteAddress;
	int BitOffsetFromAddress;

	uint4 BufferBits;
	int BufferOffset;

	int CompileTimeMinBufferBits;
	int CompileTimeMinDwordBits;
	int CompileTimeMaxRemainingBits;
};

FBitStreamReaderState BitStreamReader_Create_Aligned(uint AlignedByteAddress, uint BitOffset, uint CompileTimeMaxRemainingBits)
{
	FBitStreamReaderState State;

	State.AlignedByteAddress = AlignedByteAddress;
	State.BitOffsetFromAddress = BitOffset;

	State.BufferBits = 0;
	State.BufferOffset = 0;

	State.CompileTimeMinBufferBits = 0;
	State.CompileTimeMinDwordBits = 0;
	State.CompileTimeMaxRemainingBits = CompileTimeMaxRemainingBits;

	return State;
}

FBitStreamReaderState BitStreamReader_Create(uint ByteAddress, uint BitOffset, uint CompileTimeMaxRemainingBits)
{
	uint AlignedByteAddress = ByteAddress & ~3u;
	BitOffset += (ByteAddress & 3u) << 3;
	return BitStreamReader_Create_Aligned(AlignedByteAddress, BitOffset, CompileTimeMaxRemainingBits);
}



// C5: Inlined the inline for linting not dying reasons
uint BitStreamReader_Read_RO
	(ByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int NumBits, int CompileTimeMaxBits)
{
	if (CompileTimeMaxBits > State.CompileTimeMinBufferBits)
	{
		// BitBuffer could be out of bits: Reload.

		// Add cumulated offset since last refill. No need to update at every read.
		State.BitOffsetFromAddress += State.BufferOffset;	
		uint Address = State.AlignedByteAddress + ((State.BitOffsetFromAddress >> 5) << 2);


		uint4 Data = InputBuffer.Load4(Address);

		// Shift bits down to align
		State.BufferBits.x												= BitAlignU32(Data.y,	Data.x,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 32) State.BufferBits.y	= BitAlignU32(Data.z,	Data.y,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 64) State.BufferBits.z	= BitAlignU32(Data.w,	Data.z,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 96) State.BufferBits.w	= BitAlignU32(0,		Data.w,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31

		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits	= min(32, State.CompileTimeMaxRemainingBits);
		State.CompileTimeMinBufferBits	= min(97, State.CompileTimeMaxRemainingBits);	// Up to 31 bits wasted to alignment
	}
	else if (CompileTimeMaxBits > State.CompileTimeMinDwordBits)
	{
		// Bottom dword could be out of bits: Shift down.
		State.BitOffsetFromAddress += State.BufferOffset;

		// Workaround for BitAlignU32(x, y, 32) returning x instead of y.
		// In the common case where State.CompileTimeMinDwordBits != 0, this will be optimized to just BitAlignU32.
		// TODO: Can we get rid of this special case?
		const bool bOffset32 = State.CompileTimeMinDwordBits == 0 && State.BufferOffset == 32;

		State.BufferBits.x											= bOffset32 ? State.BufferBits.y :	BitAlignU32(State.BufferBits.y, State.BufferBits.x, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 32) State.BufferBits.y	= bOffset32 ? State.BufferBits.z :	BitAlignU32(State.BufferBits.z, State.BufferBits.y, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 64) State.BufferBits.z	= bOffset32 ? State.BufferBits.w :	BitAlignU32(State.BufferBits.w, State.BufferBits.z, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 96) State.BufferBits.w	= bOffset32 ? 0u :					BitAlignU32(0,					State.BufferBits.w, State.BufferOffset);
	
		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits = min(32, State.CompileTimeMaxRemainingBits);
	}

	const uint Result = BitFieldExtractU32(State.BufferBits.x, NumBits, State.BufferOffset); // BufferOffset implicitly &31
	
	State.BufferOffset += NumBits;
	State.CompileTimeMinBufferBits    -= CompileTimeMaxBits;
	State.CompileTimeMinDwordBits     -= CompileTimeMaxBits;
	State.CompileTimeMaxRemainingBits -= CompileTimeMaxBits;

	return Result;
}

// C5: Inlined the inline for linting not dying reasons
uint2 BitStreamReader_Read2_RO
	(ByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int2 NumBits, int2 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RO(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RO(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	return uint2(ResultX, ResultY);
}

// C5: Inlined the inline for linting not dying reasons
uint3 BitStreamReader_Read3_RO
	(ByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int3 NumBits, int3 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RO(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RO(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	uint ResultZ = BitStreamReader_Read_RO(InputBuffer, State, NumBits.z, CompileTimeMaxBits.z);
	return uint3(ResultX, ResultY, ResultZ);
}

// C5: Inlined the inline for linting not dying reasons
uint4 BitStreamReader_Read4_RO
	(ByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int4 NumBits, int4 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RO(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RO(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	uint ResultZ = BitStreamReader_Read_RO(InputBuffer, State, NumBits.z, CompileTimeMaxBits.z);
	uint ResultW = BitStreamReader_Read_RO(InputBuffer, State, NumBits.w, CompileTimeMaxBits.w);
	return uint4(ResultX, ResultY, ResultZ, ResultW);
}


// C5: inlined the inline for linter not dying reasons
uint BitStreamReader_Read_RW
	(RWByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int NumBits, int CompileTimeMaxBits)
{
	if (CompileTimeMaxBits > State.CompileTimeMinBufferBits)
	{
		// BitBuffer could be out of bits: Reload.

		// Add cumulated offset since last refill. No need to update at every read.
		State.BitOffsetFromAddress += State.BufferOffset;	
		uint Address = State.AlignedByteAddress + ((State.BitOffsetFromAddress >> 5) << 2);

		uint4 Data = InputBuffer.Load4(Address);

		// Shift bits down to align
		State.BufferBits.x												= BitAlignU32(Data.y,	Data.x,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 32) State.BufferBits.y	= BitAlignU32(Data.z,	Data.y,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 64) State.BufferBits.z	= BitAlignU32(Data.w,	Data.z,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 96) State.BufferBits.w	= BitAlignU32(0,		Data.w,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31

		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits	= min(32, State.CompileTimeMaxRemainingBits);
		State.CompileTimeMinBufferBits	= min(97, State.CompileTimeMaxRemainingBits);	// Up to 31 bits wasted to alignment
	}
	else if (CompileTimeMaxBits > State.CompileTimeMinDwordBits)
	{
		// Bottom dword could be out of bits: Shift down.
		State.BitOffsetFromAddress += State.BufferOffset;

		// Workaround for BitAlignU32(x, y, 32) returning x instead of y.
		// In the common case where State.CompileTimeMinDwordBits != 0, this will be optimized to just BitAlignU32.
		// TODO: Can we get rid of this special case?
		const bool bOffset32 = State.CompileTimeMinDwordBits == 0 && State.BufferOffset == 32;

		State.BufferBits.x											= bOffset32 ? State.BufferBits.y :	BitAlignU32(State.BufferBits.y, State.BufferBits.x, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 32) State.BufferBits.y	= bOffset32 ? State.BufferBits.z :	BitAlignU32(State.BufferBits.z, State.BufferBits.y, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 64) State.BufferBits.z	= bOffset32 ? State.BufferBits.w :	BitAlignU32(State.BufferBits.w, State.BufferBits.z, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 96) State.BufferBits.w	= bOffset32 ? 0u :					BitAlignU32(0,					State.BufferBits.w, State.BufferOffset);
	
		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits = min(32, State.CompileTimeMaxRemainingBits);
	}

	const uint Result = BitFieldExtractU32(State.BufferBits.x, NumBits, State.BufferOffset); // BufferOffset implicitly &31
	
	State.BufferOffset += NumBits;
	State.CompileTimeMinBufferBits    -= CompileTimeMaxBits;
	State.CompileTimeMinDwordBits     -= CompileTimeMaxBits;
	State.CompileTimeMaxRemainingBits -= CompileTimeMaxBits;

	return Result;
}

// C5: inlined the inline for linter not dying reasons
uint2 BitStreamReader_Read2_RW
	(RWByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int2 NumBits, int2 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RW(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RW(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	return uint2(ResultX, ResultY);
}

// C5: inlined the inline for linter not dying reasons
uint3 BitStreamReader_Read3_RW
	(RWByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int3 NumBits, int3 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RW(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RW(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	uint ResultZ = BitStreamReader_Read_RW(InputBuffer, State, NumBits.z, CompileTimeMaxBits.z);
	return uint3(ResultX, ResultY, ResultZ);
}

// C5: inlined the inline for linter not dying reasons
uint4 BitStreamReader_Read4_RW
	(RWByteAddressBuffer InputBuffer, inout FBitStreamReaderState State, int4 NumBits, int4 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RW(InputBuffer, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RW(InputBuffer, State, NumBits.y, CompileTimeMaxBits.y);
	uint ResultZ = BitStreamReader_Read_RW(InputBuffer, State, NumBits.z, CompileTimeMaxBits.z);
	uint ResultW = BitStreamReader_Read_RW(InputBuffer, State, NumBits.w, CompileTimeMaxBits.w);
	return uint4(ResultX, ResultY, ResultZ, ResultW);
}



// C5: inlined the inline for linter not dying reasons
uint BitStreamReader_Read_RORW
	(ByteAddressBuffer InputBufferRO, RWByteAddressBuffer InputBufferRW, bool bRW, inout FBitStreamReaderState State, int NumBits, int CompileTimeMaxBits)
{
	if (CompileTimeMaxBits > State.CompileTimeMinBufferBits)
	{
		// BitBuffer could be out of bits: Reload.

		// Add cumulated offset since last refill. No need to update at every read.
		State.BitOffsetFromAddress += State.BufferOffset;	
		uint Address = State.AlignedByteAddress + ((State.BitOffsetFromAddress >> 5) << 2);

		uint4 Data = bRW ? InputBufferRW.Load4(Address) : InputBufferRO.Load4(Address);


		// Shift bits down to align
		State.BufferBits.x												= BitAlignU32(Data.y,	Data.x,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 32) State.BufferBits.y	= BitAlignU32(Data.z,	Data.y,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 64) State.BufferBits.z	= BitAlignU32(Data.w,	Data.z,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31
		if (State.CompileTimeMaxRemainingBits > 96) State.BufferBits.w	= BitAlignU32(0,		Data.w,	State.BitOffsetFromAddress); // BitOffsetFromAddress implicitly &31

		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits	= min(32, State.CompileTimeMaxRemainingBits);
		State.CompileTimeMinBufferBits	= min(97, State.CompileTimeMaxRemainingBits);	// Up to 31 bits wasted to alignment
	}
	else if (CompileTimeMaxBits > State.CompileTimeMinDwordBits)
	{
		// Bottom dword could be out of bits: Shift down.
		State.BitOffsetFromAddress += State.BufferOffset;

		// Workaround for BitAlignU32(x, y, 32) returning x instead of y.
		// In the common case where State.CompileTimeMinDwordBits != 0, this will be optimized to just BitAlignU32.
		// TODO: Can we get rid of this special case?
		const bool bOffset32 = State.CompileTimeMinDwordBits == 0 && State.BufferOffset == 32;

		State.BufferBits.x											= bOffset32 ? State.BufferBits.y :	BitAlignU32(State.BufferBits.y, State.BufferBits.x, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 32) State.BufferBits.y	= bOffset32 ? State.BufferBits.z :	BitAlignU32(State.BufferBits.z, State.BufferBits.y, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 64) State.BufferBits.z	= bOffset32 ? State.BufferBits.w :	BitAlignU32(State.BufferBits.w, State.BufferBits.z, State.BufferOffset);
		if (State.CompileTimeMinBufferBits > 96) State.BufferBits.w	= bOffset32 ? 0u :					BitAlignU32(0,					State.BufferBits.w, State.BufferOffset);
	
		State.BufferOffset = 0;

		State.CompileTimeMinDwordBits = min(32, State.CompileTimeMaxRemainingBits);
	}

	const uint Result = BitFieldExtractU32(State.BufferBits.x, NumBits, State.BufferOffset); // BufferOffset implicitly &31
	
	State.BufferOffset += NumBits;
	State.CompileTimeMinBufferBits    -= CompileTimeMaxBits;
	State.CompileTimeMinDwordBits     -= CompileTimeMaxBits;
	State.CompileTimeMaxRemainingBits -= CompileTimeMaxBits;

	return Result;
}

// C5: inlined the inline for linter not dying reasons
uint2 BitStreamReader_Read2_RORW
	(ByteAddressBuffer InputBufferRO, RWByteAddressBuffer InputBufferRW, bool bRW, inout FBitStreamReaderState State, int2 NumBits, int2 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.y, CompileTimeMaxBits.y);
	return uint2(ResultX, ResultY);
}

// C5: inlined the inline for linter not dying reasons
uint4 BitStreamReader_Read4_RORW
	(ByteAddressBuffer InputBufferRO, RWByteAddressBuffer InputBufferRW, bool bRW, inout FBitStreamReaderState State, int4 NumBits, int4 CompileTimeMaxBits)
{
	uint ResultX = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.x, CompileTimeMaxBits.x);
	uint ResultY = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.y, CompileTimeMaxBits.y);
	uint ResultZ = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.z, CompileTimeMaxBits.z);
	uint ResultW = BitStreamReader_Read_RORW(InputBufferRO, InputBufferRW, bRW, State, NumBits.w, CompileTimeMaxBits.w);
	return uint4(ResultX, ResultY, ResultZ, ResultW);
}


// Put bits to ByteAddressBuffer at bit offset. NumBits must be <= 31.
void PutBits(RWByteAddressBuffer Output, uint AlignedBaseAddress, uint BitOffset, uint Value, uint NumBits)
{
	uint BitOffsetInDword = (BitOffset & 31u); // &31 is implicit in shifts
	
	uint Bits = Value << BitOffsetInDword;
	uint Address = AlignedBaseAddress + ((BitOffset >> 5) << 2);
	uint EndBitPos = BitOffsetInDword + NumBits;

	uint _;
	if (EndBitPos >= 32)
	{
		uint Mask = 0xFFFFFFFFu << (EndBitPos & 31u);
		Output.InterlockedAnd(Address + 4, Mask, _);
		Output.InterlockedOr(Address + 4, Value >> (32 - BitOffsetInDword).r, _);
	}

	{
		uint Mask = ~BitFieldMaskU32(NumBits, BitOffset);
		Output.InterlockedAnd(Address, Mask, _);
		Output.InterlockedOr(Address, Value << BitOffsetInDword, _);
	}
}

struct FBitStreamWriterState
{
	uint AlignedByteAddress;
	uint BufferBits;
	uint BufferOffset;
	uint BufferMask;
};

FBitStreamWriterState BitStreamWriter_Create_Aligned(uint AlignedBaseAddressInBytes, uint BitOffset)
{
	FBitStreamWriterState State;

	State.AlignedByteAddress = AlignedBaseAddressInBytes + ((BitOffset >> 5) << 2);
	BitOffset &= 31u;

	State.BufferBits = 0;
	State.BufferOffset = BitOffset;
	State.BufferMask = BitFieldMaskU32(BitOffset, 0);

	return State;
}

void BitStreamWriter_Writer(RWByteAddressBuffer Output, inout FBitStreamWriterState State, uint Value, int NumBits, int CompileTimeMaxBits)
{
	State.BufferBits |= Value << State.BufferOffset;

	// State.BufferOffset <= 31
	uint NextBufferOffset = State.BufferOffset + NumBits;
    uint _;
	if (NextBufferOffset >= 32)
	{
		Output.InterlockedAnd(State.AlignedByteAddress, State.BufferMask, _);
		Output.InterlockedOr(State.AlignedByteAddress, State.BufferBits, _);
		State.BufferMask = 0;
		
		// Shifts are mod 32, so we need special handling when shift could be >= 32.
		// State.BufferOffset can only be 0 here if NumBits >= 32 and therefore CompileTimeMaxBits >= 32.
		if (CompileTimeMaxBits >= 32)
			State.BufferBits = State.BufferOffset ? (Value >> (32 - State.BufferOffset)) : 0u;
		else
			State.BufferBits = Value >> (32 - State.BufferOffset);
		State.AlignedByteAddress += 4;
	}

	State.BufferOffset = NextBufferOffset & 31;
}

void BitStreamWriter_Flush(RWByteAddressBuffer Output, inout FBitStreamWriterState State)
{
	if (State.BufferOffset > 0)
	{
		uint _;
		uint Mask = State.BufferMask | ~BitFieldMaskU32(State.BufferOffset, 0);
		Output.InterlockedAnd(State.AlignedByteAddress, Mask, _);
		Output.InterlockedOr(State.AlignedByteAddress, State.BufferBits, _);
	}
}

// Utility functions for packing bits into uints.
// When Position and NumBits can be determined at compile time this should be just as fast as manual bit packing.
uint ReadBits(uint4 Data, inout uint Position, uint NumBits)
{
	uint DwordIndex = Position >> 5;
	uint BitIndex = Position & 31;

	uint Value = Data[DwordIndex] >> BitIndex;
	if (BitIndex + NumBits > 32)
	{
		Value |= Data[DwordIndex + 1] << (32 - BitIndex);
	}

	Position += NumBits;

	uint Mask = ((1u << NumBits) - 1u);
	return Value & Mask;
}

void WriteBits(inout uint4 Data, inout uint Position, uint Value, uint NumBits)
{
	uint DwordIndex = Position >> 5;
	uint BitIndex = Position & 31;

	Data[DwordIndex] |= Value << BitIndex;
	if (BitIndex + NumBits > 32)
	{
		Data[DwordIndex + 1] |= Value >> (32 - BitIndex);
	}

	Position += NumBits;
}


#define NANITE_USE_UNCOMPRESSED_VERTEX_DATA					0
#define NANITE_USE_STRIP_INDICES							1

#define NANITE_MAX_CLUSTER_TRIANGLES						128
#define NANITE_MAX_CLUSTER_VERTICES							256
#define NANITE_MAX_UVS										4

#define NANITE_ROOT_PAGE_GPU_SIZE_BITS						15
#define NANITE_STREAMING_PAGE_GPU_SIZE_BITS					17

#define NANITE_MAX_CLUSTERS_PER_PAGE_BITS					8
#define NANITE_MAX_CLUSTERS_PER_PAGE						256

#define NANITE_MAX_TRANSCODE_GROUPS_PER_PAGE				128

#define NANITE_NUM_PACKED_CLUSTER_FLOAT4S					7
#define NANITE_GPU_PAGE_HEADER_SIZE							16

#define NANITE_MAX_POSITION_QUANTIZATION_BITS				21	// (21*3 = 63) < 64
#define NANITE_MIN_POSITION_PRECISION						-8

#define NANITE_MAX_NORMAL_QUANTIZATION_BITS					15
#define NANITE_MAX_TANGENT_QUANTIZATION_BITS				12
#define NANITE_MAX_TEXCOORD_QUANTIZATION_BITS				15
#define NANITE_MAX_COLOR_QUANTIZATION_BITS					8

#define NANITE_VERTEX_COLOR_MODE_VARIABLE					2

struct FPageHeader
{
	uint	NumClusters;
};

struct FCluster
{
	uint	PageBaseAddress;

	uint	NumVerts;
	uint	PositionOffset;

	uint	NumTris;
	uint	IndexOffset;

	int3	PosStart;
	uint	BitsPerIndex;
	int		PosPrecision;
	uint3	PosBits;
	uint	NormalPrecision;
	uint	TangentPrecision;

	float4	LODBounds;

	float3	BoxBoundsCenter;
	float	LODError;
	float	EdgeLength;

	float3	BoxBoundsExtent;
	uint	Flags;

	uint	AttributeOffset;
	uint	BitsPerAttribute;
	uint	DecodeInfoOffset;
	bool	bHasTangents;
	uint	NumUVs;
	uint	ColorMode;
	uint	UV_Prec;

	uint	ColorMin;
	uint	ColorBits;
	uint	GroupIndex;		// Debug only

	// Material Slow path
	uint	MaterialTableOffset;
	uint	MaterialTableLength;

	uint	VertReuseBatchCountTableOffset;	// dword offset from page base
	uint	VertReuseBatchCountTableSize;	// number of entries, each 4-bit

	// Material Fast path
	uint	Material0Length;
	uint	Material0Index;
	uint 	Material1Length;
	uint	Material1Index;
	uint	Material2Index;

	uint4	VertReuseBatchInfo;
};



uint4 							PageConstants;



FCluster UnpackCluster(uint4 ClusterData[NANITE_NUM_PACKED_CLUSTER_FLOAT4S])
{
	FCluster Cluster;
	Cluster.PageBaseAddress		= 0;

	Cluster.NumVerts			= BitFieldExtractU32(ClusterData[0].x, 9, 0);
	Cluster.PositionOffset		= BitFieldExtractU32(ClusterData[0].x, 23, 9);
	Cluster.NumTris				= BitFieldExtractU32(ClusterData[0].y, 8, 0);
	Cluster.IndexOffset			= BitFieldExtractU32(ClusterData[0].y, 24, 8);

	Cluster.ColorMin			= ClusterData[0].z;
	Cluster.ColorBits			= BitFieldExtractU32(ClusterData[0].w, 16, 0);
	Cluster.GroupIndex			= BitFieldExtractU32(ClusterData[0].w, 16, 16);			// Debug only

	Cluster.PosStart			= ClusterData[1].xyz;
	Cluster.BitsPerIndex		= BitFieldExtractU32(ClusterData[1].w, 4, 0);
	Cluster.PosPrecision		= (int)BitFieldExtractU32(ClusterData[1].w, 5, 4) + NANITE_MIN_POSITION_PRECISION;
	Cluster.PosBits.x			= BitFieldExtractU32(ClusterData[1].w, 5, 9);
	Cluster.PosBits.y			= BitFieldExtractU32(ClusterData[1].w, 5, 14);
	Cluster.PosBits.z			= BitFieldExtractU32(ClusterData[1].w, 5, 19);
	Cluster.NormalPrecision		= BitFieldExtractU32(ClusterData[1].w, 4, 24);
	Cluster.TangentPrecision	= BitFieldExtractU32(ClusterData[1].w, 4, 28);

	Cluster.LODBounds			= asfloat(ClusterData[2]);

	Cluster.BoxBoundsCenter		= asfloat(ClusterData[3].xyz);
	Cluster.LODError			= f16tof32(ClusterData[3].w);
	Cluster.EdgeLength			= f16tof32(ClusterData[3].w >> 16);

	Cluster.BoxBoundsExtent		= asfloat(ClusterData[4].xyz);
	Cluster.Flags				= ClusterData[4].w;

	Cluster.AttributeOffset		= BitFieldExtractU32(ClusterData[5].x, 22,  0);
	Cluster.BitsPerAttribute	= BitFieldExtractU32(ClusterData[5].x, 10, 22);
	Cluster.DecodeInfoOffset	= BitFieldExtractU32(ClusterData[5].y, 22,  0);
	Cluster.bHasTangents		= BitFieldExtractU32(ClusterData[5].y,  1, 22);
	Cluster.NumUVs				= BitFieldExtractU32(ClusterData[5].y,  3, 23);
	Cluster.ColorMode			= BitFieldExtractU32(ClusterData[5].y,  2, 26);
	Cluster.UV_Prec				= ClusterData[5].z;
	const uint MaterialEncoding = ClusterData[5].w;

	// Material Table Range Encoding (32 bits)
	// uint TriStart        :  8;  // max 128 triangles
	// uint TriLength       :  8;  // max 128 triangles
	// uint MaterialIndex   :  6;  // max  64 materials
	// uint Padding         : 10;

	// Material Packed Range - Fast Path (32 bits)
	// uint Material0Index  : 6;  // max  64 materials (0:Material0Length)
	// uint Material1Index  : 6;  // max  64 materials (Material0Length:Material1Length)
	// uint Material2Index  : 6;  // max  64 materials (remainder)
	// uint Material0Length : 7;  // max 128 triangles (num minus one)
	// uint Material1Length : 7;  // max  64 triangles (materials are sorted, so at most 128/2)

	// Material Packed Range - Slow Path (32 bits)
	// uint BufferIndex     : 19; // 2^19 max value (tons, it's per prim)
	// uint BufferLength    : 6;  // max 64 ranges (num minus one)
	// uint Padding         : 7;  // always 127 for slow path. corresponds to Material1Length=127 in fast path

	if (MaterialEncoding < 0xFE000000u)
	{
		// Fast inline path
		Cluster.MaterialTableOffset	= 0;
		Cluster.MaterialTableLength	= 0;		
		Cluster.Material0Index		= BitFieldExtractU32(MaterialEncoding, 6, 0);
		Cluster.Material1Index		= BitFieldExtractU32(MaterialEncoding, 6, 6);
		Cluster.Material2Index		= BitFieldExtractU32(MaterialEncoding, 6, 12);
		Cluster.Material0Length		= BitFieldExtractU32(MaterialEncoding, 7, 18) + 1;
		Cluster.Material1Length		= BitFieldExtractU32(MaterialEncoding, 7, 25);

		Cluster.VertReuseBatchCountTableOffset = 0;
		Cluster.VertReuseBatchCountTableSize = 0;
		Cluster.VertReuseBatchInfo	= ClusterData[6];
	}
	else
	{
		// Slow global search path
		Cluster.MaterialTableOffset = BitFieldExtractU32(MaterialEncoding, 19, 0);
		Cluster.MaterialTableLength	= BitFieldExtractU32(MaterialEncoding, 6, 19) + 1;
		Cluster.Material0Index		= 0;
		Cluster.Material1Index		= 0;
		Cluster.Material2Index		= 0;
		Cluster.Material0Length		= 0;
		Cluster.Material1Length		= 0;

		Cluster.VertReuseBatchCountTableOffset = ClusterData[6].x;
		Cluster.VertReuseBatchCountTableSize = ClusterData[6].y;
		Cluster.VertReuseBatchInfo = 0;
	}

	return Cluster;
}

uint GPUPageIndexToGPUOffset(uint PageIndex)
{
	const uint MaxStreamingPages = PageConstants.y;
	return (min(PageIndex, MaxStreamingPages) << NANITE_STREAMING_PAGE_GPU_SIZE_BITS) + ((uint)max((int)PageIndex - (int)MaxStreamingPages, 0) << NANITE_ROOT_PAGE_GPU_SIZE_BITS);
}

FPageHeader UnpackPageHeader(uint4 Data)
{
	FPageHeader Header;
	Header.NumClusters = Data.x;
	return Header;
}

FPageHeader GetPageHeader(ByteAddressBuffer InputBuffer, uint PageAddress)
{
	return UnpackPageHeader(InputBuffer.Load4(PageAddress));
}

FPageHeader GetPageHeader(RWByteAddressBuffer InputBuffer, uint PageAddress)
{
	return UnpackPageHeader(InputBuffer.Load4(PageAddress));
}

FCluster GetCluster(ByteAddressBuffer InputBuffer, uint SrcBaseOffset, uint ClusterIndex, uint NumPageClusters)
{
	const uint ClusterSOAStride = ( NumPageClusters << 4 );
	const uint ClusterBaseAddress = SrcBaseOffset + ( ClusterIndex << 4 );
	
	uint4 ClusterData[NANITE_NUM_PACKED_CLUSTER_FLOAT4S];
	for(int i = 0; i < NANITE_NUM_PACKED_CLUSTER_FLOAT4S; i++)
	{
		ClusterData[i] = InputBuffer.Load4( ClusterBaseAddress + i * ClusterSOAStride + NANITE_GPU_PAGE_HEADER_SIZE ); // Adding NANITE_GPU_PAGE_HEADER_SIZE inside the loop prevents compiler confusion about offset modifier and generates better code
	}
	
	return UnpackCluster(ClusterData);
}

FCluster GetCluster(RWByteAddressBuffer InputBuffer, uint SrcBaseOffset, uint ClusterIndex, uint NumPageClusters)
{
	const uint ClusterSOAStride = (NumPageClusters << 4);
	const uint ClusterBaseAddress = SrcBaseOffset + (ClusterIndex << 4);

	uint4 ClusterData[NANITE_NUM_PACKED_CLUSTER_FLOAT4S];
	for (int i = 0; i < NANITE_NUM_PACKED_CLUSTER_FLOAT4S; i++)
	{
		ClusterData[i] = InputBuffer.Load4( ClusterBaseAddress + i * ClusterSOAStride + NANITE_GPU_PAGE_HEADER_SIZE );  // Adding NANITE_GPU_PAGE_HEADER_SIZE inside the loop prevents compiler confusion about offset modifier and generates better code
	}
	return UnpackCluster(ClusterData);
}



float3 UnpackPosition(uint2 Packed, FCluster Cluster)
{
	int3 Pos;
	Pos.x = BitFieldExtractU32(Packed.x, Cluster.PosBits.x, 0);

	Packed.x = BitAlignU32(Packed.y, Packed.x, Cluster.PosBits.x);
	Packed.y >>= Cluster.PosBits.x;
	Pos.y = BitFieldExtractU32(Packed.x, Cluster.PosBits.y, 0);

	Packed.x = BitAlignU32(Packed.y, Packed.x, Cluster.PosBits.y);
	Pos.z = BitFieldExtractU32(Packed.x, Cluster.PosBits.z, 0);

	const float Scale = asfloat(asint(1.0f) - (Cluster.PosPrecision << 23));
	return (Pos + Cluster.PosStart) * Scale;
}

struct FNaniteRawAttributeData
{
	float4 TangentX_AndSign;
	float3 TangentZ;
	float4 Color;
	float2 TexCoords[NANITE_MAX_UVS];
};

FNaniteRawAttributeData WaveReadLaneAt(FNaniteRawAttributeData In, uint SrcIndex)
{
	FNaniteRawAttributeData Out;
	Out.TangentX_AndSign = WaveReadLaneAt(In.TangentX_AndSign, SrcIndex);
	Out.TangentZ = WaveReadLaneAt(In.TangentZ, SrcIndex);
	Out.Color = WaveReadLaneAt(In.Color, SrcIndex);

	for (uint i = 0; i < NANITE_MAX_UVS; ++i)
	{
		Out.TexCoords[i] = WaveReadLaneAt(In.TexCoords[i], SrcIndex);
	}
	return Out;
}

#define SIZEOF_UV_RANGE	32
struct FUVRange
{
	int2 Min;
	uint2 GapStart;
	uint2 GapLength;
	int Precision;
};


FUVRange UnpackUVRange(uint4 Data[2])
{
	FUVRange Range;
	Range.Min = (int2) Data[0].xy;
	Range.GapStart = Data[0].zw;
	Range.GapLength = Data[1].xy;
	Range.Precision = Data[1].z;
	return Range;
}

FUVRange GetUVRange(ByteAddressBuffer InputBuffer, uint StartOffset, uint Index)
{
	uint Offset = StartOffset + Index * SIZEOF_UV_RANGE;
	uint4 Data[2];
	Data[0] = InputBuffer.Load4(Offset);
	Data[1] = InputBuffer.Load4(Offset + 16);
	return UnpackUVRange(Data);
}

FUVRange GetUVRange(RWByteAddressBuffer InputBuffer, uint StartOffset, uint Index)
{
	uint Offset = StartOffset + Index * SIZEOF_UV_RANGE;
	uint4 Data[2];
	Data[0] = InputBuffer.Load4(Offset);
	Data[1] = InputBuffer.Load4(Offset + 16);
	return UnpackUVRange(Data);
}

float2 UnpackTexCoord(uint2 Packed, FUVRange UVRange)
{
	uint2 T = Packed + select(Packed > UVRange.GapStart, UVRange.GapLength, 0u);

	const float Scale = asfloat(asint(1.0f) - (UVRange.Precision << 23));
	return float2((int2) T + UVRange.Min) * Scale;
}

float3 UnpackNormal(uint Packed, uint Bits)
{
	uint Mask = BitFieldMaskU32(Bits, 0);
	float2 F = uint2(BitFieldExtractU32(Packed, Bits, 0), BitFieldExtractU32(Packed, Bits, Bits)) * (2.0f / Mask) - 1.0f;
	float3 N = float3(F.xy, 1.0 - abs(F.x) - abs(F.y));
	float T = saturate(-N.z);
	N.xy += select(N.xy >= 0.0, -T, T);
	return normalize(N);
}


uint CalculateMaxAttributeBits(uint NumTexCoordInterpolators)
{
	uint Size = 0u;
	Size += 2u * NANITE_MAX_NORMAL_QUANTIZATION_BITS;
	Size += 1u + NANITE_MAX_TANGENT_QUANTIZATION_BITS;
	Size += 4u * NANITE_MAX_COLOR_QUANTIZATION_BITS;
	Size += NumTexCoordInterpolators * (2u * NANITE_MAX_TEXCOORD_QUANTIZATION_BITS);
	return Size;
}

void DecodeMaterialRange(uint EncodedRange, out uint TriStart, out uint TriLength, out uint MaterialIndex)
{
	// uint32 TriStart      :  8; // max 128 triangles
	// uint32 TriLength     :  8; // max 128 triangles
	// uint32 MaterialIndex :  6; // max  64 materials
	// uint32 Padding       : 10;

	TriStart = BitFieldExtractU32(EncodedRange, 8, 0);
	TriLength = BitFieldExtractU32(EncodedRange, 8, 8);
	MaterialIndex = BitFieldExtractU32(EncodedRange, 6, 16);
}

bool IsMaterialFastPath(FCluster InCluster)
{
	return (InCluster.Material0Length > 0);
}

float3 UnpackTangentX(float3 TangentZ, uint TangentAngleBits, uint NumTangentBits)
{
	const bool bSwapXZ = (abs(TangentZ.z) > abs(TangentZ.x));
	if (bSwapXZ)
		TangentZ.xz = TangentZ.zx;

	const float3 TangentRefX = float3(-TangentZ.y, TangentZ.x, 0.0f);
	const float3 TangentRefY = cross(TangentZ, TangentRefX);

	const float Scale = rsqrt(dot(TangentRefX.xy, TangentRefX.xy));
	
	const float TangentAngle = float(TangentAngleBits) * ((2.0f * PI) / (1u << NumTangentBits));
	float3 TangentX = TangentRefX * (cos(TangentAngle) * Scale) + TangentRefY * (sin(TangentAngle) * Scale);
	if (bSwapXZ)
		TangentX.xz = TangentX.zx;
	return TangentX;
}

struct FPageInstallInfo
{
	uint SrcPageOffset;
	uint DstPageOffset;
	uint PageDependenciesStart;
	uint PageDependenciesNum;
};

uint								StartPageIndex;
StructuredBuffer<FPageInstallInfo>	InstallInfoBuffer;
StructuredBuffer<uint>				PageDependenciesBuffer;
ByteAddressBuffer					SrcPageBuffer;
RWByteAddressBuffer					DstPageBuffer;

// C5: for debugging
RWStructuredBuffer<uint4> TriStripBuffer;
RWStructuredBuffer<uint> MatIdBuffer;
RWByteAddressBuffer PosBuffer;
RWStructuredBuffer<uint4> RefPosBuffer;
RWStructuredBuffer<FNaniteRawAttributeData> AttributeDataBuffer;

struct FPageDiskHeader
{
	uint GpuSize;
	uint NumClusters;
	uint NumRawFloat4s;
	uint NumTexCoords;
	uint NumVertexRefs;
	uint DecodeInfoOffset;
	uint StripBitmaskOffset;
	uint VertexRefBitmaskOffset;
};
#define SIZEOF_PAGE_DISK_HEADER	(8*4)

FPageDiskHeader GetPageDiskHeader(uint PageBaseOffset)
{
	uint4 Data[2];
	Data[0] = SrcPageBuffer.Load4(PageBaseOffset + 0);
	Data[1] = SrcPageBuffer.Load4(PageBaseOffset + 16);

	FPageDiskHeader DiskHeader;
	DiskHeader.GpuSize					= Data[0].x;
	DiskHeader.NumClusters				= Data[0].y;
	DiskHeader.NumRawFloat4s			= Data[0].z;
	DiskHeader.NumTexCoords				= Data[0].w;
	DiskHeader.NumVertexRefs			= Data[1].x;
	DiskHeader.DecodeInfoOffset			= Data[1].y;
	DiskHeader.StripBitmaskOffset		= Data[1].z;
	DiskHeader.VertexRefBitmaskOffset	= Data[1].w;
	return DiskHeader;
}

struct FClusterDiskHeader
{
	uint IndexDataOffset;
	uint PageClusterMapOffset;
	uint VertexRefDataOffset;
	uint PositionDataOffset;
	uint AttributeDataOffset;
	uint NumVertexRefs;
	uint NumPrevRefVerticesBeforeDwords;
	uint NumPrevNewVerticesBeforeDwords;
};

#define SIZEOF_CLUSTER_DISK_HEADER	(8*4)

FClusterDiskHeader GetClusterDiskHeader(uint PageBaseOffset, uint ClusterIndex)
{
	uint ByteOffset = PageBaseOffset + SIZEOF_PAGE_DISK_HEADER + ClusterIndex * SIZEOF_CLUSTER_DISK_HEADER;
	uint4 Data[2];
	Data[0]	= SrcPageBuffer.Load4(ByteOffset);
	Data[1] = SrcPageBuffer.Load4(ByteOffset + 16);
	
	FClusterDiskHeader Header;
	Header.IndexDataOffset					= Data[0].x;
	Header.PageClusterMapOffset				= Data[0].y;
	Header.VertexRefDataOffset				= Data[0].z;
	Header.PositionDataOffset				= Data[0].w;
	Header.AttributeDataOffset				= Data[1].x;
	Header.NumVertexRefs					= Data[1].y;
	Header.NumPrevRefVerticesBeforeDwords	= Data[1].z;
	Header.NumPrevNewVerticesBeforeDwords	= Data[1].w;
	return Header;
}

uint ReadUnalignedDword(ByteAddressBuffer InputBuffer, uint BaseAddressInBytes, int BitOffset)
{
	uint ByteAddress = BaseAddressInBytes + (BitOffset >> 3);
	uint AlignedByteAddress = ByteAddress & ~3;
	BitOffset = ((ByteAddress - AlignedByteAddress) << 3) | (BitOffset & 7);

	uint2 Data = InputBuffer.Load2(AlignedByteAddress);
	return BitAlignU32(Data.y, Data.x, BitOffset);
}


uint ReadByte(ByteAddressBuffer	InputBuffer, uint Address)
{
	return (InputBuffer.Load(Address & ~3u) >> ((Address & 3u)*8)) & 0xFFu;	//TODO: use bytealign intrinsic?
}

uint ReadUnalignedDwordFromAlignedBase(ByteAddressBuffer SrcBuffer, uint AlignedBaseAddress, uint BitOffset)
{
	uint2 Data = SrcBuffer.Load2(AlignedBaseAddress);
	return BitAlignU32(Data.y, Data.x, BitOffset);
}
uint ReadUnalignedDwordFromAlignedBase(RWByteAddressBuffer SrcBuffer, uint AlignedBaseAddress, uint BitOffset)
{
	uint2 Data = SrcBuffer.Load2(AlignedBaseAddress);
	return BitAlignU32(Data.y, Data.x, BitOffset);
}

void CopyBits(RWByteAddressBuffer DstBuffer, uint DstBaseAddress, uint DstBitOffset, ByteAddressBuffer SrcBuffer, uint SrcBaseAddress, uint SrcBitOffset, uint NumBits)
{
	if (NumBits == 0)
		return;

	// TODO: optimize me
	uint DstDword = (DstBaseAddress + (DstBitOffset >> 3)) >> 2;
	DstBitOffset = (((DstBaseAddress & 3u) << 3) + DstBitOffset) & 31u;
	uint SrcDword = (SrcBaseAddress + (SrcBitOffset >> 3)) >> 2;
	SrcBitOffset = (((SrcBaseAddress & 3u) << 3) + SrcBitOffset) & 31u;

	uint DstNumDwords = (DstBitOffset + NumBits + 31u) >> 5;
	uint DstLastBitOffset = (DstBitOffset + NumBits) & 31u;
	
	const uint FirstMask = 0xFFFFFFFFu << DstBitOffset;
	const uint LastMask = DstLastBitOffset ? BitFieldMaskU32(DstLastBitOffset, 0) : 0xFFFFFFFFu;
	const uint Mask = FirstMask & (DstNumDwords == 1 ? LastMask : 0xFFFFFFFFu);

	// C5: added unused var to make linter happy
	uint _;
	{
		uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
		DstBuffer.InterlockedAnd(DstDword * 4, ~Mask, _);
		DstBuffer.InterlockedOr(DstDword * 4, (Data << DstBitOffset) & Mask, _);
		DstDword++;
		DstNumDwords--;
	}

	if (DstNumDwords > 0)
	{
		SrcBitOffset += 32 - DstBitOffset;
		SrcDword += SrcBitOffset >> 5;
		SrcBitOffset &= 31u;

		while (DstNumDwords > 1)
		{
			uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
			DstBuffer.Store(DstDword * 4, Data);
			DstDword++;
			SrcDword++;
			DstNumDwords--;
		}
		
		uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
		DstBuffer.InterlockedAnd(DstDword * 4, ~LastMask, _);
		DstBuffer.InterlockedOr(DstDword * 4, Data & LastMask, _);
	}
}

// C5: Added version that can use RW buffers instead
void CopyBits(RWByteAddressBuffer DstBuffer, uint DstBaseAddress, uint DstBitOffset, RWByteAddressBuffer SrcBuffer, uint SrcBaseAddress, uint SrcBitOffset, uint NumBits)
{
	if (NumBits == 0)
		return;

	// TODO: optimize me
	uint DstDword = (DstBaseAddress + (DstBitOffset >> 3)) >> 2;
	DstBitOffset = (((DstBaseAddress & 3u) << 3) + DstBitOffset) & 31u;
	uint SrcDword = (SrcBaseAddress + (SrcBitOffset >> 3)) >> 2;
	SrcBitOffset = (((SrcBaseAddress & 3u) << 3) + SrcBitOffset) & 31u;

	uint DstNumDwords = (DstBitOffset + NumBits + 31u) >> 5;
	uint DstLastBitOffset = (DstBitOffset + NumBits) & 31u;
	
	const uint FirstMask = 0xFFFFFFFFu << DstBitOffset;
	const uint LastMask = DstLastBitOffset ? BitFieldMaskU32(DstLastBitOffset, 0) : 0xFFFFFFFFu;
	const uint Mask = FirstMask & (DstNumDwords == 1 ? LastMask : 0xFFFFFFFFu);

	uint _;
	{
		uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
		DstBuffer.InterlockedAnd(DstDword * 4, ~Mask, _);
		DstBuffer.InterlockedOr(DstDword * 4, (Data << DstBitOffset) & Mask, _);
		DstDword++;
		DstNumDwords--;
	}

	if (DstNumDwords > 0)
	{
		SrcBitOffset += 32 - DstBitOffset;
		SrcDword += SrcBitOffset >> 5;
		SrcBitOffset &= 31u;

		while (DstNumDwords > 1)
		{
			uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
			DstBuffer.Store(DstDword * 4, Data);
			DstDword++;
			SrcDword++;
			DstNumDwords--;
		}
		
		uint Data = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset);
		DstBuffer.InterlockedAnd(DstDword * 4, ~LastMask, _);
		DstBuffer.InterlockedOr(DstDword * 4, Data & LastMask, _);
	}
}

// Debug only. Performance doesn't matter.
void CopyDwords(RWByteAddressBuffer DstBuffer, uint DstAddress, ByteAddressBuffer SrcBuffer, uint SrcAddress, uint NumDwords)
{
	for(uint i = 0; i < NumDwords; i++)
	{
		DstBuffer.Store(DstAddress + i * 4, SrcBuffer.Load(SrcAddress + i * 4));
	}
}

uint3 UnpackStripIndices(uint SrcPageBaseOffset, FPageDiskHeader PageDiskHeader, FClusterDiskHeader ClusterDiskHeader, uint LocalClusterIndex, uint TriIndex)
{
	const uint DwordIndex = TriIndex >> 5;
	const uint BitIndex = TriIndex & 31u;

	//Bitmask.x: bIsStart, Bitmask.y: bIsLeft, Bitmask.z: bIsNewVertex
	const uint3 StripBitmasks = SrcPageBuffer.Load3(SrcPageBaseOffset + PageDiskHeader.StripBitmaskOffset + (LocalClusterIndex * (NANITE_MAX_CLUSTER_TRIANGLES / 32) + DwordIndex) * 12);

	const uint SMask = StripBitmasks.x;
	const uint LMask = StripBitmasks.y;
	const uint WMask = StripBitmasks.z;
	const uint SLMask = SMask & LMask;

	//const uint HeadRefVertexMask = ( SMask & LMask & WMask ) | ( ~SMask & WMask );
	const uint HeadRefVertexMask = (SLMask | ~SMask) & WMask;	// 1 if head of triangle is ref. S case with 3 refs or L/R case with 1 ref.

	const uint PrevBitsMask = (1u << BitIndex) - 1u;
	
	const uint NumPrevRefVerticesBeforeDword = DwordIndex ? BitFieldExtractU32(ClusterDiskHeader.NumPrevRefVerticesBeforeDwords, 10u, DwordIndex * 10u - 10u) : 0u;
	const uint NumPrevNewVerticesBeforeDword = DwordIndex ? BitFieldExtractU32(ClusterDiskHeader.NumPrevNewVerticesBeforeDwords, 10u, DwordIndex * 10u - 10u) : 0u;

	int CurrentDwordNumPrevRefVertices = (countbits(SLMask & PrevBitsMask) << 1) + countbits(WMask & PrevBitsMask);
	int CurrentDwordNumPrevNewVertices = (countbits(SMask & PrevBitsMask) << 1) + BitIndex - CurrentDwordNumPrevRefVertices;

	int NumPrevRefVertices = NumPrevRefVerticesBeforeDword + CurrentDwordNumPrevRefVertices;
	int NumPrevNewVertices = NumPrevNewVerticesBeforeDword + CurrentDwordNumPrevNewVertices;

	const int IsStart = BitFieldExtractI32(SMask, 1, BitIndex);		// -1: true, 0: false
	const int IsLeft = BitFieldExtractI32(LMask, 1, BitIndex);		// -1: true, 0: false
	const int IsRef = BitFieldExtractI32(WMask, 1, BitIndex);		// -1: true, 0: false

	const uint BaseVertex = NumPrevNewVertices - 1u;

	uint3 OutIndices;
	uint ReadBaseAddress = SrcPageBaseOffset + ClusterDiskHeader.IndexDataOffset;
	uint IndexData = ReadUnalignedDword(SrcPageBuffer, ReadBaseAddress, (NumPrevRefVertices + ~IsStart) * 5);	// -1 if not Start

	if (IsStart)
	{
		const int MinusNumRefVertices = (IsLeft << 1) + IsRef;
		uint NextVertex = NumPrevNewVertices;

		if (MinusNumRefVertices <= -1) { OutIndices.x = BaseVertex - (IndexData & 31u); IndexData >>= 5; }
		else { OutIndices[0] = NextVertex++; }
		if (MinusNumRefVertices <= -2) { OutIndices.y = BaseVertex - (IndexData & 31u); IndexData >>= 5; }
		else { OutIndices[1] = NextVertex++; }
		if (MinusNumRefVertices <= -3) { OutIndices.z = BaseVertex - (IndexData & 31u); }
		else { OutIndices[2] = NextVertex++; }
	}
	else
	{
		// Handle two first vertices
		const uint PrevBitIndex = BitIndex - 1u;
		const int IsPrevStart = BitFieldExtractI32(SMask, 1, PrevBitIndex);
		const int IsPrevHeadRef = BitFieldExtractI32(HeadRefVertexMask, 1, PrevBitIndex);
		//const int NumPrevNewVerticesInTriangle = IsPrevStart ? ( 3u - ( bfe_u32( /*SLMask*/ LMask, PrevBitIndex, 1 ) << 1 ) - bfe_u32( /*SMask &*/ WMask, PrevBitIndex, 1 ) ) : /*1u - IsPrevRefVertex*/ 0u;
		const int NumPrevNewVerticesInTriangle = IsPrevStart & (3u - ((BitFieldExtractU32( /*SLMask*/ LMask, 1, PrevBitIndex) << 1) | BitFieldExtractU32( /*SMask &*/ WMask, 1, PrevBitIndex)));

		//OutIndices[ 1 ] = IsPrevRefVertex ? ( BaseVertex - ( IndexData & 31u ) + NumPrevNewVerticesInTriangle ) : BaseVertex;	// BaseVertex = ( NumPrevNewVertices - 1 );
		OutIndices.y = BaseVertex + (IsPrevHeadRef & (NumPrevNewVerticesInTriangle - (IndexData & 31u)));
		//OutIndices[ 2 ] = IsRefVertex ? ( BaseVertex - bfe_u32( IndexData, 5, 5 ) ) : NumPrevNewVertices;
		OutIndices.z = NumPrevNewVertices + (IsRef & (-1 - BitFieldExtractU32(IndexData, 5, 5)));

		// We have to search for the third vertex. 
		// Left triangles search for previous Right/Start. Right triangles search for previous Left/Start.
		const uint SearchMask = SMask | (LMask ^ IsLeft);				// SMask | ( IsRight ? LMask : RMask );
		const uint FoundBitIndex = firstbithigh(SearchMask & PrevBitsMask);
		const int IsFoundCaseS = BitFieldExtractI32(SMask, 1, FoundBitIndex);		// -1: true, 0: false

		const uint FoundPrevBitsMask = (1u << FoundBitIndex) - 1u;
		int FoundCurrentDwordNumPrevRefVertices = (countbits(SLMask & FoundPrevBitsMask) << 1) + countbits(WMask & FoundPrevBitsMask);
		int FoundCurrentDwordNumPrevNewVertices = (countbits(SMask & FoundPrevBitsMask) << 1) + FoundBitIndex - FoundCurrentDwordNumPrevRefVertices;

		int FoundNumPrevNewVertices = NumPrevNewVerticesBeforeDword + FoundCurrentDwordNumPrevNewVertices;
		int FoundNumPrevRefVertices = NumPrevRefVerticesBeforeDword + FoundCurrentDwordNumPrevRefVertices;

		const uint FoundNumRefVertices = (BitFieldExtractU32(LMask, 1, FoundBitIndex) << 1) + BitFieldExtractU32(WMask, 1, FoundBitIndex);
		const uint IsBeforeFoundRefVertex = BitFieldExtractU32(HeadRefVertexMask, 1, FoundBitIndex - 1);

		// ReadOffset: Where is the vertex relative to triangle we searched for?
		const int ReadOffset = IsFoundCaseS ? IsLeft : 1;
		const uint FoundIndexData = ReadUnalignedDword(SrcPageBuffer, ReadBaseAddress, (FoundNumPrevRefVertices - ReadOffset) * 5);
		const uint FoundIndex = (FoundNumPrevNewVertices - 1u) - BitFieldExtractU32(FoundIndexData, 5, 0);

		bool bCondition = IsFoundCaseS ? ((int)FoundNumRefVertices >= 1 - IsLeft) : IsBeforeFoundRefVertex;
		int FoundNewVertex = FoundNumPrevNewVertices + (IsFoundCaseS ? (IsLeft & (FoundNumRefVertices == 0)) : -1);
		OutIndices.x = bCondition ? FoundIndex : FoundNewVertex;

		// Would it be better to code New verts instead of Ref verts?
		// HeadRefVertexMask would just be WMask?

		if (IsLeft)
		{
			OutIndices.yz = OutIndices.zy;
		}
	}

	return OutIndices;
}

#define TRANSCODE_THREADS_PER_GROUP_BITS	7
#define TRANSCODE_THREADS_PER_GROUP			(1 << TRANSCODE_THREADS_PER_GROUP_BITS)
#define TRANSCODE_THREADS_PER_PAGE			(NANITE_MAX_TRANSCODE_GROUPS_PER_PAGE << TRANSCODE_THREADS_PER_GROUP_BITS)

void TranscodeVertexAttributes(FPageDiskHeader PageDiskHeader, FCluster Cluster, uint DstPageBaseOffset, uint LocalClusterIndex, uint VertexIndex,
								FCluster SrcCluster, FClusterDiskHeader SrcClusterDiskHeader, uint SrcPageBaseOffset, uint SrcLocalClusterIndex, uint SrcCodedVertexIndex,
								bool bIsParentRef, uint ParentGPUPageIndex,
								uint CompileTimeNumTexCoords
)
{
	const uint CompileTimeMaxAttributeBits = CalculateMaxAttributeBits(CompileTimeNumTexCoords);

	const uint BaseAddress = GPUPageIndexToGPUOffset(ParentGPUPageIndex);

	const uint BitsPerAttribute = bIsParentRef ? SrcCluster.BitsPerAttribute : ((SrcCluster.BitsPerAttribute + 7) & ~7u);
	const uint Address = bIsParentRef ? (BaseAddress + SrcCluster.AttributeOffset) : (SrcPageBaseOffset + SrcClusterDiskHeader.AttributeDataOffset);

	FBitStreamWriterState OutputStream = BitStreamWriter_Create_Aligned(DstPageBaseOffset + Cluster.AttributeOffset, VertexIndex * Cluster.BitsPerAttribute);	
	FBitStreamReaderState InputStream = BitStreamReader_Create(Address, SrcCodedVertexIndex * BitsPerAttribute, CompileTimeMaxAttributeBits);

	// Normal
	const uint PackedNormal = BitStreamReader_Read_RORW(SrcPageBuffer, DstPageBuffer, bIsParentRef, InputStream, 2 * Cluster.NormalPrecision, 2 * NANITE_MAX_NORMAL_QUANTIZATION_BITS);
	BitStreamWriter_Writer(DstPageBuffer, OutputStream, PackedNormal, 2 * Cluster.NormalPrecision, 2 * NANITE_MAX_NORMAL_QUANTIZATION_BITS);

	// Tangent
	const int NumTangentBits = (Cluster.bHasTangents ? (1 + Cluster.TangentPrecision) : 0);
	const uint PackedTangent = BitStreamReader_Read_RORW(SrcPageBuffer, DstPageBuffer, bIsParentRef, InputStream, NumTangentBits, 1 + NANITE_MAX_TANGENT_QUANTIZATION_BITS);
	BitStreamWriter_Writer(DstPageBuffer, OutputStream, PackedTangent, NumTangentBits, 1 + NANITE_MAX_TANGENT_QUANTIZATION_BITS);

	// Color
    {
        uint4 SrcComponentBits = UnpackToUint4(SrcCluster.ColorBits, 4);
        uint4 SrcColorDelta = BitStreamReader_Read4_RORW(SrcPageBuffer, DstPageBuffer, bIsParentRef, InputStream, SrcComponentBits,  8 );

        if (Cluster.ColorMode == NANITE_VERTEX_COLOR_MODE_VARIABLE)
        {
            uint SrcPackedColorDelta = SrcColorDelta.x | (SrcColorDelta.y << 8) | (SrcColorDelta.z << 16) | (SrcColorDelta.w << 24);
            uint PackedColor = SrcCluster.ColorMin + SrcPackedColorDelta;

            uint4 DstComponentBits = UnpackToUint4(Cluster.ColorBits, 4);
            uint DstPackedColorDelta = PackedColor - Cluster.ColorMin;

            uint PackedDeltaColor = BitFieldExtractU32(DstPackedColorDelta, 8, 0) |
                                    (BitFieldExtractU32(DstPackedColorDelta, 8, 8) << (DstComponentBits.x)) |
                                    (BitFieldExtractU32(DstPackedColorDelta, 8, 16) << (DstComponentBits.x + DstComponentBits.y)) |
                                    (BitFieldExtractU32(DstPackedColorDelta, 8, 24) << (DstComponentBits.x + DstComponentBits.y + DstComponentBits.z));

            BitStreamWriter_Writer(DstPageBuffer, OutputStream, PackedDeltaColor, DstComponentBits.x + DstComponentBits.y + DstComponentBits.z + DstComponentBits.w, 4 * NANITE_MAX_COLOR_QUANTIZATION_BITS);
        }
    }

	// UVs
	for (uint TexCoordIndex = 0; TexCoordIndex <  CompileTimeNumTexCoords ; TexCoordIndex++)
	{
		const uint SrcU_NumBits		= BitFieldExtractU32(SrcCluster.UV_Prec, 4, TexCoordIndex * 8 + 0);
		const uint SrcV_NumBits		= BitFieldExtractU32(SrcCluster.UV_Prec, 4, TexCoordIndex * 8 + 4);

		const uint DstU_NumBits		= BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8 + 0);
		const uint DstV_NumBits		= BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8 + 4);

		const int2 SrcPackedUV		= BitStreamReader_Read2_RORW(SrcPageBuffer, DstPageBuffer, bIsParentRef, InputStream, int2(SrcU_NumBits, SrcV_NumBits), NANITE_MAX_TEXCOORD_QUANTIZATION_BITS);
        
		FUVRange SrcUVRange;
		if (bIsParentRef)
			SrcUVRange = GetUVRange(DstPageBuffer, BaseAddress + SrcCluster.DecodeInfoOffset, TexCoordIndex);
		else
			SrcUVRange = GetUVRange(SrcPageBuffer, SrcPageBaseOffset + PageDiskHeader.DecodeInfoOffset + SrcLocalClusterIndex * CompileTimeNumTexCoords * 32, TexCoordIndex);

		const FUVRange UVRange	= GetUVRange(SrcPageBuffer, SrcPageBaseOffset + PageDiskHeader.DecodeInfoOffset + LocalClusterIndex * CompileTimeNumTexCoords *  32, TexCoordIndex);
        
		const float Scale		= asfloat(asint(1.0f) + ((UVRange.Precision - SrcUVRange.Precision) << 23));
		const int2 SrcUV		= SrcPackedUV + select(SrcPackedUV > SrcUVRange.GapStart, SrcUVRange.GapLength, 0u) + SrcUVRange.Min;
		int2 DstUV				= int2(round(SrcUV*Scale));
		uint2 DstPackedUV		= (uint2)max(DstUV - UVRange.Min, 0);

		const uint2 GapMid		= UVRange.GapStart + (UVRange.GapLength >> 1);
		const bool2 bOverMid	= DstPackedUV > GapMid;
		
		const uint2 RangeMin	= select(bOverMid, UVRange.GapStart + 1u, 0u);
		const uint2 RangeMax	= select(bOverMid, uint2(BitFieldMaskU32(DstU_NumBits, 0), BitFieldMaskU32(DstV_NumBits, 0)), UVRange.GapStart);
		DstPackedUV				= select(bOverMid, DstPackedUV - UVRange.GapLength, DstPackedUV);
		DstPackedUV				= fastClamp(DstPackedUV, RangeMin, RangeMax);
		
		BitStreamWriter_Writer(DstPageBuffer, OutputStream, (DstPackedUV.y << DstU_NumBits) | DstPackedUV.x, DstU_NumBits + DstV_NumBits, 2 * NANITE_MAX_TEXCOORD_QUANTIZATION_BITS);
	}

    BitStreamWriter_Flush(DstPageBuffer, OutputStream);
}



// C5: non buffer specific version
// Decodes vertex attributes for N vertices. N must be compile-time constant and <= 3.
// Decoding multiple vertices from the same cluster simultaneously tends to generate better code than decoding them individually.
void GetRawAttributeDataN(inout FNaniteRawAttributeData RawAttributeData[3],
	RWByteAddressBuffer ClusterPageData,
	FCluster Cluster,
	uint3 TriIndices,
	uint CompileTimeN,
	uint CompileTimeMaxTexCoords
)
{
	// Always process first UV set. Even if it isn't used, we might still need TangentToWorld.
	CompileTimeMaxTexCoords = max(1, min(NANITE_MAX_UVS, CompileTimeMaxTexCoords));

	const uint DecodeInfoOffset = Cluster.PageBaseAddress + Cluster.DecodeInfoOffset;
	const uint AttributeDataOffset = Cluster.PageBaseAddress + Cluster.AttributeOffset;

	uint i;

	for (i = 0; i < CompileTimeN; i++)
	{
		RawAttributeData[i] = (FNaniteRawAttributeData) 0;
	}

#if NANITE_USE_UNCOMPRESSED_VERTEX_DATA
	uint3 ReadOffset = AttributeDataOffset + TriIndices * Cluster.BitsPerAttribute / 8;
	for(i = 0; i < CompileTimeN; i++)
	{
		RawAttributeData[i].TangentZ = asfloat(ClusterPageData.Load3(ReadOffset[i]));
		ReadOffset[i] += 12;
		if(Cluster.bHasTangents)
		{
			RawAttributeData[i].TangentX_AndSign = asfloat(ClusterPageData.Load4(ReadOffset[i]));
			ReadOffset[i] += 16;
		}
		RawAttributeData[i].Color = float4(UnpackToUint4(ClusterPageData.Load(ReadOffset[i]), 8)) * (1.0f / 255.0f);
		ReadOffset[i] += 4;
	}

	for (uint TexCoordIndex = 0; TexCoordIndex < CompileTimeMaxTexCoords; TexCoordIndex++)
	{
		if(TexCoordIndex < Cluster.NumUVs)
		{
			for (uint i = 0; i < CompileTimeN; i++)
			{
				RawAttributeData[i].TexCoords[TexCoordIndex] = asfloat(ClusterPageData.Load2(ReadOffset[i]));
			}
			ReadOffset += 8;
		}
	}
#else
	const uint CompileTimeMaxAttributeBits = CalculateMaxAttributeBits(CompileTimeMaxTexCoords);

	// Watch out! Make sure control flow around BitStreamReader is always compile-time constant or codegen degrades significantly

	uint4 ColorMin = uint4(UnpackByte0(Cluster.ColorMin), UnpackByte1(Cluster.ColorMin), UnpackByte2(Cluster.ColorMin), UnpackByte3(Cluster.ColorMin));
	const uint4 NumComponentBits = UnpackToUint4(Cluster.ColorBits, 4);

	FBitStreamReaderState AttributeStream[3];

	for (i = 0; i < CompileTimeN; i++)
	{
		AttributeStream[i] = BitStreamReader_Create_Aligned(AttributeDataOffset, TriIndices[i] * Cluster.BitsPerAttribute, CompileTimeMaxAttributeBits);

		const uint NormalBits = BitStreamReader_Read_RW(ClusterPageData, AttributeStream[i], 2 * Cluster.NormalPrecision, 2 * NANITE_MAX_NORMAL_QUANTIZATION_BITS);
		const float3 TangentZ = UnpackNormal(NormalBits, Cluster.NormalPrecision);
		RawAttributeData[i].TangentZ = TangentZ;

		const uint NumTangentBits = Cluster.bHasTangents ? (Cluster.TangentPrecision + 1) : 0u;
		const uint TangentAngleAndSignBits = BitStreamReader_Read_RW(ClusterPageData, AttributeStream[i], NumTangentBits, NANITE_MAX_TANGENT_QUANTIZATION_BITS + 1);
	

		if (Cluster.bHasTangents)
		{
			const bool bTangentYSign = (TangentAngleAndSignBits & (1u << Cluster.TangentPrecision)) != 0;
			const uint TangentAngleBits = BitFieldExtractU32(TangentAngleAndSignBits, Cluster.TangentPrecision, 0);
			RawAttributeData[i].TangentX_AndSign = float4(UnpackTangentX(TangentZ, TangentAngleBits, Cluster.TangentPrecision), bTangentYSign ? -1.0f : 1.0f);
		}
		else
		{
			RawAttributeData[i].TangentX_AndSign = 0.0f;
		}

		const uint4 ColorDelta = BitStreamReader_Read4_RW(ClusterPageData, AttributeStream[i], NumComponentBits, NANITE_MAX_COLOR_QUANTIZATION_BITS);
		RawAttributeData[i].Color = float4(ColorMin + ColorDelta) * (1.0f / 255.0f);
	}


	for (uint TexCoordIndex = 0; TexCoordIndex < CompileTimeMaxTexCoords; ++TexCoordIndex)
	{
		const uint2 UVPrec = uint2(BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8), BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8 + 4));
		
		uint2 UVBits[3];

		for (uint i = 0; i < CompileTimeN; i++)
		{
			UVBits[i] = BitStreamReader_Read2_RW(ClusterPageData, AttributeStream[i], UVPrec, NANITE_MAX_TEXCOORD_QUANTIZATION_BITS);
		}


		if (TexCoordIndex < Cluster.NumUVs)
		{
			FUVRange UVRange = GetUVRange(ClusterPageData, DecodeInfoOffset, TexCoordIndex);

			for (uint i = 0; i < CompileTimeN; i++)
			{
				RawAttributeData[i].TexCoords[TexCoordIndex] = UnpackTexCoord(UVBits[i], UVRange);
			}
		}
	}
#endif
}

// C5: assignable buffer version:
void GetRawAttributeData3(inout FNaniteRawAttributeData RawAttributeData[3],
	RWByteAddressBuffer dataBuffer,
	FCluster Cluster,
	uint3 VertexIndices,
	uint CompileTimeMaxTexCoords
	)
{
	GetRawAttributeDataN(RawAttributeData, dataBuffer, Cluster, VertexIndices, 3, CompileTimeMaxTexCoords);
}

// C5: assignable buffer version:
uint GetRelativeMaterialIndex(RWByteAddressBuffer DataBuffer, FCluster InCluster, uint InTriIndex)
{
	uint MaterialIndex = 0xFFFFFFFF;


	if (IsMaterialFastPath(InCluster))
	{
		if (InTriIndex < InCluster.Material0Length)
		{
			MaterialIndex = InCluster.Material0Index;
		}
		else if (InTriIndex < (InCluster.Material0Length + InCluster.Material1Length))
		{
			MaterialIndex = InCluster.Material1Index;
		}
		else
		{
			MaterialIndex = InCluster.Material2Index;
		}
	}
	else
	{
		uint TableOffset = InCluster.PageBaseAddress + InCluster.MaterialTableOffset * 4;
		for (uint TableEntry = 0; TableEntry < InCluster.MaterialTableLength; ++TableEntry)
		{
			uint EncodedRange = DataBuffer.Load(TableOffset);
			TableOffset += 4;

			uint TriStart;
			uint TriLength;
			uint TriMaterialIndex;
			DecodeMaterialRange(EncodedRange, TriStart, TriLength, TriMaterialIndex);

			if (InTriIndex >= TriStart && InTriIndex < (TriStart + TriLength))
			{
				MaterialIndex = TriMaterialIndex;
				break;
			}
		}
	}

	return MaterialIndex;
}

groupshared uint GroupNumRefsInPrevDwords8888[2];	// Packed byte counts: 8:8:8:8
groupshared uint GroupRefToVertex[NANITE_MAX_CLUSTER_VERTICES];
groupshared uint GroupNonRefToVertex[NANITE_MAX_CLUSTER_VERTICES];

[numthreads(TRANSCODE_THREADS_PER_GROUP, 1, 1)]
void TranscodePageToGPU(uint2	GroupID	: SV_GroupID,
						uint	GroupIndex	: SV_GroupIndex)
{
	uint	LocalPageIndex			= StartPageIndex + GroupID.y;

	FPageInstallInfo InstallInfo	= InstallInfoBuffer[LocalPageIndex];
	uint	SrcPageBaseOffset		= InstallInfo.SrcPageOffset;
	uint	DstPageBaseOffset		= InstallInfo.DstPageOffset;
	
	FPageDiskHeader PageDiskHeader	= GetPageDiskHeader(SrcPageBaseOffset);

	const uint NumTexCoords = PageDiskHeader.NumTexCoords;
	uint SrcPackedClusterOffset = SrcPageBaseOffset + SIZEOF_PAGE_DISK_HEADER + PageDiskHeader.NumClusters * SIZEOF_CLUSTER_DISK_HEADER;
	uint DstPackedClusterOffset = DstPageBaseOffset;

	uint NumRawFloat4s = PageDiskHeader.NumRawFloat4s;
	uint PageThread = (GroupID.x << TRANSCODE_THREADS_PER_GROUP_BITS) | GroupIndex;

	// Raw copy: FPackedClusters, Material Dwords and DecodeInfo.
	for(uint i = PageThread; i < NumRawFloat4s; i += TRANSCODE_THREADS_PER_PAGE)
	{
		uint4 Data = SrcPageBuffer.Load4(SrcPackedClusterOffset + i * 16);
		DstPageBuffer.Store4(DstPackedClusterOffset + i * 16, Data);
	}

	for(uint LocalClusterIndex = GroupID.x; LocalClusterIndex < PageDiskHeader.NumClusters; LocalClusterIndex += NANITE_MAX_TRANSCODE_GROUPS_PER_PAGE)
	{
		FClusterDiskHeader ClusterDiskHeader = GetClusterDiskHeader(SrcPageBaseOffset, LocalClusterIndex);
		FCluster Cluster = GetCluster(SrcPageBuffer, SrcPackedClusterOffset, LocalClusterIndex, PageDiskHeader.NumClusters);
		
		// Decode indices
		if (GroupIndex < Cluster.NumTris)
		{
			uint TriangleIndex = GroupIndex;
#if NANITE_USE_STRIP_INDICES
			uint3 Indices = UnpackStripIndices(SrcPageBaseOffset, PageDiskHeader, ClusterDiskHeader, LocalClusterIndex, TriangleIndex);
#else
			FBitStreamReaderState InputStream = BitStreamReader_Create(SrcPageBaseOffset + ClusterDiskHeader.IndexDataOffset, TriangleIndex * 24, 24);
			uint Indices24 = BitStreamReader_Read_RO(SrcPageBuffer, InputStream, 24, 24);
			uint3 Indices = uint3(Indices24 & 0xFF, (Indices24 >> 8) & 0xFF, (Indices24 >> 16) & 0xFF);
#endif
			// Rotate triangle so first vertex has the lowest index
			if (Indices.y < min(Indices.x, Indices.z)) Indices = Indices.yzx;
			else if (Indices.z < min(Indices.x, Indices.y)) Indices = Indices.zxy;

			// C5: tri strip debug start
			uint DbgRoot = LocalPageIndex * NANITE_MAX_CLUSTERS_PER_PAGE * NANITE_MAX_CLUSTER_TRIANGLES;
			DbgRoot += LocalClusterIndex * NANITE_MAX_CLUSTER_TRIANGLES;
			DbgRoot += TriangleIndex;
			TriStripBuffer[DbgRoot].x = 1;
			TriStripBuffer[DbgRoot].yzw = Indices;
			// C5: tri strip debug end

			// Store triangle as one base index and two 5-bit offsets. Cluster constraints guarantee that the offsets are never larger than 5 bits.
			uint BaseIndex = Indices.x;
			uint Delta0 = Indices.y - BaseIndex;
			uint Delta1 = Indices.z - BaseIndex;

			uint PackedIndices = BaseIndex | (Delta0 << Cluster.BitsPerIndex) | (Delta1 << (Cluster.BitsPerIndex + 5));
			const uint BitsPerTriangle = Cluster.BitsPerIndex + 2 * 5;

			PutBits(DstPageBuffer, DstPageBaseOffset + Cluster.IndexOffset, TriangleIndex * BitsPerTriangle, PackedIndices, BitsPerTriangle);
		}

		// Calculate dword-based prefix sum of ref bitmask
		// TODO: optimize me
		const uint AlignedBitmaskOffset = SrcPageBaseOffset + PageDiskHeader.VertexRefBitmaskOffset + LocalClusterIndex * (NANITE_MAX_CLUSTER_VERTICES / 8);
		GroupMemoryBarrierWithGroupSync();
		if (GroupIndex < 2) GroupNumRefsInPrevDwords8888[GroupIndex] = 0;
		GroupMemoryBarrierWithGroupSync();
		if (GroupIndex < 7) {
			const uint Count = countbits(SrcPageBuffer.Load(AlignedBitmaskOffset + GroupIndex * 4));
			const uint Count8888 = Count * 0x01010101u;	// Broadcast count to all bytes
			const uint Index = GroupIndex + 1;
			InterlockedAdd(GroupNumRefsInPrevDwords8888[Index >> 2], Count8888 << ((Index & 3) << 3));	// Add to bytes above
			if (Cluster.NumVerts > 128 && Index < 4)
			{
				// Add low dword byte counts to all bytes in high dword when there are more than 128 vertices.
				InterlockedAdd(GroupNumRefsInPrevDwords8888[1], Count8888); 
			}
		}
		GroupMemoryBarrierWithGroupSync();

		for (uint VertexIndex = GroupIndex; VertexIndex < Cluster.NumVerts; VertexIndex += TRANSCODE_THREADS_PER_GROUP)
		{
			const uint DwordIndex = VertexIndex >> 5;
			const uint BitIndex = VertexIndex & 31u;
			
			const uint Shift = ((DwordIndex & 3) << 3);
			const uint NumRefsInPrevDwords = (GroupNumRefsInPrevDwords8888[DwordIndex >> 2] >> Shift) & 0xFF;

			const uint DwordMask = SrcPageBuffer.Load(AlignedBitmaskOffset + DwordIndex * 4);
			const uint NumPrevRefVertices = countbits(BitFieldExtractU32(DwordMask, BitIndex, 0)) + NumRefsInPrevDwords;

			const bool bIsRef = (DwordMask & (1u << BitIndex)) != 0u;
			if (bIsRef)
			{
				GroupRefToVertex[NumPrevRefVertices] = VertexIndex;
			}
			else
			{
				const uint NumPrevNonRefVertices = VertexIndex - NumPrevRefVertices;
				GroupNonRefToVertex[NumPrevNonRefVertices] = VertexIndex;
			}
		}
		GroupMemoryBarrierWithGroupSync();

		// Non-Ref vertices
		const uint NumNonRefVertices = Cluster.NumVerts - ClusterDiskHeader.NumVertexRefs;
		for (uint NonRefVertexIndex = GroupIndex; NonRefVertexIndex < NumNonRefVertices; NonRefVertexIndex += TRANSCODE_THREADS_PER_GROUP)
		{
			const uint VertexIndex = GroupNonRefToVertex[NonRefVertexIndex];

#if NANITE_USE_UNCOMPRESSED_VERTEX_DATA
			// Position
			uint3 PositionData = SrcPageBuffer.Load3(SrcPageBaseOffset + ClusterDiskHeader.PositionDataOffset + NonRefVertexIndex * 12);
			DstPageBuffer.Store3(DstPageBaseOffset + Cluster.PositionOffset + VertexIndex * 12, PositionData);

			// Attributes
			CopyDwords(	DstPageBuffer, DstPageBaseOffset + Cluster.AttributeOffset + VertexIndex * Cluster.BitsPerAttribute / 8,
						SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.AttributeDataOffset + NonRefVertexIndex * Cluster.BitsPerAttribute / 8, Cluster.BitsPerAttribute / 32);
#else
			// Position
			const uint PositionBitsPerVertex = Cluster.PosBits.x + Cluster.PosBits.y + Cluster.PosBits.z;
			const uint SrcPositionBitsPerVertex = (PositionBitsPerVertex + 7) & ~7u;
			CopyBits(	DstPageBuffer, DstPageBaseOffset + Cluster.PositionOffset, VertexIndex * PositionBitsPerVertex,
						SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.PositionDataOffset, NonRefVertexIndex * SrcPositionBitsPerVertex, PositionBitsPerVertex);
			
			// C5: vert pos debug start
			uint DbgRoot = LocalPageIndex * NANITE_MAX_CLUSTERS_PER_PAGE * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += LocalClusterIndex * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += VertexIndex;
			DbgRoot *= 16;
			CopyBits(PosBuffer, DbgRoot, 0,
			         SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.PositionDataOffset, NonRefVertexIndex * SrcPositionBitsPerVertex, PositionBitsPerVertex);
			uint2 PackedPos = PosBuffer.Load2(DbgRoot);
			float3 UnpackedPos = UnpackPosition(PackedPos, Cluster);
			PosBuffer.Store(DbgRoot + 0, 1);
			PosBuffer.Store3(DbgRoot + 4, asuint(UnpackedPos));
			// C5: vert pos debug end
			
			// Attributes
			const uint SrcBitsPerAttribute = ((Cluster.BitsPerAttribute + 7) & ~7u);
			CopyBits(	DstPageBuffer, DstPageBaseOffset + Cluster.AttributeOffset, VertexIndex* Cluster.BitsPerAttribute,
						SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.AttributeDataOffset, NonRefVertexIndex* SrcBitsPerAttribute, Cluster.BitsPerAttribute);

#endif
		}
	
		// Ref vertices
		for (uint RefVertexIndex = GroupIndex; RefVertexIndex < ClusterDiskHeader.NumVertexRefs; RefVertexIndex += TRANSCODE_THREADS_PER_GROUP)
		{
			const uint VertexIndex = GroupRefToVertex[RefVertexIndex];
			const uint PageClusterIndex = ReadByte(SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.VertexRefDataOffset + RefVertexIndex);
			const uint PageClusterData = SrcPageBuffer.Load(SrcPageBaseOffset + ClusterDiskHeader.PageClusterMapOffset + PageClusterIndex * 4);

			uint ParentPageIndex = PageClusterData >> NANITE_MAX_CLUSTERS_PER_PAGE_BITS;
			uint SrcLocalClusterIndex = BitFieldExtractU32(PageClusterData, NANITE_MAX_CLUSTERS_PER_PAGE_BITS, 0);
			uint SrcCodedVertexIndex = ReadByte(SrcPageBuffer, SrcPageBaseOffset + ClusterDiskHeader.VertexRefDataOffset + RefVertexIndex + PageDiskHeader.NumVertexRefs);

			// C5: ref vert debug start
			uint DbgRoot = LocalPageIndex * NANITE_MAX_CLUSTERS_PER_PAGE * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += LocalClusterIndex * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += VertexIndex;
			PosBuffer.Store(DbgRoot * 16, 0);
			RefPosBuffer[DbgRoot].x = 1;
			RefPosBuffer[DbgRoot].y = ParentPageIndex;
			RefPosBuffer[DbgRoot].z = SrcLocalClusterIndex;
			RefPosBuffer[DbgRoot].w = SrcCodedVertexIndex;
			// C5: ref vert debug end

			FClusterDiskHeader SrcClusterDiskHeader = GetClusterDiskHeader(SrcPageBaseOffset, SrcLocalClusterIndex);
			FCluster SrcCluster;
			uint ParentGPUPageIndex = 0;
			
			const bool bIsParentRef = (ParentPageIndex != 0);
			if (bIsParentRef)
			{
				ParentGPUPageIndex = PageDependenciesBuffer[InstallInfo.PageDependenciesStart + (ParentPageIndex - 1)];
				uint ParentPageAddress = GPUPageIndexToGPUOffset(ParentGPUPageIndex);
				FPageHeader ParentPageHeader = GetPageHeader(DstPageBuffer, ParentPageAddress);
				SrcCluster = GetCluster(DstPageBuffer, ParentPageAddress, SrcLocalClusterIndex, ParentPageHeader.NumClusters);
			}
			else
			{
				SrcCluster = GetCluster(SrcPageBuffer, SrcPackedClusterOffset, SrcLocalClusterIndex, PageDiskHeader.NumClusters);
			}
			
			// Transcode position 
			{
				int3 SrcPosition;
				if (bIsParentRef)
				{
					uint BaseAddress = GPUPageIndexToGPUOffset(ParentGPUPageIndex) + SrcCluster.PositionOffset;
					uint SrcPositionBitsPerVertex = SrcCluster.PosBits.x + SrcCluster.PosBits.y + SrcCluster.PosBits.z;
					FBitStreamReaderState InputStream = BitStreamReader_Create(BaseAddress, SrcCodedVertexIndex * SrcPositionBitsPerVertex, 3 * NANITE_MAX_POSITION_QUANTIZATION_BITS);
					SrcPosition = BitStreamReader_Read3_RW(DstPageBuffer, InputStream, SrcCluster.PosBits, NANITE_MAX_POSITION_QUANTIZATION_BITS);
				}
				else
				{
					uint BaseAddress = SrcPageBaseOffset + SrcClusterDiskHeader.PositionDataOffset;
					uint SrcPositionBitsPerVertex = (SrcCluster.PosBits.x + SrcCluster.PosBits.y + SrcCluster.PosBits.z + 7) & ~7u;
					FBitStreamReaderState InputStream = BitStreamReader_Create(BaseAddress, SrcCodedVertexIndex * SrcPositionBitsPerVertex, 3 * NANITE_MAX_POSITION_QUANTIZATION_BITS);
					SrcPosition = BitStreamReader_Read3_RO(SrcPageBuffer, InputStream, SrcCluster.PosBits, NANITE_MAX_POSITION_QUANTIZATION_BITS);
				}

				int3 DstPosition = SrcPosition + SrcCluster.PosStart - Cluster.PosStart;
				const uint PositionBitsPerVertex = Cluster.PosBits.x + Cluster.PosBits.y + Cluster.PosBits.z;
				
				FBitStreamWriterState OutputStream = BitStreamWriter_Create_Aligned(DstPageBaseOffset + Cluster.PositionOffset, VertexIndex * PositionBitsPerVertex);
				BitStreamWriter_Writer(DstPageBuffer, OutputStream, DstPosition.x, Cluster.PosBits.x, NANITE_MAX_POSITION_QUANTIZATION_BITS);
				BitStreamWriter_Writer(DstPageBuffer, OutputStream, DstPosition.y, Cluster.PosBits.y, NANITE_MAX_POSITION_QUANTIZATION_BITS);
				BitStreamWriter_Writer(DstPageBuffer, OutputStream, DstPosition.z, Cluster.PosBits.z, NANITE_MAX_POSITION_QUANTIZATION_BITS);
				BitStreamWriter_Flush(DstPageBuffer, OutputStream);
			}

			// Specialize vertex transcoding codegen for each of the possible values for NumTexCoords
			if (NumTexCoords == 0)
			{
				TranscodeVertexAttributes(PageDiskHeader, Cluster, DstPageBaseOffset, LocalClusterIndex, VertexIndex,
					SrcCluster, SrcClusterDiskHeader, SrcPageBaseOffset, SrcLocalClusterIndex, SrcCodedVertexIndex, bIsParentRef, ParentGPUPageIndex, 0);
			}
			else if(NumTexCoords == 1)
            {
                TranscodeVertexAttributes(PageDiskHeader, Cluster, DstPageBaseOffset, LocalClusterIndex, VertexIndex,
                    SrcCluster, SrcClusterDiskHeader, SrcPageBaseOffset, SrcLocalClusterIndex, SrcCodedVertexIndex, bIsParentRef, ParentGPUPageIndex, 1);
            }
            else if(NumTexCoords == 2)
            {
                TranscodeVertexAttributes(PageDiskHeader, Cluster, DstPageBaseOffset, LocalClusterIndex, VertexIndex,
                    SrcCluster, SrcClusterDiskHeader, SrcPageBaseOffset, SrcLocalClusterIndex, SrcCodedVertexIndex, bIsParentRef, ParentGPUPageIndex, 2);
            }
            else if(NumTexCoords == 3)
            {
                TranscodeVertexAttributes(PageDiskHeader, Cluster, DstPageBaseOffset, LocalClusterIndex, VertexIndex,
                    SrcCluster, SrcClusterDiskHeader, SrcPageBaseOffset, SrcLocalClusterIndex, SrcCodedVertexIndex, bIsParentRef, ParentGPUPageIndex, 3);
            }
            else if(NumTexCoords == 4)
            {
                TranscodeVertexAttributes(PageDiskHeader, Cluster, DstPageBaseOffset, LocalClusterIndex, VertexIndex,
                    SrcCluster, SrcClusterDiskHeader, SrcPageBaseOffset, SrcLocalClusterIndex, SrcCodedVertexIndex, bIsParentRef, ParentGPUPageIndex, 4);
            }
		}
		GroupMemoryBarrierWithGroupSync();

		// C5: Data exfiltration start
		for (uint VertexIndex = GroupIndex; VertexIndex < Cluster.NumVerts; VertexIndex += TRANSCODE_THREADS_PER_GROUP) {
			// get cluster
			uint page_addr = InstallInfoBuffer[LocalPageIndex].DstPageOffset;
			FPageHeader page_header = GetPageHeader(DstPageBuffer, page_addr);
			FCluster dst_cluster = GetCluster(DstPageBuffer, page_addr, LocalClusterIndex, page_header.NumClusters);
			dst_cluster.PageBaseAddress = page_addr;
			// get packed pos
			const uint BitsPerVertex = dst_cluster.PosBits.x + dst_cluster.PosBits.y + dst_cluster.PosBits.z;
			const uint BitOffset = VertexIndex * BitsPerVertex;	// TODO: Use Mul24
			uint3 Data = DstPageBuffer.Load3(dst_cluster.PageBaseAddress + dst_cluster.PositionOffset + ((BitOffset >> 5) << 2));
			uint2 packed_pos = uint2(BitAlignU32(Data.y, Data.x, BitOffset), BitAlignU32(Data.z, Data.y, BitOffset));
			// unpack pos
			float3 unpacked_pos = UnpackPosition(packed_pos, dst_cluster);

			// C5: ref vert debug start
			uint DbgRoot = LocalPageIndex * NANITE_MAX_CLUSTERS_PER_PAGE * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += LocalClusterIndex * NANITE_MAX_CLUSTER_VERTICES;
			DbgRoot += VertexIndex;
			DbgRoot *= 16;
			PosBuffer.Store(DbgRoot, 1);
			PosBuffer.Store3(DbgRoot + 4, asuint(unpacked_pos));
			// C5: ref vert debug end
		}

		if (GroupIndex < Cluster.NumTris)
		{
			uint TriangleIndex = GroupIndex;

			uint DbgRoot = LocalPageIndex * NANITE_MAX_CLUSTERS_PER_PAGE * NANITE_MAX_CLUSTER_TRIANGLES;
			DbgRoot += LocalClusterIndex * NANITE_MAX_CLUSTER_TRIANGLES;
			DbgRoot += TriangleIndex;
			
			uint4 strip = TriStripBuffer[DbgRoot];
			if (strip.x == 1) {
				uint page_addr = InstallInfoBuffer[LocalPageIndex].DstPageOffset;
				FPageHeader page_header = GetPageHeader(DstPageBuffer, page_addr);
				FCluster dst_cluster = GetCluster(DstPageBuffer, page_addr, LocalClusterIndex, page_header.NumClusters);
				dst_cluster.PageBaseAddress = page_addr;

				FNaniteRawAttributeData data[3];
				GetRawAttributeData3(data, DstPageBuffer, dst_cluster, strip.yzw, NANITE_MAX_UVS);
				AttributeDataBuffer[(DbgRoot * 3) + 0] = data[0];
				AttributeDataBuffer[(DbgRoot * 3) + 1] = data[1];
				AttributeDataBuffer[(DbgRoot * 3) + 2] = data[2];

				MatIdBuffer[DbgRoot] = GetRelativeMaterialIndex(DstPageBuffer, dst_cluster, TriangleIndex);
			}
		}
	}
}
