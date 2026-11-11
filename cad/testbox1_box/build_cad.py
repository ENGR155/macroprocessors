"""Generate millimetre BRep CAD; installed CadQuery 2.8.0, OCP 7.9.3.1."""
from pathlib import Path
import json, math
import cadquery as cq

OUT=Path(__file__).resolve().parent
PARTS=OUT/'parts'; PARTS.mkdir(exist_ok=True)
P={'base_width':180.,'base_depth':160.,'base_thickness':18.,'panel_width':90.,'panel_thickness':6.,'panel_top':190.,'axis_x':90.,'axis_y':65.,'em_face_z':170.,'em_diameter':25.,'em_height':20.,'em_bore':25.6,'helper_diameter':19.05,'helper_thickness':1.5875,'helper_pocket_diameter':19.6,'helper_pocket_depth':1.9,'helper_floor_z':168.1,'payload_diameter_ASSUMED':12.7,'payload_height_ASSUMED':6.,'gap_min':10.,'gap_max':20.}
parts={};meta={}
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):
    return cq.Workplane(obj=cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis)))
def hole(s,x,y,z,d,h,axis=(0,0,1)):return s.cut(cyl(x,y,z,d/2,h,axis))
def add(name,s,kind='fabricate',material='PETG',note=''):
    s=s.clean();parts[name]=s;meta[name]={'kind':kind,'material':material,'note':note}
    return s
def slots_z(s,points,length,width,z,h):
    for x,y in points:
        c=cq.Workplane('XY').workplane(offset=z).center(x,y).slot2D(length,width,0).extrude(h)
        s=s.cut(c)
    return s
def build():
    base=box(0,0,0,180,160,18)
    for x in (75,105):
        base=hole(base,x,115,-1,4.5,20)
        base=base.cut(cq.Workplane(obj=cq.Solid.makeCone(5,2.25,3,cq.Vector(x,115,0),cq.Vector(0,0,1))))
    for x in (60,120):
        for y in (35,95):base=hole(base,x,y,7,2.5,12)
    add('01_plywood_base',base,'fabricate','plywood','Countersinks on underside; M4/wood screws heads must finish flush.')
    clamp=box(45,100,18,90,30,25)
    for x in (60,120):
        clamp=hole(clamp,x,99,31,4.5,38,(0,1,0))
    for x in (75,105):
        clamp=hole(clamp,x,115,17,2.5,24)
    add('02_wood_rear_clamp',clamp,'fabricate','hardwood')
    panel=box(45,130,18,90,6,172)
    for x in (60,120):panel=hole(panel,x,129,31,4.5,8,(0,1,0))
    for x in (56,124):panel=hole(panel,x,129,178,4.5,8,(0,1,0))
    # Cable tie slots, outside optical center.
    for z in (65,110,150):
        for x in (49,127):panel=panel.cut(box(x,129,z,4,8,2))
    add('03_clear_rear_panel',panel,'fabricate','cast acrylic','6mm flat sheet. Do not heat bend; bolted angle brackets join separate top plate.')
    arm=box(45,39,190,90,97,6)
    arm=hole(arm,90,65,189,26,8)
    head_mounts=[(69,44),(111,44),(69,86),(111,86)]
    for x,y in head_mounts:arm=hole(arm,x,y,189,3.4,8)
    for x in (56,124):arm=hole(arm,x,115,189,4.5,8)
    retain=[(90+17.5*math.cos(a),65+17.5*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
    for x,y in retain+[(90,46),(90,84)]:arm=hole(arm,x,y,189,3.4,8)
    for x in (60,120):arm=hole(arm,x,65,189,3.4,8)
    add('04_clear_top_cantilever',arm,'fabricate','cast acrylic','97mm front-to-back; 91mm projection from rear panel front. Center bore permits EM top access and reference Hall sensing.')
    for x,label in ((50,'left'),(118,'right')):
        a=box(x,105,186,12,25,4).union(box(x,126,165,12,4,25))
        a=hole(a,x+6,115,185,4.5,6)
        a=hole(a,x+6,125,178,4.5,7,(0,1,0))
        add('05_angle_bracket_'+label,a,'fabricate','PETG','Print on side; 4mm flanges. M4 bolt+washers+nut each flange.')
    cradle=cyl(90,65,170,21,20).union(box(64,39,184,52,52,6))
    cradle=hole(cradle,90,65,169,25.6,23)
    # Side lead exit; strain relief via tie slots in rear panel.
    cradle=cradle.cut(box(85,76,178,10,19,6))
    for x,y in head_mounts:cradle=hole(cradle,x,y,183,3.4,8)
    for x,y in retain+[(90,46),(90,84)]:cradle=hole(cradle,x,y,169,3.4,22)
    add('06_em_cradle',cradle,'fabricate','PETG','25.6mm bore. Four M3 through-bolts retain cassette; no unknown coil thread used. 10x6mm side lead exit.')
    cassette=box(64,39,167,52,52,3)
    cassette=hole(cassette,90,65,168.1,19.6,2.9)
    for x,y in retain:cassette=hole(cassette,x,y,165,3.4,7)
    # Two integral standoffs support guard; only these contact guard.
    for y in (46,84):
        cassette=cassette.union(cyl(90,y,164,4,3))
        cassette=hole(cassette,90,y,163,3.4,8)
    add('07_helper_retainer_cassette',cassette,'fabricate','PETG','Pocket open upward. Helper rests on floor168.1mm and is captive under EM when bolted. Cassette also positively supports coil rim; remove four bolts to change helper.')
    guard=box(78,39,162,24,52,2)
    guard=slots_z(guard,[(90,46),(90,84)],8,3.4,161,4)
    # Four tie slots for package-independent board retention.
    for x in (80,98):
        for y in (59,69):guard=guard.cut(box(x,y,161,2,2,4))
    add('08_lower_Hall_guard',guard,'fabricate','polycarbonate','2mm protective stop; slot travel +/-2.3mm lateral. Board/sensor total envelope <=12x8x2mm sits on top; solder leads exit sides. Sensor not a fitted socket.')
    upper=box(50,57,196,80,16,2)
    upper=slots_z(upper,[(60,65),(120,65)],8,3.4,195,4)
    for x in (80,98):upper=upper.cut(box(x,60,195,2,10,4))
    add('09_upper_Hall_carrier',upper,'fabricate','PETG','Board/sensor retained with nylon ties/adhesive; adjust lateral position in slots and orient sensor sensitive axis vertically. Confirm package before assembly.')
    tray=box(55,30,18,70,70,6).cut(box(58,33,19.5,64,64,6))
    for x in (60,120):
        for y in (35,95):tray=hole(tray,x,y,17,3.4,9)
    add('10_catch_tray',tray,'fabricate','PETG','64x64mm clear cavity, floor1.5mm. Add nonmagnetic foam; screw to base. No enclosure or supply geometry assumed.')
    add('REF_electromagnet_25x20',cyl(90,65,170,12.5,20),'reference','steel/copper','Nominal project envelope, not measured supplier drawing; remove references for manufacturing.')
    add('REF_helper_19p05x1p5875',cyl(90,65,168.1,19.05/2,1.5875),'reference','N42','Candidate DC1 dimensions; sits on pocket floor. 0.3125mm top clearance to EM.')
    add('REF_payload_ASSUMED_12p7x6_gap15',cyl(90,65,149,6.35,6),'reference','hypothetical','ILLUSTRATIVE ONLY. Top155mm =>15mm EM face gap. Total moving mass must be10g; this envelope is not an ordered part.')
    add('REF_lower_Hall_allowance',box(84,61,164,12,8,2),'reference','electronics allowance','Package+carrier allowance, not actual sensor package. Must confirm <=2mm total height or lower guard (changes stop clearance).')
    add('REF_upper_Hall_allowance',box(84,61,198,12,8,2),'reference','electronics allowance','Package+carrier allowance, not actual sensor package.')
    return head_mounts,retain

def export():
    build();assy=cq.Assembly(name='testbox1_box_maglev')
    palette={'plywood':cq.Color(.63,.43,.24),'hardwood':cq.Color(.58,.38,.20),'cast acrylic':cq.Color(.64,.84,.94,.38),'PETG':cq.Color(.16,.23,.29),'polycarbonate':cq.Color(.74,.90,.95,.6),'steel/copper':cq.Color(.45,.46,.48),'N42':cq.Color(.70,.72,.75),'hypothetical':cq.Color(.90,.52,.12),'electronics allowance':cq.Color(.08,.48,.26)}
    for name,s in parts.items():
        shape=s.val();b=shape.BoundingBox();meta[name].update({'bbox_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],'volume_mm3':shape.Volume(),'solid_count':len(shape.Solids()),'valid':shape.isValid()})
        assert shape.isValid() and len(shape.Solids())==1,name
        cq.exporters.export(s,str(PARTS/(name+'.step')))
        if meta[name]['kind']=='fabricate':cq.exporters.export(s,str(PARTS/(name+'.stl')),tolerance=.06,angularTolerance=.15)
        assy.add(s,name=name,color=palette[meta[name]['material']])
    assy.export(str(OUT/'testbox1_box_maglev.step'))
    cq.exporters.export(cq.Compound.makeCompound([s.val() for n,s in parts.items() if meta[n]['kind']=='fabricate']),str(OUT/'fabricated_parts_assembled.step'))
    (OUT/'parameters.json').write_text(json.dumps(P,indent=2))
    (OUT/'component_manifest.json').write_text(json.dumps(meta,indent=2))
    # Project directly from real BRep assembly, plus dimensioned orthographic drawing below.
    comp=cq.Compound.makeCompound([s.val() for s in parts.values()])
    cq.exporters.export(comp,str(OUT/'cad_isometric.svg'),opt={'width':1100,'height':900,'projectionDir':(1,-1,0.75),'showHidden':False,'strokeWidth':0.7,'strokeColor':(25,45,60),'showAxes':False})
    for name,vec in [('cad_front',(0,-1,0)),('cad_side',(1,0,0))]:cq.exporters.export(comp,str(OUT/(name+'.svg')),opt={'width':800,'height':800,'projectionDir':vec,'showHidden':False,'showAxes':False,'strokeWidth':.6})
    print(json.dumps({'components':len(parts),'all_valid':all(x['valid'] for x in meta.values()),'output':str(OUT)},indent=2))
if __name__=='__main__':export()
