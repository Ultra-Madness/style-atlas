from pathlib import Path
import json,html,base64,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site';OUT.mkdir(exist_ok=True)
CAT=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
ICONS=json.loads((ROOT/'assets/branding/icons.json').read_text(encoding='utf-8'))
MANIFEST_NAME='manifest.'+ICONS['identity']+'.webmanifest'
APP_BASE='/style-atlas/'
esc=lambda s:html.escape(str(s),quote=True)
labels={'F1':'Editorial & documentary','F2':'Cinematic atmosphere','F3':'Precision realism','F4':'Line, print & optical','F5':'Painterly & luminous','F6':'Anime & concept','F7':'Tactile 3D'}
def instruction(e):return f"Use style {e['number']} - {e['id']} {e['name']} - for [NEW SUBJECT], adapted to [FORMAT]. Apply this rendering recipe with a fresh subject and composition: {e['recipe']}"
def render(offline=False):
    entries=CAT['entries'];default=next(e for e in entries if e['id']==CAT['default_style_id'])
    def image(e):
        if offline:return 'data:image/jpeg;base64,'+base64.b64encode((ROOT/e['thumbnail']).read_bytes()).decode('ascii')
        return './'+e['thumbnail']
    filters='<button type="button" class="filter" data-family="all" aria-pressed="true">All styles <span>29</span></button>'
    filters+=''.join(f'<button type="button" class="filter" data-family="{f["id"]}" aria-pressed="false">{esc(labels[f["id"]])}<span>{len(f["members"])}</span></button>' for f in CAT['families'])
    cards=[]
    for e in entries:
        f=next(f for f in CAT['families'] if f['id']==e['family_id']);s=e['source'];isdefault=e['id']==default['id']
        details=''.join(f'<dt>{key}</dt><dd>{esc(e[field])}</dd>' for key,field in [('Lighting','lighting'),('Palette','palette'),('Contrast','contrast'),('Texture / material','texture'),('Composition','composition'),('Treatment','treatment'),('Individual distinction','distinction')])
        cards.append(f'''<article class="card{' is-default' if isdefault else ''}" id="{e['id']}" data-style="{e['id']}" data-family="{e['family_id']}" data-job="{s['job_id']}" data-image-index="{s['image_index']}">
<div class="reference"><img src="{image(e)}" alt="Source reference for style {e['number']}: {esc(e['name'])}" width="520" height="680" decoding="async" loading="eager"><span class="refmark">SOURCE REFERENCE</span><button type="button" class="expand enhanced-only" data-view="{e['id']}" aria-label="Enlarge reference for style {e['number']}">Enlarge</button></div>
<div class="body"><div class="titleline"><span class="number">{e['number']:02d}</span><div><h2 class="name">{esc(e['name'])}</h2><div class="id">{e['id']}</div>{'<span class="defaultbadge">CURRENT DEFAULT</span>' if isdefault else ''}</div></div>
<p class="family">{esc(f['name'])}</p><p class="cues">{esc(' / '.join(e['tags']))}</p>
<button type="button" class="copy enhanced-only" data-copy="{e['id']}" aria-label="Copy style instruction for style {e['number']}">Copy style instruction</button>
<p class="source">Reference: {esc(s['creator'])} (observed creator label) / <a href="{esc(s['source_url'])}" target="_blank" rel="noopener noreferrer">View original source</a></p>
<details><summary>Recipe &amp; style details</summary><p class="recipe">{esc(e['recipe'])}</p><dl class="detailgrid">{details}</dl><p class="caution">{esc(e['confidence'])}</p><label>Style instruction<textarea class="instructionbox" readonly aria-label="Style instruction {e['number']}">{esc(instruction(e))}</textarea></label></details>
<div class="manualcopy" hidden><p class="caution">Copy permission is unavailable here. Long-press or select this instruction:</p><textarea class="instructionbox" readonly aria-label="Manual copy instruction {e['number']}">{esc(instruction(e))}</textarea></div></div></article>''')
    data={'version':CAT['version'],'default_style_id':CAT['default_style_id'],'families':CAT['families'],'entries':[{**e,'instruction':instruction(e)} for e in entries]}
    jsondata=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    css=(ROOT/'src/styles.css').read_text(encoding='utf-8');js=(ROOT/'src/app.js').read_text(encoding='utf-8')
    cssname='styles.'+hashlib.sha256(css.encode()).hexdigest()[:12]+'.css'
    jsname='app.'+hashlib.sha256(js.encode()).hexdigest()[:12]+'.js'
    stylesheet='<style>'+css+'</style>' if offline else f'<link rel="stylesheet" href="./{cssname}">'
    script='<script>'+js+'</script>' if offline else f'<script defer src="./{jsname}"></script>'
    policy="default-src 'none'; img-src data:; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; object-src 'none'" if offline else "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; base-uri 'none'; object-src 'none'"
    def branding_url(name,mime):
        if offline:return 'data:'+mime+';base64,'+base64.b64encode((ROOT/'assets/branding'/name).read_bytes()).decode('ascii')
        return './assets/branding/'+name
    logo=branding_url(ICONS['svg'],'image/svg+xml')
    icon_meta=f'<link rel="icon" href="{branding_url(ICONS["favicon"],"image/x-icon")}" sizes="16x16 32x32 48x48"><link rel="icon" type="image/png" sizes="32x32" href="{branding_url(ICONS["png"]["32"],"image/png")}"><link rel="icon" type="image/svg+xml" sizes="any" href="{logo}"><link rel="apple-touch-icon" sizes="180x180" href="{branding_url(ICONS["png"]["180"],"image/png")}"><meta name="apple-mobile-web-app-title" content="Style Atlas"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="application-name" content="Style Atlas">'
    if not offline:icon_meta+=f'<link rel="manifest" href="./{MANIFEST_NAME}">'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="{ICONS['background']}"><meta name="description" content="Browse 29 visual reference styles by picture and number. Current default: Style 8 Olive Kitchen Chronicle."><meta http-equiv="Content-Security-Policy" content="{policy}"><title>Style Atlas / 29 visual references</title>{icon_meta}{stylesheet}</head><body>
<header><div class="mast"><span class="mast-brand"><img src="{logo}" alt="" aria-hidden="true" width="28" height="28">STYLE ATLAS / BATCH 01</span><a href="#gallery">29 visual references</a></div><div class="intro"><div><p class="eyebrow">A CREATIVE REFERENCE LIBRARY</p><h1>Choose by eye.<br>Call by <em>number.</em></h1></div><p class="lede">Find a look you like, then say <strong>use style 17.</strong> Each reference has a recipe for a fresh subject. Pictures and recipes are available even without scripts.</p></div>
<a class="defaultbar" href="#{default['id']}" aria-label="Go to current default style 8"><img src="{image(default)}" alt="Current default style 8 reference" width="54" height="66"><span><small>Current default / Style 08</small><strong>Olive Kitchen Chronicle</strong></span><span>View default &darr;</span></a></header>
<main><section class="controls enhanced-only" aria-label="Find a style"><div class="searchrow"><label class="searchbox"><input id="search" type="search" aria-label="Search styles" placeholder="Number, name, color or mood..." autocomplete="off"></label><button type="button" class="reset" id="reset">Reset filters</button></div><div class="filters" id="filters" aria-label="Style families">{filters}</div></section>
<noscript><p class="previewnote">All 29 references and recipes are shown below. Open this page in Safari or Chrome to use search, filters and copy buttons.</p></noscript>
<div class="resultsbar"><p id="count" role="status" aria-live="polite">29 of 29 styles</p><p>Original reference thumbnails / 7 families</p></div><section class="grid" id="gallery" aria-label="Visual style gallery">{''.join(cards)}</section><section id="empty" hidden><h2>No styles found.</h2><p>Try a number from 1-29 or clear the filters.</p><button type="button" class="reset" id="emptyreset">Show all styles</button></section></main>
<footer><div class="footerline"><strong>29 / MIDJOURNEY STYLE REFERENCES</strong><span>Version {CAT['version']} / Observed 19 October 2026</span></div><p>Original source images are included as clearly labeled reference thumbnails. Creator labels and links were observed in the source feed; no ownership of reference imagery is claimed. Recipes describe rendering traits for new subjects. Lighting, camera, medium and material descriptions are visual inferences, not known metadata.</p><p><a href="./Style-Atlas-Offline.html" download>Download the offline gallery</a> / <a href="./catalog.json" download>Download style data</a></p></footer>
<dialog id="viewer"><div class="dialoghead"><h2 id="viewtitle"></h2><button type="button" class="close" id="close" aria-label="Close enlarged reference">&times;</button></div><img class="dialogimage" id="viewimage" alt=""><p class="dialogfoot" id="viewsource"></p></dialog><div class="toast" id="toast" role="status" aria-live="polite"></div><script id="catalog-data" type="application/json">{jsondata}</script>{script}</body></html>'''
def build():
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    manifest={'id':APP_BASE,'name':'Style Atlas - Visual Library','short_name':'Style Atlas','description':'29 visual styles, references and reusable prompt recipes.','lang':'en','start_url':APP_BASE,'scope':APP_BASE,'display':'standalone','background_color':ICONS['background'],'theme_color':ICONS['background'],'icons':[]}
    for size in [192,512]:
        for purpose in ['any','maskable']:
            key=str(size) if purpose=='any' else 'maskable-'+str(size)
            manifest['icons'].append({'src':'./assets/branding/'+ICONS['png'][key],'sizes':f'{size}x{size}','type':'image/png','purpose':purpose})
    (OUT/MANIFEST_NAME).write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    for name in ['styles.css','app.js']:
        content=(ROOT/'src'/name).read_text(encoding='utf-8').encode('utf-8'); stem,suffix=name.rsplit('.',1)
        (OUT/(stem+'.'+hashlib.sha256(content).hexdigest()[:12]+'.'+suffix)).write_bytes(content)
    (OUT/'catalog.json').write_text(json.dumps(CAT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'index.html').write_text(render(),encoding='utf-8')
    (OUT/'Style-Atlas-Offline.html').write_text(render(True),encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    print(json.dumps({'version':CAT['version'],'cards':len(CAT['entries']),'default':CAT['default_style_id'],'output':'site'}))
if __name__=='__main__':build()
