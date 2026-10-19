"""Generate original geometric branding. Requires Pillow only when artwork changes."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/branding';OUT.mkdir(parents=True,exist_ok=True)
INK='#142D2D'
COLORS=['#F6EACD','#F1B255','#ED6C4F','#5DB6B4','#63808E','#ADB96B']
def point(radius,angle):
    a=math.radians(angle);return (512+radius*math.cos(a),512+radius*math.sin(a))
def blades(radius=344):
    outer=[point(radius,-90+i*60) for i in range(6)]
    inner=[point(135,-60+i*60) for i in range(6)]
    return [[outer[i],outer[(i+1)%6],inner[(i+1)%6],inner[i]] for i in range(6)]
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" role="img" aria-labelledby="title"><title id="title">Style Atlas color aperture</title><rect width="1024" height="1024" fill="'+INK+'"/>'
for pts,color in zip(blades(),COLORS):
    svg+='<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'" fill="'+color+'" stroke="'+INK+'" stroke-width="12" stroke-linejoin="round"/>'
svg+='</svg>\n'
identity=hashlib.sha256(svg.encode()).hexdigest()[:12]
prefix='style-atlas.'+identity
(OUT/(prefix+'.svg')).write_text(svg,encoding='utf-8')
def raster(radius=344):
    scale=4;im=Image.new('RGB',(4096,4096),INK);d=ImageDraw.Draw(im)
    for points,color in zip(blades(radius),COLORS):
        points=[(round(x*scale),round(y*scale)) for x,y in points]
        d.polygon(points,fill=color);d.line(points+[points[0]],fill=INK,width=12*scale,joint='curve')
    return im
master=raster(); files={}
for size in [16,32,180,192,512]:
    name=f'{prefix}.{size}.png';master.resize((size,size),Image.Resampling.LANCZOS).save(OUT/name,optimize=True);files[str(size)]=name
master.resize((256,256),Image.Resampling.LANCZOS).save(OUT/(prefix+'.ico'),format='ICO',sizes=[(16,16),(32,32),(48,48)])
masked=raster(312)
for size in [192,512]:
    name=f'{prefix}.maskable-{size}.png';masked.resize((size,size),Image.Resampling.LANCZOS).save(OUT/name,optimize=True);files['maskable-'+str(size)]=name
meta={'identity':identity,'background':INK,'svg':prefix+'.svg','favicon':prefix+'.ico','png':files,'maskable_art_radius_fraction':312/1024,'description':'Six contrasting swatches form a rotating aperture around a deep-ink hexagonal opening. Original vector artwork; no reference image is used.'}
(OUT/'icons.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta,indent=2))
