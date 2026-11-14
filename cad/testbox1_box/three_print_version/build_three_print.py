"""Three mechanically connected, separately printable solids. All geometry millimetres."""
from pathlib import Path
import json,math
import cadquery as cq
ROOT=Path(__file__).resolve().parent
P={'base_w':180.,'base_d':160.,'base_t':8.,'upright_w':90.,'upright_t':12.,'upright_y':130.,'upright_top':190.,'arm_front':39.,'arm_t':10.,'axis_x':90.,'axis_y':65.,'em_face_z':170.,'em_d':25.,'em_h':20.,'em_bore':26.,'helper_d':19.05,'helper_h':1.5875,'helper_pocket_d':19.6,'helper_pocket_depth':1.9,'helper_floor_z':168.1,'retainer_bolt_radius':19.,'payload_assumed_d':12.7,'payload_assumed_h':6.,'gap_min':10.,'gap_max':20.}
parts={};meta={};refs={}
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Workplane(obj=cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis)))
def hole(s,x,y,z,d,h,axis=(0,0,1)):return s.cut(cyl(x,y,z,d/2,h,axis))
def triangle_yz(x,dx,pts):return cq.Workplane('YZ').workplane(offset=x).polyline(pts).close().extrude(dx)
def add(n,s,notes):
    s=s.clean();assert s.val().isValid() and len(s.val().Solids())==1,n
    parts[n]=s;meta[n]={'notes':notes}
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
    # Recess only: broad arm top remains the print-bed contact face when inverted.
    arm=arm.cut(box(84,61,armtop-2,12,8,3))
    arm=arm.cut(box(88,69,armtop-2,4,34,3))
    # External tie/lead slots, outside the EM and retaining column envelopes.
    for x in (57,119):arm=arm.cut(box(x,95,emtop-1,4,8,P['arm_t']+2))
    add('02_cantilever_vented_head_upper_sensor',arm,'Print upside down with Z200 top face on bed. Upper locating rim Ø26 bore and0.8mm extra axial clearance above nominal coil; four M3 columns; no lower ring or large unsupported bridge. Use measured nonmagnetic compliant shims to remove coil play. Integrated rear mounting flange and gussets. Upper Hall allowance12x8x2 recessed atZ198; secure with nonmagnetic adhesive/tape. No extra upper carrier print.')
    cassette=box(64,39,167,52,52,3)
    cassette=hole(cassette,cx,cy,P['helper_floor_z'],P['helper_pocket_d'],4)
    for x,y in retain:cassette=hole(cassette,x,y,166,3.4,5)
    guard=box(80,39,162,20,52,2)
    cassette=cassette.union(guard)
    # End walls create a connected U section and leave both X sides open for service.
    for y in (39,87):cassette=cassette.union(box(80,y,164,20,4,3))
    for x in (81,97):
        for y in (59,69):cassette=cassette.cut(box(x,y,161,2,2,4))
    add('03_helper_cassette_lower_sensor_guard',cassette,'Print front face Y39 down, 52x8 footprint,52 high,8mm outer brim. Both guard and cassette strips plus end wall touch bed; end-wall closure bridges only3mm. Four M3 socket heads ≤6mm diameter under cassette; NO lower washers. Sensor inserted laterally through3mm open gap; 12x8x2 allowance leaves1mm clearance.')
    refs['REF_EM_nominal_25x20']=cyl(cx,cy,face,P['em_d']/2,P['em_h'])
    refs['REF_helper_nominal']=cyl(cx,cy,P['helper_floor_z'],P['helper_d']/2,P['helper_h'])
    refs['REF_payload_ASSUMED_gap15']=cyl(cx,cy,face-15-P['payload_assumed_h'],P['payload_assumed_d']/2,P['payload_assumed_h'])
    refs['REF_Hall_lower_allowance']=box(84,61,164,12,8,2)
    refs['REF_Hall_upper_allowance']=box(84,61,198,12,8,2)
    return retain,bolt_rear
def bounds(s):
    b=s.val().BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def bed_transform(name,s):
    if name.startswith('01'):return s
    if name.startswith('02'):return s.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
    return s.rotate((0,0,0),(1,0,0),90).translate((-64,170,-39))
def export():
    from conform_stl import repair
    conformity=[]
    retain,rear=build();assembly=cq.Assembly(name='testbox1_PLA_three_print_assembly');fabrication=cq.Assembly(name='three_printed_parts_only')
    colors=[cq.Color(.28,.43,.52),cq.Color(.39,.60,.67),cq.Color(.80,.55,.25)]
    for (name,s),color in zip(parts.items(),colors):
        bed=bed_transform(name,s);shape=s.val();printshape=bed.val()
        b=bounds(bed);assert abs(b[2])<1e-5 and b[3]<=220 and b[4]<=220 and b[5]<=256,name
        cq.exporters.export(s,str(ROOT/(name+'_assembled.step')))
        cq.exporters.export(bed,str(ROOT/(name+'_PRINT.stl')),tolerance=.05,angularTolerance=.12)
        conformity.append(repair(ROOT/(name+'_PRINT.stl')))
        cq.exporters.export(bed,str(ROOT/(name+'_PRINT.step')))
        meta[name].update({'kind':'print','material_selected':'PLA','thermal_validation':'NOT ESTABLISHED','assembly_bbox_mm':bounds(s),'print_bbox_mm':b,'volume_mm3':shape.Volume(),'solid_count':len(shape.Solids()),'valid':shape.isValid(),'print_valid':printshape.isValid(),'rotation_about_X_deg':0 if name.startswith('01') else 180 if name.startswith('02') else 90,'translation_mm':[0,0,0] if name.startswith('01') else [-45,142,200] if name.startswith('02') else [-64,170,-39]})
        assembly.add(s,name=name,color=color);fabrication.add(s,name=name,color=color)
    fabrication.export(str(ROOT/'three_print_parts_assembled.step'))
    for name,s in refs.items():
        color=cq.Color(.88,.67,.24) if 'payload' in name else cq.Color(.20,.65,.35) if 'Hall' in name else cq.Color(.65,.66,.68)
        assembly.add(s,name=name,color=color)
    assembly.export(str(ROOT/'testbox1_PLA_three_print_assembly.step'))
    (ROOT/'component_manifest.json').write_text(json.dumps(meta,indent=2))
    (ROOT/'mesh_conformity.json').write_text(json.dumps(conformity,indent=2))
    (ROOT/'dimensions.json').write_text(json.dumps({'driving_parameters':P,'retainer_bolt_xy':retain,'rear_bolt_xz':rear,'note':'P values drive named dimensions; supporting coordinate details remain explicit in generator.'},indent=2))
    for name,s in refs.items():cq.exporters.export(s,str(ROOT/(name+'.step')))
    comp=cq.Compound.makeCompound([s.val() for s in [*parts.values(),*refs.values()]])
    cq.exporters.export(comp,str(ROOT/'cad_isometric.svg'),opt={'width':1100,'height':900,'projectionDir':(1,-1,.75),'showHidden':False,'strokeWidth':.7,'strokeColor':(25,45,60),'showAxes':False})
    print(json.dumps({'printed_parts':len(parts),'assembly_solids':len(parts)+len(refs),'valid':all(m['valid'] for m in meta.values()),'output':str(ROOT)},indent=2))
if __name__=='__main__':export()
