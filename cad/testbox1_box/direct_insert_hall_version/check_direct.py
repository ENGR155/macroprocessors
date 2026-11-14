"""Check delivered files without importing the geometry generator."""
from pathlib import Path
import json,struct,collections,itertools,hashlib
import cadquery as q
R=Path(__file__).resolve().parent
M=json.loads((R/'component_manifest.json').read_text());C=[]
BASELINE=json.loads((R/'baseline_sha256.json').read_text())
S={n:q.importers.importStep(str(R/(n+'_assembled.step'))).val() for n in M}
F={p.stem:q.importers.importStep(str(p)).val() for p in R.glob('REF_*.step')}
def ck(n,ok,detail=None):C.append({'name':n,'passed':bool(ok),'detail':detail})
def box(x,y,z,dx,dy,dz):return q.Solid.makeBox(dx,dy,dz,q.Vector(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return q.Solid.makeCylinder(r,h,q.Vector(x,y,z),q.Vector(*axis))
def v(a,b):return a.intersect(b).Volume()
def b(s):
    t=s.BoundingBox();return [t.xmin,t.ymin,t.zmin,t.xmax,t.ymax,t.zmax]
def sweep(s,lo=-4.2,hi=4.2):
    a=b(s);return box(a[0],a[1],a[2]+lo,a[3]-a[0],a[4]-a[1],a[5]-a[2]+hi-lo)
def mesh(path,count):
    raw=path.read_bytes();num=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*num
    edges=collections.Counter();adj=collections.defaultdict(set);vs=[];deg=0
    for i in range(num):
        f=struct.unpack_from('<12f',raw,84+50*i);t=[tuple(round(x,5) for x in f[j:j+3]) for j in (3,6,9)];vs+=t
        deg+=len(set(t))<3
        for j in range(3):
            a,c=t[j],t[(j+1)%3];edges[tuple(sorted((a,c)))]+=1;adj[a].add(c);adj[c].add(a)
    remain=set(adj);components=0
    while remain:
        components+=1;stack=[remain.pop()]
        while stack:
            for a in adj[stack.pop()]:
                if a in remain:remain.remove(a);stack.append(a)
    ck(path.name+' closed manifold/object count',not deg and all(n==2 for n in edges.values()) and components==count,{'components':components,'triangles':num,'nonmanifold_edges':sum(n!=2 for n in edges.values())})
    bounds=[min(t[i] for t in vs) for i in range(3)]+[max(t[i] for t in vs) for i in range(3)]
    ck(path.name+' on bed and inside220x220x256',abs(bounds[2])<.001 and bounds[0]>=-.001 and bounds[1]>=-.001 and bounds[3]<=220 and bounds[4]<=220 and bounds[5]<=256,bounds)

for n,s in {**S,**F}.items():
    count=3 if 'native_pins' in n else 1
    ck(n+' valid expected solids',s.isValid() and len(s.Solids())==count,{'solids':len(s.Solids())})
pairs=[]
for (a,sa),(c,sc) in itertools.combinations({**S,**F}.items(),2):
    overlap=v(sa,sc)
    if overlap>1e-5:pairs.append([a,c,overlap])
ck('parked geometry no overlaps',not pairs,pairs)
for n in M:
    mesh(R/(n+'_PRINT.stl'),1)
    p=q.importers.importStep(str(R/(n+'_PRINT.step'))).val()
    ck(n+' print solid valid',p.isValid() and len(p.Solids())==1)
for j,count in [(1,1),(2,1),(3,2),(4,1)]:mesh(R/f'JOB0{j}_PRINT.stl',count)
for name in ['JOB01_PRINT.stl','JOB01_PRINT.step','04_D68_payload_carrier_PRINT.stl','04_D68_payload_carrier_PRINT.step','04_D68_payload_carrier_assembled.step']:
    digest=hashlib.sha256((R/name).read_bytes()).hexdigest()
    ck(name+' preserved',digest==BASELINE[name],digest)
N=list(M);head=S[N[1]];cassette=S[N[2]];rod=S[N[4]]
stationary={n:s for n,s in S.items() if n!=N[4]}
stationary.update({n:s for n,s in F.items() if not any(k in n for k in ('LPG','native_pins','upper_retaining','lower_retaining'))})
strip=q.importers.importStep(str(R/'OPTIONAL_NONPRINT_retainer_strip.step')).val()
stationary['optional_top_retainer']=strip
for i in range(4):stationary['optional_top_disk_'+str(i)]=cyl(90,65,193+i*1.5875,19.05/2,1.5875)
fullrod=box(108,58.6,106.8,10,12,145.4)
ck('continuous whole rod prism clears fixed geometry',all(v(fullrod,s)<1e-5 for s in stationary.values()))
payload=q.Compound.makeCompound([F[n] for n in F if any(k in n for k in ('D68','nylon_retaining'))]+[S[N[3]]])
payload_sweep=sweep(payload,-5,5)
UP=[207.5+8*i for i in range(5)];LOW=[117.5+8*i for i in range(5)]
# Per-port body, maximum native pins and the positive retaining loop are checked
# for the full continuous common stroke. All 25 upper/lower pairs use these
# disjoint upper/lower intervals, not independent fine adjustments.
for label,ports,reference_floor in [('upper',UP,207.5),('lower',LOW,149.5)]:
    body=F['REF_'+label+'_LPG_max_body'];pins=F['REF_'+label+'_native_pins'];loop=F['REF_'+label+'_retaining_loop']
    for z in ports:
        for kind,shape in [('body',body),('pins',pins),('loop',loop)]:
            shape=shape.translate((0,0,z-reference_floor))
            ck(f'{label} port{z} {kind} fits rod',v(shape,rod)<1e-5)
            sw=sweep(shape)
            ck(f'{label} port{z} {kind} full continuous stroke clears',all(v(sw,s)<1e-5 for s in stationary.values()) and v(sw,payload_sweep)<1e-5)
        # Worst-pitch, width and vertical-play pin corridor in the transverse bay.
        lead=q.Compound.makeCompound([box(110,64.6+d-.275,z+.2,15.5,.55,1.5) for d in (-1.32,0,1.32)])
        ck(f'{label} port{z} pin pitch/play envelope fits',v(lead,rod)<1e-5)
        insertion=box(101.75,62.55,z,8.25,4.1,1.62)
        ck(f'{label} port{z} body insertion path clear',v(insertion,rod)<1e-5)

# One clamp only, fixed at Z195. A regular nut bears on the track in the rod.
shaft=cyl(113,54,195,1.5,20,(0,1,0))
nut=q.Workplane('XZ').workplane(offset=-70.4).center(113,195).polygon(6,6.35085).extrude(2.4).val().rotate((113,0,195),(113,1,195),30)
cap=cyl(113,51,195,2.8,3,(0,1,0))
for delta in (-4.2,-4,0,4,4.2):
    shifted=rod.translate((0,0,delta))
    ck(f'clamp shaft slot clearance {delta}',v(shaft,shifted)<1e-5 and v(shaft,head)<1e-5)
    ck(f'regular nut clearance {delta}',v(nut,shifted)<1e-5 and v(nut,head)<1e-5)
    ck(f'head counterbore clearance {delta}',v(cap,head)<1e-5)
# Rear-open top pocket: lower nut through it, then move toward the rod track.
nut_drop=sweep(nut.translate((0,6,10)), -10,0)
ck('nut top insertion pocket clear',v(nut_drop,head)<1e-5)
helper=cyl(90,65,163.1,19.15/2,6.75)
ck('four disk maximum plus adhesive below fits',v(helper,cassette)<1e-5)
ck('four disk maximum plus adhesive above fits',v(helper.translate((0,0,30)),head)<1e-5)
em=cyl(90,65,170,12.75,20.6)
ck('chosen enlarged EM envelope preserved',v(em,head)<1e-5 and v(em,cassette)<1e-5 and v(em,fullrod)<1e-5)
ck('payload entire10to20mm gap clears new guides/rod',all(v(payload_sweep,s)<1e-5 for s in [head,cassette,fullrod]))
ck('job04 one holder, no separate carriage',len(q.importers.importStep(str(R/'JOB04_PRINT.step')).val().Solids())==1)
result={'passed':all(c['passed'] for c in C),'check_count':len(C),'scope':'Nominal exported geometry, manifold meshes and conservative continuous motion. No print, wire flexibility, clamp friction, sensor saturation or thermal guarantee.','checks':C}
(R/'check_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'passed':result['passed'],'check_count':len(C),'failed':[c for c in C if not c['passed']]},indent=2))
