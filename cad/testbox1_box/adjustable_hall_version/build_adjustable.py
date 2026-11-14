"""Vertical adjustable Hall assembly: eight print bodies, four jobs. Units mm."""
from pathlib import Path
import json,math,shutil
import cadquery as cq
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'purchased_parts_version'
P={'base_w':180.,'base_d':160.,'base_t':8.,'upright_w':90.,'upright_t':12.,'upright_y':130.,'upright_top':190.,'arm_front':39.,'arm_t':10.,'axis_x':90.,'axis_y':65.,'em_face_z':170.,'em_d':25.,'em_h':20.,'em_bore':26.,'helper_d':19.05,'helper_h':1.5875,'helper_count':4,'helper_pocket_d':19.6,'helper_pocket_depth':7.,'helper_floor_z':163.,'retainer_bolt_radius':19.,'payload_D68_d':9.525,'payload_D68_h':12.7,'payload_D68_mass_g':6.79,'gap_min':10.,'gap_max':20.}
parts={};meta={};refs={};optional={}
MOTION={'rail_x':145.,'rail_y':65.,'upper_body_floor_range_mm':[203.5,243.5],'lower_body_floor_range_mm':[113.5,153.5],'upper_carriage_center_range_mm':[210.5,250.5],'lower_carriage_center_range_mm':[111.5,151.5],'upper_index_Z_mm':[214.5,222.5,230.5,238.5,246.5],'lower_index_Z_mm':[147.5,139.5,131.5,123.5,115.5],'coarse_pitch_mm':8.,'fine_operating_half_travel_mm':4.,'slot_overall_mm':11.4,'slot_width_mm':3.4,'rail_cross_section_mm':[10,12],'guide_bore_mm':[10.6,12.6],'clamp_nut_regular_M3_mm':{'across_flats':5.5,'thickness':2.4},'parked_upper_center_Z_mm':210.5,'parked_lower_center_Z_mm':151.5}

def preserve_file(name):
    """Keep approved bytes; a standalone extracted delivery already contains them."""
    source=OLD/name;target=ROOT/name
    if source.is_file():shutil.copy2(source,target)
    elif not target.is_file():raise FileNotFoundError(f'Preserved input missing: {name}')
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

def vertical_guide(s,lo,hi):
    # Reinforced ear remains within the original Z band, preserving flat-bed print.
    s=s.union(box(125,54,lo,29,22,hi-lo))
    s=s.cut(box(139.7,58.7,lo-1,10.6,12.6,hi-lo+2))
    return hole(s,145,53,(lo+hi)/2,3.4,24,(0,1,0))

def indexed_rail(upper):
    low,high=(188,270) if upper else (92,174)
    s=box(140,59,low,10,12,high-low)
    # Rear-only widened shoulder shares Y59 plane for support-free side printing.
    shoulder=(200,201.5) if upper else (160.5,162)
    s=s.union(box(136,59,shoulder[0],18,18,shoulder[1]-shoulder[0]))
    levels=MOTION['upper_index_Z_mm'] if upper else MOTION['lower_index_Z_mm']
    for z in levels+[195 if upper else 166,266 if upper else 96]:s=hole(s,145,58,z,3.4,20,(0,1,0))
    return s

def sensor_carriage(center_z,body_offset):
    s=box(137,54,center_z-9,16,22,18)
    s=s.cut(box(139.7,58.7,center_z-10,10.6,12.6,20))
    floor=center_z+body_offset
    s=s.union(box(101,56,floor-2,36,18,4))
    s=hall_seat(s,104,65,floor,floor+2)
    slot=cq.Workplane('XZ').workplane(offset=-77).center(145,center_z).slot2D(11.4,3.4,90).extrude(24)
    s=s.cut(slot)
    # Nut flats are captured laterally; the nut can translate with fixed bolt
    # inside the rear open track while carriage makes its +/-4mm fine motion.
    s=s.cut(box(142.1,73,center_z-7.6,5.8,4,15.2))
    return s
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
    arm=vertical_guide(arm,190,200)
    for y in (80,87.8):arm=arm.cut(box(121,y,189,3,1.2,12))
    # Optional alternative DC1 location. Only one four-disk stack is installed.
    # Inverted printing needs removable manual support within this7mm-deep pocket.
    arm=hole(arm,90,65,193,19.6,8)
    # External tie/lead slots, outside the EM and retaining column envelopes.
    for x in (57,119):arm=arm.cut(box(x,95,emtop-1,4,8,P['arm_t']+2))
    add('02_cantilever_vented_head_upper_sensor',arm,'Updated JOB02: inverted Z200 face down, outboard keyed vertical rail guide. Original coil25x20,upperDC1pocket,backM4joint preserved. Fixed rail mountM3x30 atZ195.')
    cassette=box(64,39,162,65,52,8)
    cassette=hole(cassette,cx,cy,P['helper_floor_z'],P['helper_pocket_d'],P['helper_pocket_depth']+1)
    for x,y in retain:cassette=hole(cassette,x,y,161,3.4,11)
    cassette=vertical_guide(cassette,162,170)
    for y in (80,87.8):cassette=cassette.cut(box(121,y,161,3,1.2,10))
    add('03_four_DC1_stack_cassette_lower_LPG_seat',cassette,'Updated JOB03: broad underside flat,originalfourDC1pocket andM3x45interface, outboard keyed vertical rail guide. Fixed rail mountM3x30 atZ166.')
    # D68 cup has bottom support and an explicit NONPRINTED loop over magnet and
    # under base for positive upward retention; no friction-only mounting claim.
    carrier=cyl(cx,cy,140.3,8,2).union(cyl(cx,cy,142.3,6.8,12.3))
    carrier=hole(carrier,cx,cy,142.3,10,14)
    carrier=carrier.cut(box(cx-8,cy-1.5,140.2,16,3,.9))
    # Two shallow vertical outer guides keep the loop's strap in one plane.
    for x in (cx-6.8,cx+6.1):carrier=carrier.cut(box(x,cy-1.5,142.3,.7,3,12.4))
    for x in (cx-8,cx+6.1):carrier=carrier.cut(box(x,cy-1.5,140.2,1.9,3,2.2))
    add('04_D68_payload_carrier',carrier,'Print broad base down beside cassette in JOB03. Ø10 cup forD68 Ø9.525x12.7; magnettop0.4mmabove cup. Nonprintednylonloop≤3mmwide≤0.8mmthick goesOVERmagnettop andUNDERbasegroove; buckle belowcup. Add measured nonmagnetic ballast until WHOLE moving assembly10g. Never rely on friction alone.')
    add('05_upper_indexed_rail',indexed_rail(True),'JOB04 flat FRONTY59 on bed. Fixed keyed rail:five8mm-pitchindexholes, mountZ195, removableM3x20 endstopZ266,integralrootshoulderZ200..201.5. InsertcarriagefromfreeendBEFOREinstallingendstopbolt.')
    add('06_lower_indexed_rail',indexed_rail(False),'JOB04 flat FRONTY59 on bed. Fixed keyed rail:five8mm-pitchindexholes,mountZ166,removableM3x20 endstopZ96,integralrootshoulderZ160.5..162.')
    add('07_upper_LPG_sliding_carriage',sensor_carriage(210.5,-7),'JOB04 broadpodfloorandsleevebaseCOPLANARflat. No support under upperpod or sleeve. ExactLPGbodyseat,leadfanoutandstrainrelief;M3x25capturedfinebolt+REGULAR2.4mmnutslidesinreartrack. Upperbodyfloor203.5..243.5,±4finepersetting.')
    add('08_lower_LPG_sliding_carriage',sensor_carriage(151.5,2),'JOB04 sleeveBASEflat,underpodremovableprinted-supportsfrombuildplate. ExactLPGseat;M3x25capturedfinebolt+regularnut. Lowerbodyfloor113.5..153.5,±4finepersetting.')
    refs['REF_EM_nominal_25x20']=cyl(cx,cy,face,P['em_d']/2,P['em_h'])
    for i in range(4):refs['REF_DC1_disk_'+str(i+1)]=cyl(cx,cy,P['helper_floor_z']+i*P['helper_h'],P['helper_d']/2,P['helper_h'])
    refs['REF_D68_N52_gap15']=cyl(cx,cy,142.3,P['payload_D68_d']/2,P['payload_D68_h'])
    refs['REF_DRV5056_lower_LPG_max_body']=hall_ref(104,65,153.5)
    refs['REF_DRV5056_upper_LPG_max_body']=hall_ref(104,65,203.5)
    refs['REF_lower_leads_formed']=leads_ref(104,65,153.5)
    refs['REF_upper_leads_formed']=leads_ref(104,65,203.5)
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
    if name.startswith('04'):return s.translate((-82,-57,-140.3))
    if name.startswith('05'):return s.rotate((0,0,0),(1,0,0),90).translate((-136,270,-59))
    if name.startswith('06'):return s.rotate((0,0,0),(1,0,0),90).translate((-136,174,-59))
    if name.startswith('07'):return s.translate((-101,-54,-201.5))
    return s.translate((-101,-54,-142.5))
def export():
    from conform_stl import repair
    conformity=[]
    retain,rear=build();assembly=cq.Assembly(name='testbox1_adjustable_hall');fabrication=cq.Assembly(name='eight_printed_bodies_four_jobs')
    colors=[cq.Color(.28,.43,.52),cq.Color(.39,.60,.67),cq.Color(.80,.55,.25),cq.Color(.73,.40,.20),cq.Color(.35,.50,.56),cq.Color(.35,.50,.56),cq.Color(.68,.28,.18),cq.Color(.68,.28,.18)]
    for (name,s),color in zip(parts.items(),colors):
        bed=bed_transform(name,s);shape=s.val();printshape=bed.val()
        b=bounds(bed);assert abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,name
        if name.startswith(('01','04')):
            for suffix in ('_assembled.step','_PRINT.stl','_PRINT.step'):preserve_file(name+suffix)
        else:
            cq.exporters.export(s,str(ROOT/(name+'_assembled.step')))
            cq.exporters.export(bed,str(ROOT/(name+'_PRINT.stl')),tolerance=.05,angularTolerance=.12)
            conformity.append(repair(ROOT/(name+'_PRINT.stl')))
            cq.exporters.export(bed,str(ROOT/(name+'_PRINT.step')))
        meta[name].update({'kind':'print','job':int(name[:2]) if int(name[:2])<4 else 3 if name.startswith('04') else 4,'material_selected':'PLA','thermal_validation':'NOT ESTABLISHED','assembly_bbox_mm':bounds(s),'print_bbox_mm':b,'volume_mm3':shape.Volume(),'solid_count':len(shape.Solids()),'valid':shape.isValid(),'print_valid':printshape.isValid()})
        assembly.add(s,name=name,color=color);fabrication.add(s,name=name,color=color)
    fabrication.export(str(ROOT/'eight_printed_parts_assembled.step'))
    for name,s in refs.items():
        color=cq.Color(.88,.67,.24) if 'payload' in name else cq.Color(.20,.65,.35) if 'Hall' in name else cq.Color(.65,.66,.68)
        assembly.add(s,name=name,color=color)
    assembly.export(str(ROOT/'testbox1_adjustable_hall_assembly.step'))
    alt=cq.Assembly(name='OPTIONAL_top_stack_configuration')
    for n,s in parts.items():alt.add(s,name=n)
    for n,s in refs.items():
        if not n.startswith('REF_DC1_disk'):alt.add(s,name=n)
    for n,s in optional.items():alt.add(s,name=n)
    alt.export(str(ROOT/'OPTIONAL_top_stack_configuration.step'))
    cq.exporters.export(optional['NONPRINT_top_stack_retainer_strip'],str(ROOT/'OPTIONAL_NONPRINT_retainer_strip.step'))
    jobs={2:[bed_transform(n,s) for n,s in parts.items() if n.startswith('02')],3:[bed_transform(n,s) for n,s in parts.items() if n.startswith('03')]+[bed_transform(n,s).translate((107,0,0)) for n,s in parts.items() if n.startswith('04')],4:[]}
    placement={'05':(0,0,0),'06':(30,0,0),'07':(65,0,0),'08':(65,40,0)}
    for n,s in parts.items():
        if n[:2] in placement:jobs[4].append(bed_transform(n,s).translate(placement[n[:2]]))
    for suffix in ('.stl','.step'):preserve_file('JOB01_PRINT'+suffix)
    preserve_file('OPTIONAL_retainer_cut_template.svg')
    for job,shapes in jobs.items():
        compound=cq.Compound.makeCompound([s.val() for s in shapes]);target=ROOT/f'JOB0{job}_PRINT.stl'
        cq.exporters.export(compound,str(target),tolerance=.05,angularTolerance=.12);conformity.append(repair(target))
        cq.exporters.export(compound,str(ROOT/f'JOB0{job}_PRINT.step'))
    (ROOT/'component_manifest.json').write_text(json.dumps(meta,indent=2))
    (ROOT/'mesh_conformity.json').write_text(json.dumps(conformity,indent=2))
    (ROOT/'dimensions.json').write_text(json.dumps({'driving_parameters':P,'retainer_bolt_xy':retain,'rear_bolt_xz':rear,'note':'P values drive named dimensions; supporting coordinate details remain explicit in generator.'},indent=2))
    (ROOT/'adjustment_ranges.json').write_text(json.dumps(MOTION,indent=2))
    (ROOT/'service_wiring.json').write_text(json.dumps({'minimum_free_flexible_lead_length_mm':150,'minimum_bend_radius_mm':10,'body_pins_fixed_to_carriage':True,'loop_corridor_nominal_X_mm':[120,132],'loop_corridor_nominal_Y_mm':[80,110],'upper_loop_Z_mm':[195,260],'lower_loop_Z_mm':[100,172],'notes':'Route behind pods in Y-Z plane, away from rail X145 and rear panel Y130. Flexible conductors are consumables, not rigid moving pin references. Both moving and fixed strain relief required.'},indent=2))
    for name,s in refs.items():cq.exporters.export(s,str(ROOT/(name+'.step')))
    comp=cq.Compound.makeCompound([s.val() for s in [*parts.values(),*refs.values()]])
    cq.exporters.export(comp,str(ROOT/'cad_isometric.svg'),opt={'width':1100,'height':900,'projectionDir':(1,-1,.75),'showHidden':False,'strokeWidth':.7,'strokeColor':(25,45,60),'showAxes':False})
    mass=parts['04_D68_payload_carrier'].val().Volume()/1000*1.30
    (ROOT/'payload_mass_budget.json').write_text(json.dumps({'D68_supplier_mass_g':6.79,'printed_carrier_volume_mm3':parts['04_D68_payload_carrier'].val().Volume(),'PLA_density_ASSUMED_g_cm3':1.30,'carrier_solid_mass_at_assumed_density_g':mass,'remaining_tie_ballast_adhesive_g':10-6.79-mass,'must_weigh_complete_payload':True},indent=2))
    print(json.dumps({'printed_bodies':len(parts),'print_jobs':4,'assembly_reference_entries':len(refs),'valid':all(m['valid'] for m in meta.values()),'output':str(ROOT)},indent=2))
if __name__=='__main__':export()
