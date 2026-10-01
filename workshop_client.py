"""Explicit MCP discovery/calls without an AI host; uses the workshop v1 SDK."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(server: str, tool: str | None, arguments: str) -> None:
    params = StdioServerParameters(command=sys.executable,
                                   args=[str(Path(server).resolve())])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print('Tools:', ', '.join(t.name for t in tools.tools))
            if tool:
                result = await session.call_tool(tool, json.loads(arguments))
                print(result.model_dump_json(indent=2))
                if result.isError:
                    raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server', default='mcp_server_sdk.py')
    parser.add_argument('--tool')
    parser.add_argument('--arguments', default='{}')
    parser.add_argument('--arguments-file', help='Read input JSON from a file to avoid shell quoting issues')
    args = parser.parse_args()
    if args.arguments_file:
        args.arguments = Path(args.arguments_file).read_text(encoding='utf-8-sig')
    asyncio.run(run(args.server, args.tool, args.arguments))
