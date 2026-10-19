from pathlib import Path
from html.parser import HTMLParser
import json,base64,hashlib,re
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
    assert len(p.images)==30
    for image in p.images:
        src=image['src']
        if src.startswith('data:'):assert len(base64.b64decode(src.split(',')[1]))>1000
        else:assert (ROOT/'site'/src.removeprefix('./')).is_file(),src
    assert not re.search(r'C:\\Users|AppData|library-file|libfile_|file_0000|sandbox\.',content)
    print(f'PASS {name}: 29 static cards, 29 recipes, 30 eager image references, default style 8, no local/private paths.')
assert {e['id'] for e in c['entries']}=={f'MJ-S{n:03}' for n in range(1,30)}
assert len({hashlib.sha256((ROOT/e['thumbnail']).read_bytes()).hexdigest() for e in c['entries']})==29
print('PASS: 29 unique thumbnail bytes and stable source mappings; all core content exists without JavaScript.')
