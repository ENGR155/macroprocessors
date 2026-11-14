"""Independent exported STEP/STL review. Never imports the CAD generator."""
from pathlib import Path
import cadquery as cq
import math,json,itertools,struct,collections
R=Path(__file__).resolve().parent
names=['01_frame_base_upright_tray','02_cantilever_vented_head_upper_sensor','03_helper_cassette_lower_sensor_guard']
S={n:cq.importers.importStep(str(R/(n+'_assembled.step'))).val() for n in names}
S.update({p.stem:cq.importers.importStep(str(p)).val() for p in R.glob('REF_*.step')})
C=[]
def check(n,ok,detail):C.append(dict(name=n,passed=bool(ok),detail=detail))
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis))
def inter(a,b):return a.intersect(b).Volume()
for n,s in S.items():check(n+' valid single solid',s.isValid() and len(s.Solids())==1,{'solids':len(s.Solids()),'bbox_mm':bb(s),'volume_mm3':s.Volume()})
assembly=cq.importers.importStep(str(R/'testbox1_PLA_three_print_assembly.step')).val()
check('assembly eight solids',len(assembly.Solids())==8,len(assembly.Solids()))
printed=cq.importers.importStep(str(R/'three_print_parts_assembled.step')).val()
check('exactly three fabrication solids',len(printed.Solids())==3,len(printed.Solids()))
coll=[]
for (na,a),(nb,b) in itertools.combinations(S.items(),2):
 v=inter(a,b)
 if v>1e-5:coll.append([na,nb,v])
check('all 28 assembly pairs nonintersecting',not coll,coll)
expected_dims=[[180,160,190],[90,103,40],[52,52,8]]
for n,expected in zip(names,expected_dims):
 b=bb(S[n]);d=[b[i+3]-b[i] for i in range(3)]
 check(n+' independent assembly dimensions',all(abs(a-b)<1e-5 for a,b in zip(d,expected)),d)
for idx,n in enumerate(names):
 p=cq.importers.importStep(str(R/(n+'_PRINT.step'))).val();b=bb(p);dims=[b[i+3]-b[i] for i in range(3)]
 check(n+' fits central 220mm bed and 256mm height',b[0]>=-1e-5 and b[1]>=-1e-5 and abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
 expected=[S[n],S[n].rotate((0,0,0),(1,0,0),180).translate((-45,142,200)),S[n].rotate((0,0,0),(1,0,0),90).translate((-64,170,-39))][idx]
 difference=p.cut(expected).Volume()+expected.cut(p).Volume()
 check(n+' explicit physical print orientation',difference<1e-4,{'symmetric_difference_mm3':difference,'print_bbox_mm':b})
 faces=[f for f in p.Faces() if abs(f.BoundingBox().zmin)<1e-5 and abs(f.BoundingBox().zmax)<1e-5]
 area=sum(f.Area() for f in faces)
 check(n+' substantial actual flat bed contact',area>[27000,8000,200][idx],{'bed_contact_mm2':area,'footprint_mm':dims[:2],'height_mm':dims[2]})
 raw=(R/(n+'_PRINT.stl')).read_bytes();count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count
 edges=collections.Counter();vertices=[];adj=collections.defaultdict(set);deg=0
 for i in range(count):
  vals=struct.unpack_from('<12f',raw,84+i*50);v=[tuple(round(c,5) for c in vals[j:j+3]) for j in (3,6,9)];vertices.extend(v)
  if len(set(v))!=3:deg+=1
  for a,z in ((0,1),(1,2),(2,0)):
   edges[tuple(sorted((v[a],v[z])))]+=1;adj[v[a]].add(v[z]);adj[v[z]].add(v[a])
 left=set(adj);components=0
 while left:
  components+=1;stack=[left.pop()]
  while stack:
   for v in adj[stack.pop()]:
    if v in left:left.remove(v);stack.append(v)
 nonmanifold=sum(x!=2 for x in edges.values())
 check(n+' STL one closed connected manifold',nonmanifold==0 and deg==0 and components==1,{'triangles':count,'nonmanifold_edges':nonmanifold,'degenerate_faces':deg,'connected_components':components})
 mb=[min(v[j] for v in vertices) for j in range(3)]+[max(v[j] for v in vertices) for j in range(3)]
 check(n+' STL dimensions match print STEP',all(abs(a-z)<.06 for a,z in zip(mb,b)),mb)
fixed={n:s for n,s in S.items() if 'payload' not in n}
bad=[]
for gap in range(10,21):
 payload=cyl(90,65,170-gap-6,6.35,6)
 for n,s in fixed.items():
  v=inter(payload,s)
  if v>1e-5:bad.append([gap,n,v])
check('12.7x6 assumed payload complete 10-20mm sweep',not bad,bad)
check('guard minimum nominal clearance',abs(bb(S[names[2]])[2]-160-2)<1e-5,{'EM_face_min_gap_mm':10,'guard_bottom_z_mm':162,'nominal_margin_mm':2})
helper=cyl(90,65,168.1,19.15/2,1.69)
check('19.15x1.69 worst-case helper fit',all(inter(helper,S[n])<1e-5 for n in names),{'diametral_clearance_mm':.45,'axial_clearance_mm':.21})
em_tol=cyl(90,65,170,25.5/2,20.6)
check('assumed expanded EM25.5x20.6 envelope fit',all(inter(em_tol,S[n])<1e-5 for n in names),{'NOTE':'chosen tolerance scenario, not supplier specification','cavity_nominal_diameter_mm':26,'available_height_mm':20.8})
# Insertion: remove cassette/helper/lower sensor, translate nominal EM vertically into upper collar.
bad=[]
for bottom in range(140,171,2):
 em=cyl(90,65,bottom,12.5,20)
 for n in names[:2]:
  v=inter(em,S[n])
  if v>1e-5:bad.append([bottom,n,v])
check('nominal EM inserts from below with cassette removed',not bad,bad)
wire=cq.Solid.makeBox(4,30,2,cq.Vector(88,77.5,179))
check('4x2mm radial lead exit through open cage',inter(wire,S[names[1]])<1e-5,'Chosen exit x88..92,y77.5..107.5,z179..181; actual purchased lead position still must be checked')
retain=[(90+19*math.cos(a),65+19*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
bad=[]
for x,y in retain:
 envelopes={'M3 shaft':cyl(x,y,166.95,1.5,33.1),'M3 socket head 6diax3':cyl(x,y,164,3,3),'M3 upper washer7dia':cyl(x,y,200,3.5,.5),'M3 upper nut6.4dia':cyl(x,y,200.5,3.2,2.4)}
 for label,envelope in envelopes.items():
  for n,s in S.items():
   v=inter(envelope,s)
   if v>1e-5:bad.append([label,[x,y],n,v])
check('M3 shafts heads and upper hardware clear',not bad,{'NO_LOWER_WASHERS':True,'collisions':bad,'nominal_shaft_stack_mm':33,'M3x40_spare_after_0p5washer_2p4nut_mm':4.1})
bad=[]
for x,z in [(60,172),(120,172),(60,184),(120,184)]:
 envelopes={'M4 shaft':cyl(x,119.9,z,2,22.2,(0,1,0)),'M4 front sockethead7dia':cyl(x,115.2,z,3.5,4,(0,1,0)),'M4 front washer9dia':cyl(x,119.2,z,4.5,.8,(0,1,0)),'M4 rear washer9dia':cyl(x,142,z,4.5,.8,(0,1,0)),'M4 rear nut8.2dia':cyl(x,142.8,z,4.1,3.2,(0,1,0))}
 for label,envelope in envelopes.items():
  for n,s in S.items():
   v=inter(envelope,s)
   if v>1e-5:bad.append([label,[x,z],n,v])
check('M4 rear fastener hardware envelopes clear',not bad,{'collisions':bad,'nominal_stack_mm':22,'M4x30_spare_after_two_0p8washers_3p2nut_mm':3.2})
# Sensor can enter from either open side without intersecting fixed plastic.
bad=[]
for x0 in range(60,85,2):
 sensor=cq.Solid.makeBox(12,8,2,cq.Vector(x0,61,164))
 v=inter(sensor,S[names[2]])
 if v>1e-5:bad.append([x0,v])
check('lower 12x8x2 Hall allowance inserts from side',not bad,bad)
scenario={'load_N':5,'effective_modulus_MPa_ASSUMED':500,'upright_width_mm':90,'upright_thickness_mm':12,'free_upright_height_mm_ASSUMED':80,'arm_lever_mm':65,'arm_width_mm':90,'arm_thickness_mm':10}
F=5;E=500;L=65;H=80;I=90*12**3/12;Ia=90*10**3/12
scenario.update({'upright_rotation_vertical_drop_mm':F*L*H/(E*I)*L,'arm_bending_vertical_drop_mm':F*L**3/(3*E*Ia),'upright_axial_compression_mm':F*182/(E*90*12)})
scenario['total_vertical_drop_mm']=sum(scenario[k] for k in ('upright_rotation_vertical_drop_mm','arm_bending_vertical_drop_mm','upright_axial_compression_mm'))
scenario['limitations']='Idealized scenario only, excludes local joint compliance, gusset flexure, print defects, material anisotropy, creep and heating. Not a structural or thermal qualification.'
result={'passed':all(x['passed'] for x in C),'check_count':len(C),'scope':'Independent exported geometry, nominal assembly and orientation checks only','checks':C,'conditional_beam_scenario':scenario}
(R/'independent_check_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'passed':result['passed'],'check_count':len(C),'failed':[x for x in C if not x['passed']],'conditional_beam_scenario':scenario},indent=2))
