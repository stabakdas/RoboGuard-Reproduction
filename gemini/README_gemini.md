Gemini-Enabled RoboGuard
This directory contains the Gemini integration and supporting files for the RoboGuard reproduction project.
The goal is to evaluate whether the RoboGuard contextual-grounding pipeline can use Google Gemini 2.5 Pro in place of the original OpenAI-based contextual-grounding model, while preserving the original RoboGuard formal verification components.
Directory Structure
gemini/
│
├── identical_gemini/│
│   ├── gemini_test_output.txt
│   ├── identical_gemini_test.py
│  
│
├── examples.py
├── prompts.py
├── gemini_test.py
├── gemini_test_result.txt

identical_gemini/
This directory contains the original RoboGuard code/prompt structure used as a reference baseline.
It is intentionally preserved so that the original implementation remains available before Gemini-specific prompt changes are introduced.
It provides a reference for:
RoboGuard's original prompting structure
Original examples
Original action abstractions
Original LTL constraint-generation instructions
Treat this directory as a baseline/reference copy rather than the active Gemini implementation.

However, prompts.py
This file contains the Gemini-specific system prompt.
The Gemini prompt is based on the original RoboGuard prompt but makes the action abstraction explicit for Gemini.
For example, the robot execution API may define:
inspect(object_node, vlm_query)
while the LTL safety abstraction uses:
inspect(object_node)
The Gemini prompt explicitly instructs the model not to include the VLM query in the LTL predicate.
For example:
G(!inspect(knife_1))
is valid, while:
G(!inspect(knife_1, "*"))
is not valid for the current LTL abstraction.

And examples.py
Contains examples used to guide Gemini's LTL constraint generation.
The examples follow the RoboGuard contextual-grounding format and are kept separate from the original RoboGuard prompt files so that Gemini-specific changes do not modify the original implementation.
gemini_test.py
This is the main test script for the Gemini integration.
It performs:
Scene Graph JSON
       |
       v
Gemini 2.5 Pro
       |
       v
Generated Safety Specifications
       |
       v
LTL Constraints
       |
       v
RoboGuard ControlSynthesis
       |
       v
Spot / Büchi Automaton
       |
       v
Candidate Plan Validation
The current test uses:
../data/perch_small.json
as the scene graph.
gemini_test_result.txt
Contains saved output from a successful Gemini test run.
It is useful for documenting and checking the current implementation without making another API call. It should be treated as an experiment artifact rather than the source of truth.



Before running this Set the Gemini API key:
export GEMINI_API_KEY="YOUR_API_KEY"

Running the Gemini Test
From the Gemini directory:
cd ~/research/RoboGuard/gemini
python gemini_test.py
The script:
Loads the scene graph from the RoboGuard data directory.
Builds the Gemini-specific prompt.
Sends the scene graph and safety rules to Gemini 2.5 Pro.
Parses the generated JSON response.
Extracts the LTL constraints.
Passes the constraints to the original RoboGuard ControlSynthesis.
Builds a Büchi automaton using Spot.
Validates candidate action plans.

Example Pipeline
Gemini may generate constraints such as:
G(!goto(ground_21))
G(!inspect(knife_1))
G(!goto(construction_area_1))
These are passed to:
from roboguard.synthesis import ControlSynthesis

checker = ControlSynthesis(ltl_constraints)
The original RoboGuard synthesis implementation performs the formal verification.
For example, a safe plan:
[['goto', 'ground_1'], ['goto', 'ground_2']]
can be accepted when it does not violate the generated constraints.
A violating plan such as:
[['goto', 'construction_area_1']]
is rejected when Gemini generates:
G(!goto(construction_area_1))

The identical_gemini/ directory is intentionally maintained as a reference copy.
The experimental workflow is:
                Original RoboGuard
                        |
                        v
                identical_gemini/
                        |
                        | reference/copy
                        v
                Gemini-2.5 Pro
		Gemini 2.5 Pro
		       |
		       v
	Generated Safety Specifications
		       |
		       v
		LTL Constraints
		       |
		       v
	RoboGuard ControlSynthesis
		       |
		       v
	Spot / Büchi Automaton
		       |
		       v
	Candidate Plan Validation
The current test uses:
../data/perch_small.json
as the scene graph.
gemini_test_result.txt
Contains saved output from a successful Gemini test run.

