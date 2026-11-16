"""Package only after the actual native build and both exported-file reviews pass."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parent

def main():
    native=json.loads((R/'native_build_result.json').read_text())
    audit=json.loads((R/'independent_check_results.json').read_text())
    mesh=json.loads((R/'primary_mesh_review.json').read_text())
    assert native.get('completed') and audit.get('complete') and audit.get('passed') and mesh.get('passed'), 'Release blocked: actual build and reviews must pass.'
    for p in ('testbox1_front_632_hall_assembly.f3d','testbox1_front_632_hall_assembly.step','JOB02_PRINT.stl','JOB03_PRINT.stl','JOB04_PRINT.stl','README.md','INDEPENDENT_REVIEW.md'):
        assert (R/p).is_file() and (R/p).stat().st_size>0,p
    excluded={'native_build_error.txt','fusion_boolean_probe_ERROR.txt','package_manifest.json'}
    paths=sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'Fusion_Finalize' not in p.parts and p.name not in excluded and p.suffix not in ('.pyc','.zip'))
    manifest={'revision':'front_632_hall_version','native_build_completed':True,'independent_checks_passed':audit['check_count'],'primary_mesh_review_passed':True,'files':{str(p.relative_to(R)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}}
    (R/'package_manifest.json').write_text(json.dumps(manifest,indent=2))
    target=R.with_suffix('.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in paths+[R/'package_manifest.json']:z.write(p,R.name+'/'+str(p.relative_to(R)).replace('\\','/'))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        actual=set(z.namelist());wanted={R.name+'/'+str(p.relative_to(R)).replace('\\','/') for p in paths+[R/'package_manifest.json']}
        assert actual==wanted
    print(json.dumps({'release':str(target),'bytes':target.stat().st_size,'files':len(paths)+1,'verified_zip_crc':True,'independent_checks':audit['check_count']},indent=2))

if __name__=='__main__':main()
