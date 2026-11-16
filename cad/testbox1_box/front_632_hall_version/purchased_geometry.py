"""Purchased-parts assembly: four print bodies in three jobs. All dimensions mm."""
from pathlib import Path
import json,math
import cadquery as cq
ROOT=Path(__file__).resolve().parent
P={'base_w':180.,'base_d':160.,'base_t':8.,'upright_w':90.,'upright_t':12.,'upright_y':130.,'upright_top':190.,'arm_front':39.,'arm_t':10.,'axis_x':90.,'axis_y':65.,'em_face_z':170.,'em_d':25.,'em_h':20.,'em_bore':26.,'helper_d':19.05,'helper_h':1.5875,'helper_count':4,'helper_pocket_d':19.6,'helper_pocket_depth':7.,'helper_floor_z':163.,'retainer_bolt_radius':19.,'payload_D68_d':9.525,'payload_D68_h':12.7,'payload_D68_mass_g':6.79,'gap_min':10.,'gap_max':20.}
parts={};meta={};refs={};optional={}
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Workplane(obj=cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis)))
def hole(s,x,y,z,d,h,axis=(0,0,1)):return s.cut(cyl(x,y,z,d/2,h,axis))
def triangle_yz(x,dx,pts):return cq.Workplane('YZ').workplane(offset=x).polyline(pts).close().extrude(dx)
def add(n,s,notes):
    s=s.clean();assert s.val().isValid() and len(s.val().Solids())==1,n
    parts[n]=s;meta[n]={'notes':notes}

def hall_seat(s,cx,cy,floor,top):
    """LPG flat body, 3mm straight shoulder bay, fanout and separate solder lanes.
    Package body max3.25 alongX x4.1 alongY x1.62 alongZ. Face can flip.
    """
    s=s.cut(box(cx-1.85,cy-2.25,floor,3.7,4.5,top-floor+1))
    # Open lead shoulder/bend bay. No unprintable webs at native1.27mm pitch.
    s=s.cut(box(cx+1.85,cy-5,floor,8.15,10,top-floor+1))
    for dy in (-3,0,3):s=s.cut(box(cx+10,cy+dy-.8,floor,128-(cx+10),1.6,top-floor+1))
    # Nylon body strap, and separate downstream lead-bundle strain relief.
    s=s.cut(box(cx-1.35,cy-4.5,top-.8,2.7,9,2))
    bottom=s.val().BoundingBox().zmin-1
    for x,y in [(cx-1.5,cy-4.5),(cx-1.5,cy+3.3),(122.5,cy-5.5),(122.5,cy+4.3)]:
        s=s.cut(box(x,y,bottom,3,1.2,top-bottom+1))
    return s

def hall_ref(cx,cy,z,flip=False):
    # Conservative maximum body envelope (not a cosmetic nominal transistor).
    return box(cx-1.625,cy-2.05,z,3.25,4.1,1.62)

def leads_ref(cx,cy,z):
    # Native lead section3mm straight before fan-out. Three unjoined copper solids.
    shapes=[]
    for native,target in zip((-1.27,0,1.27),(-3,0,3)):
        straight=box(cx+1.625,cy+native-.275,z+.505,3,.55,.51)
        a=cq.Vector(cx+4.625,cy+native,z+.76);b=cq.Vector(cx+10,cy+target,z+.76);v=b-a
        formed=cq.Workplane(obj=cq.Solid.makeCylinder(.275,v.Length+.02,a-v.normalized()*.01,v.normalized()))
        end=box(cx+9.99,cy+target-.275,z+.505,5.01,.55,.51)
        pin=straight.union(formed).union(end).clean()
        assert len(pin.val().Solids())==1
        shapes.append(pin)
    return cq.Workplane(obj=cq.Compound.makeCompound([v.val() for v in shapes]))
def build():
    W,D,T=P['base_w'],P['base_d'],P['base_t']; rear=P['upright_y'];back=rear+P['upright_t'];top=P['upright_top'];cx,cy=P['axis_x'],P['axis_y'];face=P['em_face_z'];emtop=face+P['em_h'];armtop=emtop+P['arm_t']
    bolt_rear=[(60,172),(120,172),(60,184),(120,184)]
    retain=[(cx+P['retainer_bolt_radius']*math.cos(a),cy+P['retainer_bolt_radius']*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
    base=box(0,0,0,W,D,T).union(box(45,rear,T,P['upright_w'],P['upright_t'],top-T))
    for x in (45,127):
        base=base.union(triangle_yz(x,8,[(95,T),(rear,T),(rear,110)]))
        base=base.union(triangle_yz(x,8,[(back,T),(158,T),(back,60)]))
    # Catch tray is fused into the base; no additional printed component.
    tray=box(55,30,T,70,70,6).cut(box(58,33,T+1.5,64,64,7))
    base=base.union(tray)
    for x,z in bolt_rear:base=hole(base,x,rear-1,z,4.5,P['upright_t']+2,(0,1,0))
    for z in (75,125,150):
        for x in (49,127):base=base.cut(box(x,rear-1,z,4,P['upright_t']+2,2))
    add('01_frame_base_upright_tray',base,'Print base underside flat on bed; 180x160x190. Integrated 12mm upright and front/rear root gussets. Four M4 through holes at X60/120,Z172/184.')
    arm=box(45,P['arm_front'],emtop,90,back-P['arm_front'],P['arm_t'])
    arm=arm.union(box(45,120,160,90,10,30))
    for x in (45,127):arm=arm.union(triangle_yz(x,8,[(100,emtop),(120,emtop),(120,175)]))
    # Open coil cage: upper locating rim and four bolt columns. Cassette provides
    # positive support underneath, so no unsupported lower ring needs printing.
    cage=cyl(cx,cy,emtop-3,23,3)
    for x,y in retain:cage=cage.union(cyl(x,y,face,4,P['em_h']))
    cage=hole(cage,cx,cy,face-1,P['em_bore'],P['em_h']+2)
    arm=arm.union(cage)
    # Allow height variation instead of hard-clamping a nominal20mm coil at zero
    # axial clearance. Fit a measured nonmagnetic retaining shim after inspection.
    arm=hole(arm,cx,cy,emtop-.1,P['em_bore'],.9)
    for x,z in bolt_rear:arm=hole(arm,x,119,z,4.5,12,(0,1,0))
    for x,y in retain:arm=hole(arm,x,y,face-1,3.4,armtop-face+2)
    # Exact LPG seat, marked face parallel toXY. Upper floor permits body1.62 high.
    arm=hall_seat(arm,104,65,198,armtop)
    # Optional alternative DC1 location. Only one four-disk stack is installed.
    # Inverted printing needs removable manual support within this7mm-deep pocket.
    arm=hole(arm,90,65,193,19.6,8)
    # External tie/lead slots, outside the EM and retaining column envelopes.
    for x in (57,119):arm=arm.cut(box(x,95,emtop-1,4,8,P['arm_t']+2))
    add('02_cantilever_vented_head_upper_sensor',arm,'Print inverted Z200 face on bed. Exact DRV5056QLPG body seat3.7x4.5, 3mm straight-lead relief and free fanout to3mm-pitch solder channels. Body strap plus lead strain-relief slots. Ø26 coil upper rim,0.8mm axial clearance.')
    cassette=box(64,39,162,65,52,8)
    cassette=hole(cassette,cx,cy,P['helper_floor_z'],P['helper_pocket_d'],P['helper_pocket_depth']+1)
    for x,y in retain:cassette=hole(cassette,x,y,161,3.4,11)
    cassette=hall_seat(cassette,104,65,168,170)
    add('03_four_DC1_stack_cassette_lower_LPG_seat',cassette,'Print broad underside flat. Ø19.6x7 pocket for3–4DC1 disks, floorZ163,bottomZ162. LowerDRV5056QLPG flat seat atX104Y65Z168 is14mm offaxis beside stack. Strap retained body and separate strain-relief/solder lanes extend+X. M3x45 head bolts required for38mmstack.')
    # D68 cup has bottom support and an explicit NONPRINTED loop over magnet and
    # under base for positive upward retention; no friction-only mounting claim.
    carrier=cyl(cx,cy,140.3,8,2).union(cyl(cx,cy,142.3,6.8,12.3))
    carrier=hole(carrier,cx,cy,142.3,10,14)
    carrier=carrier.cut(box(cx-8,cy-1.5,140.2,16,3,.9))
    # Two shallow vertical outer guides keep the loop's strap in one plane.
    for x in (cx-6.8,cx+6.1):carrier=carrier.cut(box(x,cy-1.5,142.3,.7,3,12.4))
    for x in (cx-8,cx+6.1):carrier=carrier.cut(box(x,cy-1.5,140.2,1.9,3,2.2))
    add('04_D68_payload_carrier',carrier,'Print broad base down beside cassette in JOB03. Ø10 cup forD68 Ø9.525x12.7; magnettop0.4mmabove cup. Nonprintednylonloop≤3mmwide≤0.8mmthick goesOVERmagnettop andUNDERbasegroove; buckle belowcup. Add measured nonmagnetic ballast until WHOLE moving assembly10g. Never rely on friction alone.')
    refs['REF_EM_nominal_25x20']=cyl(cx,cy,face,P['em_d']/2,P['em_h'])
    for i in range(4):refs['REF_DC1_disk_'+str(i+1)]=cyl(cx,cy,P['helper_floor_z']+i*P['helper_h'],P['helper_d']/2,P['helper_h'])
    refs['REF_D68_N52_gap15']=cyl(cx,cy,142.3,P['payload_D68_d']/2,P['payload_D68_h'])
    refs['REF_DRV5056_lower_LPG_max_body']=hall_ref(104,65,168)
    refs['REF_DRV5056_upper_LPG_max_body']=hall_ref(104,65,198)
    refs['REF_lower_leads_formed']=leads_ref(104,65,168)
    refs['REF_upper_leads_formed']=leads_ref(104,65,198)
    # Rectangular conservative nonprinted nylon loop; buckle is specified belowcup.
    tie=box(cx-4.5,cy-1.5,155,9,3,.8).union(box(cx-6.9,cy-1.5,140.3,.8,3,14.7)).union(box(cx+6.1,cy-1.5,140.3,.8,3,14.7)).union(box(cx-6.9,cy-1.5,140.3,13.8,3,.8))
    left=[(83.1,154.6),(83.9,154.6),(85.1,155),(86,155),(86,155.8),(85.2,155.8)]
    right=[(180-x,z) for x,z in left]
    for pts in (left,right):tie=tie.union(cq.Workplane('XZ').workplane(offset=-66.5).polyline(pts).close().extrude(3))
    assert len(tie.val().Solids())==1
    refs['REF_nylon_retaining_loop_envelope']=tie
    strip=box(65,61,200,50,8,1)
    for x in (71,109):strip=hole(strip,x,65,199,3.4,3)
    strip=strip.rotate((90,65,0),(90,65,1),45)
    optional['NONPRINT_top_stack_retainer_strip']=strip
    for i in range(4):optional['REF_TOP_DC1_disk_'+str(i+1)]=cyl(cx,cy,193+i*P['helper_h'],P['helper_d']/2,P['helper_h'])
    return retain,bolt_rear
def bounds(s):
    b=s.val().BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def bed_transform(name,s):
    if name.startswith('01'):return s
    if name.startswith('02'):return s.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
    if name.startswith('03'):return s.translate((-64,-39,-162))
    return s.translate((-82,-57,-140.3))
def export():
    from conform_stl import repair
    conformity=[]
    retain,rear=build();assembly=cq.Assembly(name='testbox1_purchased_parts');fabrication=cq.Assembly(name='four_printed_bodies_three_jobs')
    colors=[cq.Color(.28,.43,.52),cq.Color(.39,.60,.67),cq.Color(.80,.55,.25),cq.Color(.73,.40,.20)]
    for (name,s),color in zip(parts.items(),colors):
        bed=bed_transform(name,s);shape=s.val();printshape=bed.val()
        b=bounds(bed);assert abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,name
        cq.exporters.export(s,str(ROOT/(name+'_assembled.step')))
        cq.exporters.export(bed,str(ROOT/(name+'_PRINT.stl')),tolerance=.05,angularTolerance=.12)
        conformity.append(repair(ROOT/(name+'_PRINT.stl')))
        cq.exporters.export(bed,str(ROOT/(name+'_PRINT.step')))
        meta[name].update({'kind':'print','job':1 if name.startswith('01') else 2 if name.startswith('02') else 3,'material_selected':'PLA','thermal_validation':'NOT ESTABLISHED','assembly_bbox_mm':bounds(s),'print_bbox_mm':b,'volume_mm3':shape.Volume(),'solid_count':len(shape.Solids()),'valid':shape.isValid(),'print_valid':printshape.isValid(),'rotation_about_X_deg':180 if name.startswith('02') else 0})
        assembly.add(s,name=name,color=color);fabrication.add(s,name=name,color=color)
    fabrication.export(str(ROOT/'four_printed_parts_assembled.step'))
    for name,s in refs.items():
        color=cq.Color(.88,.67,.24) if 'payload' in name else cq.Color(.20,.65,.35) if 'Hall' in name else cq.Color(.65,.66,.68)
        assembly.add(s,name=name,color=color)
    assembly.export(str(ROOT/'testbox1_purchased_parts_assembly.step'))
    alt=cq.Assembly(name='OPTIONAL_top_stack_configuration')
    for n,s in parts.items():alt.add(s,name=n)
    for n,s in refs.items():
        if not n.startswith('REF_DC1_disk'):alt.add(s,name=n)
    for n,s in optional.items():alt.add(s,name=n)
    alt.export(str(ROOT/'OPTIONAL_top_stack_configuration.step'))
    cq.exporters.export(optional['NONPRINT_top_stack_retainer_strip'],str(ROOT/'OPTIONAL_NONPRINT_retainer_strip.step'))
    jobs={1:[bed_transform(n,s) for n,s in parts.items() if n.startswith('01')],2:[bed_transform(n,s) for n,s in parts.items() if n.startswith('02')],3:[bed_transform(n,s) for n,s in parts.items() if n.startswith('03')]+[bed_transform(n,s).translate((82,0,0)) for n,s in parts.items() if n.startswith('04')]}
    for job,shapes in jobs.items():
        compound=cq.Compound.makeCompound([s.val() for s in shapes]);target=ROOT/f'JOB0{job}_PRINT.stl'
        cq.exporters.export(compound,str(target),tolerance=.05,angularTolerance=.12);conformity.append(repair(target))
        cq.exporters.export(compound,str(ROOT/f'JOB0{job}_PRINT.step'))
    (ROOT/'component_manifest.json').write_text(json.dumps(meta,indent=2))
    (ROOT/'mesh_conformity.json').write_text(json.dumps(conformity,indent=2))
    (ROOT/'dimensions.json').write_text(json.dumps({'driving_parameters':P,'retainer_bolt_xy':retain,'rear_bolt_xz':rear,'note':'P values drive named dimensions; supporting coordinate details remain explicit in generator.'},indent=2))
    for name,s in refs.items():cq.exporters.export(s,str(ROOT/(name+'.step')))
    comp=cq.Compound.makeCompound([s.val() for s in [*parts.values(),*refs.values()]])
    cq.exporters.export(comp,str(ROOT/'cad_isometric.svg'),opt={'width':1100,'height':900,'projectionDir':(1,-1,.75),'showHidden':False,'strokeWidth':.7,'strokeColor':(25,45,60),'showAxes':False})
    mass=parts['04_D68_payload_carrier'].val().Volume()/1000*1.30
    (ROOT/'payload_mass_budget.json').write_text(json.dumps({'D68_supplier_mass_g':6.79,'printed_carrier_volume_mm3':parts['04_D68_payload_carrier'].val().Volume(),'PLA_density_ASSUMED_g_cm3':1.30,'carrier_solid_mass_at_assumed_density_g':mass,'remaining_tie_ballast_adhesive_g':10-6.79-mass,'must_weigh_complete_payload':True},indent=2))
    print(json.dumps({'printed_bodies':len(parts),'print_jobs':3,'assembly_reference_entries':len(refs),'valid':all(m['valid'] for m in meta.values()),'output':str(ROOT)},indent=2))
if __name__=='__main__':export()
