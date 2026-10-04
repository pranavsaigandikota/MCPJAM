"""Verify the workshop against the running GUI, real MCP stdio, and local socket.

Run with MCPJAM open. This changes tempo, swing, and kick mute temporarily,
then restores those values. No Gemini key is required.
"""
import asyncio
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from gemini_host import observe, state_from

ROOT = Path(__file__).resolve().parent


async def check_server(filename, expected):
    checks = 0
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT / filename)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = {tool.name: tool for tool in (await session.list_tools()).tools}
            assert set(tools) == expected, (filename, set(tools))
            checks += 1
            assert tools['set_tempo'].inputSchema['properties']['bpm']['type'] == 'integer'
            checks += 1
            original = state_from(await session.call_tool('get_state', {}))
            assert original['ok'] is True
            checks += 1
            print(f"{filename}: connected to app; audio_enabled={original['audio_enabled']}")

            async def accepted(name, arguments):
                result = await session.call_tool(name, arguments)
                assert not result.isError, result
                await observe(session, name, arguments)
                await asyncio.sleep(0.15)
                await observe(session, name, arguments)

            async def rejected(name, arguments):
                before = state_from(await session.call_tool('get_state', {}))
                result = await session.call_tool(name, arguments)
                assert result.isError, (name, arguments, result)
                # Allow the GUI queue to process; a backend clamp must not hide missing validation.
                await asyncio.sleep(0.15)
                after = state_from(await session.call_tool('get_state', {}))
                assert before == after, (name, arguments, 'state changed after rejected call')

            try:
                for bpm in (40, 120, 240):
                    await accepted('set_tempo', {'bpm': bpm})
                    checks += 1
                for value in (39, 241, 'not a number', 120.5):
                    await rejected('set_tempo', {'bpm': value})
                    checks += 1
                if 'set_swing' in tools:
                    assert tools['set_swing'].inputSchema['properties']['amount']['type'] == 'integer'
                    checks += 1
                    for amount in (35, 0, 75):
                        await accepted('set_swing', {'amount': amount})
                        checks += 1
                    for amount in (-1, 100, 'bad', 35.5):
                        await rejected('set_swing', {'amount': amount})
                        checks += 1
                if 'mute_track' in tools:
                    for muted in (True, False):
                        await accepted('mute_track', {'track': 'kick', 'muted': muted})
                        checks += 1
                    await rejected('mute_track', {'track': 'violin', 'muted': True})
                    checks += 1
            finally:
                await accepted('set_tempo', {'bpm': original['bpm']})
                if 'set_swing' in tools:
                    await accepted('set_swing', {'amount': original['swing']})
                if 'mute_track' in tools:
                    await accepted('mute_track', {'track': 'kick', 'muted': original['muted']['kick']})
    print(f'PASS: {filename}: {checks} checks; original state restored.')
    return checks


async def main():
    count = await check_server('mcp_server_sdk.py', {'get_state', 'set_tempo'})
    count += await check_server('mcp_server_solution.py', {'get_state', 'set_tempo', 'set_swing', 'mute_track'})
    print(f'PASS: {count} live checks (GUI + audio status + MCP stdio + backend socket).')


if __name__ == '__main__':
    asyncio.run(main())
