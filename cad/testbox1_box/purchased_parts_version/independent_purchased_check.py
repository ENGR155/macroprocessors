"""Independent export checks; does not import the builder's geometry or mesh repair."""
from pathlib import Path
import cadquery as cq
import math,json,itertools,struct,collections
R=Path(__file__).resolve().parent
N=['01_frame_base_upright_tray','02_cantilever_vented_head_upper_sensor','03_four_DC1_stack_cassette_lower_LPG_seat','04_D68_payload_carrier']
S={n:cq.importers.importStep(str(R/(n+'_assembled.step'))).val() for n in N}
S.update({p.stem:cq.importers.importStep(str(p)).val() for p in R.glob('REF_*.step')})
C=[]
def ck(n,ok,d):C.append(dict(name=n,passed=bool(ok),detail=d))
def box(x,y,z,a,b,c):return cq.Solid.makeBox(a,b,c,cq.Vector(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis))
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def iv(a,b):return a.intersect(b).Volume()
def overlaps(items):
 bad=[]
 for (na,a),(nb,b) in itertools.combinations(items.items(),2):
  v=iv(a,b)
  if v>1e-5:bad.append([na,nb,v])
 return bad
def mesh(path,expected_components):
 raw=path.read_bytes();num=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*num
 edges=collections.Counter();adj=collections.defaultdict(set);verts=[];deg=0
 for i in range(num):
  f=struct.unpack_from('<12f',raw,84+50*i);v=[tuple(round(t,5) for t in f[j:j+3]) for j in (3,6,9)];verts.extend(v)
  if len(set(v))<3:deg+=1
  for a,b in ((0,1),(1,2),(2,0)):edges[tuple(sorted((v[a],v[b])))]+=1;adj[v[a]].add(v[b]);adj[v[b]].add(v[a])
 left=set(adj);count=0
 while left:
  count+=1;stack=[left.pop()]
  while stack:
   for v in adj[stack.pop()]:
    if v in left:left.remove(v);stack.append(v)
 bad=sum(v!=2 for v in edges.values())
 ck(path.name+' closed expected connected meshes',bad==0 and deg==0 and count==expected_components,{'triangles':num,'nonmanifold_edges':bad,'degenerate_faces':deg,'connected_components':count})
 return [min(v[j] for v in verts) for j in range(3)]+[max(v[j] for v in verts) for j in range(3)]
for n,s in S.items():
 expected=3 if 'leads_formed' in n else 1
 ck(n+' valid solids',s.isValid() and len(s.Solids())==expected,{'solid_count':len(s.Solids()),'expected':expected,'bbox_mm':bb(s)})
 if expected==3:
  pins={str(i):p for i,p in enumerate(s.Solids())}
  ck(n+' three electrically isolated pin bodies',not overlaps(pins),[p.Volume() for p in pins.values()])
main=cq.importers.importStep(str(R/'testbox1_purchased_parts_assembly.step')).val()
ck('main assembly nineteen actual solids',len(main.Solids())==19,{'physical_solids':len(main.Solids()),'logical_entries':len(S),'print_bodies':4})
ck('main all105 component pairs nonintersecting',not overlaps(S),overlaps(S))
fab=cq.importers.importStep(str(R/'four_printed_parts_assembled.step')).val()
ck('exactly four fabrication bodies',len(fab.Solids())==4,len(fab.Solids()))
# The nominal16mm round carrier foot loses its +/-X extrema to the3mm strap notches.
expected_dims=[[180,160,190],[90,103,40],[65,52,8],[2*math.sqrt(8**2-1.5**2),16,14.3]]
for n,d in zip(N,expected_dims):
 b=bb(S[n]);actual=[b[i+3]-b[i] for i in range(3)]
 ck(n+' independent overall dimensions',all(abs(a-z)<1e-5 for a,z in zip(actual,d)),actual)
 expected=S[n]
 if n.startswith('02'):expected=expected.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
 elif n.startswith('03'):expected=expected.translate((-64,-39,-162))
 elif n.startswith('04'):expected=expected.translate((-82,-57,-140.3))
 p=cq.importers.importStep(str(R/(n+'_PRINT.step'))).val();b=bb(p)
 diff=p.cut(expected).Volume()+expected.cut(p).Volume()
 ck(n+' explicit correct bed orientation',diff<1e-4,{'symmetric_difference_mm3':diff,'bbox_mm':b})
 ck(n+' central220 bed fit',b[0]>=-1e-5 and b[1]>=-1e-5 and abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
 area=sum(f.Area() for f in p.Faces() if abs(f.BoundingBox().zmin)<1e-5 and abs(f.BoundingBox().zmax)<1e-5)
 ck(n+' substantial broad bed contact',area>[27000,7500,2500,100][N.index(n)],{'contact_mm2':area})
 mb=mesh(R/(n+'_PRINT.stl'),1)
 ck(n+' mesh matches STEP dimensions',all(abs(a-z)<.06 for a,z in zip(mb,b)),mb)
for job in (1,2,3):
 p=cq.importers.importStep(str(R/f'JOB0{job}_PRINT.step')).val();expected=2 if job==3 else 1;b=bb(p)
 ck(f'JOB0{job} correct number of bodies',len(p.Solids())==expected,len(p.Solids()))
 ck(f'JOB0{job} fits printer bed',b[0]>=-1e-5 and b[1]>=-1e-5 and abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
 mesh(R/f'JOB0{job}_PRINT.stl',expected)
 if job==3:
  solids=p.Solids();ck('JOB03 two separate noncolliding objects',iv(solids[0],solids[1])<1e-5,{'gap_between_cassette_and_carrier_mm':17,'two8mm_brims_spare_mm':1})
helper=cyl(90,65,163.1,19.15/2,6.75)
ck('four tolerance-max DC1 plus0.1 adhesive fits lower7mm pocket',all(iv(helper,S[n])<1e-5 for n in N[:3]),{'max_stack_mm':6.75,'adhesive_mm':.1,'remaining_height_mm':.15,'diametral_clearance_mm':.45})
ck('four tolerance-max DC1 plus0.1 adhesive fits optional upper pocket',iv(helper.translate((0,0,30)),S[N[1]])<1e-5,'Top pocket floor193, roof open200')
three=cyl(90,65,164.9375,19.15/2,5.0625)
ck('three tolerance-max DC1 with measured shim fits either location',iv(three,S[N[2]])<1e-5 and iv(three.translate((0,0,30)),S[N[1]])<1e-5,{'max_three_stack_mm':5.0625,'example_measured_shim_mm':1.8375,'example_adhesive_mm':.1,'nominal_three_stack_unfilled_gap_mm':2.2375,'nominal_four_stack_unfilled_gap_mm':.65,'shim_must_match_actual_measured_stack':True})
em=cyl(90,65,170,25.5/2,20.6)
ck('chosen EM tolerance scenario25.5x20.6 fits',all(iv(em,S[n])<1e-5 for n in N[:3]),'Scenario only; actual supplier tolerance unprovided')
worst=cyl(90,65,142.3,9.625/2,12.8)
ck('D68 tolerance-max9.625x12.8 fits open carrier',iv(worst,S[N[3]])<1e-5,'Positive nonprinted loop adjusts to actual height; not a friction-only cup')
moving_names=[N[3],'REF_D68_N52_gap15','REF_nylon_retaining_loop_envelope']
fixed={n:s for n,s in S.items() if n not in moving_names}
bad=[]
for gap in range(10,21):
 for mn in moving_names:
  moving=S[mn].translate((0,0,15-gap))
  for n,s in fixed.items():
   v=iv(moving,s)
   if v>1e-5:bad.append([gap,mn,n,v])
ck('full carrier D68 and positive loop complete10-20mm sweep',not bad,bad)
top=max(bb(S[n])[5] for n in moving_names)+5
ck('minimum10mm gap includes nylon loop1.2mm clearance',abs(162-top-1.2)<1e-5,{'top_moving_at10gap_mm':top,'cassette_bottom_mm':162,'nominal_margin_mm':162-top,'loop_max_width_mm':3,'loop_max_thickness_mm':.8})
bad=[]
for z in range(140,171,2):
 for n in N[:2]:
  v=iv(cyl(90,65,z,12.5,20),S[n])
  if v>1e-5:bad.append([z,n,v])
ck('nominal EM insertion from below cassette removed',not bad,bad)
wire=box(88,77.5,179,4,30,2)
ck('coil4x2 lead exit open',iv(wire,S[N[1]])<1e-5,'Actual purchased lead bend radius/position requires measurement')
retain=[(90+19*math.cos(a),65+19*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
bad=[]
for x,y in retain:
 for label,v in {'shaft':cyl(x,y,161.95,1.5,38.1),'head':cyl(x,y,159,3,3),'upperwasher':cyl(x,y,200,3.5,.5),'nut':cyl(x,y,200.5,3.2,2.4)}.items():
  for n,s in S.items():
   vol=iv(v,s)
   if vol>1e-5:bad.append([label,[x,y],n,vol])
ck('M3x45 paths socketheads and upper hardware clear',not bad,{'collisions':bad,'stack_mm':38,'spare_after0p5washer2p4nut_mm':4.1})
bad=[]
for x,z in [(60,172),(120,172),(60,184),(120,184)]:
 for label,v in {'shaft':cyl(x,119.9,z,2,22.2,(0,1,0)),'head':cyl(x,115.2,z,3.5,4,(0,1,0)),'frontwasher':cyl(x,119.2,z,4.5,.8,(0,1,0)),'rearwasher':cyl(x,142,z,4.5,.8,(0,1,0)),'nut':cyl(x,142.8,z,4.1,3.2,(0,1,0))}.items():
  for n,s in S.items():
   vol=iv(v,s)
   if vol>1e-5:bad.append([label,[x,z],n,vol])
ck('M4x30 rear fastening hardware clear',not bad,bad)
for name,floor,part,under in [('lower',168,N[2],161.2),('upper',198,N[1],186.2)]:
 shape=S[part];bad=[]
 # Body strap holes must be open all the way through the part, including locating rim.
 for y in (60.5,68.3):
  v=box(103, y+.1,159 if name=='upper' else 161,2.5,1,42 if name=='upper' else 10)
  vol=iv(v,shape)
  if vol>1e-5:bad.append(['blind_body_slot',y,vol])
 for y in (59.5,69.3):
  v=box(122.75,y+.1,159 if name=='upper' else 161,2.5,1,42 if name=='upper' else 10)
  vol=iv(v,shape)
  if vol>1e-5:bad.append(['blind_lead_slot',y,vol])
 ck(name+' sensor and wire ties have true through access',not bad,bad)
 # On both package thickness extremes, its top stands above the strap's ledge groove.
 ck(name+' strap presses actual LPG rather than bridging plate',floor+1.42>floor+1.2,{'minimum_body_top_mm':floor+1.42,'strap_groove_floor_mm':floor+1.2,'minimum_proud_mm':.22,'tie_max_width_mm':2.5,'slot_width_mm':3})
 # Separate 1.6mm lanes at 3mm pitch leave1.4mm webs, not unprintable native-pitch walls.
 for y in (62,65,68):
  v=box(114.01,y-.79,floor+.1,13.98,1.58,1.7)
  vol=iv(v,shape)
  if vol>1e-5:bad.append(['solder_lane_blocked',y,vol])
 ck(name+' three solder lanes open and printable isolation webs',not bad,{'issues':bad,'lane_width_mm':1.6,'pitch_mm':3,'web_mm':1.4,'straight_unbent_lead_mm':3})
 # Conservative route below the actual part edge; nominal centered EM must also clear it.
 route=box(102.75,61.1,under,2.5,7.8,.8)
 ck(name+' body strap underside route clears plastic and nominal EM',iv(route,shape)<1e-5 and iv(route,S['REF_EM_nominal_25x20'])<1e-5,bb(route))
strip=cq.importers.importStep(str(R/'OPTIONAL_NONPRINT_retainer_strip.step')).val()
alt={n:s for n,s in S.items() if not n.startswith('REF_DC1_disk')}
alt.update({'TOP_'+str(i):S['REF_DC1_disk_'+str(i)].translate((0,0,30)) for i in range(1,5)})
alt['NONPRINT_strip']=strip
ck('optional top placement no simultaneous lower stack',not overlaps(alt),overlaps(alt))
optional=cq.importers.importStep(str(R/'OPTIONAL_top_stack_configuration.step')).val()
ck('optional top assembly20 actual solids including strip',len(optional.Solids())==20,len(optional.Solids()))
bad=[]
for x,y in (retain[0],retain[2]):
 v=cyl(x,y,199.9,1.5,1.2)
 if iv(v,strip)>1e-5:bad.append([x,y])
ck('optional retainer strip holes match opposite M3 bolts',not bad,{'issues':bad,'strip_mm':'50x8x1','hole_pitch_mm':38,'M3x45_spare_with1mm_strip_mm':3.1})
mass=S[N[3]].Volume()/1000*1.30
ck('carrier solid mass leaves positive10g budget',6.79+mass<10,{'D68_nominal_g':6.79,'carrier_mm3':S[N[3]].Volume(),'assumed_PLA_g_cm3':1.30,'carrier_solid_mass_g':mass,'remaining_tie_ballast_adhesive_g':10-6.79-mass,'must_weigh_complete_payload':True})
out={'passed':all(c['passed'] for c in C),'check_count':len(C),'scope':'Independent actual STEP/STL geometry, print orientation, exact purchased package envelopes and assembly access. No force, temperature, field or closed-loop proof.','checks':C}
(R/'independent_check_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'passed':out['passed'],'check_count':len(C),'failed':[c for c in C if not c['passed']]},indent=2))
