"""Additional STL winding and volume review using only the Python standard library."""
from pathlib import Path
import struct,json
R=Path(__file__).resolve().parent
out=[]
for name,info in json.loads((R/'component_manifest.json').read_text()).items():
    raw=(R/(name+'_PRINT.stl')).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count
    volume=0;bad=0
    for v in struct.iter_unpack('<12fH',raw[84:]):
        nx,ny,nz=v[:3];ax,ay,az,bx,by,bz,cx,cy,cz=v[3:12]
        volume+=(ax*(by*cz-bz*cy)+ay*(bz*cx-bx*cz)+az*(bx*cy-by*cx))/6
        ux,uy,uz=bx-ax,by-ay,bz-az;vx,vy,vz=cx-ax,cy-ay,cz-az
        dot=nx*(uy*vz-uz*vy)+ny*(uz*vx-ux*vz)+nz*(ux*vy-uy*vx)
        bad+=dot < -1e-9
    ratio=volume/info['volume_mm3']
    out.append({'part':name,'triangles':count,'signed_mesh_volume_mm3':volume,'opposite_face_normals':bad,'mesh_over_assembly_volume':ratio,'passed':volume>0 and bad==0 and (name.startswith('05') or abs(ratio-1)<.005)})
result={'passed':all(x['passed'] for x in out),'scope':'Primary-agent STL winding and volume review. The rod print includes sanding stock; its volume exceeds the finished assembly rod by design.','parts':out}
(R/'primary_mesh_review.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'passed':result['passed'],'parts':len(out),'opposite_face_normals':sum(x['opposite_face_normals'] for x in out)},indent=2))
