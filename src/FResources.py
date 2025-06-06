from src.unreal_io import *
from src.FNaniteStreamingPage import FNaniteStreamingPage
from typing import BinaryIO
import enum
import io

class EFPageStreamingStateFlags(enum.IntFlag):
	RELATIVE_ENCODING = enum.auto()

class FPageStreamingState:
	def __init__(self, f: BinaryIO):
		self.BulkOffset = read_u32(f)
		self.BulkSize = read_u32(f)
		self.PageSize = read_u32(f)
		self.DependenciesStart = read_u32(f)
		self.DependenciesNum = read_u16(f)
		self.MaxHierarchyDepth = read_u8(f)
		self.Flags = EFPageStreamingStateFlags(read_u8(f))
		self.Data = b''

# GPU loads it in SOA format but for some reason it's stored as AOS
# something must be SOAing the data befor it's sent
class FHierarchyNodeSlice:
	def __init__(self, f: BinaryIO):
		self.LODBounds = FVector4f(f)
		# misc0
		self.BoxBoundsCenter = FVector3f(f)
		self.MinLODError = read_f16(f)
		self.MaxParentLODError = read_f16(f)
		# misc1
		self.BoxBoundsExtent = FVector3f(f)
		self.ChildStartReference = read_u32(f)
		self.bLoaded = self.ChildStartReference != 0xFFFFFFFF
		# misc2
		ResourcePageIndex_NumPages_GroupPartSize = read_u32(f)
		self.bEnabled = ResourcePageIndex_NumPages_GroupPartSize != 0
		self.bLeaf = ResourcePageIndex_NumPages_GroupPartSize != 0xFFFFFFFF
		self.NumChildren, self.StartPageIndex, self.NumPages = read_bitfield(ResourcePageIndex_NumPages_GroupPartSize, 9, 3, 20) if self.bLeaf and self.bEnabled else (0,0,0)
		
	def __repr__(self):
		flags = []
		if self.bEnabled: flags.append('Enabled')
		if self.bLoaded: flags.append('Loaded')
		if self.bLeaf: flags.append('Leaf')
		return ' | '.join(flags + [f'mlod:{self.MinLODError} plod:{self.MaxParentLODError}'])



class FPageStreamingState:
	def __init__(self, f: BinaryIO):
		self.BulkOffset = read_u32(f)
		self.BulkSize = read_u32(f)
		self.PageSize = read_u32(f)
		self.DependenciesStart = read_u32(f)
		self.DependenciesNum = read_u16(f)
		self.MaxHierarchyDepth = read_u8(f)
		self.Flags = EFPageStreamingStateFlags(read_u8(f))
		# custom data
		self.data: FNaniteStreamingPage = None
		self.dependencies: list[int] = []
		


class FResources:
	def __init__(self, asset: BinaryIO, bulk: BinaryIO):
		
		self.root_pages_data = asset.read(read_u32(asset))
		self.PageStreamingStates: list['FPageStreamingState'] = [FPageStreamingState(asset) for _ in range(read_u32(asset))]
		
		self.HierarchyNodes: list[FHierarchyNodeSlice] = []
		for _ in range(read_u32(asset)):
			self.HierarchyNodes.append([
				FHierarchyNodeSlice(asset),
				FHierarchyNodeSlice(asset),
				FHierarchyNodeSlice(asset),
				FHierarchyNodeSlice(asset)
			])

		self.HierarchyRootOffsets = read_list(asset, read_u32)
		self.PageDependencies = read_list(asset, read_u32)
		self.ImposterAtlas = read_list(asset, read_u16)
		self.NumRootPages = read_u32(asset)
		self.PositionPrecision = read_s32(asset)
		self.NormalPrecision = read_s32(asset)
		self.NumInputTriangles = read_u32(asset)
		self.NumInputVertices = read_u32(asset)
		self.NumInputMeshes = read_u16(asset)
		self.NumInputTexCoords = read_u16(asset)
		self.NumClusters = read_u32(asset)

		self.RootPageIndex = 0

		
		self.PageData:list[FNaniteStreamingPage]  = list()
		self.upload_buffer: bytes = b''
		self.install_info:list[tuple[int,int,int,int]] = list()
		with io.BytesIO(self.root_pages_data) as root_io:
			for i, p in enumerate(self.PageStreamingStates):
				print(f'parsing page {i + 1} / {len(self.PageStreamingStates)}')
				p.dependencies.extend(self.PageDependencies[p.DependenciesStart:p.DependenciesStart+p.DependenciesNum])
				for d in p.dependencies:
					assert(d < i)
				data = None
				# root pages are listed first
				if i < self.NumRootPages:
					root_io.seek(p.BulkOffset)
					data = root_io.read(p.BulkSize)
				else:
					# then bulk pages
					bulk.seek(p.BulkOffset)
					data = bulk.read(p.BulkSize)
				
				with io.BytesIO(data) as passed:
					p.data = FNaniteStreamingPage(passed, p, self)
				self.PageData.append(p.data)

				to_upload = data[p.BulkSize - p.PageSize:]
				self.install_info.append((len(self.upload_buffer), ((1<< 17) * i), p.DependenciesStart, p.DependenciesNum))
				self.upload_buffer += to_upload