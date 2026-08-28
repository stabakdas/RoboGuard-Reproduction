import json

from spine.spine import SPINE, GraphHandler


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

    handler = GraphHandler("")

    # Same graph initialization used by RoboGuard.
    success = handler.reset(
        str(working_graph).replace("'", '"'),
        init_location,
    )

    print(f"Graph reset: {success}")
    print(f"Current location: {handler.current_location}")
    print(f"Number of graph nodes: {len(handler.graph.nodes)}")

    # Same SPINE initialization used by RoboGuard.
    planner = SPINE(handler)

    print("\nCalling SPINE...")
    response, success, logs = planner.request(
        "Inspect the plan."
    )

    print(f"SPINE success: {success}")

    if logs:
        print("\n--- SPINE LOGS ---")
        for log in logs:
            print(log)

    print("\n--- SPINE RESPONSE ---")
    print(response)

    if success:
        print("\n--- CANDIDATE PLAN ---")
        print(response["plan"])


if __name__ == "__main__":
    main()

