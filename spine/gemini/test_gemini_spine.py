import json

from spine.mapping.graph_util import GraphHandler

from gemini_spine import GeminiSPINE


GRAPH_PATH = "/home/stabak/research/RoboGuard/data/perch_small.json"


def main():
    # Load the same scene graph used by RoboGuard.
    with open(GRAPH_PATH) as f:
        working_graph = json.load(f)

    # Same initialization used in RoboGuard eval.py.
    if "current_location" in working_graph:
        init_location = working_graph["current_location"]
    else:
        init_location = "ground_1"

    # Use the original SPINE GraphHandler.
    handler = GraphHandler("")

    success = handler.reset(
        str(working_graph).replace("'", '"'),
        init_location,
    )

    print(f"Graph reset: {success}")
    print(f"Current location: {handler.current_location}")
    print(f"Number of graph nodes: {len(handler.graph.nodes)}")

    # Use Gemini instead of OpenAI.
    planner = GeminiSPINE(handler)

    print("\nCalling Gemini-SPINE...")

    response, success, logs = planner.request(
        "Inspect the plan."
    )

    print(f"Gemini-SPINE success: {success}")

    if logs:
        print("\n--- SPINE LOGS ---")

        for log in logs:
            print(log)

    print("\n--- GEMINI-SPINE RESPONSE ---")
    print(response)

    if success:
        print("\n--- CANDIDATE PLAN ---")

        for action, argument in response["plan"]:
            print(f"\t{action}( {argument} )")

        print("\n--- REASONING ---")
        print(response.get("reasoning", ""))


if __name__ == "__main__":
    main()
