# MCPJAM workshop delivery

Use the [live Figma deck](https://www.figma.com/slides/mmQgw9DYp2CZDK7xDu69aZ/MCP-Servers-Slides). All PowerPoint/PDF files are archived snapshots. The maintained deck includes the default-120-BPM song → missing tool → added set_tempo activity, client payloads on slide 16, the comparison on slide 19, and a code screenshot on slide 20.
Plan 55 minutes, including 15 minutes audience build/test, with 5 minutes spare.
Installation starts near the beginning; security, enterprise and production practices
are part of the live workshop.

Read [Instructor-Guide.md](Instructor-Guide.md) for matching slide content and notes,
[Student-Quick-Start.md](Student-Quick-Start.md) for the exercise, and [../README.md](../README.md)
for the maintained Windows/macOS setup and launch instructions.

MCPJAM-Student-Code.zip contains the current starter, reference solution, app,
optional Gemini/music host, and bundled GeneralUser GS soundfont/license.
Create your own virtual environment after extracting; native audio runtimes are not copied.

Other older PowerPoint and PDF files are historical exports. Use the live Figma deck. Slide 15 maps the lab; slide 20 is MCP BUILD and 21 is the Copilot connection and 22–23 are MCP TEST.

Start with [the live lab](../workshop/README.md). Student edits are in
workshop/starter; reference answers are in workshop/solutions. The root server
files remain launchers for older commands and slides. The JSON now connects
to the starter on Windows/Mac, using each student's .venv interpreter.

[Velvet-Circuit-30s.mp3](Velvet-Circuit-30s.mp3) is the original 30-second R&B
score demo. [Music guide](../MUSIC_GENERATOR.md) explains the full score tools.

[Tempo-Code-Snippet.png](Tempo-Code-Snippet.png) is the exact code screenshot on slide 20.
The copyable version is in the root README → Student exercise. Run
`python verify_tempo_lab.py` after full audio setup to check the real MP3 activity.
