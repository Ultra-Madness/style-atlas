from pathlib import Path
from html.parser import HTMLParser
import json,base64,hashlib,re,struct
ROOT=Path(__file__).resolve().parents[1]
c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
css=(ROOT/'src/styles.css').read_text(encoding='utf-8')
assert 'html:not(.has-js) .enhanced-only' in css
assert '\n:not(.has-js) .enhanced-only' not in css
class Inspect(HTMLParser):
    def __init__(self):super().__init__();self.cards=[];self.images=[];self.recipes=0;self.defaults=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='article':self.cards.append(a)
        if tag=='img' and a.get('src'):self.images.append(a)
        if tag=='p' and a.get('class')=='recipe':self.recipes+=1
        if tag=='span' and a.get('class')=='defaultbadge':self.defaults+=1
for name in ['index.html','Style-Atlas-Offline.html']:
    content=(ROOT/'site'/name).read_text(encoding='utf-8'); p=Inspect();p.feed(content)
    assert len(p.cards)==29 and p.recipes==29 and p.defaults==1
    assert [a['data-style'] for a in p.cards]==[e['id'] for e in c['entries']]
    for e,a in zip(c['entries'],p.cards):
        assert a['data-job']==e['source']['job_id'] and int(a['data-image-index'])==e['source']['image_index']
        assert e['recipe'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') in content or e['recipe'] in content
    assert len(p.images)==31
    for relative in re.findall(r'(?:href|src)="\./([^"?]+\.(?:css|js))"',content):
        assert (ROOT/'site'/relative).is_file(),relative
        assert re.search(r'\.[a-f0-9]{12}\.',relative),relative
    for image in p.images:
        src=image['src']
        if src.startswith('data:'):assert len(base64.b64decode(src.split(',')[1]))>100
        else:assert (ROOT/'site'/src.removeprefix('./')).is_file(),src
    assert not re.search(r'C:\\Users|AppData|library-file|libfile_|file_0000|sandbox\.',content)
    print(f'PASS {name}: 29 static cards, 29 recipes, 30 reference images plus header mark, default style 8, no local/private paths.')
assert {e['id'] for e in c['entries']}=={f'MJ-S{n:03}' for n in range(1,30)}
assert len({hashlib.sha256((ROOT/e['thumbnail']).read_bytes()).hexdigest() for e in c['entries']})==29
print('PASS: 29 unique thumbnail bytes and stable source mappings; all core content exists without JavaScript.')
icons=json.loads((ROOT/'assets/branding/icons.json').read_text(encoding='utf-8'))
manifest_name='manifest.'+icons['identity']+'.webmanifest'
manifest=json.loads((ROOT/'site'/manifest_name).read_text(encoding='utf-8'))
hosted=(ROOT/'site/index.html').read_text(encoding='utf-8')
assert f'href="./{manifest_name}"' in hosted
assert manifest['start_url']==manifest['scope']==manifest['id']=='/style-atlas/'
assert manifest['display']=='standalone' and manifest['short_name']=='Style Atlas'
assert len(manifest['icons'])==4
for i in manifest['icons']:
    b=(ROOT/'site'/i['src'].removeprefix('./')).read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',b[16:24]); assert i['sizes']==f'{width}x{height}'
    assert width in [192,512] and b[25]==2  # opaque RGB, including the maskable background
    assert icons['identity'] in i['src']
assert icons['maskable_art_radius_fraction']<0.39
apple=(ROOT/'assets/branding'/icons['png']['180']).read_bytes()
assert struct.unpack('>II',apple[16:24])==(180,180)
assert 'rel="apple-touch-icon" sizes="180x180"' in hosted
assert icons['png']['180'] in hosted and icons['svg'] in hosted
ico=(ROOT/'assets/branding'/icons['favicon']).read_bytes()
assert struct.unpack('<HHH',ico[:6])==(0,1,3)
print('PASS: versioned SVG/ICO/favicon, Apple 180, PNG 192/512 and opaque maskable icons; Pages scope and launch URL.')
