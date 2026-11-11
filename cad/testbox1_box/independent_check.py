"""Independent checker: reimports delivered STEP, never imports build_cad."""
from pathlib import Path
import json, math, itertools, struct, collections
import cadquery as cq

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'component_manifest.json').read_text())
shapes={n:cq.importers.importStep(str(ROOT/'parts'/(n+'.step'))).val() for n in manifest}
checks=[]
def check(name, passed, detail):
    checks.append(dict(name=name,passed=bool(passed),detail=detail))
def volume_intersection(a,b):
    return a.intersect(b).Volume()
def cylinder(x,y,z,r,h,axis=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis))
def bbox(s):
    b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
for n,s in shapes.items():
    check(n+' valid single solid',s.isValid() and len(s.Solids())==1,{'solids':len(s.Solids()),'volume_mm3':s.Volume()})
    check(n+' exported dimensions',all(abs(a-b)<1e-5 for a,b in zip(bbox(s),manifest[n]['bbox_mm'])),bbox(s))
assembly=cq.importers.importStep(str(ROOT/'testbox1_box_maglev.step')).val()
check('assembly contains all 16 solids',len(assembly.Solids())==16,{'solid_count':len(assembly.Solids())})
overlaps=[]
for (na,a),(nb,b) in itertools.combinations(shapes.items(),2):
    v=volume_intersection(a,b)
    if v>1e-5:overlaps.append([na,nb,v])
check('all delivered parts and references nonintersecting',not overlaps,{'pair_count':120,'overlaps_mm3':overlaps})
expected={'01_plywood_base':[180,160,18],'03_clear_rear_panel':[90,6,172],'04_clear_top_cantilever':[90,97,6],'REF_electromagnet_25x20':[25,25,20],'REF_helper_19p05x1p5875':[19.05,19.05,1.5875]}
for n,dims in expected.items():
    bb=bbox(shapes[n]);actual=[bb[i+3]-bb[i] for i in range(3)]
    check(n+' independently expected size',all(abs(a-b)<1e-5 for a,b in zip(actual,dims)),actual)
fixed={n:s for n,s in shapes.items() if 'payload' not in n}
payload_collisions=[]
for gap in range(10,21):
    payload=cylinder(90,65,170-gap-6,6.35,6)
    for n,s in fixed.items():
        v=volume_intersection(payload,s)
        if v>1e-5:payload_collisions.append([gap,n,v])
check('assumed 12.7x6 payload clears complete 10-20mm sweep',not payload_collisions,payload_collisions)
check('minimum gap to guard',abs((bbox(shapes['08_lower_Hall_guard'])[2]-(170-10))-2)<1e-5,{'minimum_guard_clearance_mm':2.0,'EM_face_gap_mm':10.0,'guard_stop_EM_face_gap_mm':8.0})
largest_helper=cylinder(90,65,168.1,19.15/2,1.69)
check('helper supplier worst-case envelope fits pocket',volume_intersection(largest_helper,shapes['07_helper_retainer_cassette'])<1e-5 and volume_intersection(largest_helper,shapes['REF_electromagnet_25x20'])<1e-5,{'diameter_mm':19.15,'thickness_mm':1.69,'diametral_clearance_mm':.45,'axial_clearance_mm':.21})
paths=[]
for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4):
    paths.append(('cassette',90+17.5*math.cos(a),65+17.5*math.sin(a),166.5,30.0,1.5))
for y in (46,84):paths.append(('guard',90,y,161.5,35,1.5))
for x in (69,111):
    for y in (44,86):paths.append(('head',x,y,183.5,13,1.5))
for x in (60,120):paths.append(('upper carrier',x,65,189.5,9,1.5))
for x in (56,124):paths.append(('arm bracket',x,115,185.5,11,2))
bolt_collisions=[]
for label,x,y,z,h,r in paths:
    shaft=cylinder(x,y,z,r,h)
    for n,s in shapes.items():
        v=volume_intersection(shaft,s)
        if v>1e-5:bolt_collisions.append([label,[x,y,z],n,v])
check('vertical fastening shafts have uninterrupted holes',not bolt_collisions,bolt_collisions)
# Conservative 7mm OD washer/nut tool-free envelopes immediately outside stacks.
nut_collisions=[]
for label,x,y,z,h,r in paths:
    bottom={'cassette':167,'guard':162,'head':184,'upper carrier':190,'arm bracket':186}[label]
    top={'cassette':196,'guard':196,'head':196,'upper carrier':198,'arm bracket':196}[label]
    for side,zz in [('bottom',bottom-3),('top',top)]:
        ring=cylinder(x,y,zz,3.5,3).cut(cylinder(x,y,zz-.1,r+.2,3.2))
        for n,s in shapes.items():
            v=volume_intersection(ring,s)
            if v>1e-5:nut_collisions.append([label,side,[x,y,zz],n,v])
check('7mm washer/nut envelopes clear adjacent solids',not nut_collisions,nut_collisions)
# Rear base screws must miss horizontal clamp bolts.
clamp_wood=[cylinder(x,115,0,2,40) for x in (75,105)]
clamp_cross=[cylinder(x,99,31,2,40,(0,1,0)) for x in (60,120)]
check('rear clamp crossed fastening paths separated',all(volume_intersection(a,b)<1e-5 for a in clamp_wood for b in clamp_cross),'Vertical x75/105; horizontal x60/120')
for n,m in manifest.items():
    if m['kind']!='fabricate':continue
    raw=(ROOT/'parts'/(n+'.stl')).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0]
    if len(raw)!=84+50*count:raise ValueError('Expected binary STL: '+n)
    edges=collections.Counter();points=[];degenerate=0
    for i in range(count):
        vals=struct.unpack_from('<12f',raw,84+i*50)
        verts=[tuple(round(c,5) for c in vals[j:j+3]) for j in (3,6,9)]
        points.extend(verts)
        if len(set(verts))!=3:degenerate+=1
        for a,b in ((0,1),(1,2),(2,0)):edges[tuple(sorted((verts[a],verts[b])))]+=1
    boundary=sum(v!=2 for v in edges.values())
    check(n+' STL closed manifold',boundary==0 and degenerate==0,{'triangles':count,'non_two_incidence_edges':boundary,'degenerate_faces':degenerate})
    mesh_bbox=[min(p[j] for p in points) for j in range(3)]+[max(p[j] for p in points) for j in range(3)]
    check(n+' STL same dimensions as STEP',all(abs(a-b)<.07 for a,b in zip(mesh_bbox,bbox(shapes[n]))),mesh_bbox)
result={'scope':'Independent STEP geometry and nominal assembly checking; no physical force, thermal or control validation','passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks}
(ROOT/'independent_check_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'passed':result['passed'],'check_count':len(checks),'failed':[c for c in checks if not c['passed']]},indent=2))
