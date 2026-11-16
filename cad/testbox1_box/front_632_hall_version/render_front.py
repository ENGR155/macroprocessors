"""Render the delivered STEP geometry for visual inspection."""
from pathlib import Path
import json
import cadquery as cq
import vtk

R = Path(__file__).resolve().parent

def render(detail=False):
    manifest=json.loads((R/'component_manifest.json').read_text())
    entries=[(n,R/(n+'_assembled.step'),i) for i,n in enumerate(manifest)]
    entries += [(p.stem,p,5) for p in R.glob('REF_*.step')]
    ren=vtk.vtkRenderer(); ren.SetBackground(.96,.975,.985)
    palette=[(.38,.55,.65),(.60,.77,.83),(.83,.56,.25),(.68,.32,.16),(.28,.52,.38)]
    rod_bounds=None
    for n,p,i in entries:
        is_sensor=any(t in n.lower() for t in ('lpg','sensor_body','hall_body','native_pin','wire','solder'))
        if detail and not (n.startswith('05') or is_sensor): continue
        s=cq.importers.importStep(str(p)).val()
        if n.startswith('05'): rod_bounds=s.BoundingBox()
        pts,tris=s.tessellate(.07,.12)
        vp=vtk.vtkPoints()
        for v in pts:vp.InsertNextPoint(v.x,v.y,v.z)
        cells=vtk.vtkCellArray()
        for tri in tris:
            cells.InsertNextCell(3)
            for j in tri:cells.InsertCellPoint(j)
        poly=vtk.vtkPolyData();poly.SetPoints(vp);poly.SetPolys(cells)
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(40);normals.ConsistencyOn();normals.AutoOrientNormalsOn()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        color=palette[i] if i<5 else (.82,.18,.12) if any(t in n.lower() for t in ('lpg','sensor_body','hall_body')) else (.45,.48,.50)
        actor.GetProperty().SetColor(*color);actor.GetProperty().SetAmbient(.3);actor.GetProperty().SetDiffuse(.7)
        ren.AddActor(actor)
    cam=ren.GetActiveCamera();cam.SetViewUp(0,0,1);cam.ParallelProjectionOn()
    if detail:
        b=rod_bounds;cx=(b.xmin+b.xmax)/2;cy=(b.ymin+b.ymax)/2;cz=(b.zmin+b.zmax)/2
        cam.SetPosition(cx+140,cy+290,cz+50);cam.SetFocalPoint(cx,cy,cz);cam.SetParallelScale(87)
    else:
        cam.SetPosition(410,-590,390);cam.SetFocalPoint(95,75,122);cam.SetParallelScale(180)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1400,1400);win.SetMultiSamples(0);win.AddRenderer(ren)
    def label(t,x,y,size):
        a=vtk.vtkTextActor();a.SetInput(t);a.SetPosition(x,y);a.GetTextProperty().SetColor(.12,.21,.27);a.GetTextProperty().SetFontSize(size);ren.AddActor2D(a)
    label('FRONT HALL HOLDER / #6-32 HARDWARE',45,1320,34)
    label('One common rod | both sensors move vertically together',45,1270,23)
    label('Open-sided seats release the sensor and attached soldered wires.' if detail else 'Front = open approach opposite the upright.',45,75,24)
    label('Rod includes sanding stock; fit its bearing faces before assembly.' if detail else 'Both helper-magnet pockets available; shown allocation is not magnetic validation.',45,40,20)
    label('Delivered CAD geometry. Print fit, temperature and sensor headroom require measurement.',45,13,18)
    win.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(R/('rod_detail.png' if detail else 'assembly_preview.png')));writer.SetInputConnection(capture.GetOutputPort());writer.Write();win.Finalize()

if __name__=='__main__':
    render();render(True)
    print('Rendered assembly and common rod from delivered STEP files.')
