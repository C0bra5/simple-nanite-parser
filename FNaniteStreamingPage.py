from unreal_io import *
from nanite_constants import *
from typing import BinaryIO, Annotated
import FResources
import io
import os
import enum
import math


class FPageDiskHeader:

	def __init__(self, f: BinaryIO):
		self.GpuSize = read_u32(f)
		self.NumClusters = read_u32(f)
		self.NumRawFloat4s = read_u32(f)
		self.NumTexCoords = read_u32(f)
		self.NumVertexRefs = read_u32(f)
		self.DecodeInfoOffset = read_u32(f)
		self.StripBitmaskOffset = read_u32(f)
		self.VertexRefBitmaskOffset = read_u32(f)

class FPageGPUHeader:
	def __init__(self, f: BinaryIO):
		self.NumClusters = read_u32(f)
		f.seek(12, os.SEEK_CUR)
    	
class FFixupChunk:

	class FHierarchyFixup:
		def __init__(self, f: BinaryIO):
			self.PageIndex = read_u32(f)

			HierarchyNodeAndChildIndex = read_u32(f)
			self.NodeIndex = HierarchyNodeAndChildIndex >> 6
			self.ChildIndex = HierarchyNodeAndChildIndex & 0b111111

			self.ClusterGroupPartStartIndex = read_u32(f)
			
			PageDependencyStartAndNum = read_u32(f)
			self.PageDependencyStart = PageDependencyStartAndNum >> 3
			self.PageDependencyNum = PageDependencyStartAndNum & 0b111
			
	
	class FClusterFixup:
		def __init__(self, f: BinaryIO):
			PageAndClusterIndex = read_u32(f)
			self.PageIndex = PageAndClusterIndex >> 8
			self.ClusterIndex = PageAndClusterIndex & 0xFF

			PageDependencyStartAndNum = read_u32(f)
			self.PageDependencyStart = PageDependencyStartAndNum >> 3
			self.PageDependencyNum = PageDependencyStartAndNum & 0b111

	class FFixupChunkHeader:
		def __init__(self, f: BinaryIO):
			read_magic(f, NANITE_FIXUP_MAGIC)
			self.NumClusters = read_u16(f)
			self.NumHierachyFixups = read_u16(f)
			self.NumClusterFixups = read_u16(f)
	
	def __init__(self, f: BinaryIO):
		self.Header = FFixupChunk.FFixupChunkHeader(f)
		self.HierarchyFixups = read_list_with_len(f, self.Header.NumHierachyFixups, FFixupChunk.FHierarchyFixup)
		self.ClusterFixups = read_list_with_len(f, self.Header.NumClusterFixups, FFixupChunk.FClusterFixup)

class FClusterDiskHeader:
	def __init__(self, f: BinaryIO):
		self.IndexDataOffset = read_u32(f)
		self.PageClusterMapOffset = read_u32(f)
		self.VertexRefDataOffset = read_u32(f)
		self.PositionDataOffset = read_u32(f)
		self.AttributeDataOffset = read_u32(f)
		self.NumVertexRefs = read_u32(f)
		self.NumPrevRefVerticesBeforeDwords = read_u32(f)
		self.NumPrevNewVerticesBeforeDwords = read_u32(f)

class FCluster:

	class FColorBits:
		def __init__(self, r: BinaryIO|int, g: int|None = None, b: int|None = None, a:int|None= None):
			if isinstance(r, int) and isinstance(g, int) and isinstance(b, int) and isinstance(a, int):
				self.R: int = r
				self.G: int = g
				self.B: int = b
				self.A: int = a
			elif isinstance(r, io.IOBase):
				self.R, self.G, self.B, self.A = read_bitfield(read_u16(r), 4,4,4,4)
			else:
				raise ValueError("Bad arg types!")
			
		def __repl__(self):
			return f'FColorBits({self.R},{self.G},{self.B},{self.A})'

	class FClusterFlags(enum.IntFlag):
		ROOT_LEAF = enum.auto()
		"""Cluster is leaf when only root pages are streamed in"""
		STREAMING_LEAF = enum.auto()
		"""Cluster is a leaf in the current streaming state"""
		ROOT_FULL_LEAF = enum.auto()
		"""Cluster is a leaf when fully streamed in"""
		ROOT_ROOT_GROUP = enum.auto()
		"""Cluster is in a group that is fully inside the root pages"""

	class FUV_Prec:
		def __init__(self, u: BinaryIO|int, v: int|None = None):
			if isinstance(u, int) and isinstance(v, int):
				self.U: int = u
				self.V: int = v
			elif isinstance(u, io.IOBase):
				self.U, self.V = read_bitfield(read_u8(u), 4,4)
			else:
				raise ValueError("Bad arg types!")

		def __repr__(self):
			return f'FUV_Prec({self.U}, {self.V})'

	class FColorMode(enum.Enum):
		WHITE = 0
		CONSTANT = 1
		VARIABLE = 2

	def __init__(self, f: BinaryIO):
		origin = f.tell()
		# SOA0
		self.NumVerts, self.PositionOffset = read_bitfield(read_u32(f), 9,23)
		self.NumTris = read_u8(f)
		self.IndexOffset = read_u24(f)
		self.ColorMin = read_u32(f)
		self.ColorBits = FCluster.FColorBits(f)
		self.GroupIndex = read_u16(f) # debug only
		# SOA1
		self.PosStart = FIntVector3(f)
		self.PosBits = FUIntVector3(0,0,0)
		(
			self.BitsPerIndex,
			self.PosPrecision,
			self.PosBits.x,
			self.PosBits.y,
			self.PosBits.z,
			self.NormalPrecision,
			self.TangentPrecision
		) = read_bitfield(read_u32(f), 4,5,5,5,5,4,4)
		self.PosPrecision += NANITE_MIN_POSITION_PRECISION
		# SOA2
		self.LODBounds = FVector4f(f)
		# SOA3
		self.BoxBoundsCenter = FVector3f(f)
		self.LODError = read_f16(f)
		self.EdgeLength = read_f16(f)
		# SOA4
		self.BoxBoundsExtent = FVector3f(f)
		self.Flags = FCluster.FClusterFlags(read_u32(f))
		# SOA5
		self.AttributeOffset, self.BitsPerAttribute = read_bitfield(read_u32(f), 22,10)
		self.DecodeInfoOffset, self.HasTangents, self.NumUVs, ColorMode = read_bitfield(read_u32(f), 22,1,3,2)
		self.HasTangents = bool(self.HasTangents)
		self.ColorMode = FCluster.FColorMode(ColorMode)
		self.UV_PREC = [FCluster.FUV_Prec(f) for _ in range(4)]
		PackedMaterialTable = read_u32(f)

		if PackedMaterialTable < 0xFE000000:
			# Fast inline path
			self.MaterialTableOffset = 0
			self.MaterialTableLength = 0		
			(
				self.Material0Index,
				self.Material1Index,
				self.Material2Index,
				self.Material0Length,
				self.Material1Length,
			) = read_bitfield(PackedMaterialTable, 6, 6, 6, 7, 7)
			self.Material0Length += 1
			# SOA6
			self.VertReuseBatchCountTableOffset = 0
			self.VertReuseBatchCountTableSize = 0
			self.VertReuseBatchInfo	= FUIntVector4(f)
		else:
			# Slow global search path
			(
				self.MaterialTableOffset,
				self.MaterialTableLength
			) = read_bitfield(PackedMaterialTable, 19, 6)
			self.MaterialTableLength += 1
			self.Material0Index = 0
			self.Material1Index = 0
			self.Material2Index = 0
			self.Material0Length = 0
			self.Material1Length = 0
			# SOA6
			self.VertReuseBatchCountTableOffset = read_u32(f)
			self.VertReuseBatchCountTableSize = read_u32(f)
			self.VertReuseBatchInfo = 0
			f.seek(8, os.SEEK_CUR)
		assert(f.tell() - origin == 16 * 7)

		# custom stuff
		self.StripIndices: list[FUIntVector3] = [None] * self.NumTris
		self.Vertices: list[FVertex] = [None] * self.NumVerts
		self.local_page_index: int = None
		self.local_cluster_index: int = None

_precision_lookup = {}
for i in range (-32, 32):
	_precision_lookup[i] = 2.0 ** -(i)

# bits are dword alligned so we gotta do a bit of logic to unfuck the layout
def GetPos(SrcBuffer: BinaryIO, SrcBaseAddress: uint, SrcBitOffset: uint, Cluster: FCluster) -> int:
	NumBits = Cluster.PosBits.x + Cluster.PosBits.y + Cluster.PosBits.z
	if NumBits == 0:
		return 0
	with io.BytesIO(b'\x00' * 8) as buf:
		buf.seek(0, os.SEEK_SET)
		CopyBits(buf, 0, 0, SrcBuffer, SrcBaseAddress, SrcBitOffset, NumBits)
		buf.seek(0, os.SEEK_SET)

		Packed = FUIntVector2(buf)
		Pos = FIntVector3(0, 0, 0)
		Pos.x = BitFieldExtractU32(Packed.x, Cluster.PosBits.x, 0)

		Packed.x = BitAlignU32(Packed.y, Packed.x, Cluster.PosBits.x)
		Packed.y >>= Cluster.PosBits.x
		Pos.y = BitFieldExtractU32(Packed.x, Cluster.PosBits.y, 0)

		Packed.x = BitAlignU32(Packed.y, Packed.x, Cluster.PosBits.y)
		Pos.z = BitFieldExtractU32(Packed.x, Cluster.PosBits.z, 0)

		Scale = _precision_lookup[Cluster.PosPrecision]
		ret = FVertex(
			(Pos.x + Cluster.PosStart.x) * Scale,
			(Pos.y + Cluster.PosStart.y) * Scale,
			(Pos.z + Cluster.PosStart.z) * Scale
		)
		return ret

	
def CopyBits(
		DstBuffer: BinaryIO, DstBaseAddress: uint, DstBitOffset: uint,
		SrcBuffer: BinaryIO, SrcBaseAddress: uint, SrcBitOffset: uint, NumBits: uint
	):

	if NumBits == 0:
		return

	# TODO: optimize me
	DstDword: uint = (DstBaseAddress + (DstBitOffset >> 3)) >> 2
	DstBitOffset = ((u32_rshift((DstBaseAddress & 3), 3) & 0xFFFFFFFF) + DstBitOffset) & 31
	SrcDword: uint = (SrcBaseAddress + (SrcBitOffset >> 3)) >> 2
	SrcBitOffset = ((u32_rshift((SrcBaseAddress & 3), 3) & 0xFFFFFFFF) + SrcBitOffset) & 31

	DstNumDwords: uint = (DstBitOffset + NumBits + 31) >> 5
	DstLastBitOffset: uint = (DstBitOffset + NumBits) & 31
	
	FirstMask: uint = u32_rshift(0xFFFFFFFF, DstBitOffset)
	LastMask: uint = BitFieldMaskU32(DstLastBitOffset, 0) if DstLastBitOffset else 0xFFFFFFFF
	Mask: uint = FirstMask & (LastMask if DstNumDwords == 1 else 0xFFFFFFFF)

	if True:
		Data:uint = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset)
		DstBuffer.seek(DstDword * 4)
		dst_data:uint = read_u32(DstBuffer)
		dst_data &= ~Mask
		dst_data |= u32_rshift(Data, DstBitOffset) & Mask
		DstBuffer.seek(DstDword * 4)
		DstBuffer.write(struct.pack('<I', dst_data))
		DstDword += 1
		DstNumDwords -= 1

	if DstNumDwords > 0:
		SrcBitOffset += 32 - DstBitOffset
		SrcDword += SrcBitOffset >> 5
		SrcBitOffset &= 31

		while DstNumDwords > 1:
			Data: uint = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset)
			DstBuffer.write(DstDword * 4, Data)
			DstDword += 1
			SrcDword += 1
			DstNumDwords -= 1
		
		Data:uint = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset)
		dst_data:uint = read_u32(DstBuffer)
		dst_data &= ~LastMask
		dst_data |= Data & LastMask
		DstBuffer.seek(DstDword * 4)
		DstBuffer.write(struct.pack('<I', dst_data))

class FNaniteStreamingPage:
	def __init__(self, f: BinaryIO, PageStreamingState: 'FResources.FPageStreamingState', Resources: 'FResources.FResources'):
		# read headers
		origin = f.tell()
		self.Fixups = FFixupChunk(f)
		assert(f.tell() - origin == PageStreamingState.BulkSize - PageStreamingState.PageSize)
		
		MaxStreamingPages = 512 * 1024 * 1024 // u32_rshift(1, 17) # 4096
		assert(MaxStreamingPages + 2048 <= u32_rshift(1, 16))

		# apply higharchy fixups
		for Fixup in self.Fixups.HierarchyFixups:
			HierarchyNodeIndex = Fixup.NodeIndex
			assert(HierarchyNodeIndex < len(Resources.HierarchyNodes))
			ChildIndex = Fixup.ChildIndex
			GroupStartIndex = Fixup.ClusterGroupPartStartIndex
			TargetGPUPageIndex = MaxStreamingPages + Resources.RootPageIndex + Fixup.PageIndex
			ChildStartReference = u32_rshift(TargetGPUPageIndex, 8) | GroupStartIndex

			# Only install part if it has no other dependencies
			if Fixup.PageDependencyNum == 0:
				Resources.HierarchyNodes[HierarchyNodeIndex][ChildIndex].ChildStartReference = ChildStartReference
		
		SrcPageBaseOffset = f.tell()
		self.PageDiskHeader = FPageDiskHeader(f)
		assert(f.tell() - SrcPageBaseOffset == 8*4)

		self.ClusterDiskHeaders: list[FClusterDiskHeader] = read_list_with_len(f, self.Fixups.Header.NumClusters, FClusterDiskHeader)
		self.GPUPageHeader = FPageGPUHeader(f)
		assert(self.GPUPageHeader.NumClusters == self.Fixups.Header.NumClusters)
		assert(self.GPUPageHeader.NumClusters == len(self.ClusterDiskHeaders))

		self.Clusters: list[FCluster] = list()
		origin = f.tell()
		NUM_CLUSTERS = len(self.ClusterDiskHeaders)
		RF4_STRIDE = 16
		SOA_STRIDE = RF4_STRIDE * NUM_CLUSTERS
		R4F_ARRAY_COUNT = 7
		with io.BytesIO() as buffer:
			for ClusterIndex in range(NUM_CLUSTERS):
				buffer.seek(0, os.SEEK_SET)
				for SOA_Offset in range(R4F_ARRAY_COUNT):
					f.seek(origin + (RF4_STRIDE * ClusterIndex) + (SOA_STRIDE * SOA_Offset), os.SEEK_SET)
					buffer.write(f.read(RF4_STRIDE))
				buffer.flush()
				buffer.seek(0, os.SEEK_SET)
				self.Clusters.append(FCluster(buffer))

		f4len = f.tell() - origin
		assert(f4len ==  NUM_CLUSTERS * RF4_STRIDE * R4F_ARRAY_COUNT)
		
		# Skipping the parsing for now since compute shader is doing a better and faster job at this
		# # this could probably be multi-threaded to hell and back
		# for LocalClusterIndex in range(NUM_CLUSTERS):
		# 	# get releavent clusters
		# 	Cluster = self.Clusters[LocalClusterIndex]
		# 	ClusterDiskHeader = self.ClusterDiskHeaders[LocalClusterIndex]
			
		# 	# unpack strip indices
		# 	for TriangleIndex in range(Cluster.NumTris):
		# 		Indices = FNaniteStreamingPage.UnpackStripIndices(f, SrcPageBaseOffset, self.PageDiskHeader, ClusterDiskHeader, LocalClusterIndex, TriangleIndex)
		# 		assert (Indices.x != Indices.y)
		# 		assert (Indices.x != Indices.z)
		# 		assert (Indices.z != Indices.y)
		# 		# Rotate triangle so first vertex has the lowest index
		# 		if Indices.y < min(Indices.x, Indices.z):
		# 			Indices.x, Indices.y, Indices.z = Indices.yzx()
		# 		elif Indices.z < min(Indices.x, Indices.y):
		# 			Indices.x, Indices.y, Indices.z = Indices.zxy()

		# 		Cluster.StripIndices[TriangleIndex] = Indices
		# 		assert(len(Cluster.StripIndices) <= NANITE_MAX_CLUSTER_TRIANGLES)
		# 		# # Store triangle as one base index and two 5-bit offsets.
		# 		# # Cluster constraints guarantee that the offsets are never larger than 5 bits.
		# 		# BaseIndex: uint = Indices.x
		# 		# Delta0: uint = Indices.y - BaseIndex
		# 		# Delta1: uint = Indices.z - BaseIndex

		# 		# PackedIndices: uint = BaseIndex | (Delta0 << Cluster.BitsPerIndex) | (Delta1 << (Cluster.BitsPerIndex + 5))
		# 		# BitsPerTriangle: uint = Cluster.BitsPerIndex + 2 * 5
			
		# 	# no clue what this does it but does something!
		# 	AlignedBitmaskOffset: uint = SrcPageBaseOffset + self.PageDiskHeader.VertexRefBitmaskOffset + LocalClusterIndex * 32 # NANITE_MAX_CLUSTER_VERTICES / 8
		# 	GroupNumRefsInPrevDwords8888 = [0,0]
		# 	for GroupIndex in range(7):
		# 		f.seek(AlignedBitmaskOffset + GroupIndex * 4, os.SEEK_SET)
		# 		Count:uint = int.bit_count(read_u32(f))
		# 		Count8888: uint = Count * 0x01010101; # Broadcast count to all bytes
		# 		Index: uint = GroupIndex + 1
		# 		GroupNumRefsInPrevDwords8888[Index >> 2] += u32_rshift(Count8888, u32_rshift((Index & 3), 3)) # Add to bytes above
		# 		if Cluster.NumVerts > 128 and Index < 4:
		# 			# Add low dword byte counts to all bytes in high dword when there are more than 128 vertices.
		# 			GroupNumRefsInPrevDwords8888[1] += Count8888
		# 	assert(len(GroupNumRefsInPrevDwords8888) == 2)
			
		# 	# this could also be parallelized
		# 	GroupRefToVertex = [0] * 256
		# 	GroupNonRefToVertex = [0] * 256

		# 	for VertexIndex in range(Cluster.NumVerts):
		# 		DwordIndex: uint = VertexIndex >> 5
		# 		BitIndex: uint = VertexIndex & 31

		# 		Shift: uint = u32_rshift((DwordIndex & 3), 3)
		# 		NumRefsInPrevDwords: uint = (GroupNumRefsInPrevDwords8888[DwordIndex >> 2] >> Shift) & 0xFF
		# 		f.seek(AlignedBitmaskOffset + DwordIndex * 4, os.SEEK_SET)
		# 		DwordMask: uint = read_u32(f)
		# 		NumPrevRefVertices: uint = int.bit_count(BitFieldExtractU32(DwordMask, BitIndex, 0)) + NumRefsInPrevDwords

		# 		if (DwordMask & u32_rshift(1, BitIndex)) != 0:
		# 			GroupRefToVertex[NumPrevRefVertices] = VertexIndex
		# 		else:
		# 			NumPrevNonRefVertices: uint = VertexIndex - NumPrevRefVertices
		# 			GroupNonRefToVertex[NumPrevNonRefVertices] = VertexIndex
		# 	assert(len(GroupRefToVertex) == 256)
		# 	assert(len(GroupNonRefToVertex) == 256)

			
		# 	NumNonRefVertices:uint = Cluster.NumVerts - ClusterDiskHeader.NumVertexRefs
		# 	for NonRefVertexIndex in range(NumNonRefVertices):
		# 		VertexIndex: uint = GroupNonRefToVertex[NonRefVertexIndex]
		# 		# Position
		# 		PositionBitsPerVertex: uint = Cluster.PosBits.x + Cluster.PosBits.y + Cluster.PosBits.z
		# 		SrcPositionBitsPerVertex: uint = (PositionBitsPerVertex + 7) & ~7
				
		# 		Cluster.Vertices[VertexIndex] = GetPos(
		# 				f,
		# 				SrcPageBaseOffset + ClusterDiskHeader.PositionDataOffset,
		# 				NonRefVertexIndex * SrcPositionBitsPerVertex,
		# 				Cluster
		# 			)
		# 		SrcBitsPerAttribute:uint = (Cluster.BitsPerAttribute + 7) & ~7


	[staticmethod]
	def UnpackStripIndices(f: BinaryIO, SrcPageBaseOffset:int, PageDiskHeader: FPageDiskHeader,ClusterDiskHeader: FClusterDiskHeader, LocalClusterIndex: int, TriIndex: int):
		DwordIndex: uint = TriIndex >> 5
		BitIndex: uint = TriIndex & 31
		
		# Bitmask.x: bIsStart, Bitmask.y: bIsLeft, Bitmask.z: bIsNewVertex
		f.seek(SrcPageBaseOffset + PageDiskHeader.StripBitmaskOffset + (LocalClusterIndex * 4 + DwordIndex) * 12, os.SEEK_SET)
		SMask:uint = read_u32(f)
		LMask:uint = read_u32(f)
		WMask:uint = read_u32(f)
		SLMask:uint = SMask & LMask
		assert(0 <= SMask <= 0xFFFFFFFF)
		assert(0 <= LMask <= 0xFFFFFFFF)
		assert(0 <= WMask <= 0xFFFFFFFF)
		assert(0 <= SLMask <= 0xFFFFFFFF)

		# const uint HeadRefVertexMask = ( SMask & LMask & WMask ) | ( ~SMask & WMask );
		HeadRefVertexMask: uint = (SLMask | ~SMask) & WMask;	# 1 if head of triangle is ref. S case with 3 refs or L/R case with 1 ref.
		assert(0 <= HeadRefVertexMask <= 0xFFFFFFFF)

		PrevBitsMask:uint = u32_rshift(1, BitIndex) - 1
		assert(0 <= PrevBitsMask <= 0xFFFFFFFF)

		NumPrevRefVerticesBeforeDword:uint = BitFieldExtractU32(ClusterDiskHeader.NumPrevRefVerticesBeforeDwords, 10, DwordIndex * 10 - 10) if DwordIndex else 0
		NumPrevNewVerticesBeforeDword:uint = BitFieldExtractU32(ClusterDiskHeader.NumPrevNewVerticesBeforeDwords, 10, DwordIndex * 10 - 10) if DwordIndex else 0
		assert(0 <= NumPrevRefVerticesBeforeDword <= 0b1111111111)
		assert(0 <= NumPrevNewVerticesBeforeDword <= 0b1111111111)

		CurrentDwordNumPrevRefVertices:int = u32_rshift(int.bit_count(SLMask & PrevBitsMask), 1) + int.bit_count(WMask & PrevBitsMask)
		CurrentDwordNumPrevNewVertices:int = u32_rshift(int.bit_count(SMask & PrevBitsMask), 1) + BitIndex - CurrentDwordNumPrevRefVertices
		assert(0 <= CurrentDwordNumPrevRefVertices <= 0x7FFFFFFF)
		assert(0 <= CurrentDwordNumPrevNewVertices <= 0x7FFFFFFF)

		NumPrevRefVertices:int = NumPrevRefVerticesBeforeDword + CurrentDwordNumPrevRefVertices
		NumPrevNewVertices:int = NumPrevNewVerticesBeforeDword + CurrentDwordNumPrevNewVertices
		assert(0 <= NumPrevRefVertices <= 0x7FFFFFFF)
		assert(0 <= NumPrevNewVertices <= 0x7FFFFFFF)
		
		IsStart:int = BitFieldExtractI32(SMask, 1, BitIndex) # -1: true, 0: false
		IsLeft:int = BitFieldExtractI32(LMask, 1, BitIndex) # -1: true, 0: false
		IsRef:int = BitFieldExtractI32(WMask, 1, BitIndex) # -1: true, 0: false
		assert(IsStart in (-1,0))
		assert(IsLeft in (-1,0))
		assert(IsRef in (-1,0))

		# needs to allow underflow of u32
		BaseVertex: uint = int_to_uint(NumPrevNewVertices - 1, 32)
		assert(0 <= BaseVertex <= 0xFFFFFFFF)

		OutIndices: FUIntVector3 = FUIntVector3(0,0,0)
		ReadBaseAddress: uint = SrcPageBaseOffset + ClusterDiskHeader.IndexDataOffset
		assert(0 <= ReadBaseAddress <= 0xFFFFFFFF)
		# -1 if not Start
		IndexData: uint = ReadUnalignedDword(f, ReadBaseAddress, (NumPrevRefVertices + ~IsStart) * 5)
		assert(0 <= IndexData <= 0xFFFFFFFF)
		if IsStart:
			MinusNumRefVertices: int = (IsLeft << 1) + IsRef
			assert(-3 <= MinusNumRefVertices <= 0)
			NextVertex: uint = NumPrevNewVertices
			assert(0 <= NumPrevNewVertices <= 0xFFFFFFFF)

			# the positive side of the if else use array indexors,
			# Examining the shader decompilation revealed there is no difference in the output code.
			if MinusNumRefVertices <= -1:
				OutIndices.x = BaseVertex - (IndexData & 31)
				IndexData >>= 5
			else:
				OutIndices.x = NextVertex
				NextVertex += 1

			if MinusNumRefVertices <= -2:
				OutIndices.y = BaseVertex - (IndexData & 31)
				IndexData >>= 5
			else:
				OutIndices.y = NextVertex
				NextVertex += 1

			if MinusNumRefVertices <= -3:
				OutIndices.z = BaseVertex - (IndexData & 31)
			else:
				OutIndices.z = NextVertex
				NextVertex += 1
		else:
			# Handle two first vertices
			PrevBitIndex: uint = int_to_uint(BitIndex - 1, 32)
			assert(0 <= PrevBitIndex <= 0xFFFFFFFF)
			IsPrevStart: int = BitFieldExtractI32(SMask, 1, PrevBitIndex)
			assert(-1 <= IsPrevStart <= 0)
			IsPrevHeadRef: int = BitFieldExtractI32(HeadRefVertexMask, 1, PrevBitIndex)
			assert(-1 <= IsPrevHeadRef <= 0)
			#const int NumPrevNewVerticesInTriangle = IsPrevStart ? ( 3u - ( bfe_u32( /*SLMask*/ LMask, PrevBitIndex, 1 ) << 1 ) - bfe_u32( /*SMask &*/ WMask, PrevBitIndex, 1 ) ) : /*1u - IsPrevRefVertex*/ 0u;
			#                                                                          /*SLMask*/                                          /*SMask &*/
			NumPrevNewVerticesInTriangle:int = IsPrevStart & (3 - (u32_rshift(BitFieldExtractU32(LMask, 1, PrevBitIndex), 1) | BitFieldExtractU32(WMask, 1, PrevBitIndex)))

			#//OutIndices[ 1 ] = IsPrevRefVertex ? ( BaseVertex - ( IndexData & 31u ) + NumPrevNewVerticesInTriangle ) : BaseVertex;	// BaseVertex = ( NumPrevNewVertices - 1 );
			OutIndices.y = BaseVertex + (IsPrevHeadRef & (NumPrevNewVerticesInTriangle - (IndexData & 31)))
			#//OutIndices[ 2 ] = IsRefVertex ? ( BaseVertex - bfe_u32( IndexData, 5, 5 ) ) : NumPrevNewVertices;
			OutIndices.z = NumPrevNewVertices + (IsRef & (-1 - BitFieldExtractU32(IndexData, 5, 5)))

			# We have to search for the third vertex. 
			# Left triangles search for previous Right/Start. Right triangles search for previous Left/Start.
			SearchMask: uint = int_to_uint(SMask | (LMask ^ IsLeft), 32)				# SMask | ( IsRight ? LMask : RMask );
			assert(0 <= SearchMask <= 0xFFFFFFFF)
			FoundBitIndex: uint = firstbithigh(SearchMask & PrevBitsMask)
			assert((0 <= FoundBitIndex <= 31) or (FoundBitIndex == 0xFFFFFFFF))
			IsFoundCaseS: int = BitFieldExtractI32(SMask, 1, FoundBitIndex);		# -1: true, 0: false
			assert(-1 <= IsFoundCaseS <= 0)

			FoundPrevBitsMask: uint = u32_rshift(1, FoundBitIndex) - 1
			FoundCurrentDwordNumPrevRefVertices: int = u32_rshift(int.bit_count(SLMask & FoundPrevBitsMask), 1) + int.bit_count(WMask & FoundPrevBitsMask)
			FoundCurrentDwordNumPrevNewVertices: int = u32_rshift(int.bit_count(SMask & FoundPrevBitsMask), 1) + FoundBitIndex - FoundCurrentDwordNumPrevRefVertices

			FoundNumPrevNewVertices: int = NumPrevNewVerticesBeforeDword + FoundCurrentDwordNumPrevNewVertices
			FoundNumPrevRefVertices: int = NumPrevRefVerticesBeforeDword + FoundCurrentDwordNumPrevRefVertices

			FoundNumRefVertices: uint = u32_rshift(BitFieldExtractU32(LMask, 1, FoundBitIndex), 1) + BitFieldExtractU32(WMask, 1, FoundBitIndex)
			assert(0 <= FoundNumRefVertices <= 0xFFFFFFFF)
			IsBeforeFoundRefVertex: uint = BitFieldExtractU32(HeadRefVertexMask, 1, FoundBitIndex - 1)
			assert(0 <= IsBeforeFoundRefVertex <= 0xFFFFFFFF)

			# ReadOffset: Where is the vertex relative to triangle we searched for?
			ReadOffset: int = IsLeft if IsFoundCaseS else 1
			FoundIndexData: uint = ReadUnalignedDword(f, ReadBaseAddress, (FoundNumPrevRefVertices - ReadOffset) * 5)
			assert(0 <= FoundIndexData <= 0xFFFFFFFF)
			FoundIndex: uint = int_to_uint((FoundNumPrevNewVertices - 1) - BitFieldExtractU32(FoundIndexData, 5, 0), 32)
			assert(0 <= FoundIndex <= 0xFFFFFFFF)

			bCondition: bool = (uint_to_int(FoundNumRefVertices, 32) >= 1 - IsLeft) if IsFoundCaseS else bool(IsBeforeFoundRefVertex)
			FoundNewVertex: int = FoundNumPrevNewVertices + ((IsLeft & (FoundNumRefVertices == 0)) if IsFoundCaseS else -1)
			OutIndices.x = FoundIndex if bCondition else FoundNewVertex

			## Would it be better to code New verts instead of Ref verts?
			## HeadRefVertexMask would just be WMask?

			if IsLeft:
				OutIndices.y, OutIndices.z = OutIndices.zy()
				
		return OutIndices
