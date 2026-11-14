"""Split mesher T-junction edges at existing collinear vertices. Never cap holes.

OCCT can tessellate a tangent cylindrical union with AB on one face and AC+CB
on its neighbour. Splitting the AB triangle at the already-existing C produces
matching edge incidence without introducing a cap or changing the BRep surface.
"""
from pathlib import Path
import struct,collections,math,json

def key(v):return tuple(round(x,5) for x in v)
def norm(t):
 a,b,c=t;u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];l=math.sqrt(sum(x*x for x in n));return [x/l for x in n]
def repair(path):
 path=Path(path);raw=path.read_bytes();N=struct.unpack_from('<I',raw,80)[0]
 ts=[]
 for i in range(N):
  f=struct.unpack_from('<12f',raw,84+50*i);ts.append([tuple(f[j:j+3]) for j in (3,6,9)])
 count=0;max_deviation=0.
 for iteration in range(100):
  edges=collections.Counter();points={}
  for t in ts:
   for v in t:points[key(v)]=v
   for j in range(3):edges[tuple(sorted((key(t[j]),key(t[(j+1)%3]))))]+=1
  boundary={e for e,n in edges.items() if n!=2}
  if not boundary:break
  candidates={v for e in boundary for v in e};fixed=False
  for ti,t in enumerate(ts):
   for j in range(3):
    a,b=t[j],t[(j+1)%3]
    if tuple(sorted((key(a),key(b)))) not in boundary:continue
    u=[b[q]-a[q] for q in range(3)];l2=sum(v*v for v in u)
    for kv in candidates-{key(a),key(b)}:
     c=points[kv];v=[c[q]-a[q] for q in range(3)];s=sum(u[q]*v[q] for q in range(3))/l2
     if not .00001<s<.99999:continue
     dev=math.sqrt(sum((c[q]-(a[q]+s*u[q]))**2 for q in range(3)))
     if dev>2e-4:continue
     opposite=t[(j+2)%3]
     ts[ti]=[a,c,opposite];ts.append([c,b,opposite]);count+=1;max_deviation=max(max_deviation,dev);fixed=True;break
    if fixed:break
   if fixed:break
  if not fixed:raise RuntimeError(f'Unresolved {len(boundary)} boundary/nonmanifold edges; no collinear split applicable: {path.name}')
 else:raise RuntimeError('Too many mesh splits')
 output=bytearray(b'Conforming mesh; existing collinear T-junction vertex splits only'.ljust(80,b' '));output.extend(struct.pack('<I',len(ts)))
 for t in ts:output.extend(struct.pack('<12fH',*norm(t),*(x for v in t for x in v),0))
 path.write_bytes(output)
 return {'file':path.name,'original_triangles':N,'conforming_triangles':len(ts),'collinear_edge_splits':count,'maximum_collinearity_deviation_mm':max_deviation,'method':'split existing long edge at existing boundary vertex; no hole capping'}
if __name__=='__main__':
 root=Path(__file__).resolve().parent
 results=[repair(p) for p in root.glob('*_PRINT.stl')]
 (root/'mesh_conformity.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
