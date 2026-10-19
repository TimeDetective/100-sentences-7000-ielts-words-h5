# -*- coding: utf-8 -*-
"""Build the demo and serve the dist directory locally."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from build_course import ROOT,build

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--keep-course',action='store_true');parser.add_argument('--port',type=int,default=8780);args=parser.parse_args()
    if not args.keep_course:build()
    elif not (ROOT/'dist/course.js').exists():raise SystemExit('Build a course first')
    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(ROOT/'dist'))
    print(f'http://127.0.0.1:{args.port}/',flush=True)
    try:ThreadingHTTPServer(('127.0.0.1',args.port),handler).serve_forever()
    except KeyboardInterrupt:pass
