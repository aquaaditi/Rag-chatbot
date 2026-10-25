"""
Generation stage:  request + retrieved chunks  ->  script with [chunk ID] citations

    options.py        audience / length / style choices and the ScriptRequest type
    context.py        format chunks as the SOURCES block of the prompt
    prompts.py        the prompt template family + the grounding rules (system prompt)
    citations.py      find and check the [chunk IDs] in the LLM's answer
    script_result.py  GeneratedScript data type (text + sources + prompt + citations)
    generator.py      ScriptGenerator: retrieve -> prompt -> LLM -> check

Other stages only need `ScriptGenerator`, `ScriptRequest` and `GeneratedScript`.
"""

from src.generation.generator import ScriptGenerator
from src.generation.options import AUDIENCES, LENGTHS, STYLES, ScriptRequest
from src.generation.script_result import GeneratedScript

__all__ = ["AUDIENCES", "LENGTHS", "STYLES", "GeneratedScript", "ScriptGenerator", "ScriptRequest"]
