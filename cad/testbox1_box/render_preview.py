"""Depth-buffered offscreen preview of the delivered STEP component geometry."""
from pathlib import Path
import json
import cadquery as cq
import vtk

root=Path(__file__).resolve().parent
manifest=json.loads((root/'component_manifest.json').read_text())
colors={'plywood':(.70,.49,.28),'hardwood':(.55,.35,.19),'cast acrylic':(.52,.78,.87),'PETG':(.15,.23,.29),'polycarbonate':(.65,.85,.9),'steel/copper':(.45,.48,.50),'N42':(.74,.76,.79),'hypothetical':(.94,.55,.13),'electronics allowance':(.08,.45,.24)}
renderer=vtk.vtkRenderer();renderer.SetBackground(.96,.975,.985)
renderer.SetUseDepthPeeling(True);renderer.SetMaximumNumberOfPeels(100);renderer.SetOcclusionRatio(.05)
for name,info in manifest.items():
    shape=cq.importers.importStep(str(root/'parts'/(name+'.step'))).val()
    vertices,triangles=shape.tessellate(.08,.15)
    points=vtk.vtkPoints()
    for p in vertices:points.InsertNextPoint(p.x,p.y,p.z)
    cells=vtk.vtkCellArray()
    for tri in triangles:
        cells.InsertNextCell(3)
        for i in tri:cells.InsertCellPoint(i)
    data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(40);normals.ConsistencyOn();normals.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    prop=actor.GetProperty();prop.SetColor(*colors[info['material']]);prop.SetAmbient(.3);prop.SetDiffuse(.7)
    if info['material']=='cast acrylic':prop.SetOpacity(.20)
    elif info['material']=='polycarbonate':prop.SetOpacity(.55)
    renderer.AddActor(actor)

camera=renderer.GetActiveCamera();camera.SetPosition(390,-520,345);camera.SetFocalPoint(90,75,102);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(165)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1400,1400);window.SetAlphaBitPlanes(1);window.SetMultiSamples(0);window.AddRenderer(renderer)
def label(text,x,y,size):
    a=vtk.vtkTextActor();a.SetInput(text);a.SetPosition(x,y)
    a.GetTextProperty().SetColor(.12,.21,.27);a.GetTextProperty().SetFontSize(size)
    renderer.AddActor2D(a)
label('MAGNETIC LEVITATION STAND',45,1320,36)
label('testbox1 box | CAD geometry | millimetres',45,1270,23)
label('180 x 160 x 200 mm | 25 x 20 mm electromagnet',45,80,25)
label('Orange payload and green sensor boards are assumed envelopes.',45,43,20)
label('Bolts and wiring omitted. Prototype requires physical validation.',45,16,20)
window.Render()
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
writer=vtk.vtkPNGWriter();writer.SetFileName(str(root/'assembly_preview.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
window.Finalize()
print('Rendered depth-buffered CAD preview.')
