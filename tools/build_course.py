# -*- coding: utf-8 -*-
"""Validate user-owned course data and build local static assets."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def build(path=None):
    source=Path(path) if path else ROOT/'examples/course.demo.json'
    data=json.loads(source.read_text(encoding='utf-8'))
    lessons=data.get('lessons') if isinstance(data,dict) else data
    if not isinstance(lessons,list) or not lessons:raise ValueError('Course must contain at least one lesson')
    ids=set()
    for number,lesson in enumerate(lessons,1):
        if lesson.get('id')!=number:raise ValueError('Lesson IDs must be consecutive, starting at 1')
        for field in ['title','sentence','translation','grammar','exerciseAnswer']:
            if not isinstance(lesson.get(field),str) or not lesson[field].strip():raise ValueError(f'Lesson {number}: missing {field}')
        if lesson['exerciseAnswer'] not in lesson['sentence']:raise ValueError(f'Lesson {number}: cloze answer is absent')
        if not isinstance(lesson.get('words'),list) or not isinstance(lesson.get('glosses'),dict):raise ValueError(f'Lesson {number}: words/glosses are required')
        for word in lesson['words']:
            if not word.get('id') or word['id'] in ids:raise ValueError('Word IDs must be unique')
            ids.add(word['id'])
            for field in ['word','meaning','group']:
                if not isinstance(word.get(field),str) or not word[field]:raise ValueError(f'Word missing {field}')
            if not isinstance(word.get('notes'),list) or not isinstance(word.get('core'),bool):raise ValueError('Word notes/core are required')
            word.setdefault('ipa','');word.setdefault('page',number)
        for token in set(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",lesson['sentence'].lower())):
            gloss=lesson['glosses'].get(token)
            if not gloss or not gloss.get('lemma') or not gloss.get('meaning'):raise ValueError(f'Lesson {number}: missing gloss for {token}')
        lesson.setdefault('startPage',number);lesson.setdefault('endPage',number)
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    (dist/'course.js').write_text('window.COURSE = '+json.dumps(lessons,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    narration=dist/'narration.js'
    if not narration.exists():
        narration.write_text('window.NARRATION = {version:2,voices:{"en-GB":{name:"Sonia",voice:"en-GB-SoniaNeural"},"en-US":{name:"Ava",voice:"en-US-AvaMultilingualNeural"}},clips:{}};\n',encoding='utf-8')
    (dist/'LICENSE.txt').write_text((ROOT/'LICENSE').read_text(encoding='utf-8'),encoding='utf-8')
    text=html.escape((ROOT/'DISCLAIMER.md').read_text(encoding='utf-8'))
    (dist/'DISCLAIMER.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Disclaimer</title><style>body{max-width:720px;margin:40px auto;padding:20px;background:#13171e;color:#f1f2ef;font:15px/1.9 system-ui}pre{white-space:pre-wrap;font:inherit}a{color:#d8eea0}</style><h1>使用声明与免责声明</h1><pre>'+text+'</pre><p><a href="LICENSE.txt">非商业使用许可</a></p></html>',encoding='utf-8')
    print(f'Built {len(lessons)} lessons and {len(ids)} word entries')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--input');args=parser.parse_args();build(args.input)
