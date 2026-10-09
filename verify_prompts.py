"""Verify MCP prompt discovery/rendering and research evidence checks, without keys/audio."""
import asyncio
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import gemini_host

ROOT = Path(__file__).resolve().parent


async def protocol_check():
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT / 'mcp_server_music.py')])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            prompts = (await session.list_prompts()).prompts
            prompt = next(p for p in prompts if p.name == 'compose_music')
            assert {a.name: a.required for a in prompt.arguments} == {
                'description': True, 'reference_song': False, 'rights_context': False}
            result = await session.get_prompt('compose_music', {
                'description': 'Energetic rock with crunchy guitar and drums',
                'reference_song': 'A reference for instrumentation',
                'rights_context': 'I have permission to play the song in class'})
            text = result.messages[0].content.text
            assert 'Energetic rock' in text and 'permission to play the song in class' in text
            assert 'performance permission' in text and 'do not infer permission' in text
            assert 'get_instrument_catalog' in text and 'create_song_from_score' in text
            assert 'duration_seconds=30' in text and 'Never call play_song' in text
            # Omitting optional arguments works. Invalid description fails before side effects.
            await session.get_prompt('compose_music', {'description': 'Original jazz'})
            try:
                await session.get_prompt('compose_music', {'description': ' '})
            except Exception:
                pass
            else:
                raise AssertionError('Empty prompt should fail')
    print('PASS: real MCP prompt discovery, arguments, permission context and rendering; no audio generated')
    responses = [
        {'candidates': [{'content': {'role': 'model', 'parts': [{'functionCall': {
            'name': 'get_instrument_catalog', 'args': {'query': 'guitar'}}}]}}]},
        {'candidates': [{'content': {'role': 'model', 'parts': [{'text': 'Catalog checked.'}]}}]}
    ]
    with patch.object(gemini_host, 'generate', side_effect=responses) as generate, redirect_stdout(io.StringIO()):
        await gemini_host.run('Original rock', ROOT / 'mcp_server_music.py', 'test-model', 'test-key',
                              prompt_template='compose_music', rights_context='Permission to play in class')
        instructions = generate.call_args_list[0].args[2][0]['parts'][0]['text']
        assert 'Original rock' in instructions and 'Permission to play in class' in instructions
        declarations = generate.call_args_list[0].args[3]
        assert 'create_song_from_score' in {d['name'] for d in declarations}
        assert not any(d['name'] == 'create_pop_song' for d in declarations)
    print('PASS: bundled host consumes the real MCP prompt and calls the catalog (mocked model, no audio)')


def research_check():
    good = {'candidates': [{'content': {'parts': [{'text': 'Electric guitars, bass and drums.'}]},
                           'groundingMetadata': {'webSearchQueries': ['rock instrumentation'],
                                                 'groundingChunks': [{'web': {'uri': 'https://example.org/credits',
                                                                             'title': 'Credits'}}]}}]}
    with tempfile.TemporaryDirectory() as directory, patch.object(gemini_host, 'ROOT', Path(directory)):
        with patch.object(gemini_host, 'generate', return_value=good) as generate:
            result = gemini_host.research_music('test-key', 'test-model', 'Rock')
            assert generate.call_args.kwargs == {'research': True}
            assert result['sources'][0]['title'] == 'Credits'
            records = list((Path(directory) / 'generated_music').glob('research-*.json'))
            assert len(records) == 1 and json.loads(records[0].read_text())['groundingMetadata']['webSearchQueries']
        for response in ({'candidates': []}, {'candidates': [{'content': {'parts': [{'text': 'An unsupported guess'}]}}]}):
            with patch.object(gemini_host, 'generate', return_value=response):
                try:
                    gemini_host.research_music('test-key', 'test-model', 'Rock')
                except RuntimeError:
                    pass
                else:
                    raise AssertionError('Ungrounded research must fail')
        assert len(list((Path(directory) / 'generated_music').glob('research-*.json'))) == 1
    print('PASS: grounded-source parsing and rejection of missing research evidence (mocked API)')
    with patch.object(gemini_host.urllib.request, 'urlopen', return_value=io.BytesIO(json.dumps(good).encode())) as request:
        gemini_host.generate('test-key', 'test-model', [{'role': 'user', 'parts': [{'text': 'Rock'}]}], [], research=True)
        payload = json.loads(request.call_args.args[0].data)
        assert payload['tools'] == [{'google_search': {}}]
        assert 'Do not return lyrics' in payload['systemInstruction']['parts'][0]['text']
    print('PASS: search request enables Google Search without local mutation tools (mocked HTTP)')


if __name__ == '__main__':
    research_check()
    asyncio.run(protocol_check())
