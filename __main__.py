from src.unreal_io import *
from src.nanite_constants import *
from src.FResources import FResources
import src.FNaniteStreamingPage as FNaniteStreamingPage
import json
import argparse
import pygltflib

def float_check(a,b):
	return abs(max(a,b) - min(a,b)) < 0.00001

def identify_nanite_resources_using_fmodel_json(fmodel, uasset):
	with open(fmodel, 'r', encoding='utf-8') as fmodel:
		fmodel_data = json.load(fmodel)
	
	mesh = [x for x in fmodel_data if x['Type'] == "StaticMesh" and 'RenderData' in x is not None and 'NaniteResources' in x['RenderData']]
	if len(mesh) == 0:
		raise('mesh not found!')
	elif len(mesh) > 1:
		raise('more than one static mesh found?')
	mesh = mesh[0]

	num_root_pages = mesh['RenderData']['NaniteResources']['NumRootPages']
	root_page_size = 0
	for i in range(num_root_pages):
		root_page_size += mesh['RenderData']['NaniteResources']['PageStreamingStates'][i]['BulkSize']
	
	# This relies on you using a patched version of FModel.
	# You can get the version from this PR: https://github.com/FabianFG/CUE4Parse/pull/215
	signature:bytes = struct.pack('<I2sHHH',
		root_page_size,
		NANITE_FIXUP_MAGIC,
		mesh['RenderData']['NaniteResources']['RootData']['FixupChunk']['Header']['NumClusters'],
		mesh['RenderData']['NaniteResources']['RootData']['FixupChunk']['Header']['NumHierachyFixups'],
		mesh['RenderData']['NaniteResources']['RootData']['FixupChunk']['Header']['NumClusterFixups']
	)

	for h in mesh['RenderData']['NaniteResources']['RootData']['FixupChunk']['HierarchyFixups']:
		signature += struct.pack('<IIII',
			h['PageIndex'],
			(h['NodeIndex'] << 6) | h['ChildIndex'],
			h['ClusterGroupPartStartIndex'],
			(h['PageDependencyStart'] << 3) | h['PageDependencyNum']
		)
	
	for c in mesh['RenderData']['NaniteResources']['RootData']['FixupChunk']['ClusterFixups']:
		signature += struct.pack('<II',
			(c['PageIndex'] << 8) | c['ClusterIndex'],
			(c['PageDependencyStart'] << 3) | c['PageDependencyNum']
		)

	with open(uasset, 'rb') as f:
		data = f.read()
	resource_index = data.index(signature)
	
	if resource_index < 0:
		raise('nanite header not found')
	
	# handle multiple signature matches better™
	try:
		data.index(signature, resource_index + 1)
		raise("more than one signature match found!")
	except:
		pass
	
	material_lookup = {}
	for mi, m in enumerate(mesh['Properties']['StaticMaterials']):
		material_lookup[mi] = m['MaterialSlotName']

	return resource_index, material_lookup, mesh['Name']
	

def main(TEST_PATH: str, output_format = 'gltf'):
	
	
	EXPORT_SCALE = 1/100
	UV_INDEX = 0
	FMODEL = TEST_PATH + '.json'
	UASSET = TEST_PATH + '.uasset'
	UBULK = TEST_PATH + '.ubulk'
	if not os.path.isfile(FMODEL): raise FileNotFoundError(f"FModel json file not found: {FMODEL}")
	if not os.path.isfile(UASSET): raise FileNotFoundError(f"uasset file not found: {UASSET}")
	if not os.path.isfile(UBULK): raise FileNotFoundError(f"ubulk file not found: {UBULK}")

	
	print('locating nanite descriptor')
	uasset_offset, material_lookup, model_name = identify_nanite_resources_using_fmodel_json(
		FMODEL,
		UASSET
	)
	
	print('parsing nanite descriptor')
	with open(UASSET, 'rb') as asset, open(UBULK, 'rb') as bulk:
		asset.seek(uasset_offset, os.SEEK_SET)
		resources = FResources(asset, bulk)

	# print("validating python processed data using compute shader")
	# from hlsl_runner import extract_data_using_compute_shader
	# hlsl_data = extract_data_using_compute_shader(resources.upload_buffer, resources.install_info, resources.PageDependencies)
	# for pi, p in enumerate(resources.PageStreamingStates):
	# 	for ci, c in enumerate(p.data.Clusters):
	# 		# validate the tri strips the tri strips
	# 		for ti, t in enumerate(c.StripIndices):
	# 			ref = hlsl_data['tri_strips'][pi][ci][ti]
	# 			assert(ref is not None)
	# 			assert(ref[0] == 1)
	# 			assert(t.x == ref[1])
	# 			assert(t.y == ref[2])
	# 			assert(t.z == ref[3])
	# 			assert(hlsl_data['mat_id'][pi][ci][ti] in material_lookup)
			
	# 		# check if we missed a strip
	# 		if len(c.StripIndices) < NANITE_MAX_CLUSTER_TRIANGLES:
	# 			ref = hlsl_data['tri_strips'][pi][ci][len(c.StripIndices)]
	# 			assert(ref[0] == 0)

	# 		# Validate the vert refs
	# 		for vi, vr in enumerate(c.RefVerticies):
	# 			if vi >= c.NumVerts: break
	# 			ref = hlsl_data['ver_refs'][pi][ci][vi]
	# 			if ref[0] == 0:
	# 				assert(vr is None)
	# 			else:		
	# 				assert(ref == vr)

	# 		# Validate the verts
	# 		for vi in range(c.NumVerts):
	# 			ov = c.Vertices[vi]
	# 			ref = hlsl_data['ver_pos'][pi][ci][vi]
	# 			assert(hlsl_data['ver_attr'][pi][ci][vi] is not None)
	# 			assert(FVertex(*ref[1:]) == ov)

	# 			assert(c.VertAttrs[vi] is not None)

	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['nr'][0], c.VertAttrs[vi].Normal.x))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['nr'][1], c.VertAttrs[vi].Normal.y))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['nr'][2], c.VertAttrs[vi].Normal.z))

	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['tx'][0], c.VertAttrs[vi].TangentX_AndSign.x))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['tx'][1], c.VertAttrs[vi].TangentX_AndSign.y))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['tx'][2], c.VertAttrs[vi].TangentX_AndSign.z))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['tx'][3], c.VertAttrs[vi].TangentX_AndSign.w))

	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['cl'][0], c.VertAttrs[vi].Color.x))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['cl'][1], c.VertAttrs[vi].Color.y))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['cl'][2], c.VertAttrs[vi].Color.z))
	# 			assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['cl'][3], c.VertAttrs[vi].Color.w))

	# 			for txc_i in range(c.NumUVs):
	# 				assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['uv'][txc_i][0], c.VertAttrs[vi].TexCoords[txc_i].x))
	# 				assert(float_check(hlsl_data['ver_attr'][pi][ci][vi]['uv'][txc_i][1], c.VertAttrs[vi].TexCoords[txc_i].y))

	has_tangents = False
	max_tex_coords = 0
	num_tris = 0
	num_verts = 0
	print('parsing high quality clusters')
	HIGH_QUALITY_FLAG = FNaniteStreamingPage.FCluster.FClusterFlags(7)
	LODError: dict[float, list['FNaniteStreamingPage.FCluster']] = {}
	for pi, p in enumerate(resources.PageData):
		for ci, c in enumerate(p.Clusters):
			if c.Flags == HIGH_QUALITY_FLAG:
				has_tangents = has_tangents or c.bHasTangents
				max_tex_coords = max(max_tex_coords, c.NumUVs)
				c.local_page_index = pi
				c.local_cluster_index = ci
				if c.LODError not in LODError:
					LODError[c.LODError] = [c]
				else:
					LODError[c.LODError].append(c)
				
				num_tris += c.NumTris
				num_verts += c.NumVerts
				for vi in range(c.NumVerts):
					assert(c.Vertices[vi] is not None)
					assert(c.VertAttrs[vi] is not None)
				
				for ti in range(c.NumTris):
					assert(c.StripIndices[ti] is not None)
					assert(c.MatIndices[ti] is not None)


	match output_format:
		case 'gltf' | 'glb':
			def get_buffer(len):
				ret = io.BytesIO(b'\x00' * len)
				ret.seek(0, os.SEEK_SET)
				return ret
			
			print(f'converting to {output_format}')
			# the buffers are definitively too big, but it should help out with processing speed and it's simpler this way
			gltf_strp_idx = [get_buffer(12 * num_tris) for _ in range(len(material_lookup))]
			gltf_vert_pos = [get_buffer(12 * num_verts) for _ in range(len(material_lookup))]
			gltf_vert_nrm = [get_buffer(12 * num_verts) for _ in range(len(material_lookup))]
			gltf_vert_col = [get_buffer(16 * num_verts) for _ in range(len(material_lookup))]
			gltf_vert_tan = [get_buffer(16 * num_verts) for _ in range(len(material_lookup))]
			gltf_vert_uvs = [[get_buffer(16 * num_verts) for _ in range(max_tex_coords)] for _ in range(len(material_lookup))]

			mat_tri_indicies = [-1] * len(material_lookup)
			for lod in sorted(LODError.keys()):
				for c in LODError[lod]:
					for ti, t in enumerate(c.StripIndices):
						material_id = c.MatIndices[ti]
						new_ti = mat_tri_indicies[material_id]
						for vi in t.xyz():
							v = c.Vertices[vi]
							va = c.VertAttrs[vi]
							gltf_strp_idx[material_id].write(struct.pack('<I', new_ti := new_ti + 1))
							gltf_vert_pos[material_id].write(struct.pack('<fff', *(v * EXPORT_SCALE).xzy()))
							gltf_vert_nrm[material_id].write(struct.pack('<fff', *va.Normal.xzy()))
							gltf_vert_col[material_id].write(struct.pack('<ffff', *va.Color.xyzw()))
							if has_tangents:
								gltf_vert_tan[material_id].write(struct.pack('<ffff', va.TangentX_AndSign.xzyw()))
							for tex_coord_id in range(max_tex_coords):
								gltf_vert_uvs[material_id][tex_coord_id].write(struct.pack('<ff', *va.TexCoords[tex_coord_id].xy()))

						mat_tri_indicies[material_id] = new_ti

			gltf = pygltflib.GLTF2(
				scene=0,
				scenes=[pygltflib.Scene(nodes=[0])],
				nodes=[pygltflib.Node(mesh=0)],
				meshes=[pygltflib.Mesh(name=model_name)]
			)

			state = {
				'blob': b'',
				'accesor_index': -1
			}
			def add_buffer_accessor(data: io.BytesIO, componentType:int, elem_size:int, type: int, target: int, normalized:bool|None=False):
				accesor_index = state['accesor_index'] + 1
				state['accesor_index'] = accesor_index
				buffer_offset = len(state['blob'])
				buffer_len = data.tell()
				gltf.accessors.append(pygltflib.Accessor(
					bufferView = accesor_index,
					componentType = componentType,
					count = buffer_len // elem_size,
					type = type,
					normalized=normalized
				))
				gltf.bufferViews.append(pygltflib.BufferView(
					buffer = 0,
					byteOffset = buffer_offset,
					byteLength = buffer_len,
					target = target
				))
				data.seek(0, os.SEEK_SET)
				state['blob'] += data.read(buffer_len)
				return accesor_index
				

			for material_id, material_name in material_lookup.items():
				gltf.materials.append(pygltflib.Material(doubleSided=True, name=material_name))
				
				attributes = pygltflib.Attributes()
				
				# positions
				attributes.POSITION = add_buffer_accessor(
					data = gltf_vert_pos[material_id],
					componentType = pygltflib.FLOAT,
					elem_size = 12,
					type = pygltflib.VEC3,
					target = pygltflib.ARRAY_BUFFER
				)
				
				# normals
				attributes.NORMAL = add_buffer_accessor(
					data = gltf_vert_nrm[material_id],
					componentType = pygltflib.FLOAT,
					elem_size = 12,
					type = pygltflib.VEC3,
					target = pygltflib.ARRAY_BUFFER,
					normalized=True
				)

				# vertex colors
				attributes.COLOR_0 = add_buffer_accessor(
					data = gltf_vert_col[material_id],
					componentType = pygltflib.FLOAT,
					elem_size = 16,
					type = pygltflib.VEC4,
					target = pygltflib.ARRAY_BUFFER,
					normalized=True
				)

				# tangents
				if has_tangents:
					attributes.TANGENT = add_buffer_accessor(
						data = gltf_vert_tan[material_id],
						componentType = pygltflib.FLOAT,
						elem_size = 16,
						type = pygltflib.VEC4,
						target = pygltflib.ARRAY_BUFFER,
						normalized=True
					)

				# uvs
				for tex_coord_id in range(max_tex_coords):
					accesor_index = add_buffer_accessor(
						data = gltf_vert_uvs[material_id][tex_coord_id],
						componentType = pygltflib.FLOAT,
						elem_size = 8,
						type = pygltflib.VEC2,
						target = pygltflib.ARRAY_BUFFER,
					)
					match tex_coord_id:
						case 0: attributes.TEXCOORD_0 = accesor_index
						case 1: attributes.TEXCOORD_1 = accesor_index
						case _: setattr(attributes, f'TEXCOORD_{tex_coord_id}', accesor_index)

				# tri indices
				primitive = pygltflib.Primitive(
					material = material_id,
					attributes = attributes,
					indices = add_buffer_accessor(
						data = gltf_strp_idx[material_id],
						componentType = pygltflib.UNSIGNED_INT,
						elem_size = 4,
						type = pygltflib.SCALAR,
						target = pygltflib.ELEMENT_ARRAY_BUFFER
					)
				)

				gltf.meshes[0].primitives.append(primitive)

			gltf.buffers.append(pygltflib.Buffer(byteLength=len(state['blob'])))
			gltf.set_binary_blob(state['blob'])

			[b.close() for b in gltf_strp_idx]
			[b.close() for b in gltf_vert_pos]
			[b.close() for b in gltf_vert_nrm]
			[b.close() for b in gltf_vert_col]
			[b.close() for b in gltf_vert_tan]
			[[b.close() for b in l] for l in gltf_vert_uvs]
			
			print(f'saving {output_format}')
			gltf.save(f"./out/{model_name}.{output_format}")

		case _:
			print('converting to obj')
			lines = list()
			vertex_index = 1
			uv_index = 1
			lines.append(f'o {model_name}')
			for lod in sorted(LODError.keys()):
				for c in LODError[lod]:
					for vi, v in enumerate(c.Vertices):
						assert(v is not None)
						if v.index is None:
							v.index = vertex_index
							vertex_index += 1
							line = f"v {v.x*EXPORT_SCALE} {v.z*EXPORT_SCALE} {v.y*EXPORT_SCALE}"
							lines.append(line)
					
					for ti, t in enumerate(c.StripIndices):
						assert(t is not None)
						face_line = 'f '
						for vi in t.xyz():
							va = c.VertAttrs[vi]
							v = c.Vertices[vi]
							assert(v is not None)
							lines.append(f'vn {va.Normal.x} {va.Normal.z} {va.Normal.y}')
							lines.append(f'vt {va.TexCoords[UV_INDEX].x} {1 - va.TexCoords[UV_INDEX].y}')
							face_line += f' {v.index}/{uv_index}/{uv_index}'
							uv_index += 1
						lines.append(f'usemtl {material_lookup[c.MatIndices[ti]]}')
						lines.append(face_line)

			print('writing .obj file')
			with open(f"./out/{model_name}.obj", 'w', encoding='UTF8') as f:
				f.write('\n'.join(lines))

	
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog='simple-nanite-parser',
		description='A simple parser for cooked Unreal Engine 5.3+ static meshes that use nanite.'
	)
	valid_formats = ['glb','gltf','obj']
	parser.add_argument('filename', help="Cooked uasset or json file to parse.")
	parser.add_argument('--format', '-f', choices=valid_formats, default='glb', help="The format to use for the output file")

	args = parser.parse_args()
	if not isinstance(args.filename, str):
		raise ValueError("File name missing")
	if (not isinstance(args.format, str)) or (args.format not in valid_formats):
		raise ValueError("File name missing")
	
	main(os.path.splitext(args.filename)[0], args.format)