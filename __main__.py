from unreal_io import *
from nanite_constants import *
from FResources import FResources
import FNaniteStreamingPage
import json
from hlsl_runner import extract_data_using_compute_shader
import argparse

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
	

def main(TEST_PATH: str):
	
	
	EXPORT_SCALE = 1/100
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
	
	print('identifying high quality lod error threshold')
	max_lod_exclusive = math.inf
	for node in resources.HierarchyNodes:
		for slice in node:
			if slice.MinLODError < 0:
				max_lod_exclusive = min(max_lod_exclusive, slice.MaxParentLODError)

	print("extracting data")
	hlsl_data = extract_data_using_compute_shader(resources.upload_buffer, resources.install_info, resources.PageDependencies)
	
	# Data validation, ignore while we are extracting from the compute shader for the moment
	# for pi, p in enumerate(resources.PageStreamingStates):
	# 	for ci, c in enumerate(p.data.Clusters):
	# 		# transfer the ref vertices
	# 		for vi in range(c.NumVerts):
	# 			ov = c.Vertices[vi]
	# 			pos_ref = hlsl_data['ver_pos'][pi][ci][vi]
	# 			ext_ver = FVertex(*pos_ref[1:])
	# 			if ov is not None:
	# 				assert(pos_ref[0] == 1)
	# 				assert(ext_ver == ov)
	# 			else:
	# 				assert(pos_ref[0] == 1)
	# 				# validate ref data
	# 				ref = hlsl_data['pos_refs'][pi][ci][vi]
	# 				assert(ref is not None)
	# 				assert(ref[0] == 1)

	# 				# validate ref page id
	# 				assert(0 <= ref[1] <= p.DependenciesNum)
	# 				ref_page_id: int = pi if ref[1] == 0 else resources.PageDependencies[p.DependenciesStart + (ref[1] - 1)]
	# 				assert (0 <= ref_page_id < len(resources.PageData))
	# 				ref_page = resources.PageData[ref_page_id]
					
	# 				# validate ref cluster id
	# 				ref_cluster_id: int = ref[2]
	# 				assert(0 <= ref_cluster_id < len(ref_page.Clusters))
	# 				ref_cluster = ref_page.Clusters[ref_cluster_id]

	# 				# validate ref vertex id
	# 				ref_vertex_id: int = ref[3]
	# 				assert(0 <= ref_vertex_id < len(ref_cluster.Vertices))
	# 				rv = ref_cluster.Vertices[ref_vertex_id]
	# 				assert(rv is not None)
	# 				# transfer the vertex over
	# 				c.Vertices[vi] = rv if rv == ext_ver else ext_ver

	# 		# transfer the tri strips
	# 		for ti, t in enumerate(c.StripIndices):
	# 			ref = hlsl_data['tri_strips'][pi][ci][ti]
	# 			assert(ref is not None)
	# 			assert(ref[0] == 1)
	# 			assert(t.x == ref[1])
	# 			assert(t.y == ref[2])
	# 			assert(t.z == ref[3])
	# 			assert(hlsl_data['ver_attr'][pi][ci][ti] is not None)
	# 			assert(hlsl_data['mat_id'][pi][ci][ti] in material_lookup)

	# 		# validate extracted data
	# 		if len(c.StripIndices) < NANITE_MAX_CLUSTER_TRIANGLES or ci == len(p.data.Clusters) - 1:
	# 			ref = hlsl_data['tri_strips'][pi][ci][len(c.StripIndices)]
	# 			assert(ref[0] == 0)
	# 		else:
	# 			ref = hlsl_data['tri_strips'][pi][ci][len(c.StripIndices)]
	# 			assert(ref[0] == 1)

	print('parsing high quality clusters')
	LODError: dict[float, list['FNaniteStreamingPage.FCluster']] = {}
	for pi, p in enumerate(resources.PageData):
		for ci, c in enumerate(p.Clusters):
			if c.LODError < max_lod_exclusive:
				c.local_page_index = pi
				c.local_cluster_index = ci
				if c.LODError not in LODError:
					LODError[c.LODError] = [c]
				else:
					LODError[c.LODError].append(c)
				
				for vi in range(c.NumVerts):
					pos = hlsl_data['ver_pos'][pi][ci][vi]
					assert(pos[0] == 1)
					c.Vertices[vi] = FVertex(pos[1], pos[2], pos[3])
				
				for ti in range(c.NumTris):
					indices = hlsl_data['tri_strips'][pi][ci][ti]
					assert(indices[0] == 1)
					c.StripIndices[ti] = FUIntVector3(indices[1], indices[2], indices[3])

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
				vert_attrs = hlsl_data['ver_attr'][c.local_page_index][c.local_cluster_index][ti]
				face_line = 'f '
				for tvi, vi in enumerate(t.xyz()):
					va = vert_attrs[tvi]
					v = c.Vertices[vi]
					assert(v is not None)
					lines.append(f'vn {va["nr"][0]} {va["nr"][2]} {va["nr"][1]}')
					lines.append(f'vt {va["uv"][0]} {1 - va["uv"][1]}')
					face_line += f' {v.index}/{uv_index}/{uv_index}'
					uv_index += 1
				lines.append(f'usemtl {material_lookup[hlsl_data['mat_id'][c.local_page_index][c.local_cluster_index][ti]]}')
				lines.append(face_line)
				
	print('witing .obj file')
	with open(f"./out/{model_name}.obj", 'w', encoding='UTF8') as f:
		f.write('\n'.join(lines))

	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog='simple-nanite-parser',
		description='A simple parser for cooked Unreal Engine 5.3+ static meshes that use nanite.'
	)
	parser.add_argument('filename', help="Cooked uasset or json file to parse.")
	
	args = parser.parse_args()
	if not isinstance(args.filename, str):
		raise ValueError("File name missing")
	
	main(os.path.splitext(args.filename)[0])