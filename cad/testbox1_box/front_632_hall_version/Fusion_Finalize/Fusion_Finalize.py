"""Save the verified active assembly, without modifying its geometry."""
from pathlib import Path
import adsk.core,adsk.fusion,json,traceback,re
R=Path(__file__).resolve().parent.parent

def run(context):
    app=adsk.core.Application.get();out={}
    try:
        audit=json.loads((R/'independent_check_results.json').read_text())
        assert audit.get('complete') and audit.get('passed'),'Final exported-file audit must pass before save.'
        doc=app.activeDocument;des=adsk.fusion.Design.cast(app.activeProduct)
        names=[des.rootComponent.occurrences.item(i).component.name for i in range(des.rootComponent.occurrences.count)]
        assert all(any(n.startswith(p) for n in names) for p in ('01_frame','02_head','03_cassette','04_D68','05_common')),'Active document is not the complete assembly.'
        def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
        matches=[];seen=set();visited=0
        def scan(folder,path,depth=0):
            nonlocal visited
            if folder.id in seen or visited>=250 or depth>5:return
            seen.add(folder.id);visited+=1
            if norm(folder.name) in ('testbox1box','testbox1'):
                matches.append((folder,path))
                return
            subs=folder.dataFolders
            for i in range(subs.count):
                f=subs.item(i);scan(f,path+'/'+f.name,depth+1)
        projects=app.data.dataProjects
        for i in range(projects.count):
            p=projects.item(i);scan(p.rootFolder,p.name)
        out['matching_folder_paths']=[p for f,p in matches]
        if len(matches)==1:
            folder,path=matches[0];name='testbox1_front_632_hall_assembly'
            existing=folder.dataFiles
            if any(existing.item(i).name==name for i in range(existing.count)):name+='_2026-11-14'
            out['cloud_save_accepted']=doc.saveAs(name,folder,'Front common Hall rod; #6-32 hardware; open wired sensor seats; dual magnet pockets. Exported CAD checks passed.','')
            out['cloud_folder']=path;out['design_name']=name
            if doc.dataFile:
                out['data_file_id']=doc.dataFile.id
                try:out['web_url']=doc.dataFile.webURL
                except Exception:pass
        else:
            out['cloud_save_accepted']=False
            out['reason']='The requested folder was not uniquely found; local native Fusion archive remains available.'
        export=des.exportManager.createFusionArchiveExportOptions(str(R/'testbox1_front_632_hall_assembly.f3d'))
        out['local_archive_saved']=des.exportManager.execute(export)
        (R/'fusion_save_result.json').write_text(json.dumps(out,indent=2))
        app.userInterface.messageBox('Verified assembly saved.\n'+(out.get('cloud_folder') or out.get('reason')),'Final CAD save')
    except Exception:
        out['error']=traceback.format_exc();(R/'fusion_save_result.json').write_text(json.dumps(out,indent=2))
        app.userInterface.messageBox(traceback.format_exc(),'CAD save result')
