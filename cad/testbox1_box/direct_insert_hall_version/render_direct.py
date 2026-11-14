"""Depth-buffered offscreen preview of the delivered STEP component geometry."""
from pathlib import Path
import json
import cadquery as cq
import vtk

root=Path(__file__).resolve().parent
manifest=json.loads((root/'component_manifest.json').read_text())
for i,info in enumerate(manifest.values()): info['material']='PRINT_'+str(i)
for path in root.glob('REF_*.step'):
    manifest[path.stem]={'material':'hypothetical' if 'D68' in path.stem else 'electronics allowance' if 'LPG' in path.stem else 'steel/copper'}
colors={'plywood':(.70,.49,.28),'hardwood':(.55,.35,.19),'cast acrylic':(.52,.78,.87),'PETG':(.15,.23,.29),'polycarbonate':(.65,.85,.9),'steel/copper':(.45,.48,.50),'N42':(.74,.76,.79),'hypothetical':(.94,.55,.13),'electronics allowance':(.08,.45,.24)}
colors.update({'PRINT_0':(.38,.55,.65),'PRINT_1':(.60,.77,.83),'PRINT_2':(.83,.56,.25),'PRINT_3':(.68,.32,.16),'PRINT_4':(.28,.52,.38)})
renderer=vtk.vtkRenderer();renderer.SetBackground(.96,.975,.985)
renderer.SetUseDepthPeeling(True);renderer.SetMaximumNumberOfPeels(100);renderer.SetOcclusionRatio(.05)
for name,info in manifest.items():
    shape=cq.importers.importStep(str(root/(name+'.step' if name.startswith('REF_') else name+'_assembled.step'))).val()
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

camera=renderer.GetActiveCamera();camera.SetPosition(430,-570,410);camera.SetFocalPoint(103,75,122);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(185)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1400,1400);window.SetAlphaBitPlanes(1);window.SetMultiSamples(0);window.AddRenderer(renderer)
def label(text,x,y,size):
    a=vtk.vtkTextActor();a.SetInput(text);a.SetPosition(x,y)
    a.GetTextProperty().SetColor(.12,.21,.27);a.GetTextProperty().SetFontSize(size)
    renderer.AddActor2D(a)
label('ONE-PIECE DIRECT-INSERTION HALL ROD',45,1320,36)
label('One common printed holder | both sensors move together',45,1270,23)
label('Sensors insert through the rod; native leads exit the opposite side',45,80,25)
label('One holder on JOB04; matching guides in revised JOB02 and JOB03.',45,43,20)
label('Coil temperature, field range and stable levitation still need measurement.',45,16,20)
window.Render()
capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
writer=vtk.vtkPNGWriter();writer.SetFileName(str(root/'assembly_preview.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
window.Finalize()
print('Rendered depth-buffered CAD preview.')
