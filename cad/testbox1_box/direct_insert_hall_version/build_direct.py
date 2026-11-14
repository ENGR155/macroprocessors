"""One common direct-insertion Hall rod. Units mm; no separate carriages."""
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
parts={};refs={}

def preserve(name,target=None):
    target=target or name
    if (OLD/name).is_file():shutil.copy2(OLD/name,R/target)
    elif not (R/target).is_file():raise FileNotFoundError(target)

def ribbon(x0,x1,z0,z1,half,y,depth):
    return cq.Workplane('XZ').workplane(offset=-y).polyline([(x0,z0-half),(x1,z1-half),(x1,z1+half),(x0,z0+half)]).close().extrude(-depth)

def guide(s,dx,dy):
    return s.cut(box(113-dx/2,65-dy/2,155,dx,dy,50))

def slot_body(s,z):
    # Body projects 1.25mm out of the inboard face. A width shoulder at X110
    # stops it; the positive tilted nylon loop holds it against that shoulder.
    s=s.cut(box(107.9,62.75,z,2.1,4.5,1.9))
    s=s.cut(box(110,63.2,z,8.2,3.6,1.9))
    k=2.2/(117.4-106.75)
    for y in (59,70.4):s=s.cut(ribbon(108,118,z+.8+k*1.25,z+.8+k*11.25,1.4,y,.6))
    return s.cut(box(117.4,58.9,z+1.6,.8,12.2,2.8))

def body(z):return box(106.75,62.95,z,3.25,4.1,1.62)
def pins(z):
    return cq.Workplane(obj=cq.Compound.makeCompound([box(110,65+d-.275,z+.505,15.5,.55,.51).val() for d in (-1.27,0,1.27)]))
def loop(z):
    t=box(105.95,58.8,z-.45,.8,12.4,2.5).union(box(117.4,58.8,z+1.75,.8,12.4,2.5))
    for y in (58.8,70.4):t=t.union(ribbon(106.75,117.4,z+.8,z+3,1.25,y,.8))
    return t.clean()

parts['01_frame_base_upright_tray']=old.parts['01_frame_base_upright_tray']
head=guide(old.parts['02_cantilever_vented_head_upper_sensor'],10.8,12.8)
# Front tool counterbore ends at Y54. The nut is in the ROD, so tightening
# pulls the rod onto the guide wall without trying to squeeze a rigid sleeve.
head=hole(head,113,38,195,3.4,35,(0,1,0))
head=hole(head,113,38,195,7,16,(0,1,0))
head=head.cut(box(109.6,71.4,190,6.8,9,11)) # open-top rear nut insertion pocket
parts['02_head_common_rod_guide']=head.clean()
parts['03_cassette_common_rod_guide']=guide(old.parts['03_four_DC1_stack_cassette_lower_LPG_seat'],11.2,13.2).clean()
parts['04_D68_payload_carrier']=old.parts['04_D68_payload_carrier']
rod=box(108,59,111,10,12,137)
for z in UP+LOW:rod=slot_body(rod,z)
clamp=cq.Workplane('XZ').workplane(offset=-72).center(113,195).slot2D(11.4,3.4,90).extrude(14)
rod=rod.cut(clamp).cut(box(110.1,68.4,187.4,5.8,2.8,15.2)).clean()
# Assembly shown against upper front bearing surface: -0.4mm Y shift.
parts['05_common_direct_insert_rod']=rod.translate((0,-.4,0))
for n,s in old.refs.items():
    if not any(t in n for t in ('DRV5056','leads_formed')):refs[n]=s
for label,z in [('upper',UP[0]),('lower',LOW[-1])]:
    refs['REF_'+label+'_LPG_max_body']=body(z).translate((0,-.4,0))
    refs['REF_'+label+'_native_pins']=pins(z).translate((0,-.4,0))
    refs['REF_'+label+'_retaining_loop']=loop(z).translate((0,-.4,0))

def bounds(s):
    b=s.val().BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def flat(n,s):
    if n.startswith('01'):return s
    if n.startswith('02'):return s.rotate((0,0,0),(1,0,0),180).translate((-45,142,200))
    if n.startswith('03'):return s.translate((-64,-39,-162))
    if n.startswith('04'):return s.translate((-82,-57,-140.3))
    return rod.rotate((0,0,0),(1,0,0),90).translate((-108,248,-59))
def export():
    manifest={};audit=[];assembly=cq.Assembly(name='direct_insert_common_Hall_rod');fabrication=cq.Assembly(name='five_printed_bodies')
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
        manifest[n]={'kind':'print','job':1 if n.startswith('01') else 2 if n.startswith('02') else 3 if n.startswith(('03','04')) else 4,'assembly_bbox_mm':bounds(s),'print_bbox_mm':bounds(p),'valid':True,'solid_count':1,'volume_mm3':s.val().Volume()}
        assembly.add(s,name=n,color=cq.Color(*color));fabrication.add(s,name=n,color=cq.Color(*color))
    for n,s in refs.items():
        cq.exporters.export(s,str(R/(n+'.step')))
        assembly.add(s,name=n,color=cq.Color(.1,.6,.3) if 'body' in n else cq.Color(.65,.65,.68))
    assembly.export(str(R/'testbox1_direct_insert_hall_assembly.step'))
    fabrication.export(str(R/'five_printed_parts_assembled.step'))
    alt=cq.Assembly(name='optional_top_helper_stack')
    for n,s in parts.items():alt.add(s,name=n)
    for n,s in refs.items():
        if not n.startswith('REF_DC1_disk'):alt.add(s,name=n)
    for n,s in old.optional.items():alt.add(s,name=n)
    alt.export(str(R/'OPTIONAL_top_stack_configuration.step'))
    cq.exporters.export(old.optional['NONPRINT_top_stack_retainer_strip'],str(R/'OPTIONAL_NONPRINT_retainer_strip.step'))
    preserve('OPTIONAL_retainer_cut_template.svg')
    for ext in ('.stl','.step'):preserve('JOB01_PRINT'+ext)
    jobs={2:[flat(n,s) for n,s in parts.items() if n.startswith('02')],3:[flat(n,s) for n,s in parts.items() if n.startswith('03')]+[flat(n,s).translate((82,0,0)) for n,s in parts.items() if n.startswith('04')],4:[flat(n,s) for n,s in parts.items() if n.startswith('05')]}
    for job,items in jobs.items():
        c=cq.Compound.makeCompound([s.val() for s in items]);f=R/f'JOB0{job}_PRINT.stl'
        cq.exporters.export(c,str(f),tolerance=.05,angularTolerance=.12);audit.append(repair(f))
        cq.exporters.export(c,str(R/f'JOB0{job}_PRINT.step'))
    (R/'component_manifest.json').write_text(json.dumps(manifest,indent=2))
    (R/'mesh_conformity.json').write_text(json.dumps(audit,indent=2))
    (R/'adjustment_ranges.json').write_text(json.dumps({'upper_port_floor_Z_mm':UP,'lower_port_floor_Z_mm':LOW,'common_rod_travel_mm':[-4,4],'fine_slot_mm':[11.4,3.4],'rod_size_mm':[10,12,137],'rod_assembly_Y_shift_mm':-.4,'sensor_center_X_mm':108.375,'sensor_center_Y_mm':64.6,'upper_guide_mm':[10.8,12.8],'lower_guide_mm':[11.2,13.2],'clamp_bolt':'M3x20','regular_nut_mm':{'AF':5.5,'thickness':2.4},'port_mm':{'body_width':4.5,'height':1.9,'engagement_depth':2,'pin_bay_width':3.6}},indent=2))
    print('Exported five fabrication bodies; JOB04 is ONE connected holder.')
if __name__=='__main__':export()
