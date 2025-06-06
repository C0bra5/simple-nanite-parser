from src.unreal_io import *
from src.nanite_constants import *
from src.bit_reader import FBitStreamReader
from typing import BinaryIO
import src.FResources as FResources
import io
import os
import enum
import math


class FUVRange:
	def __init__(self, f: BinaryIO, StartOffset, Index):
		f.seek(StartOffset + Index * 32, os.SEEK_SET)
		Data = [uint4(f), uint4(f)]
		self.Min: FIntVector2 = FIntVector2(uint_to_int(Data[0].x, 32), uint_to_int(Data[0].y, 32))
		self.GapStart: FUIntVector2 = FUIntVector2(*Data[0].zw())
		self.GapLength: FUIntVector2 = FUIntVector2(*Data[1].xy())
		self.Precision: int = uint_to_int(Data[1].z, 32)

class FNaniteRawAttributeData:
	def __init__(self):
		self.TangentX_AndSign: FVector4f = None
		self.Normal: FVector3f = None
		self.Color: FVector4f = None
		self.TexCoords: list[FVector2f] = [None, None, None, None]

	def __eq__(self, value):
		if not isinstance(value, FNaniteRawAttributeData): return False
		if self.TangentX_AndSign != value.TangentX_AndSign: return False
		if self.Normal != value.Normal: return False
		if self.Color != value.Color: return False
		for i in range(len(self.TexCoords)):
			if self.TexCoords[i] != value.TexCoords[i]: return False
		return False

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

	class FClusterFlags(enum.IntFlag):
		ROOT_LEAF = enum.auto()
		"""Cluster is leaf when only root pages are streamed in"""
		STREAMING_LEAF = enum.auto()
		"""Cluster is a leaf in the current streaming state"""
		ROOT_FULL_LEAF = enum.auto()
		"""Cluster is a leaf when fully streamed in"""
		ROOT_ROOT_GROUP = enum.auto()
		"""Cluster is in a group that is fully inside the root pages"""

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
		self.ColorBits = FUIntVector4(*read_bitfield(read_u16(f), 4,4,4,4))
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
		self.DecodeInfoOffset, self.bHasTangents, self.NumUVs, ColorMode = read_bitfield(read_u32(f), 22,1,3,2)
		self.bHasTangents: bool = bool(self.bHasTangents)
		self.ColorMode: FCluster.FColorMode = FCluster.FColorMode(ColorMode)
		self.UV_Prec: uint = read_u32(f)
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
		self.RefVerticies: list[tuple[int,int,int]] = [None] * self.NumVerts
		self.VertAttrs: list[FNaniteRawAttributeData] = [None] * self.NumVerts
		self.MatIndices: list[int] = [None] * self.NumTris
		self.local_page_index: int = None
		self.local_cluster_index: int = None
		self.GroupRefToVertex = [0] * 256
		self.GroupNonRefToVertex = [0] * 256
		self.scale: int = _precision_lookup[self.PosPrecision]

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

		ret = FVertex(*((Pos + Cluster.PosStart) * Cluster.scale).xyz())
		ret.raw_pos = Pos
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
			DstBuffer.seek(DstDword * 4, os.SEEK_SET)
			DstBuffer.write(Data.to_bytes(4, 'little'))
			DstDword += 1
			SrcDword += 1
			DstNumDwords -= 1
		
		Data:uint = ReadUnalignedDwordFromAlignedBase(SrcBuffer, SrcDword * 4, SrcBitOffset)
		dst_data:uint = read_u32(DstBuffer)
		dst_data &= ~LastMask
		dst_data |= Data & LastMask
		DstBuffer.seek(DstDword * 4)
		DstBuffer.write(struct.pack('<I', dst_data))

def UnpackNormal(Packed: uint, Bits: uint) -> FVector3f:
	Mask: uint = BitFieldMaskU32(Bits, 0)
	F: FVector2f = FUIntVector2(BitFieldExtractU32(Packed, Bits, 0), BitFieldExtractU32(Packed, Bits, Bits)) * (2.0 / Mask) - 1.0
	N: FVector3f = FVector3f(*F.xy(), 1.0 - abs(F.x) - abs(F.y))
	T: float = min(1.0, max(0.0, -N.z))
	N.x += -T if N.x >= 0 else T
	N.y += -T if N.y >= 0 else T
	return N.normalize()

def UnpackTangentX(TangentZ: FVector3f, TangentAngleBits: uint, NumTangentBits: uint):
	bSwapXZ: bool = (abs(TangentZ.z) > abs(TangentZ.x))
	if bSwapXZ:
		TangentZ = FVector3f(*TangentZ.zyx())

	TangentRefX: FVector3f = FVector3f(-TangentZ.y, TangentZ.x, 0.0)
	TangentRefY: FVector3f = TangentZ.cross(TangentRefX)

	Scale: float = 1.0 / math.sqrt(FVector2f(*TangentRefX.xy()).dot(FVector2f(*TangentRefX.xy())))
	
	TangentAngle: float = float(TangentAngleBits) * ((2.0 * math.pi) / u32_rshift(1, NumTangentBits))
	TangentX: FVector3f = TangentRefX * (math.cos(TangentAngle) * Scale) + TangentRefY * (math.sin(TangentAngle) * Scale)
	if bSwapXZ:
		TangentX = FVector3f(*TangentX.zyx())
	return TangentX

def UnpackTexCoord(Packed: FUIntVector2, UVRange: FUVRange) -> FVector2f:
	t: FIntVector2 = FIntVector2(Packed) # make a copy
	t.x += UVRange.GapLength[0] if Packed[0] > UVRange.GapStart[0] else 0
	t.y += UVRange.GapLength[1] if Packed[1] > UVRange.GapStart[1] else 0

	Scale: float = _precision_lookup[UVRange.Precision]
	return (t + UVRange.Min) * Scale

def DecodeMaterialRange(EncodedRange: uint) -> tuple[uint,uint,uint]:
	# uint32 TriStart      :  8; # max 128 triangles
	# uint32 TriLength     :  8; # max 128 triangles
	# uint32 MaterialIndex :  6; # max  64 materials
	# uint32 Padding       : 10;

	TriStart = BitFieldExtractU32(EncodedRange, 8, 0)
	TriLength = BitFieldExtractU32(EncodedRange, 8, 8)
	MaterialIndex = BitFieldExtractU32(EncodedRange, 6, 16)
	return TriStart, TriLength, MaterialIndex

def IsMaterialFastPath(InCluster: FCluster) -> bool:
	return InCluster.Material0Length > 0

def GetRelativeMaterialIndex(DataBuffer: BinaryIO, InCluster: FCluster, InTriIndex: uint, gpu_page_offset: uint) -> uint:
	MaterialIndex: uint = 0xFFFFFFFF

	if IsMaterialFastPath(InCluster):
		if InTriIndex < InCluster.Material0Length:
			MaterialIndex = InCluster.Material0Index
		elif InTriIndex < (InCluster.Material0Length + InCluster.Material1Length):
			MaterialIndex = InCluster.Material1Index
		else:
			MaterialIndex = InCluster.Material2Index
	else:
		TableOffset: uint = gpu_page_offset + InCluster.MaterialTableOffset * 4
		for _ in range(InCluster.MaterialTableLength):
			DataBuffer.seek(TableOffset)
			EncodedRange: uint = read_u32(DataBuffer)
			TableOffset += 4

			TriStart, TriLength, TriMaterialIndex = DecodeMaterialRange(EncodedRange)

			if InTriIndex >= TriStart and InTriIndex < (TriStart + TriLength):
				MaterialIndex = TriMaterialIndex
				break

	return MaterialIndex

class FNaniteStreamingPage:
	def __init__(self, f: BinaryIO, PageStreamingState: 'FResources.FPageStreamingState', Resources: 'FResources.FResources'):
		# read headers
		self.origin = f.tell()
		self.Fixups = FFixupChunk(f)
		assert(f.tell() - self.origin == PageStreamingState.BulkSize - PageStreamingState.PageSize)
		
		MaxStreamingPages = 512 * 1024 * 1024 // u32_rshift(1, 17) # 4096
		assert(MaxStreamingPages + 2048 <= u32_rshift(1, 16))
		
		self.SrcPageBaseOffset = f.tell()
		self.PageDiskHeader = FPageDiskHeader(f)
		assert(f.tell() - self.SrcPageBaseOffset == 8*4)

		self.ClusterDiskHeaders: list[FClusterDiskHeader] = read_list_with_len(f, self.Fixups.Header.NumClusters, FClusterDiskHeader)
		
		self.gpu_page_offset = f.tell()
		self.GPUPageHeader = FPageGPUHeader(f)
		assert(self.GPUPageHeader.NumClusters == self.Fixups.Header.NumClusters)
		assert(self.GPUPageHeader.NumClusters == len(self.ClusterDiskHeaders))

		self.ClusterOrigin = f.tell()
		self.Clusters: list[FCluster] = list()
		
		
		# because the compute shader runs everythig in parallel, we also have to do the same thing
		# to do so we simply compartimentalize each "section" of the main parsing parallel loop
		# into a sequence of blocks, which can be gated to completion. This should mimic the behaviour
		# well enough that the parallel looping of the original code won't be an issue.
		self.read_clusters(f)
		self.read_strip_indices(f)
		self.identify_ref_verts(f)
		self.read_non_ref_verts(f)
		self.read_vert_refs(f, PageStreamingState, Resources)

			
			


	def read_clusters(self, f: BinaryIO):
		
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

	def read_strip_indices(self, f: BinaryIO):
		for LocalClusterIndex in range(len(self.Clusters)):
			Cluster = self.Clusters[LocalClusterIndex]
			ClusterDiskHeader = self.ClusterDiskHeaders[LocalClusterIndex]
			for TriangleIndex in range(Cluster.NumTris):
				Indices = FNaniteStreamingPage.UnpackStripIndices(f, self.SrcPageBaseOffset, self.PageDiskHeader, ClusterDiskHeader, LocalClusterIndex, TriangleIndex)
				assert (Indices.x != Indices.y)
				assert (Indices.x != Indices.z)
				assert (Indices.z != Indices.y)
				# Rotate triangle so first vertex has the lowest index
				if Indices.y < min(Indices.x, Indices.z):
					Indices.x, Indices.y, Indices.z = Indices.yzx()
				elif Indices.z < min(Indices.x, Indices.y):
					Indices.x, Indices.y, Indices.z = Indices.zxy()

				Cluster.StripIndices[TriangleIndex] = Indices
				assert(len(Cluster.StripIndices) <= NANITE_MAX_CLUSTER_TRIANGLES)

				Cluster.MatIndices[TriangleIndex] = GetRelativeMaterialIndex(f, Cluster, TriangleIndex, self.gpu_page_offset)


	def identify_ref_verts(self, f: BinaryIO):
		for LocalClusterIndex in range(len(self.Clusters)):
			Cluster = self.Clusters[LocalClusterIndex]
			ClusterDiskHeader = self.ClusterDiskHeaders[LocalClusterIndex]

			# no clue what this does it but does something!
			AlignedBitmaskOffset: uint = self.SrcPageBaseOffset + self.PageDiskHeader.VertexRefBitmaskOffset + LocalClusterIndex * 32 # NANITE_MAX_CLUSTER_VERTICES / 8
			GroupNumRefsInPrevDwords8888 = [0,0]
			for GroupIndex in range(7):
				f.seek(AlignedBitmaskOffset + GroupIndex * 4, os.SEEK_SET)
				Count:uint = int.bit_count(read_u32(f))
				Count8888: uint = Count * 0x01010101; # Broadcast count to all bytes
				Index: uint = GroupIndex + 1
				GroupNumRefsInPrevDwords8888[Index >> 2] += u32_rshift(Count8888, u32_rshift((Index & 3), 3)) # Add to bytes above
				if Cluster.NumVerts > 128 and Index < 4:
					# Add low dword byte counts to all bytes in high dword when there are more than 128 vertices.
					GroupNumRefsInPrevDwords8888[1] += Count8888
			assert(len(GroupNumRefsInPrevDwords8888) == 2)
			

			for VertexIndex in range(Cluster.NumVerts):
				DwordIndex: uint = VertexIndex >> 5
				BitIndex: uint = VertexIndex & 31

				Shift: uint = u32_rshift((DwordIndex & 3), 3)
				NumRefsInPrevDwords: uint = (GroupNumRefsInPrevDwords8888[DwordIndex >> 2] >> Shift) & 0xFF
				f.seek(AlignedBitmaskOffset + DwordIndex * 4, os.SEEK_SET)
				DwordMask: uint = read_u32(f)
				NumPrevRefVertices: uint = int.bit_count(BitFieldExtractU32(DwordMask, BitIndex, 0)) + NumRefsInPrevDwords

				if (DwordMask & u32_rshift(1, BitIndex)) != 0:
					Cluster.GroupRefToVertex[NumPrevRefVertices] = VertexIndex
				else:
					NumPrevNonRefVertices: uint = VertexIndex - NumPrevRefVertices
					Cluster.GroupNonRefToVertex[NumPrevNonRefVertices] = VertexIndex
			assert(len(Cluster.GroupRefToVertex) == 256)
			assert(len(Cluster.GroupNonRefToVertex) == 256)

	def read_non_ref_verts(self, f: BinaryIO):
		
		for LocalClusterIndex in range(len(self.Clusters)):
			Cluster = self.Clusters[LocalClusterIndex]
			ClusterDiskHeader = self.ClusterDiskHeaders[LocalClusterIndex]

			NumNonRefVertices:uint = Cluster.NumVerts - ClusterDiskHeader.NumVertexRefs
			for NonRefVertexIndex in range(NumNonRefVertices):
				VertexIndex: uint = Cluster.GroupNonRefToVertex[NonRefVertexIndex]
				# Position
				PositionBitsPerVertex: uint = Cluster.PosBits.x + Cluster.PosBits.y + Cluster.PosBits.z
				SrcPositionBitsPerVertex: uint = (PositionBitsPerVertex + 7) & ~7
				
				Cluster.Vertices[VertexIndex] = GetPos(
						f,
						self.SrcPageBaseOffset + ClusterDiskHeader.PositionDataOffset,
						NonRefVertexIndex * SrcPositionBitsPerVertex,
						Cluster
					)
				
				SrcBitsPerAttribute:uint = (Cluster.BitsPerAttribute + 7) & ~7
				reader = FBitStreamReader.Create_Aligned(
					self.SrcPageBaseOffset + ClusterDiskHeader.AttributeDataOffset,
					NonRefVertexIndex * SrcBitsPerAttribute,
					NANITE_MAX_ATTRIBUTE_BITS[NANITE_MAX_UVS]
				)
				Cluster.VertAttrs[VertexIndex] = self.GetAttributes(f, reader, Cluster, ClusterDiskHeader, NANITE_MAX_UVS)

	def read_vert_refs(self, f: BinaryIO, PageStreamingState: 'FResources.FPageStreamingState', Resources: 'FResources.FResources'):
		for LocalClusterIndex in range(len(self.Clusters)):
			Cluster: FCluster = self.Clusters[LocalClusterIndex]
			ClusterDiskHeader: FClusterDiskHeader = self.ClusterDiskHeaders[LocalClusterIndex]
			for RefVertexIndex in range(ClusterDiskHeader.NumVertexRefs):
				VertexIndex: uint = Cluster.GroupRefToVertex[RefVertexIndex]
				PageClusterIndex: uint = ReadByte(f, self.SrcPageBaseOffset + ClusterDiskHeader.VertexRefDataOffset + RefVertexIndex)
				f.seek(self.SrcPageBaseOffset + ClusterDiskHeader.PageClusterMapOffset + PageClusterIndex * 4)
				PageClusterData: uint = read_u32(f)
				
				ParentPageIndex: uint = PageClusterData >> NANITE_MAX_CLUSTERS_PER_PAGE_BITS
				SrcLocalClusterIndex: uint = BitFieldExtractU32(PageClusterData, NANITE_MAX_CLUSTERS_PER_PAGE_BITS, 0)
				SrcCodedVertexIndex: uint = ReadByte(f, self.SrcPageBaseOffset + ClusterDiskHeader.VertexRefDataOffset + RefVertexIndex + self.PageDiskHeader.NumVertexRefs)

				Cluster.RefVerticies[VertexIndex] = (1, ParentPageIndex, SrcLocalClusterIndex, SrcCodedVertexIndex)
				SrcCluster: FCluster
				ParentGPUPageIndex: uint = 0

				bIsParentRef: bool = ParentPageIndex != 0

				if bIsParentRef:
					ParentGPUPageIndex = Resources.PageDependencies[PageStreamingState.DependenciesStart + (ParentPageIndex - 1)]
					SrcCluster = Resources.PageData[ParentGPUPageIndex].Clusters[SrcLocalClusterIndex]
					real_src_vertex_index = SrcCodedVertexIndex
				else:
					SrcCluster = self.Clusters[SrcLocalClusterIndex]
					real_src_vertex_index = SrcCluster.GroupNonRefToVertex[SrcCodedVertexIndex]
				
				# transcode position
				src_vert = SrcCluster.Vertices[real_src_vertex_index]
				Cluster.VertAttrs[VertexIndex] = SrcCluster.VertAttrs[real_src_vertex_index]
				new_raw_pos = src_vert.raw_pos + SrcCluster.PosStart - Cluster.PosStart
				assert(SrcCluster.Vertices[SrcCodedVertexIndex] is not None)
				Cluster.Vertices[VertexIndex] = FVertex(*((new_raw_pos + Cluster.PosStart) * Cluster.scale).xyz())
				Cluster.Vertices[VertexIndex].raw_pos = new_raw_pos
				Cluster.Vertices[VertexIndex].is_ref = True

	def GetAttributes(self, ClusterPageData: BinaryIO, BitStreamReader: FBitStreamReader, Cluster: FCluster, ClusterDiskHeader: FClusterDiskHeader, CompileTimeMaxTexCoords) -> FNaniteRawAttributeData:
		ret = FNaniteRawAttributeData()

		DecodeInfoOffset: uint = self.gpu_page_offset + Cluster.DecodeInfoOffset

		ColorMin: FUIntVector4 = FUIntVector4(UnpackByte0(Cluster.ColorMin), UnpackByte1(Cluster.ColorMin), UnpackByte2(Cluster.ColorMin), UnpackByte3(Cluster.ColorMin))
		NumComponentBits: FUIntVector4 = FUIntVector4(*Cluster.ColorBits.xyzw())

		# parses normals
		NormalBits: uint = BitStreamReader.Read(ClusterPageData, 2 * Cluster.NormalPrecision, 2 * NANITE_MAX_NORMAL_QUANTIZATION_BITS)
		ret.Normal = UnpackNormal(NormalBits, Cluster.NormalPrecision)

		NumTangentBits: uint = (Cluster.TangentPrecision + 1) if Cluster.bHasTangents else 0
		TangentAngleAndSignBits: uint = BitStreamReader.Read(ClusterPageData, NumTangentBits, NANITE_MAX_TANGENT_QUANTIZATION_BITS + 1)

		if Cluster.bHasTangents:
			bTangentYSign: bool = (TangentAngleAndSignBits & u32_rshift(1, Cluster.TangentPrecision)) != 0
			TangentAngleBits: uint = BitFieldExtractU32(TangentAngleAndSignBits, Cluster.TangentPrecision, 0)
			ret.TangentX_AndSign = FVector4f(*UnpackTangentX(ret.Normal.copy(), TangentAngleBits, Cluster.TangentPrecision), -1.0 if bTangentYSign else 1.0)
		else:
			ret.TangentX_AndSign = FVector4f(0,0,0,0)
		
		ColorDelta: FUIntVector4 = BitStreamReader.Read4(
			ClusterPageData,
			NumComponentBits,
			FUIntVector4(
				NANITE_MAX_COLOR_QUANTIZATION_BITS,
				NANITE_MAX_COLOR_QUANTIZATION_BITS,
				NANITE_MAX_COLOR_QUANTIZATION_BITS,
				NANITE_MAX_COLOR_QUANTIZATION_BITS
			)
		)
		ret.Color = FVector4f(ColorMin + ColorDelta) * (1.0 / 255.0)

		for TexCoordIndex in range(Cluster.NumUVs):
			UVPrec = uint2(BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8), BitFieldExtractU32(Cluster.UV_Prec, 4, TexCoordIndex * 8 + 4))

			UVBits = BitStreamReader.Read2(ClusterPageData, UVPrec, uint2(NANITE_MAX_TEXCOORD_QUANTIZATION_BITS, NANITE_MAX_TEXCOORD_QUANTIZATION_BITS))
		

			if TexCoordIndex < Cluster.NumUVs:
					UVRange:FUVRange = FUVRange(ClusterPageData, DecodeInfoOffset, TexCoordIndex)
					
					ret.TexCoords[TexCoordIndex] = UnpackTexCoord(UVBits, UVRange)
			else:
				ret.TexCoords[TexCoordIndex] = FVector2f(0,0)
		return ret


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
