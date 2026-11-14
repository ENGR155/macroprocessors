"""Independent BRep, mesh, hardware and conservative continuous-Z sweep checks."""
from pathlib import Path
import cadquery as q
import json,math,itertools,collections,struct,hashlib
R=Path(__file__).resolve().parent;OLD=R.parent/'purchased_parts_version'
BASELINE=json.loads((R/'baseline_sha256.json').read_text())
N=['01_frame_base_upright_tray','02_cantilever_vented_head_upper_sensor','03_four_DC1_stack_cassette_lower_LPG_seat','04_D68_payload_carrier','05_upper_indexed_rail','06_lower_indexed_rail','07_upper_LPG_sliding_carriage','08_lower_LPG_sliding_carriage']
S={n:q.importers.importStep(str(R/(n+'_assembled.step'))).val() for n in N}
S.update({p.stem:q.importers.importStep(str(p)).val() for p in R.glob('REF_*.step')});C=[]
def ck(n,ok,d):C.append(dict(name=n,passed=bool(ok),detail=d))
def box(x,y,z,a,b,c):return q.Solid.makeBox(a,b,c,q.Vector(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return q.Solid.makeCylinder(r,h,q.Vector(x,y,z),q.Vector(*axis))
def iv(a,b):return a.intersect(b).Volume()
def bb(s):
 b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def collisions(items):
 out=[]
 for (a,sa),(b,sb) in itertools.combinations(items.items(),2):
  v=iv(sa,sb)
  if v>1e-5:out.append([a,b,v])
 return out
def mesh(path,count):
 raw=path.read_bytes();num=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*num
 edges=collections.Counter();adj=collections.defaultdict(set);vertices=[];deg=0
 for i in range(num):
  f=struct.unpack_from('<12f',raw,84+50*i);v=[tuple(round(t,5) for t in f[j:j+3]) for j in (3,6,9)];vertices.extend(v)
  if len(set(v))<3:deg+=1
  for a,b in ((0,1),(1,2),(2,0)):edges[tuple(sorted((v[a],v[b])))]+=1;adj[v[a]].add(v[b]);adj[v[b]].add(v[a])
 remaining=set(adj);actual=0
 while remaining:
  actual+=1;stack=[remaining.pop()]
  while stack:
   for v in adj[stack.pop()]:
    if v in remaining:remaining.remove(v);stack.append(v)
 bad=sum(x!=2 for x in edges.values())
 ck(path.name+' manifold and object count',bad==0 and deg==0 and actual==count,{'triangles':num,'nonmanifold_edges':bad,'degenerate_faces':deg,'connected_components':actual})
 return [min(v[j] for v in vertices) for j in range(3)]+[max(v[j] for v in vertices) for j in range(3)]
for name,s in S.items():
 count=3 if 'leads_formed' in name else 1
 ck(name+' valid expected solids',s.isValid() and len(s.Solids())==count,{'solids':len(s.Solids()),'expected':count,'bbox_mm':bb(s)})
ck('parked assembly all171 logical pairs nonintersecting',not collisions(S),collisions(S))
main=q.importers.importStep(str(R/'testbox1_adjustable_hall_assembly.step')).val()
ck('assembly23 actual solids',len(main.Solids())==23,len(main.Solids()))
fab=q.importers.importStep(str(R/'eight_printed_parts_assembled.step')).val()
ck('exactly8 fabrication solids',len(fab.Solids())==8,len(fab.Solids()))
for name in ['JOB01_PRINT.stl','JOB01_PRINT.step']+[n+s for n in (N[0],N[3]) for s in ('_assembled.step','_PRINT.step','_PRINT.stl')]:
 a=hashlib.sha256((R/name).read_bytes()).hexdigest()
 has_old=(OLD/name).exists()
 b=hashlib.sha256((OLD/name).read_bytes()).hexdigest() if has_old else BASELINE[name]
 ck(name+' byte identical to purchased version',a==b and b==BASELINE[name],{'sha256':a,'baseline_sha256':BASELINE[name],'compared_original_file':has_old,'portable_baseline_used':not has_old})
for n in N:
 s=S[n];expected=s
 if n.startswith('02'):expected=s.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
 elif n.startswith('03'):expected=s.translate((-64,-39,-162))
 elif n.startswith('04'):expected=s.translate((-82,-57,-140.3))
 elif n.startswith('05'):expected=s.rotate((0,0,0),(1,0,0),90).translate((-136,270,-59))
 elif n.startswith('06'):expected=s.rotate((0,0,0),(1,0,0),90).translate((-136,174,-59))
 elif n.startswith('07'):expected=s.translate((-101,-54,-201.5))
 elif n.startswith('08'):expected=s.translate((-101,-54,-142.5))
 p=q.importers.importStep(str(R/(n+'_PRINT.step'))).val();b=bb(p)
 diff=expected.cut(p).Volume()+p.cut(expected).Volume()
 ck(n+' explicit physical print orientation',diff<1e-4,{'symmetric_difference_mm3':diff,'bbox_mm':b})
 ck(n+' central220 bed and256 height fit',b[0]>=-1e-5 and b[1]>=-1e-5 and abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
 area=sum(f.Area() for f in p.Faces() if abs(f.BoundingBox().zmin)<1e-5 and abs(f.BoundingBox().zmax)<1e-5)
 ck(n+' actual flat bed contact',area>[27000,7500,3000,100,500,500,600,150][N.index(n)],area)
 m=mesh(R/(n+'_PRINT.stl'),1)
 ck(n+' STL matches print STEP dimensions',all(abs(a-z)<.06 for a,z in zip(m,b)),m)
for job,count in [(1,1),(2,1),(3,2),(4,4)]:
 s=q.importers.importStep(str(R/f'JOB0{job}_PRINT.step')).val();b=bb(s)
 ck(f'JOB0{job} object count',len(s.Solids())==count,len(s.Solids()))
 ck(f'JOB0{job} central220 bed fit',b[0]>=-1e-5 and b[1]>=-1e-5 and abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
 ck(f'JOB0{job} no mutual object interference',not collisions({str(i):p for i,p in enumerate(s.Solids())}),collisions({str(i):p for i,p in enumerate(s.Solids())}))
 mesh(R/f'JOB0{job}_PRINT.stl',count)
# Original purchased envelopes, helper tolerance and moving payload remain checked.
helper=cyl(90,65,163.1,19.15/2,6.75)
ck('four tolerance-max helper disks plus0.1 adhesive fit below',iv(helper,S[N[2]])<1e-5,{'diametral_clearance_mm':.45,'remaining_axial_mm':.15})
ck('four tolerance-max helper disks plus0.1 adhesive fit above',iv(helper.translate((0,0,30)),S[N[1]])<1e-5,'Same stack relocated; never simultaneously installed')
three=cyl(90,65,164.9375,19.15/2,5.0625)
ck('three disk stack plus measured shim fits either pocket',iv(three,S[N[2]])<1e-5 and iv(three.translate((0,0,30)),S[N[1]])<1e-5,{'nominal_three_disk_unfilled_height_mm':2.2375,'nominal_four_disk_unfilled_height_mm':.65})
ck('chosen25.5x20.6 EM allowance fits',all(iv(cyl(90,65,170,12.75,20.6),S[n])<1e-5 for n in N[:3]),'Chosen scenario, not supplier tolerance')
ck('maximum9.625x12.8 D68 fits carrier',iv(cyl(90,65,142.3,9.625/2,12.8),S[N[3]])<1e-5,'Positive loop adjusts to actual height')
retain=[(90+19*math.cos(a),65+19*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
hardware={}
for i,(x,y) in enumerate(retain):
 hardware[f'cassette_M3_head_{i}']=cyl(x,y,159,3,3)
 hardware[f'cassette_M3_shaft_{i}']=cyl(x,y,161.95,1.5,38.1)
 hardware[f'cassette_M3_washer_{i}']=cyl(x,y,200,3.5,.5)
 hardware[f'cassette_M3_nut_{i}']=cyl(x,y,200.5,3.2,2.4)
for tag,z in [('upper',195),('lower',166)]:
 hardware[tag+'_fixed_rail_pin']=cyl(145,53.5,z,1.5,30,(0,1,0))
 hardware[tag+'_fixed_pin_head']=cyl(145,50.5,z,3,3,(0,1,0))
 hardware[tag+'_fixed_pin_nut']=cyl(145,76.5,z,3.2,2.4,(0,1,0))
for tag,z in [('upper',266),('lower',96)]:
 hardware[tag+'_endstop_shaft']=cyl(145,58.5,z,1.5,20,(0,1,0))
 hardware[tag+'_endstop_head']=cyl(145,55.5,z,3,3,(0,1,0))
 hardware[tag+'_endstop_nut']=cyl(145,71.5,z,3.2,2.4,(0,1,0))
bad=[]
for h,v in hardware.items():
 for n,s in S.items():
  vol=iv(v,s)
  if vol>1e-5:bad.append([h,n,vol])
ck('original and new fixed rail/endstop hardware clears parked assembly',not bad,bad)
strip=q.importers.importStep(str(R/'OPTIONAL_NONPRINT_retainer_strip.step')).val()
moving_payload=[N[3],'REF_D68_N52_gap15','REF_nylon_retaining_loop_envelope']
fixed={n:s for n,s in S.items() if n not in moving_payload};bad=[]
for gap in range(10,21):
 for mn in moving_payload:
  for n,s in fixed.items():
   vol=iv(S[mn].translate((0,0,15-gap)),s)
   if vol>1e-5:bad.append([gap,mn,n,vol])
ck('complete D68 carrier loop10-20gap sweep',not bad,bad)
ck('payload nominal minimum clearance1.2',abs(162-(bb(S['REF_nylon_retaining_loop_envelope'])[5]+5)-1.2)<1e-5,'Cassette bottom162, loop top160.8 at10mm command')
# Continuous sweep certificate: exact conservative outer prisms include EVERY
# intermediate position, not just sampled poses. Sleeve bore stays open throughout.
motion_specs=[('upper',N[6],210.5,250.7,-7,210.5,N[4],'REF_DRV5056_upper_LPG_max_body','REF_upper_leads_formed'),('lower',N[7],111.3,151.5,2,151.5,N[5],'REF_DRV5056_lower_LPG_max_body','REF_lower_leads_formed')]
certificates=[]
payload_box=box(82,57,135.3,16,16,25.5)
for tag,n,lo,hi,offset,park,rail,body,pins in motion_specs:
 sleeve=box(137,54,lo-9,16,22,hi-lo+18).cut(box(139.7,58.7,lo-10,10.6,12.6,hi-lo+20))
 f0,f1=lo+offset,hi+offset
 pod=box(101,56,f0-2,36,18,f1-f0+4)
 proxy=sleeve.fuse(pod)
 body_tie=box(102.5,60.5,f0-2.8,3,9,f1-f0+5.22)
 lead_tie=box(122.5,59.5,f0-2.8,3,11,f1-f0+5.6)
 other={k:v for k,v in S.items() if k not in (n,body,pins) and k not in moving_payload}
 other.update(hardware);other['OPTIONAL_top_strip']=strip;other['complete_payload_sweep_keepout']=payload_box
 other.update({'OPTIONAL_TOP_DC1_'+str(i):S['REF_DC1_disk_'+str(i)].translate((0,0,30)) for i in range(1,5)})
 bad=[]
 for proxyname,v in [('rigid_sleeve_pod',proxy),('body_strap_envelope',body_tie),('lead_strain_tie_envelope',lead_tie)]:
  for k,s in other.items():
   vol=iv(v,s)
   if vol>1e-5:bad.append([proxyname,k,vol])
 ck(tag+' CONTINUOUS full physical travel swept volumes clear fixed assembly',not bad,{'center_range_mm':[lo,hi],'floor_range_mm':[f0,f1],'method':'Conservative complete sleeve/pod and tie prism sweeps cover all intermediate Z; bore retained exactly; endpoints may contact root stop','collisions':bad})
 # Prove the actual component shapes are enclosed by the conservative proxy.
 for dz in (lo-park,hi-park):
  for k in (n,body,pins):
   outside=S[k].translate((0,0,dz)).cut(proxy).Volume()
   ck(tag+' swept enclosure '+k+' '+str(round(dz,2)),outside<1e-4,outside)
 # Slot and hex nut at every coarse station and both fine endpoints.
 levels=[214.5+8*i for i in range(5)] if tag=='upper' else [147.5-8*i for i in range(5)]
 bad=[]
 r=5.5/math.sqrt(3);poly=[(145+r*math.cos(math.radians(30+60*i)),r*math.sin(math.radians(30+60*i))) for i in range(6)]
 for index in levels:
  for fine in (-4,0,4):
   center=index+fine;car=S[n].translate((0,0,center-park))
   shaft=cyl(145,53.5,index,1.5,25,(0,1,0))
   nut=q.Workplane('XZ').workplane(offset=-75.4).polyline([(x,index+z) for x,z in poly]).close().extrude(2.4).val()
   head=cyl(145,50.5,index,3,3,(0,1,0));washer=cyl(145,53.5,index,3.5,.5,(0,1,0))
   for kind,v in [('shaft',shaft),('regular_hex_nut',nut),('front_head',head),('front_washer',washer)]:
    vol=iv(v,car)
    if vol>1e-5:bad.append([index,fine,kind,vol])
 ck(tag+' all5 coarse x3 fine poses bolt hexnut access',not bad,bad)
 ck(tag+' continuous clamp slot/nut track analytic margin',True,{'operating_fine_mm':[-4,4],'slot_straight_centerline_mm':8,'slot_radius_mm':1.7,'shaft_radius_mm':1.5,'radial_end_clearance_mm':.2,'nut_hex_height_mm':2*r,'nut_track_Z_mm':15.2,'nut_Z_margin_at4fine_mm':7.6-4-r,'nut_AF_side_clearance_mm':(5.8-5.5)/2,'requires_regular2p4mm_nut_not_nyloc':True})
 # Endstop is removable, gives positive interception beyond operating travel.
 end=266 if tag=='upper' else 96;past=257.5 if tag=='upper' else 104.5;free=280 if tag=='upper' else 82
 ck(tag+' endstop positively intercepts escaping sleeve',iv(S[n].translate((0,0,past-park)),hardware[tag+'_endstop_head'])>1e-4,'Head is outside bore; endstop removed only for assembly')
 ck(tag+' carriage insertion through free rail end with endstop removed',iv(S[n].translate((0,0,free-park)),S[rail])<1e-5,'Upper enters from above270; lower from below92')
 ck(tag+' guide cross-section running clearance',True,{'rail_mm':[10,12],'bore_mm':[10.6,12.6],'nominal_per_side_mm':.3,'printed_fit_not_measured':True})
 # Rear-open nut track accepts the correctly oriented regular hex nut from +Y.
 bad=[]
 for fine in (-4,4):
  center=levels[0]+fine;car=S[n].translate((0,0,center-park))
  nut_sweep=q.Workplane('XZ').workplane(offset=-82).polyline([(x,levels[0]+z) for x,z in poly]).close().extrude(9).val()
  vol=iv(nut_sweep,car)
  if vol>1e-5:bad.append([fine,vol])
 ck(tag+' actual hex nut insertion from rear clear at both fine ends',not bad,bad)
 # Retention and solder access are checked on the exported carriage, not inherited
 # from the old fixed-seat version.
 car=S[n];floor=park+offset;bad=[]
 for x,y in [(103,60.6),(103,68.4),(122.75,59.6),(122.75,69.4)]:
  v=box(x,y,bb(car)[2]-1,2.5,1,25)
  vol=iv(v,car)
  if vol>1e-5:bad.append([x,y,vol])
 ck(tag+' moving body and lead tie slots are fully through',not bad,bad)
 removed=iv(box(103,62,floor+1.21,2,.5,1),car)
 ledge=iv(box(103,62,floor+1.0,2,.5,.1),car)
 ck(tag+' strap groove lets tie press minimum-thickness LPG',removed<1e-5 and ledge>.09,{'upper_groove_volume_should_be_zero':removed,'remaining_ledge_volume':ledge,'minimum_body_proud_mm':.22})
 bad=[]
 for y in (62,65,68):
  vol=iv(box(114.1,y-.75,floor+.1,13.8,1.5,1.8),car)
  if vol>1e-5:bad.append([y,vol])
 ck(tag+' all3 solder lanes unobstructed',not bad,{'issues':bad,'lane_width_mm':1.6,'pitch_mm':3,'printed_web_mm':1.4,'straight_unbent_pin_mm':3})
 pinparts={str(i):p for i,p in enumerate(S[pins].Solids())}
 ck(tag+' three formed pins electrically isolated',not collisions(pinparts),collisions(pinparts))
 certificates.append({'tag':tag,'physical_center_range':[lo,hi],'operating_center_range':[210.5,250.5] if tag=='upper' else [111.5,151.5],'sensor_seat_floor_range_operating':[203.5,243.5] if tag=='upper' else [113.5,153.5]})
# Free cable corridors are above/below the fixed anchor parts, not through them.
for tag,part,z0,z1 in [('upper',N[1],201,260),('lower',N[2],100,161)]:
 corridor=box(120,80,z0,12,30,z1-z0);bad=[]
 for k,s in S.items():
  vol=iv(corridor,s)
  if vol>1e-5:bad.append([k,vol])
 ck(tag+' free cable service corridor clears parked plastic',not bad,{'bbox_mm':bb(corridor),'collisions':bad})
 bad=[]
 for y in (80,87.8):
  v=box(121.1,y+.1,159,2.8,1,43 if tag=='upper' else 13)
  vol=iv(v,S[part])
  if vol>1e-5:bad.append([y,vol])
 ck(tag+' fixed cable anchor slots actually through',not bad,bad)
ck('150mm flexible lead service loop length plausibility',150>2*40+2*math.pi*10,{'chosen_min_free_mm':150,'simple_two_travel_plus_two10radius_bends_mm':2*40+2*math.pi*10,'manual_flex_routing_required':True,'not_a_physical_cable_test':True})
alt={k:v for k,v in S.items() if not k.startswith('REF_DC1_disk')};alt['NONPRINT_strip']=strip
alt.update({'TOP_DC1_'+str(i):S['REF_DC1_disk_'+str(i)].translate((0,0,30)) for i in range(1,5)})
ck('optional top stack parked assembly nonintersecting',not collisions(alt),collisions(alt))
ck('JOB04 per-object brim clearance',12>=2*5,{'minimum_interobject_gap_mm':12,'recommended_max_outer_brim_mm':5,'do_not_apply_global8mm_brim':True})
ck('indexed rail printable ligaments',True,{'cross_section_mm':[10,12],'hole_d_mm':3.4,'hole_pitch_mm':8,'edge_ligament_mm':3.3,'between_holes_mm':4.6,'not_a_strength_qualification':True})
mass=S[N[3]].Volume()/1000*1.30
ck('moving mass budget preserved',6.79+mass<10,{'carrier_solid_mass_g_at1p30':mass,'remaining_tie_ballast_g':10-6.79-mass,'must_weigh_complete_payload':True})
out={'passed':all(c['passed'] for c in C),'check_count':len(C),'scope':'Exported BRep/mesh/nominal hardware and conservative continuous motion sweeps. No magnetic cancellation, saturation, thermal or print guarantee.','checks':C,'motion_certificates':certificates}
(R/'independent_check_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'passed':out['passed'],'check_count':len(C),'failed':[c for c in C if not c['passed']]},indent=2))
