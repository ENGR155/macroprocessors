"""Render exported BRep meshes and dimensioned orthographic views, not concept art."""
from pathlib import Path
import json
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'component_manifest.json').read_text())
COLORS={'plywood':'#ba8d56','hardwood':'#997044','cast acrylic':'#a2d9e7','PETG':'#344c60','polycarbonate':'#b6e1e6','steel/copper':'#818a91','N42':'#c6cdd3','hypothetical':'#e6a343','electronics allowance':'#287f57'}
data=[]
for name,m in M.items():
    s=cq.importers.importStep(str(ROOT/'parts'/(name+'.step'))).val()
    vs,ts=s.tessellate(.15,.25)
    vs=np.array([[v.x,v.y,v.z] for v in vs]); triangles=np.array([vs[list(t)] for t in ts])
    data.append((name,m,triangles))
fig=plt.figure(figsize=(11,10),facecolor='#f5f8fa');ax=fig.add_subplot(111,projection='3d')
all_triangles=[];all_colors=[]
for name,m,t in data:
    alpha=.23 if m['material']=='cast acrylic' else .5 if m['material']=='polycarbonate' else 1
    all_triangles.extend(t);all_colors.extend([matplotlib.colors.to_rgba(COLORS[m['material']],alpha)]*len(t))
ax.add_collection3d(Poly3DCollection(all_triangles,facecolors=all_colors,edgecolors=all_colors,linewidths=0,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=290,altdeg=45),zsort='average'))
ax.set_xlim(0,180);ax.set_ylim(0,160);ax.set_zlim(0,210);ax.set_box_aspect((180,160,210));ax.view_init(19,-64);ax.set_axis_off()
fig.text(.07,.94,'MAGNETIC LEVITATION STAND',fontsize=23,weight='bold',color='#203545')
fig.text(.07,.905,'testbox1 box  |  exported CAD geometry  |  millimetres',fontsize=12,color='#536674')
fig.text(.07,.075,'180 × 160 × 200 mm overall • 25 × 20 mm electromagnet\nRemovable helper cassette • two Hall carriers • protective stop • catch tray',fontsize=12,color='#203545')
fig.text(.07,.025,'Orange payload is an assumed envelope. Screws, wiring and course boards are not modeled. Mechanical prototype; levitation requires bench validation.',fontsize=8,color='#536674')
fig.savefig(ROOT/'assembly_preview.png',dpi=170,bbox_inches='tight');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(13,10),facecolor='white')
def dim(ax,a,b,text,offset=0):
    ax.annotate('',xy=a,xytext=b,arrowprops={'arrowstyle':'<->','lw':.8,'color':'#1a506b'})
    x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
    ax.text(x+2,y+2,text,fontsize=9,color='#1a506b',rotation=90 if abs(a[0]-b[0])<.1 else 0,ha='left',va='bottom')
for ax,axes,title in zip(axs,[(0,2,1),(1,2,0)],['FRONT • X / Z','SIDE • Y / Z']):
    u,v,depth=axes
    faces=[]
    for name,m,tri in data:
        if name=='REF_upper_Hall_allowance' or m['material']=='cast acrylic': alpha=.25
        else:alpha=1
        for t in tri:faces.append((t[:,depth].mean(),t[:,[u,v]],COLORS[m['material']],alpha))
    faces.sort(key=lambda x:x[0],reverse=True)
    for _,t,c,a in faces:ax.add_collection(PolyCollection([t],facecolors=c,edgecolors='none',alpha=a))
    ax.set_aspect('equal');ax.set_xlim(-20,220);ax.set_ylim(-15,220);ax.set_axis_off();ax.set_title(title,loc='left',fontsize=14,weight='bold')
dim(axs[0],(0,-5),(180,-5),'180')
dim(axs[0],(195,0),(195,200),'200 overall')
dim(axs[0],(45,210),(135,210),'90 panel width')
dim(axs[1],(0,-5),(160,-5),'160')
dim(axs[1],(145,18),(145,190),'172 upright')
dim(axs[1],(39,208),(136,208),'97 cantilever')
axs[1].plot([20,65],[170,170],color='#b34b31',lw=.7);axs[1].plot([20,65],[160,160],color='#b34b31',lw=.7);axs[1].plot([20,65],[150,150],color='#b34b31',lw=.7)
axs[1].annotate('EM face Z170\n10–20 surface gap\npayload top Z160–150',xy=(30,160),xytext=(-10,116),fontsize=8,color='#b34b31',arrowprops={'arrowstyle':'->','color':'#b34b31'})
fig.suptitle('TESTBOX1 BOX • ASSEMBLY DIMENSIONS',x=.07,ha='left',fontsize=20,weight='bold')
fig.text(.07,.10,'All dimensions mm. CAD-derived projections. Base 18 thick; clear sheets 6 thick. EM bore25.6; helper pocket Ø19.6 × 1.9 deep.',fontsize=10)
fig.text(.07,.075,'Guard underside Z162: 2mm nominal clearance to payload at10mm gap. Helper modeled Z168.1: helper-to-payload gap8.1–18.1mm.',fontsize=10)
fig.text(.07,.05,'ASSUMED payload Ø12.7 × 6 shown at15mm surface gap. Confirm purchased payload and Hall package before fabrication.',fontsize=10)
fig.savefig(ROOT/'dimensioned_assembly.png',dpi=180,bbox_inches='tight');fig.savefig(ROOT/'dimensioned_assembly.pdf',bbox_inches='tight')
print('Created CAD-derived preview and dimensioned PNG/PDF.')


