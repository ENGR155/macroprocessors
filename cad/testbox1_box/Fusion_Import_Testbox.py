"""Fusion 360 script: import the audited STEP into a NEW document, then save local F3D.
Run in Utilities > Add-Ins > Scripts and Add-Ins. Autodesk API execution not tested here.
"""
import adsk.core,adsk.fusion,traceback,os,json
def run(context):
    app=adsk.core.Application.get();ui=app.userInterface
    try:
        here=os.path.dirname(os.path.abspath(__file__))
        path=os.path.join(here,'testbox1_box_maglev.step')
        if not os.path.isfile(path):raise RuntimeError('Keep this script beside testbox1_box_maglev.step.')
        manager=app.importManager
        options=manager.createSTEPImportOptions(path)
        # Creating a new document protects every already-open design.
        doc=manager.importToNewDocument(options)
        design=adsk.fusion.Design.cast(app.activeProduct)
        if not design:raise RuntimeError('Imported document is not a Fusion design.')
        design.rootComponent.name='testbox1_box_maglev'
        params=json.load(open(os.path.join(here,'parameters.json')))
        # Reference parameters document envelope; imported BReps are not linked to them.
        for name,value in params.items():
            design.userParameters.add('REF_'+name,adsk.core.ValueInput.createByString(str(value)+' mm'),'mm','Reference only; change source generator to rebuild geometry.')
        export=design.exportManager
        target=os.path.join(here,'testbox1_box_maglev.f3d')
        export.execute(export.createFusionArchiveExportOptions(target))
        app.activeViewport.fit()
        ui.messageBox('Imported STEP into a new design and saved local F3D:\n'+target+'\n\nUse Save to choose your testbox1 box cloud folder. Reference bodies include illustrative payload and Hall allowances; hide these before fabrication.')
    except:
        ui.messageBox('Import stopped:\n'+traceback.format_exc())
