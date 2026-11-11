"""Derive a print-oriented all-polymer frame from the audited fabrication solids."""
from pathlib import Path
import json,itertools
import cadquery as cq

HERE=Path(__file__).resolve().parent
OUT=HERE/'printed_version';PARTS=OUT/'parts';PARTS.mkdir(parents=True,exist_ok=True)
manifest=json.loads((HERE/'component_manifest.json').read_text())
fabricated=[n for n,m in manifest.items() if m['kind']=='fabricate']
assembly=cq.Assembly(name='testbox1_box_printable')
report={}

def orient_flat(shape):
    # Six orthogonal orientations; choose the largest broad face flat and bed minimum Z=0.
    choices=[]
    for rx,ry,rz in itertools.product((0,90,180,270),repeat=3):
        s=shape.rotate((0,0,0),(1,0,0),rx).rotate((0,0,0),(0,1,0),ry).rotate((0,0,0),(0,0,1),rz)
        b=s.BoundingBox();dims=[b.xlen,b.ylen,b.zlen]
        if dims[0]<=220 and dims[1]<=220:
            choices.append((dims[0]*dims[1],max(dims[0],dims[1]),s,dims))
    if not choices:raise RuntimeError('Part exceeds assumed 220x220 mm print bed')
    _,_,s,dims=min(choices,key=lambda q:(q[0],q[1]))
    b=s.BoundingBox();s=s.translate((-b.xmin-dims[0]/2,-b.ymin-dims[1]/2,-b.zmin))
    return s,dims

for name in fabricated:
    shape=cq.importers.importStep(str(HERE/'parts'/(name+'.step'))).val()
    flat,dims=orient_flat(shape)
    assert flat.isValid() and len(flat.Solids())==1
    cq.exporters.export(flat,str(PARTS/(name+'.stl')),tolerance=.06,angularTolerance=.15)
    cq.exporters.export(flat,str(PARTS/(name+'.step')))
    assembly.add(shape,name=name,color=cq.Color(.66,.47,.29) if 'base' in name or 'clamp' in name else cq.Color(.18,.31,.43))
    report[name]={'material':'PETG','bed_oriented_size_mm':[round(x,3) for x in dims],'bed_clearance_assumed_mm':220,'valid_single_solid':True}
assembly.export(str(OUT/'testbox1_box_printable.step'))
(OUT/'print_manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'print_parts':len(report),'assembly':str(OUT/'testbox1_box_printable.step'),'all_flat_bed_parts_fit_220mm':True},indent=2))
