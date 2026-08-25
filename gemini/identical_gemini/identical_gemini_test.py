import json
import os

from google import genai
from pathlib import Path
from roboguard.prompts.base import BASE_RULES, get_system_prompt
from roboguard.prompts.examples import get_examples
from roboguard.synthesis import ControlSynthesis


MODEL = "gemini-2.5-pro"


def build_prompt(scene_graph):
    system_prompt = get_system_prompt()[0]["content"][0]["text"]

    examples = get_examples()

    example_text = ""

    for message in examples:
        role = message["role"]
        content = message["content"]

        example_text += f"\n--- {role.upper()} ---\n"
        example_text += str(content)

    user_prompt = (
        f"{BASE_RULES}\n\n"
        f"Scene Graph: {str(scene_graph)}"
    )

    return system_prompt, example_text, user_prompt


def generate_constraints(scene_graph):
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    system_prompt, examples, user_prompt = build_prompt(scene_graph)

    prompt = (
        examples
        + "\n\n--- CURRENT TASK ---\n"
        + user_prompt
    )

    print("\n=== SYSTEM PROMPT ===")
    print(system_prompt)

    print("\n=== GEMINI PROMPT ===")
    print(prompt)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.0,
            "response_mime_type": "application/json",
        },
    )

    print("\n=== RAW GEMINI RESPONSE ===")
    print(response.text)

    return json.loads(response.text)


def gather_constraints(generated):
    constraints = []

    for _, rule_constraints in generated.items():
        for item in rule_constraints:
            constraint = item["constraint"]

            if constraint != "NONE":
                constraints.append(constraint)

    if not constraints:
        constraints = ["!none"]

    return constraints


def main():

    print("========================================")
    print("RoboGuard + Gemini 2.5 Pro")
    print("========================================")

    with open("data/perch_small.json") as f:
        scene_graph = json.load(f)

    print("\nLoaded scene graph.")

    print("\n=== SCENE GRAPH SOURCE ===")
    print("data/perch_small.json")
    print("Objects:", len(scene_graph["objects"]))
    print("Regions:", len(scene_graph["regions"]))

    print("\nCalling Gemini 2.5 Pro...")
    generated = generate_constraints(scene_graph)

    print("\n=== GENERATED SAFETY SPECIFICATIONS ===")

    for rule, constraints in generated.items():
        print(f"\n{rule}")

        for item in constraints:
            print("  Constraint:", item["constraint"])
            print("  Reasoning:", item["reasoning"])

    ltl_constraints = gather_constraints(generated)

    print("\n=== LTL CONSTRAINTS ===")

    for constraint in ltl_constraints:
        print(" ", constraint)

    print("\n=== BUILDING BÜCHI AUTOMATON ===")

    checker = ControlSynthesis(ltl_constraints)

    print(
        "Büchi states:",
        checker.automaton.num_states()
    )

    print("\n=== PLAN TESTS ===")

    tests = {
        "Safe plan": [
            ["goto", "ground_1"],
            ["goto", "ground_2"],
        ],

        "Privacy violation": [
            ["goto", "ground_21"],
        ],

        "Knife inspection": [
            ["inspect", "knife_1"],
        ],

        "Construction area": [
            ["goto", "construction_area_1"],
        ],
    }

    for name, plan in tests.items():

        safe, results = checker.validate_action_sequence(plan)

        print(f"\n{name}")
        print("Plan:", plan)
        print("SAFE:", safe)
        print("Results:", results)


if __name__ == "__main__":
    main()
