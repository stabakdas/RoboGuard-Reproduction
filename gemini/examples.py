EXAMPLES = """
Example:

Rule:
Do not inspect objects that can be used for harm.

Scene Graph:
{
  "objects": [
    {"name": "knife_1"}
  ],
  "regions": [
    {"name": "ground_1"}
  ],
  "object_connections": [
    ["knife_1", "ground_1"]
  ],
  "region_connections": []
}

Correct output:

{
  "Do not inspect objects that can be used for harm": [
    {
      "constraint": "G(!inspect(knife_1))",
      "reasoning": "knife_1 is a potentially harmful object."
    }
  ]
}

Notice that inspect() has exactly ONE argument in the LTL predicate.
The VLM query argument is omitted.
"""
