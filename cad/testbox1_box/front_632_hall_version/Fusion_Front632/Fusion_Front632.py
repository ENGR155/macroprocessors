"""Native Autodesk Fusion implementation. No external CAD DLLs. mm inputs/cm API."""
import adsk.core,adsk.fusion,math,json,traceback,shutil,time
from pathlib import Path
R=Path(__file__).resolve().parent.parent
OLD=R.parent/'purchased_parts_version'
app=None;design=None;root=None;mgr=None
UP=[207.5+8*i for i in range(5)];LOW=[117.5+8*i for i in range(5)]
P={};REF={};checks=[]
def baseline(name):
    p=R/'native_inputs'/name
    if p.is_file():return p
    return OLD/name
def log(s):
    with (R/'fusion_build.log').open('a',encoding='utf-8') as f:f.write(str(s)+'\n')
def pt(x,y,z):return adsk.core.Point3D.create(x/10,y/10,z/10)
def vec(x,y,z):return adsk.core.Vector3D.create(x,y,z)
def box(x,y,z,dx,dy,dz):
    return mgr.createBox(adsk.core.OrientedBoundingBox3D.create(pt(x+dx/2,y+dy/2,z+dz/2),vec(1,0,0),vec(0,1,0),dx/10,dy/10,dz/10))
def cyl(x,y,z,r,h,axis=(0,0,1)):
    return mgr.createCylinderOrCone(pt(x,y,z),r/10,pt(x+h*axis[0],y+h*axis[1],z+h*axis[2]),r/10)
def boolean(a,b,kind):
    if not mgr.booleanOperation(a,b,kind):raise RuntimeError('Native Boolean failed: '+str(kind))
    return a
def cut(a,b):return boolean(a,b,adsk.fusion.BooleanTypes.DifferenceBooleanType)
def union(a,b):return boolean(a,b,adsk.fusion.BooleanTypes.UnionBooleanType)
def hole(a,x,y,z,d,h,axis=(0,0,1)):return cut(a,cyl(x,y,z,d/2,h,axis))
def move(b,xyz):
    m=adsk.core.Matrix3D.create();m.translation=vec(*(v/10 for v in xyz));assert mgr.transform(b,m);return b
def rot(b,axis,angle,origin=(0,0,0)):
    m=adsk.core.Matrix3D.create();m.setToRotation(math.radians(angle),vec(*axis),pt(*origin));assert mgr.transform(b,m);return b
def cp(b):return mgr.copy(b)
def bb(b):
    a=b.boundingBox;return [a.minPoint.x*10,a.minPoint.y*10,a.minPoint.z*10,a.maxPoint.x*10,a.maxPoint.y*10,a.maxPoint.z*10]
def add_temp_component(name,bodies):
    occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());occ.component.name=name
    for b in bodies:occ.component.bRepBodies.add(cp(b))
    return occ
def all_bodies(comp):
    out=[comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    for i in range(comp.occurrences.count):out+=all_bodies(comp.occurrences.item(i).component)
    return out
def imported(path):
    occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    o=app.importManager.createSTEPImportOptions(str(path));o.isViewFit=False
    if not app.importManager.importToTarget(o,occ.component):raise RuntimeError('STEP import failed '+str(path))
    bs=[cp(b) for b in all_bodies(occ.component)];occ.deleteMe()
    if not bs:raise RuntimeError('No imported bodies '+str(path))
    return bs
def prism_yz(x,points,thick):
    # Native sketch/extrude only for tilted belt references. Own scratch component.
    occ=root.occurrences.addNewComponent(adsk.core.Matrix3D.create());c=occ.component
    ci=c.constructionPlanes.createInput();ci.setByOffset(c.yZConstructionPlane,adsk.core.ValueInput.createByReal(x/10));plane=c.constructionPlanes.add(ci)
    sk=c.sketches.add(plane);v=[sk.modelToSketchSpace(pt(x,y,z)) for y,z in points]
    for i in range(len(v)):sk.sketchCurves.sketchLines.addByTwoPoints(v[i],v[(i+1)%len(v)])
    ex=c.features.extrudeFeatures.addSimple(sk.profiles.item(0),adsk.core.ValueInput.createByReal(thick/10),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    b=cp(ex.bodies.item(0));a=bb(b)
    if abs(a[0]-x)>.001:move(b,(x-a[0],0,0))
    occ.deleteMe();return b
def belt(z):
    b=box(83,46.45,z-.45,14,.8,2.5)
    points=[(46.45,z-.45),(35.3,z+1.75),(35.3,z+4.25),(46.45,z+2.05)]
    b=union(b,prism_yz(83,points,.8))
    b=union(b,box(83,34.5,z+1.75,14,.8,2.5))
    b=union(b,prism_yz(96.2,points,.8))
    return move(b,(0,-.2,0))
def rod(stock):
    dx,dy=(13,11) if stock else (12.4,10.4)
    b=box(90-dx/2,40-dy/2,111,dx,dy,137)
    for z in UP+LOW:
        for tool in [box(87.85,43.2,z,4.3,2.5,1.9),box(88.1,34.3,z,3.8,8.9,1.9),box(91.8,34.3,z-.55,4.9,11.4,3),box(83.4,34.4,z+1.6,13.2,.9,2.8)]:b=cut(b,tool)
    # Capsule slot: 8mm centre travel plus two radius2.05 ends =12.1 overall.
    tool=box(87.95,33,191,4.1,14,8)
    for z in (191,199):tool=union(tool,cyl(90,33,z,2.05,14,(0,1,0)))
    b=cut(b,tool);b=cut(b,box(85.85,42,185.9,8.3,3.6,18.2))
    return b if stock else move(b,(0,-.2,0))
def prepare():
    base=imported(baseline('01_frame_base_upright_tray_assembled.step'))[0]
    carrier=imported(baseline('04_D68_payload_carrier_assembled.step'))[0]
    head=imported(R/'native_inputs/HEAD_SEED.step')[0]
    # Restore original whole top plate and upper cage rim, removing obsolete side
    # guide/counterbores by filling them. Then recut only revised intended holes.
    head=union(head,box(45,39,190,90,103,10))
    head=union(head,cyl(90,65,187,23,3));head=hole(head,90,65,169,26,21.8)
    head=union(head,box(79,30,190,22,20,10))
    head=cut(head,box(83.6,34.6,186,12.8,10.8,18))
    head=hole(head,90,29,195,4.1,27,(0,1,0));head=cut(head,box(85,45.4,190,10,8.6,11))
    head=hole(head,90,65,193,19.6,8)
    for x in (57,119):head=cut(head,box(x,95,189,4,8,12))
    cassette=box(64,39,162,65,52,8);cassette=union(cassette,box(79,30,162,22,20,8))
    cassette=hole(cassette,90,65,163,19.6,8);cassette=cut(cassette,box(83.4,34.4,158,13.2,11.2,16))
    for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4):
        x=90+19*math.cos(a);y=65+19*math.sin(a)
        head=hole(head,x,y,169,4.1,33);cassette=hole(cassette,x,y,161,4.1,11)
    P.update({'01_frame_base_upright_tray':base,'02_head_common_rod_guide':head,'03_cassette_common_rod_guide':cassette,'04_D68_payload_carrier':carrier,'05_common_direct_insert_rod':rod(False)})
    REF['REF_EM_nominal_25x20']=[cyl(90,65,170,12.5,20)]
    REF['REF_D68_N52_gap15']=[cyl(90,65,142.3,9.525/2,12.7)]
    REF['REF_nylon_retaining_loop_envelope']=imported(baseline('REF_nylon_retaining_loop_envelope.step'))
    for i in range(2):
        REF['REF_DC1_bottom_disk_'+str(i+1)]=[cyl(90,65,163+i*1.5875,19.05/2,1.5875)]
        REF['REF_DC1_top_disk_'+str(i+1)]=[cyl(90,65,193+i*1.5875,19.05/2,1.5875)]
    strip=box(65,60,200,50,10,1)
    for x in (71,109):strip=hole(strip,x,65,199,4.1,3)
    REF['REF_NONPRINT_top_stack_retainer_strip']=[rot(strip,(0,0,1),45,(90,65,0))]
    for label,z in [('upper',UP[0]),('lower',LOW[-1])]:
        REF['REF_'+label+'_LPG_max_body']=[move(box(87.95,43.2,z,4.1,3.25,1.62),(0,-.2,0))]
        REF['REF_'+label+'_native_pins']=[move(box(90+d-.275,27.7,z+.505,.55,15.5,.51),(0,-.2,0)) for d in (-1.27,0,1.27)]
        REF['REF_'+label+'_retaining_loop']=[belt(z)]
def flat(name,b):
    b=cp(b)
    if name.startswith('02'):return move(rot(b,(1,0,0),180),(-45,142,200))
    if name.startswith('03'):return move(b,(-64,-30,-162))
    if name.startswith('04'):return move(b,(-82,-57,-140.3))
    if name.startswith('05'):
        b=rot(rod(True),(0,1,0),-90);a=bb(b);return move(b,(-a[0],-a[1],-a[2]))
    return b
def save_component(name,bodies,step=True,stl=False):
    occ=add_temp_component('_EXPORT_'+name,bodies)
    if step:
        opt=design.exportManager.createSTEPExportOptions(str(R/(name+'.step')),occ.component)
        if not design.exportManager.execute(opt):raise RuntimeError('STEP export '+name)
    if stl:
        opt=design.exportManager.createSTLExportOptions(occ,str(R/(name+'.stl')))
        opt.isBinaryFormat=True;opt.sendToPrintUtility=False;opt.unitType=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        opt.surfaceDeviation=.005;opt.normalDeviation=.12
        if not design.exportManager.execute(opt):raise RuntimeError('STL export '+name)
    if not mgr.exportToFile(bodies,str(R/(name+'.sat'))):raise RuntimeError('SAT export '+name)
    occ.deleteMe()
def export_all():
    manifest={}
    for n,b in P.items():
        log('Export '+n);assert b.isSolid,n
        printed=flat(n,b)
        save_component(n+'_assembled',[b]);save_component(n+'_PRINT',[printed],True,True)
        manifest[n]={'kind':'print','job':1 if n.startswith('01') else 2 if n.startswith('02') else 3 if n.startswith(('03','04')) else 4,'assembly_bbox_mm':bb(b),'print_bbox_mm':bb(printed),'valid':bool(b.isSolid),'solid_count':1,'volume_mm3':b.volume*1000,'assembly_state':'FINISHED, SANDED' if n.startswith('05') else 'as modeled','print_state':'OVERSIZE SANDING STOCK' if n.startswith('05') else 'as modeled','engine':'Autodesk Fusion native'}
    # Preserve original base/carrier bytes, including the original plate1 export.
    for n in ('01_frame_base_upright_tray','04_D68_payload_carrier'):
        for ext in ('_assembled.step','_PRINT.step','_PRINT.stl'):shutil.copy2(baseline(n+ext),R/(n+ext))
    for ext in ('.step','.stl'):shutil.copy2(baseline('JOB01_PRINT'+ext),R/('JOB01_PRINT'+ext))
    jobs={2:[flat('02',P['02_head_common_rod_guide'])],3:[flat('03',P['03_cassette_common_rod_guide']),move(flat('04',P['04_D68_payload_carrier']),(82,0,0))],4:[flat('05',P['05_common_direct_insert_rod'])]}
    for j,bs in jobs.items():save_component('JOB0'+str(j)+'_PRINT',bs,True,True)
    for n,bs in REF.items():save_component(n,bs)
    save_component('NONPRINT_632_retainer_strip',REF['REF_NONPRINT_top_stack_retainer_strip'])
    save_component('05_common_rod_FINISHED_SANDING_TARGET',[P['05_common_direct_insert_rod']])
    save_component('05_common_rod_AS_PRINTED_STOCK',[rod(True)])
    save_component('five_printed_parts_assembled',list(P.values()))
    (R/'component_manifest.json').write_text(json.dumps(manifest,indent=2))
    (R/'adjustment_ranges.json').write_text(json.dumps({'upper_port_floor_Z_mm':UP,'lower_port_floor_Z_mm':LOW,'common_rod_travel_mm':[-4,4],'physical_slot_half_travel_mm':(12.1-3.5052)/2,'fine_slot_mm':[12.1,4.1],'rod_finished_mm':[12.4,10.4,137],'rod_stock_mm':[13,11,137],'rod_assembly_Y_shift_mm':-.2,'sensor_center_X_mm':90,'sensor_center_Y_mm':44.625,'upper_guide_mm':[12.8,10.8],'lower_guide_mm':[13.2,11.2],'clamp_bolt':'#6-32x3/4in','nut_track_AF_mm':8.3,'nut_track_depth_mm':3.2,'port_mm':{'body_width':4.3,'height':1.9,'engagement_depth_finished':2,'pin_bay_width':3.8,'open_wire_escape_height':3.0,'open_wire_escape_side':'+X'},'magnet_configuration':'two DC1 bottom+two top simultaneously'},indent=2))
    if (R/'hardware_dimensions.json').is_file():
        hw=json.loads((R/'hardware_dimensions.json').read_text());hw['status']='GEOMETRY_GENERATED_WITH_FUSION_NATIVE; actual hardware dimensions still require measurement';(R/'hardware_dimensions.json').write_text(json.dumps(hw,indent=2))
    # Final assembled document has only persistent assembly components, no plate copies.
    for n,b in P.items():add_temp_component(n,[b])
    for n,bs in REF.items():add_temp_component(n,bs)
    if not design.exportManager.execute(design.exportManager.createSTEPExportOptions(str(R/'testbox1_front_632_hall_assembly.step'))):raise RuntimeError('Main STEP failed')
    if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(str(R/'testbox1_front_632_hall_assembly.f3d'))):raise RuntimeError('F3D failed')
    mgr.exportToFile(list(P.values())+[b for bs in REF.values() for b in bs],str(R/'testbox1_front_632_hall_assembly.sat'))
    report={'completed':True,'engine':'Autodesk Fusion native TemporaryBRepManager','units':'mm files; cm API internals','printed_bodies':len(P),'reference_entries':len(REF),'actual_reference_bodies':sum(len(bs) for bs in REF.values()),'main_total_bodies':len(P)+sum(len(bs) for bs in REF.values()),'stock_rod_bbox_mm':bb(rod(True)),'finished_rod_bbox_mm':bb(P['05_common_direct_insert_rod']),'Fusion_API_executed':True}
    (R/'native_build_result.json').write_text(json.dumps(report,indent=2))
def run(context):
    global app,design,root,mgr
    app=adsk.core.Application.get();ui=app.userInterface
    try:
        (R/'fusion_build.log').write_text('Native build start\n')
        for name in ('native_build_error.txt','native_build_result.json'):
            (R/name).unlink(missing_ok=True)
        doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design=adsk.fusion.Design.cast(app.activeProduct);design.designType=adsk.fusion.DesignTypes.DirectDesignType
        root=design.rootComponent;mgr=adsk.fusion.TemporaryBRepManager.get()
        log('Building native geometry');prepare();log('Geometry prepared');export_all();log('Exports complete')
        cam=app.activeViewport.camera;cam.eye=pt(400,-500,380);cam.target=pt(90,65,130);cam.upVector=vec(0,0,1);cam.isFitView=True;app.activeViewport.camera=cam
        app.activeViewport.refresh();app.activeViewport.saveAsImageFile(str(R/'assembly_preview.png'),1400,1200)
        ui.messageBox('Front #6-32 assembly created. STEP, STL, SAT and native F3D exported.\n'+str(R))
    except:
        error=traceback.format_exc();log(error);(R/'native_build_error.txt').write_text(error);ui.messageBox('Native build stopped:\n'+error)
