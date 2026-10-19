"""Build local neural narration assets; the deployed app needs no TTS credentials."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path

import edge_tts
from mutagen.mp3 import MP3

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.voice-cache'
OUT=ROOT/'dist/audio'
VOICES={'en-GB':{'name':'Sonia','voice':'en-GB-SoniaNeural'},'en-US':{'name':'Ava','voice':'en-US-AvaMultilingualNeural'}}

def normalize(text):return ' '.join(text.split()).lower()

async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    course=json.loads((ROOT/'dist/course.js').read_text().removeprefix('window.COURSE = ').rstrip(';\n'))
    texts={}
    for l in course:
        texts[normalize(l['sentence'])]={'text':l['sentence'],'kind':'sentence'}
        for w in l['words']:texts.setdefault(normalize(w['word']),{'text':w['word'],'kind':'word'})
        for token,g in l['glosses'].items():texts.setdefault(normalize(g['lemma']),{'text':g['lemma'],'kind':'word'})
    sample='A little progress, at your own pace.'
    texts[normalize(sample)]={'text':sample,'kind':'sample'}
    # Full sentences first, then core vocabulary, followed by the full lookup vocabulary.
    core={normalize(w['word']) for l in course for w in l['words'] if w['core']}
    ordered=sorted(texts.items(),key=lambda item:(0 if item[1]['kind']=='sentence' else 1 if item[0] in core else 2,item[0]))
    if args.limit:ordered=ordered[:args.limit]
    CACHE.mkdir(exist_ok=True)
    manifest={'version':2,'voices':VOICES,'clips':{}}
    jobs=[]
    for key,item in ordered:
        for lang in VOICES:
            for mode in (['natural','slow'] if item['kind']=='sentence' else ['natural']):
                jobs.append((key,item,lang,mode))
    sem=asyncio.Semaphore(4);done=0
    async def generate(job):
        nonlocal done
        key,item,lang,mode=job
        rate='-18%' if mode=='slow' else '-3%' if item['kind']=='sentence' else '-2%'
        digest=hashlib.sha256((item['text']+'|'+VOICES[lang]['voice']+'|'+rate).encode()).hexdigest()[:20]
        folder=OUT/lang;folder.mkdir(parents=True,exist_ok=True)
        audio=folder/(digest+'.mp3');metadata=CACHE/(digest+'.jsonl')
        async with sem:
            if not(audio.exists() and audio.stat().st_size>1000 and metadata.exists()):
                for attempt in range(3):
                    try:
                        t=edge_tts.Communicate(item['text'],VOICES[lang]['voice'],rate=rate,boundary='WordBoundary',connect_timeout=15,receive_timeout=40)
                        await asyncio.wait_for(t.save(str(audio),str(metadata)),timeout=65)
                        break
                    except Exception:
                        if attempt==2:raise
                        await asyncio.sleep(2*(attempt+1))
            info=MP3(audio).info
            if info.length<.15:raise ValueError('Empty audio: '+str(audio))
            boundaries=[]
            for line in metadata.read_text().splitlines():
                row=json.loads(line)
                if row['type']=='WordBoundary':boundaries.append({'text':row['text'],'start':round(row['offset']/10000000,3),'end':round((row['offset']+row['duration'])/10000000,3)})
            clip={'src':audio.relative_to(ROOT/'dist').as_posix(),'voice':VOICES[lang]['name'],'duration':round(info.length,3),'kind':item['kind']}
            if item['kind']=='sentence':clip['words']=boundaries
            manifest['clips'].setdefault(key,{}).setdefault(lang,{})[mode]=clip
            done+=1
            if done%20==0 or done==len(jobs):print(f'Generated/validated {done}/{len(jobs)} clips',flush=True)
    await asyncio.gather(*(generate(job) for job in jobs))
    (ROOT/'dist/narration.js').write_text('window.NARRATION = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n')
    print(json.dumps({'clips':len(jobs),'phrases':len(ordered),'voices':VOICES,'bytes':sum(p.stat().st_size for p in OUT.rglob('*.mp3'))}),flush=True)

asyncio.run(main())
