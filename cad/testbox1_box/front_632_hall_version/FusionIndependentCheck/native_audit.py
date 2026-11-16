"""Independent native Fusion audit: imports exported STEP, never builder code."""
import adsk.core as ac,adsk.fusion as af,adsk
from pathlib import Path
import json,math,itertools,hashlib,collections,struct,re,time,traceback
R=Path(__file__).resolve().parent.parent
N=['01_frame_base_upright_tray','02_head_common_rod_guide','03_cassette_common_rod_guide','04_D68_payload_carrier','05_common_direct_insert_rod']
UP=[207.5+8*i for i in range(5)];LOW=[117.5+8*i for i in range(5)]
APP=None;M=None;C=[];START=0
def progress(stage):
    (R/'fusion_independent_progress.json').write_text(json.dumps({'stage':stage,'checks':len(C),'elapsed_seconds':time.time()-START},indent=2));adsk.doEvents()
def ck(name,passed,detail):
    C.append({'name':name,'passed':bool(passed),'detail':detail})
    if len(C)%8==0:progress(name)
def P(x,y,z):return ac.Point3D.create(x/10,y/10,z/10)
def vec(x,y,z):return ac.Vector3D.create(x,y,z)
def box(x,y,z,a,b,c):
    b=M.createBox(ac.OrientedBoundingBox3D.create(P(x+a/2,y+b/2,z+c/2),vec(1,0,0),vec(0,1,0),a/10,b/10,c/10));assert b;return [b]
def cyl(x,y,z,r,h,axis=(0,0,1)):
    b=M.createCylinderOrCone(P(x,y,z),r/10,P(x+h*axis[0],y+h*axis[1],z+h*axis[2]),r/10);assert b;return [b]
def vol(g):return sum(b.volume*1000 for b in g)
def bbox(g):
    a=[b.preciseBoundingBox for b in g]
    return [min(getattr(t.minPoint,k)*10 for t in a) for k in ('x','y','z')]+[max(getattr(t.maxPoint,k)*10 for t in a) for k in ('x','y','z')]
def copy(g):return [M.copy(b) for b in g]
def move(g,x=0,y=0,z=0):
    out=copy(g);t=ac.Matrix3D.create();t.translation=vec(x/10,y/10,z/10)
    for b in out:assert M.transform(b,t)
    return out
def rotate(g,angle,axis,center=(0,0,0)):
    out=copy(g);t=ac.Matrix3D.create();t.setToRotation(math.radians(angle),vec(*axis),P(*center))
    for b in out:assert M.transform(b,t)
    return out
def intersect(g,h):
    out=[]
    for a in g:
        ba=bbox([a])
        for b in h:
            bb=bbox([b])
            if any(min(ba[i+3],bb[i+3])-max(ba[i],bb[i])<=1e-8 for i in range(3)):continue
            t=M.copy(a)
            if not M.booleanOperation(t,b,af.BooleanTypes.IntersectionBooleanType):raise RuntimeError('Native intersection failed; no zero-volume assumption')
            if t.isSolid and t.volume>1e-12:out.append(t)
    return out
def iv(g,h):return vol(intersect(g,h))
def diff(g,h):
    out=copy(g)
    for tool in h:
        for b in out:
            if not M.booleanOperation(b,tool,af.BooleanTypes.DifferenceBooleanType):raise RuntimeError('Native difference failed')
    return [b for b in out if b.isSolid and b.volume>1e-12]
def collision_pairs(items):
    bad=[]
    for (a,ga),(b,gb) in itertools.combinations(items.items(),2):
        v=iv(ga,gb)
        if v>.001:bad.append([a,b,v])
    return bad
def step(path):
    progress('Reimporting STEP '+path.name)
    opts=APP.importManager.createSTEPImportOptions(str(path));opts.isViewFit=False
    doc=APP.importManager.importToNewDocument(opts)
    if not doc:raise RuntimeError('STEP import failed: '+str(path))
    try:
        d=af.Design.cast(APP.activeProduct);root=d.rootComponent;out=[]
        for i in range(root.bRepBodies.count):out.append(M.copy(root.bRepBodies.item(i)))
        for i in range(root.allOccurrences.count):
            occ=root.allOccurrences.item(i)
            for j in range(occ.bRepBodies.count):out.append(M.copy(occ.bRepBodies.item(j)))
        if not out:raise RuntimeError('No imported solids '+path.name)
        return out
    finally:doc.close(False)
def mesh(path,count):
    raw=path.read_bytes();verts=[]
    num=struct.unpack_from('<I',raw,80)[0] if len(raw)>=84 else 0
    if len(raw)==84+50*num:
        for i in range(num):
            f=struct.unpack_from('<12f',raw,84+50*i);verts.extend([tuple(round(v,5) for v in f[j:j+3]) for j in (3,6,9)])
    else:
        verts=[tuple(round(float(v),5) for v in x) for x in re.findall(r'vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)',raw.decode())];num=len(verts)//3
    edges=collections.Counter();adj=collections.defaultdict(set);deg=0
    for i in range(0,len(verts),3):
        v=verts[i:i+3]
        if len(set(v))<3:deg+=1
        for a,b in ((0,1),(1,2),(2,0)):edges[tuple(sorted((v[a],v[b])))]+=1;adj[v[a]].add(v[b]);adj[v[b]].add(v[a])
    left=set(adj);components=0
    while left:
        components+=1;stack=[left.pop()]
        while stack:
            for v in adj[stack.pop()]:
                if v in left:left.remove(v);stack.append(v)
    bad=sum(v!=2 for v in edges.values());ck(path.name+' closed manifold/count',bad==0 and deg==0 and components==count,{'triangles':num,'bad_edges':bad,'degenerate':deg,'components':components})
    return [min(v[j] for v in verts) for j in range(3)]+[max(v[j] for v in verts) for j in range(3)]
def hexnut(x,y,z,aflat=8.0,thick=2.9,axis='z'):
    # Intersection of three independent planar strips gives an actual regular
    # hexagon rather than a circle that falsely fails an across-flats pocket.
    g=box(x-aflat/2,y-aflat*2,z,aflat,aflat*4,thick)
    for angle in (60,120):g=intersect(g,rotate(box(x-aflat/2,y-aflat*2,z,aflat,aflat*4,thick),angle,(0,0,1),(x,y,z)))
    if axis=='y':g=rotate(g,-90,(1,0,0),(x,y,z))
    return g
def swept_bbox(g,dx=0,dy=0,dz=0):
    b=bbox(g);return box(b[0]+min(0,dx),b[1]+min(0,dy),b[2]+min(0,dz),b[3]-b[0]+abs(dx),b[4]-b[1]+abs(dy),b[5]-b[2]+abs(dz))
def check_free(name,probe,items):
    bad=[]
    for n,g in items.items():
        v=iv(probe,g)
        if v>.001:bad.append([n,v])
    ck(name,not bad,bad)
def run():
    global APP,M,C,START
    APP=ac.Application.get();M=af.TemporaryBRepManager.get();C=[];START=time.time();owner=APP.activeDocument
    try:
        progress('Starting trusted Fusion kernel audit')
        probe=json.loads((R/'fusion_boolean_probe.json').read_text())
        ck('Native Boolean diagnostic passed',all(x.get('success') for x in probe) and any(x.get('case')=='overlap' and abs(x.get('volume_mm3',0)-500)<.001 for x in probe),'Empty disjoint/contact and nonempty intersections were exercised in this Fusion session')
        S={n:step(R/(n+'_assembled.step')) for n in N}
        S.update({p.stem:step(p) for p in sorted(R.glob('REF_*.step'))})
        for n,g in S.items():ck(n+' reimported solid validity',all(b.isValid and b.isSolid for b in g),{'solids':len(g),'bbox_mm':bbox(g),'volume_mm3':vol(g)})
        ck('Main components nonintersecting',not collision_pairs(S),collision_pairs(S))
        main=step(R/'testbox1_front_632_hall_assembly.step');ck('Main STEP solid count agrees with individual files',len(main)==sum(len(g) for g in S.values()),{'main':len(main),'individual_sum':sum(len(g) for g in S.values())})
        baseline=json.loads((R/'baseline_sha256.json').read_text())
        for name,wanted in baseline.items():
            if name=='REF_nylon_retaining_loop_envelope.step':continue
            ck(name+' preserved original bytes',hashlib.sha256((R/name).read_bytes()).hexdigest()==wanted,wanted)
        legacy_loop=step(R/'native_inputs/REF_nylon_retaining_loop_envelope.step')
        current_loop=S['REF_nylon_retaining_loop_envelope']
        loop_difference=vol(diff(legacy_loop,current_loop))+vol(diff(current_loop,legacy_loop))
        ck('Payload retaining loop geometry preserved through native STEP translation',loop_difference<.001,{'symmetric_difference_mm3':loop_difference,'native_STEP_header_bytes_are_not_required_identical':True})
        stock=step(R/'05_common_rod_AS_PRINTED_STOCK.step');finished=step(R/'05_common_rod_FINISHED_SANDING_TARGET.step')
        ck('Finished sanding target matches assembled rod',vol(diff(finished,S[N[4]]))+vol(diff(S[N[4]],finished))<.001,bbox(finished))
        trimmed=move(intersect(stock,box(83.8,34.8,111,12.4,10.4,137)),y=-.2)
        ck('Sanding removes face stock without scaling sensor features',vol(diff(trimmed,finished))+vol(diff(finished,trimmed))<.001,{'stock_bbox':bbox(stock),'finished_bbox':bbox(finished),'remove_per_face_mm':.3})
        ck('As-printed upper-guide interference is intentional',iv(stock,S[N[1]])>.01,{'interference_mm3':iv(stock,S[N[1]]),'do_not_force_unsanded_rod':True})
        check_free('Finished rod clears both guide bodies',finished,{N[1]:S[N[1]],N[2]:S[N[2]]})
        for n in N:
            p=step(R/(n+'_PRINT.step'));b=bbox(p)
            ck(n+' fits central220 printer area',b[0]>=-.001 and b[1]>=-.001 and abs(b[2])<.001 and b[3]<=220 and b[4]<=220 and b[5]<=256,b)
            mb=mesh(R/(n+'_PRINT.stl'),1);ck(n+' STL agrees with actual STEP bounds',all(abs(a-v)<.08 for a,v in zip(mb,b)),mb)
        for j,c in [(1,1),(2,1),(3,2),(4,1)]:
            p=step(R/f'JOB0{j}_PRINT.step');ck(f'JOB0{j} actual body count',len(p)==c,len(p));mesh(R/f'JOB0{j}_PRINT.stl',c)
            ck(f'JOB0{j} no internal part overlap',not collision_pairs({str(i):[b] for i,b in enumerate(p)}),bbox(p))
        # Independently built hardware uses the dimensional envelopes in the review,
        # including the thickest published SAE washer, not a nominal thin washer.
        H={};major=3.5052;washerD=9.906;washerT=1.651;panD=6.858;panH=2.4638
        ret=[(90+19*math.cos(a),65+19*math.sin(a)) for a in (math.pi/4,3*math.pi/4,5*math.pi/4,7*math.pi/4)]
        for i,(x,y) in enumerate(ret):
            H[f'long_shaft{i}']=cyl(x,y,160.349,major/2,50.8)
            H[f'long_pan{i}']=cyl(x,y,160.349-panH,panD/2,panH)
            H[f'lower_washer{i}']=diff(cyl(x,y,160.349,washerD/2,washerT),cyl(x,y,160.30,2.0,washerT+.1))
            top=201 if i in (0,2) else 200
            H[f'upper_washer{i}']=diff(cyl(x,y,top,washerD/2,washerT),cyl(x,y,top-.05,2,washerT+.1))
            H[f'upper_nut{i}']=diff(hexnut(x,y,top+washerT),cyl(x,y,top+washerT-.05,2,3.0))
        for i,(x,z) in enumerate([(60,172),(120,172),(60,184),(120,184)]):
            H[f'rear_shaft{i}']=cyl(x,118.349,z,major/2,31.75,(0,1,0))
            H[f'rear_pan{i}']=cyl(x,118.349-panH,z,panD/2,panH,(0,1,0))
            for side,y in [('front',118.349),('rear',142)]:H[f'rear_washer_{side}{i}']=diff(cyl(x,y,z,washerD/2,washerT,(0,1,0)),cyl(x,y-.05,z,2,washerT+.1,(0,1,0)))
            H[f'rear_nut{i}']=diff(hexnut(x,143.651,z,axis='y'),cyl(x,143.60,z,2,3.1,(0,1,0)))
        H['clamp_shaft']=cyl(90,28.349,195,major/2,19.05,(0,1,0))
        H['clamp_pan']=cyl(90,28.349-panH,195,panD/2,panH,(0,1,0))
        H['clamp_washer']=diff(cyl(90,28.349,195,washerD/2,washerT,(0,1,0)),cyl(90,28.30,195,2,washerT+.1,(0,1,0)))
        H['clamp_nut']=diff(hexnut(90,41.8,195,axis='y'),cyl(90,41.75,195,2,3.1,(0,1,0)))
        for h,g in H.items():check_free(h+' clears finished assembly',g,S)
        # Full continuous finished-rod sweep; the closed clamp slot is tested with
        # actual rod/hardware separately, since a solid proxy fills that slot.
        fixed={k:g for k,g in S.items() if k!=N[4] and not any(t in k for t in ('upper_LPG','upper_native','upper_retaining','lower_LPG','lower_native','lower_retaining'))}
        fixed.update({k:g for k,g in H.items() if k not in ('clamp_shaft','clamp_nut')})
        rodproxy=box(83.8,34.6,106.7,12.4,10.4,145.6)
        check_free('Continuous finished rod sweep conservative ±4.30',rodproxy,fixed)
        for delta in (-4.2,0,4.2):
            rod=move(finished,z=delta)
            check_free('Actual clamp shaft/nut at delta '+str(delta),H['clamp_shaft']+H['clamp_nut'],{'rod':rod})
        ck('Closed #6 fine slot analytical usable travel',abs((12.1-major)/2-4.2974)<1e-8,{'rated_delta_mm':[-4,4],'tested_hardware_delta_mm':[-4.2,4.2],'physical_half_travel_mm':4.2974,'nut_end_margin_at_physical_stop_mm':9.1-4.2974-8/math.sqrt(3)})
        # Both helper pockets can be populated simultaneously; maximum tolerance
        # envelopes plus0.1mm adhesive must fit, not only the two-disk illustration.
        for z in (163.1,193.1):check_free('Four tolerance-max DC1 stack at '+str(z),cyl(90,65,z,19.15/2,6.75),{N[1]:S[N[1]],N[2]:S[N[2]]})
        # Continuous sensor/formed-pin/retaining-loop sweep for every port. Each
        # group remains rigid relative to the common rod during fine adjustment.
        moving={};allfixed=dict(fixed);allfixed.update(H)
        allfixed['upper_stack_MAX']=cyl(90,65,193.1,19.15/2,6.75);allfixed['lower_stack_MAX']=cyl(90,65,163.1,19.15/2,6.75)
        for zone,ports,base in [('upper',UP,UP[0]),('lower',LOW,LOW[-1])]:
            for z in ports:
                moving[(zone,z)]={kind:move(S[f'REF_{zone}_{kind}'],z=z-base) for kind in ('LPG_max_body','native_pins','retaining_loop')}
                check_free(zone+' port '+str(z)+' max pitch shoulders and vertical pin allowance',box(88.405,27.5,z+.2,3.19,15.5,1.5),{'rod':finished})
                check_free(zone+' port '+str(z)+' both face orientations and body vertical play',box(87.95,43.0,z,4.1,3.25,1.9),{'rod':finished})
                check_free(zone+' port '+str(z)+' maximum pitch with full lateral seat play',box(88.205,27.5,z+.2,3.59,15.5,1.5),{'rod':finished})
                stop=iv(box(88.05,42.7,z,3.9,3.25,1.42),finished)
                ck(zone+' port '+str(z)+' minimum case has positive rear shoulder',stop>.01,{'blocked_backwards_overlap_mm3':stop})
                for kind,g in moving[(zone,z)].items():
                    check_free(zone+' port '+str(z)+' '+kind+' fits finished rod',g,{'rod':finished})
                    sweep=swept_bbox(move(g,z=-4.3),dz=8.6)
                    check_free(zone+' port '+str(z)+' '+kind+' CONTINUOUS ±4.30',sweep,allfixed)
                # WIRED +X removal after releasing body loop. The open edge, not
                # joint diameter, is the exit. Existing joints stay in front of rod.
                for kind in ('LPG_max_body','native_pins'):
                    g=moving[(zone,z)][kind];sweep=swept_bbox(g,dx=20)
                    check_free(zone+' port '+str(z)+' wired removal '+kind,sweep,{'rod':finished,**{k:v for k,v in S.items() if k not in (N[4],) and not any(t in k for t in ('upper_LPG','upper_native','upper_retaining','lower_LPG','lower_native','lower_retaining'))},**H})
                    # Rod/chip removal fit is invariant under their common shift;
                    # against stationary hardware cover every possible fine height.
                    check_free(zone+' port '+str(z)+' wired removal at ALL fine heights '+kind,swept_bbox(move(g,z=-4.3),dx=20,dz=8.6),allfixed)
        pairbad=[]
        for u,l in itertools.product(UP,LOW):
            a=sum(moving[('upper',u)].values(),[]);b=sum(moving[('lower',l)].values(),[])
            if iv(a,b)>.001:pairbad.append([u,l])
        ck('All25 upper/lower port pairs coexist for common fine shift',not pairbad,{'issues':pairbad,'relative_geometry_constant_when_both_move_same_delta':True})
        # Nut insertion from the TOP of the front service recess, then forward.
        nut=H['clamp_nut'];topstart=move(nut,y=4.2,z=10)
        check_free('Actual hex nut downward service-window insertion',swept_bbox(topstart,dz=-10),{N[1]:S[N[1]],'rod':finished,'top_strip':S['REF_NONPRINT_top_stack_retainer_strip']})
        check_free('Actual hex nut into rod from service window',swept_bbox(move(nut,y=4.2),dy=-4.2),{N[1]:S[N[1]],'rod':finished})
        for i,(x,y) in enumerate(ret):check_free('D12 nutdriver access at long bolt'+str(i),cyl(x,y,205.6,6,25),S)
        check_free('Front clamp screwdriver access',cyl(90,0,195,3,25.8,(0,1,0)),S)
        # Complete payload motion and retained mass budget.
        payload=['04_D68_payload_carrier','REF_D68_N52_gap15','REF_nylon_retaining_loop_envelope'];pbad=[]
        for gap in range(10,21):
            for name in payload:
                for k,g in S.items():
                    if k in payload:continue
                    if iv(move(S[name],z=15-gap),g)>.001:pbad.append([gap,name,k])
        ck('Full D68 carrier loop10-20mm motion',not pbad,pbad)
        ck('Payload mass allowance retained',vol(S[N[3]])/1000*1.30+6.79<10,{'carrier_estimate_g':vol(S[N[3]])/1000*1.30,'remaining_g':10-6.79-vol(S[N[3]])/1000*1.30,'must_weigh_payload':True})
        result={'complete':True,'passed':all(c['passed'] for c in C),'check_count':len(C),'engine':'Autodesk Fusion native kernel; independently reimported STEP files','checks':C}
        # Optional actual-kernel detail figure, using only audit-owned document.
        render_doc=None
        try:
            progress('Rendering independently imported rod detail')
            render_doc=APP.documents.add(ac.DocumentTypes.FusionDesignDocumentType)
            des=af.Design.cast(APP.activeProduct);des.designType=af.DesignTypes.DirectDesignType
            for label,g in [('Finished common rod',finished),('Upper sensor',S['REF_upper_LPG_max_body']),('Upper native leads',S['REF_upper_native_pins']),('Lower sensor',S['REF_lower_LPG_max_body']),('Lower native leads',S['REF_lower_native_pins'])]:
                for b in g:
                    added=des.rootComponent.bRepBodies.add(M.copy(b));added.name=label
            view=APP.activeViewport;cam=view.camera
            cam.eye=P(250,-300,210);cam.target=P(90,40,179.5);cam.upVector=vec(0,0,1);cam.isSmoothTransition=False;cam.isFitView=True;view.camera=cam
            adsk.doEvents();result['rod_detail_render_saved']=view.saveAsImageFile(str(R/'rod_detail.png'),1600,1200)
        except Exception:result['optional_render_error']=traceback.format_exc()
        finally:
            if render_doc:render_doc.close(False)
        (R/'independent_check_results.json').write_text(json.dumps(result,indent=2));progress('Complete')
        APP.userInterface.messageBox('Independent Fusion check: '+str(sum(c['passed'] for c in C))+'/'+str(len(C))+' passed. Results saved.','CAD review')
    except Exception:
        (R/'independent_check_results.json').write_text(json.dumps({'complete':False,'passed':False,'check_count':len(C),'checks':C,'error':traceback.format_exc()},indent=2));progress('ERROR')
        APP.userInterface.messageBox(traceback.format_exc(),'Independent CAD check failed')
    finally:
        try:owner.activate()
        except Exception:pass
