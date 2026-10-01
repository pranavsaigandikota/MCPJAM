"""Integration check: real stdio MCP SDK against a controlled mock DAW."""
import asyncio
import json
import socketserver
import sys
import threading
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

state = {'ok': True, 'bpm': 90, 'swing': 0, 'muted': {'kick': False}}
received = []
reject = False

class Backend(socketserver.StreamRequestHandler):
    def handle(self):
        command = json.loads(self.rfile.readline())
        received.append(command)
        if reject:
            response = {'ok': False, 'error': 'controlled backend failure'}
        elif command['cmd'] == 'get_state':
            response = state
        else:
            if command['cmd'] == 'set_tempo': state['bpm'] = command['bpm']
            if command['cmd'] == 'set_swing': state['swing'] = command['amount']
            if command['cmd'] == 'mute_track': state['muted'][command['track']] = command['muted']
            response = {'ok': True}
        self.wfile.write(json.dumps(response).encode() + b'\n')

async def check():
    global reject
    checks = 0
    for server, names in [('mcp_server_sdk.py', {'get_state','set_tempo'}),
                          ('workshop_delivery/mcp_server_solution.py', {'get_state','set_tempo','set_swing','mute_track'})]:
        params = StdioServerParameters(command=sys.executable, args=[str(Path(server).resolve())])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                assert {t.name for t in (await session.list_tools()).tools} == names; checks += 1
                for bpm in [40,120,240]:
                    result = await session.call_tool('set_tempo', {'bpm':bpm})
                    assert not result.isError and state['bpm']==bpm; checks += 1
                for bpm in [39,500]:
                    count=len(received)
                    assert (await session.call_tool('set_tempo', {'bpm':bpm})).isError
                    assert len(received)==count; checks += 1
                if 'set_swing' in names:
                    for value in [0,35,75]:
                        assert not (await session.call_tool('set_swing', {'amount':value})).isError
                        assert state['swing']==value; checks += 1
                    count=len(received)
                    assert (await session.call_tool('set_swing', {'amount':100})).isError
                    assert len(received)==count; checks += 1
                    for value in [True,False]:
                        assert not (await session.call_tool('mute_track', {'track':'kick','muted':value})).isError
                        assert state['muted']['kick']==value; checks += 1
                    count=len(received)
                    assert (await session.call_tool('mute_track', {'track':'violin','muted':True})).isError
                    assert len(received)==count; checks += 1
                assert not (await session.call_tool('get_state', {})).isError; checks += 1
                reject=True
                assert (await session.call_tool('set_tempo', {'bpm':120})).isError; checks += 1
                reject=False
    print(f'PASS: {checks} protocol and tool checks (real stdio MCP, mock DAW).')

if __name__ == '__main__':
    with socketserver.ThreadingTCPServer(('127.0.0.1',8765), Backend) as backend:
        thread=threading.Thread(target=backend.serve_forever,daemon=True); thread.start()
        try: asyncio.run(check())
        finally: backend.shutdown()
