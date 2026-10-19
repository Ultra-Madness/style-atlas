const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {matches,select}=require('../src/app.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/catalog.json'),'utf8'));
assert.equal(data.entries.length,29);
assert.equal(data.default_style_id,'MJ-S008');
for(const entry of data.entries){
  for(const query of [String(entry.number),`style ${entry.number}`,entry.id,entry.name]) assert.equal(select(data.entries,'all',query)[0].id,entry.id);
}
for(const family of data.families) assert.deepEqual(select(data.entries,family.id,'').map(e=>e.id).sort(),family.members.slice().sort());
assert.equal(select(data.entries,'all','zzzz-nothing').length,0);
assert(select(data.entries,'all','olive').some(e=>e.id==='MJ-S008'));
assert.equal(select(data.entries,'all','').length,29);
assert.equal(matches(data.entries[0],'style 17'),false);
assert.equal(data.entries[20].source.job_id,'7bf6accf-ed7e-4fee-a9d7-a0ad7a65fdbe');
assert.equal(data.entries[21].source.job_id,'08cd8759-143c-4623-8eca-c56f0250436a');
console.log('PASS: all 29 IDs/names/numbers, 7 filters, empty/reset selection, default 8, corrected S021/S022.');
