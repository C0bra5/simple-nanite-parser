from src.nanite_constants import *
from src.hlsl_constants import *

from compushady import HEAP_READBACK, Buffer, HEAP_UPLOAD, Compute
from compushady.formats import R8_UINT
from compushady.shaders import hlsl

import struct
import os

def compile_shader(shader_path: str) -> bytes:
	with open(shader_path, 'r', encoding='utf-8') as f:
		shader_code = f.read()
	# compile the shader
	return hlsl.compile(shader_code, entry_point="TranscodePageToGPU", target="cs_6_6")

_COMPILED_SHADER:bytes = compile_shader(r'.\exfiltrate_nanite.hlsl')

def create_readback_buffer(original_buffer) -> Buffer:
	ret = Buffer(original_buffer.size, HEAP_READBACK)
	original_buffer.copy_to(ret)
	return ret

def create_raw_buffer(data):
	# yes the staging buffer is required, don't yeet it
	if isinstance(data, bytes):
		ret = Buffer(len(data), format=R8_UINT )
		staging_buffer = Buffer(ret.size, HEAP_UPLOAD)
		staging_buffer.upload(data)
		staging_buffer.copy_to(ret)
		return ret
	if isinstance(data, int):
		ret = Buffer(data, format=R8_UINT )
		# creates a staging buffer with the right size and in memory optimized for uploading data
		staging_buffer = Buffer(ret.size, HEAP_UPLOAD)
		staging_buffer.upload(b'\x00' * ret.size)
		staging_buffer.copy_to(ret)
		return ret
	assert(False)


def extract_data_using_compute_shader(SRC_RAW_DATA: bytes, INSTALL_INFO_ENTRIES: list[tuple[int,int,int,int]], PAGE_DEPENDENCIES: list[int]):

	PAGE_DEPENDENCIES_RAW_DATA = b''.join([b.to_bytes(4, 'little') for b in PAGE_DEPENDENCIES])

	INSTALL_INFO_RAW_DATA = b''
	for page_index, raw_info in enumerate(INSTALL_INFO_ENTRIES):
		src_offset, dst_offset, dep_start, dep_num = raw_info
		assert(dst_offset == NANITE_STREAMING_PAGE_GPU_SIZE * page_index)
		# src offset
		INSTALL_INFO_RAW_DATA +=  struct.pack("<IIII", src_offset,dst_offset,dep_start,dep_num)

	ATTR_DATA_LEN = 4 * (4 + 3 + 4 + (2 * NANITE_MAX_UVS))
	ATTR_DATA_LEN_PER_STRIP = 3 * ATTR_DATA_LEN

	# original buffers
	InstallInfoBuffer = create_raw_buffer(INSTALL_INFO_RAW_DATA)
	PageDependenciesBuffer = create_raw_buffer(PAGE_DEPENDENCIES_RAW_DATA)
	SrcPageBuffer = create_raw_buffer(SRC_RAW_DATA)
	DstPageBuffer = create_raw_buffer(NANITE_STREAMING_PAGE_GPU_SIZE * len(INSTALL_INFO_ENTRIES))

	# data extraction buffers
	TriStripBuffer = create_raw_buffer(HLSL_SIZE_UINT4 * NANITE_MAX_CLUSTER_TRIANGLES * NANITE_MAX_CLUSTERS_PER_PAGE * len(INSTALL_INFO_ENTRIES))
	MatIdBuffer = create_raw_buffer(HLSL_SIZE_UINT * NANITE_MAX_CLUSTER_TRIANGLES * NANITE_MAX_CLUSTERS_PER_PAGE * len(INSTALL_INFO_ENTRIES))
	PosBuffer = create_raw_buffer(HLSL_SIZE_FLOAT4 * NANITE_MAX_CLUSTER_VERTICES * NANITE_MAX_CLUSTERS_PER_PAGE * len(INSTALL_INFO_ENTRIES))
	RefPosBuffer = create_raw_buffer(HLSL_SIZE_UINT4 * NANITE_MAX_CLUSTER_VERTICES * NANITE_MAX_CLUSTERS_PER_PAGE * len(INSTALL_INFO_ENTRIES))
	AttributeDataBuffer = create_raw_buffer(ATTR_DATA_LEN_PER_STRIP * NANITE_MAX_CLUSTER_TRIANGLES * NANITE_MAX_CLUSTERS_PER_PAGE * len(INSTALL_INFO_ENTRIES))

	# with open('./shader.dxbc', 'wb') as f:
	# 	f.write(COMPILED_SHADER)
	
	for i in range(len(INSTALL_INFO_ENTRIES)):
		# globals obtained by decompiling the compiled shader and looking for the $globals cbuffer
		Globals = create_raw_buffer(
			struct.pack('<IIII', 0, 4096, 0, 0) #uint4 PageConstants;    
			+ struct.pack('<I', i)   #uint StartPageIndex;
		)
		compute = Compute(
			_COMPILED_SHADER,
			cbv=[Globals],
			srv=[InstallInfoBuffer, PageDependenciesBuffer, SrcPageBuffer],
			uav=[DstPageBuffer, TriStripBuffer, MatIdBuffer, PosBuffer, RefPosBuffer, AttributeDataBuffer],
		)
		compute.dispatch(NANITE_MAX_TRANSCODE_GROUPS_PER_PAGE, 1, 1)
		

	ret = {}
	ret['tri_strips'] = list()
	ret['mat_id'] = list()
	ret['pos_refs'] = list()
	ret['ver_pos'] = list()
	ret['ver_attr'] = list()

	# unpack the data
	tri_strip_readback = create_readback_buffer(TriStripBuffer)
	mat_id_strip_readback = create_readback_buffer(MatIdBuffer)
	attr_data_readback = create_readback_buffer(AttributeDataBuffer)
	index = 0
	for _ in range(len(INSTALL_INFO_ENTRIES)): # page
		ret['tri_strips'].append(tri_strip_list := list())
		ret['ver_attr'].append(attr_page_list := list())
		ret['mat_id'].append(mat_id_page_list := list())
		for _ in range(NANITE_MAX_CLUSTERS_PER_PAGE): # cluster
			tri_strip_list.append(tri_strip_cluster_list := list())
			attr_page_list.append(attr_cluster_list := list())
			mat_id_page_list.append(mat_id_cluster_list := list())
			for _ in range(NANITE_MAX_CLUSTER_TRIANGLES): # verts
				row = tri_strip_readback.readback(16, 16 * index)
				strip = struct.unpack_from("<IIII", row, 0)
				tri_strip_cluster_list.append(strip)
				# unpack vertex attrs
				if strip[0] == 0:
					attr_cluster_list.append(None)
					mat_id_cluster_list.append(None)
				else:
					row = mat_id_strip_readback.readback(4, 4 * index)
					mat_id_cluster_list.append(struct.unpack("<I", row)[0])
					attr_data = []
					for vi in range(3):
						row = attr_data_readback.readback(ATTR_DATA_LEN, ATTR_DATA_LEN_PER_STRIP * index + ATTR_DATA_LEN * vi)
						attr_data.append({
							'tx' : struct.unpack_from('<ffff', row, 0),
							'nr': struct.unpack_from('<fff', row, 16),
							'cl': struct.unpack_from('<ffff', row, 16 + 12),
							'uv': struct.unpack_from('<ffffffff', row, 16 + 12 + 16)
						})
					attr_cluster_list.append(attr_data)
				index += 1
					


	# unpack the data
	pos_read_back = create_readback_buffer(PosBuffer)
	ref_pos_read_back = create_readback_buffer(RefPosBuffer)
	index = 0
	for _ in range(len(INSTALL_INFO_ENTRIES)): # page
		ret['ver_pos'].append(pos_page_list := list())
		ret['pos_refs'].append(ref_page_list := list())
		for _ in range(NANITE_MAX_CLUSTERS_PER_PAGE): # cluster
			pos_page_list.append(pos_cluster_list := list())
			ref_page_list.append(ref_cluster_list := list())
			for _ in range(NANITE_MAX_CLUSTER_VERTICES): # verts
				pos_cluster_list.append(struct.unpack("<Ifff", pos_read_back.readback(16, 16 * index)))
				ref_cluster_list.append(struct.unpack("<IIII", ref_pos_read_back.readback(16, 16 * index)))
				index += 1


	return ret