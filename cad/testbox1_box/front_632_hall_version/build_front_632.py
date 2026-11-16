"""Front common Hall rod, open wired removal, #6-32 hardware. Dimensions mm."""
from pathlib import Path
import importlib.util,json,shutil,math
import cadquery as cq
from conform_stl import repair
R=Path(__file__).resolve().parent
OLD=R.parent/'purchased_parts_version'
source=OLD/'build_purchased.py'
if not source.is_file():source=R/'purchased_geometry.py'
spec=importlib.util.spec_from_file_location('purchased_geometry',source)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
old.hall_seat=lambda s,*args:s
old.build()
box,cyl,hole=old.box,old.cyl,old.hole
UP=[207.5+8*i for i in range(5)]
LOW=[117.5+8*i for i in range(5)]
parts={};refs={};finished_rod=None;stock_rod=None
HW={'screw_major_mm':3.5052,'clearance_hole_mm':4.1,'nut_nominal_AF_mm':7.9375,'nut_nominal_thickness_mm':2.778125,'nut_track_AF_mm':8.3,'nut_track_depth_mm':3.2,'nut_track_Z_length_mm':18.2,'pan_head_max_diameter_mm':6.858,'pan_head_max_height_mm':2.4638,'washer_max_diameter_mm':9.906,'washer_max_thickness_mm':1.651,'cassette_screws':'4 x #6-32 x2in (50.8mm)','rear_joint_screws':'4 x #6-32 x1.25in (31.75mm)','Hall_clamp_screw':'1 x #6-32 x0.75in (19.05mm)','rod_finished_mm':[12.4,10.4,137],'rod_stock_mm':[13,11,137]}

def preserve(name,target=None):
    target=target or name
    if (OLD/name).is_file():shutil.copy2(OLD/name,R/target)
    elif not (R/target).is_file():raise FileNotFoundError(target)

def ribbon(x0,x1,z0,z1,half,y,depth):
    return cq.Workplane('XZ').workplane(offset=-y).polyline([(x0,z0-half),(x1,z1-half),(x1,z1+half),(x0,z0+half)]).close().extrude(-depth)

def guide(s,dx,dy,lo,hi):
    s=s.union(box(79,30,lo,22,20,hi-lo))
    return s.cut(box(90-dx/2,40-dy/2,lo-4,dx,dy,hi-lo+8))

def slot_body(s,z):
    # Sensor from +Y (toward coil); pins point toward the front, -Y.
    s=s.cut(box(87.85,43.2,z,4.3,2.5,1.9))
    s=s.cut(box(88.1,34.3,z,3.8,8.9,1.9))
    # Open +X path: remove the retaining loop, then move the chip and its
    # soldered flying leads sideways. No joint is pulled through a tunnel.
    s=s.cut(box(91.8,34.3,z-.55,4.9,11.4,3))
    # Front return is raised above the pin exits; side grooves follow tilted belt.
    s=s.cut(box(83.4,34.4,z+1.6,13.2,.9,2.8))
    return s

def body(z):return box(87.95,43.2,z,4.1,3.25,1.62)
def pins(z):
    return cq.Workplane(obj=cq.Compound.makeCompound([box(90+d-.275,27.7,z+.505,.55,15.5,.51).val() for d in (-1.27,0,1.27)]))
def loop(z):
    t=box(83,46.45,z-.45,14,.8,2.5).union(box(83,34.5,z+1.75,14,.8,2.5))
    # Y-Z ribbons, one on each side. Belt rises toward the front -Y return.
    pts=[(46.45,z-.45),(35.3,z+1.75),(35.3,z+4.25),(46.45,z+2.05)]
    for x in (83,96.2):t=t.union(cq.Workplane('YZ').workplane(offset=x).polyline(pts).close().extrude(.8))
    return t.clean()

parts['01_frame_base_upright_tray']=old.parts['01_frame_base_upright_tray']
head=guide(old.parts['02_cantilever_vented_head_upper_sensor'],12.8,10.8,190,200)
# Front pan head and washer bear directly on Y30, with open driver access.
# Nut is in the ROD; tightening pulls it onto the guide's front bearing wall.
head=hole(head,90,29,195,4.1,27,(0,1,0))
head=head.cut(box(85,45.4,190,10,8.6,11))
ret=[(90+19*math.cos(a),65+19*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
for x,y in ret:head=hole(head,x,y,169,4.1,33)
parts['02_head_common_rod_guide']=head.clean()
cassette=guide(old.parts['03_four_DC1_stack_cassette_lower_LPG_seat'],13.2,11.2,162,170)
for x,y in ret:cassette=hole(cassette,x,y,161,4.1,11)
parts['03_cassette_common_rod_guide']=cassette.clean()
parts['04_D68_payload_carrier']=old.parts['04_D68_payload_carrier']
def make_rod(stock):
    dx,dy=(13,11) if stock else (12.4,10.4)
    s=box(90-dx/2,40-dy/2,111,dx,dy,137)
    for z in UP+LOW:s=slot_body(s,z)
    clamp=cq.Workplane('XZ').workplane(offset=-47).center(90,195).slot2D(12.1,4.1,90).extrude(14)
    s=s.cut(clamp).cut(box(85.85,42,185.9,8.3,3.6,18.2)).clean()
    return s
stock_rod=make_rod(True)
finished_rod=make_rod(False).translate((0,-.2,0))
parts['05_common_direct_insert_rod']=finished_rod
for n,s in old.refs.items():
    if not any(t in n for t in ('DRV5056','leads_formed','DC1_disk')):refs[n]=s
for i in range(2):
    refs['REF_DC1_bottom_disk_'+str(i+1)]=cyl(90,65,163+i*1.5875,19.05/2,1.5875)
    refs['REF_DC1_top_disk_'+str(i+1)]=cyl(90,65,193+i*1.5875,19.05/2,1.5875)
strip=box(65,60,200,50,10,1)
for x in (71,109):strip=hole(strip,x,65,199,4.1,3)
strip=strip.rotate((90,65,0),(90,65,1),45)
refs['REF_NONPRINT_top_stack_retainer_strip']=strip
for label,z in [('upper',UP[0]),('lower',LOW[-1])]:
    refs['REF_'+label+'_LPG_max_body']=body(z).translate((0,-.2,0))
    refs['REF_'+label+'_native_pins']=pins(z).translate((0,-.2,0))
    refs['REF_'+label+'_retaining_loop']=loop(z).translate((0,-.2,0))

def bounds(s):
    b=s.val().BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def flat(n,s):
    if n.startswith('01'):return s
    if n.startswith('02'):return s.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
    if n.startswith('03'):return s.translate((-64,-30,-162))
    if n.startswith('04'):return s.translate((-82,-57,-140.3))
    # Rod printed on left X face, with its OPEN +X wire escape facing UP.
    p=stock_rod.rotate((0,0,0),(0,1,0),-90)
    b=p.val().BoundingBox();return p.translate((-b.xmin,-b.ymin,-b.zmin))
def export():
    manifest={};audit=[];assembly=cq.Assembly(name='front_632_common_Hall_rod');fabrication=cq.Assembly(name='five_printed_bodies')
    palette=[(.38,.55,.65),(.60,.77,.83),(.83,.56,.25),(.68,.32,.16),(.28,.52,.38)]
    for (n,s),color in zip(parts.items(),palette):
        assert s.val().isValid() and len(s.val().Solids())==1,n
        p=flat(n,s)
        if n.startswith(('01','04')):
            original='01_frame_base_upright_tray' if n.startswith('01') else '04_D68_payload_carrier'
            for suffix in ('_assembled.step','_PRINT.step','_PRINT.stl'):preserve(original+suffix,n+suffix)
        else:
            cq.exporters.export(s,str(R/(n+'_assembled.step')))
            cq.exporters.export(p,str(R/(n+'_PRINT.step')))
            cq.exporters.export(p,str(R/(n+'_PRINT.stl')),tolerance=.05,angularTolerance=.12)
            audit.append(repair(R/(n+'_PRINT.stl')))
        manifest[n]={'kind':'print','job':1 if n.startswith('01') else 2 if n.startswith('02') else 3 if n.startswith(('03','04')) else 4,'assembly_bbox_mm':bounds(s),'print_bbox_mm':bounds(p),'valid':True,'solid_count':1,'volume_mm3':s.val().Volume(),'assembly_state':'FINISHED, SANDED' if n.startswith('05') else 'as modeled','print_state':'OVERSIZE SANDING STOCK' if n.startswith('05') else 'as modeled'}
        assembly.add(s,name=n,color=cq.Color(*color));fabrication.add(s,name=n,color=cq.Color(*color))
    for n,s in refs.items():
        cq.exporters.export(s,str(R/(n+'.step')))
        assembly.add(s,name=n,color=cq.Color(.1,.6,.3) if 'body' in n else cq.Color(.65,.65,.68))
    assembly.export(str(R/'testbox1_front_632_hall_assembly.step'))
    fabrication.export(str(R/'five_printed_parts_assembled.step'))
    alt=cq.Assembly(name='both_pockets_capacity_example_four_disks_each')
    for n,s in parts.items():alt.add(s,name=n)
    for n,s in refs.items():
        if 'DC1_' not in n:alt.add(s,name=n)
    for i in range(4):
        alt.add(cyl(90,65,163+i*1.5875,19.05/2,1.5875),name='capacity_BOTTOM_disk_'+str(i+1))
        alt.add(cyl(90,65,193+i*1.5875,19.05/2,1.5875),name='capacity_TOP_disk_'+str(i+1))
    alt.export(str(R/'OPTIONAL_capacity_four_disks_each.step'))
    cq.exporters.export(strip,str(R/'NONPRINT_632_retainer_strip.step'))
    cq.exporters.export(finished_rod,str(R/'05_common_rod_FINISHED_SANDING_TARGET.step'))
    cq.exporters.export(stock_rod,str(R/'05_common_rod_AS_PRINTED_STOCK.step'))
    for ext in ('.stl','.step'):preserve('JOB01_PRINT'+ext)
    jobs={2:[flat(n,s) for n,s in parts.items() if n.startswith('02')],3:[flat(n,s) for n,s in parts.items() if n.startswith('03')]+[flat(n,s).translate((82,0,0)) for n,s in parts.items() if n.startswith('04')],4:[flat(n,s) for n,s in parts.items() if n.startswith('05')]}
    for job,items in jobs.items():
        c=cq.Compound.makeCompound([s.val() for s in items]);f=R/f'JOB0{job}_PRINT.stl'
        cq.exporters.export(c,str(f),tolerance=.05,angularTolerance=.12);audit.append(repair(f))
        cq.exporters.export(c,str(R/f'JOB0{job}_PRINT.step'))
    (R/'component_manifest.json').write_text(json.dumps(manifest,indent=2))
    (R/'mesh_conformity.json').write_text(json.dumps(audit,indent=2))
    (R/'hardware_dimensions.json').write_text(json.dumps(HW,indent=2))
    (R/'adjustment_ranges.json').write_text(json.dumps({'upper_port_floor_Z_mm':UP,'lower_port_floor_Z_mm':LOW,'common_rod_travel_mm':[-4,4],'physical_slot_half_travel_mm':(12.1-3.5052)/2,'fine_slot_mm':[12.1,4.1],'rod_finished_mm':[12.4,10.4,137],'rod_stock_mm':[13,11,137],'rod_assembly_Y_shift_mm':-.2,'sensor_center_X_mm':90,'sensor_center_Y_mm':44.625,'upper_guide_mm':[12.8,10.8],'lower_guide_mm':[13.2,11.2],'clamp_bolt':'#6-32x3/4in','regular_nut_mm':{'AF_nominal':7.9375,'thickness_nominal':2.778125,'pocket_AF':8.3,'pocket_depth':3.2},'port_mm':{'body_width':4.3,'height':1.9,'engagement_depth_finished':2,'pin_bay_width':3.8,'open_wire_escape_height':3.0,'open_wire_escape_side':'+X'},'magnet_configuration':'mainassembly two DC1 bottom+two top; capacityexample four each, NOT extra purchased magnets'},indent=2))
    print('Exported five fabrication bodies; JOB04 is ONE connected OVERSIZE holder, mainassembly FINISHED.')
if __name__=='__main__':export()
