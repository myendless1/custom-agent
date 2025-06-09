from autogen_agentchat.agents import AssistantAgent
import os
from .common_agents import FileSystemAgent
from .utils import print_colored
from autogen_agentchat.ui import Console
import json

class CoderAgent(AssistantAgent):
    def __init__(self, name, model_client, tools, reflect_on_tool_use=True, workspace='./executions/test/', log_dir='ca_logs'):
        super().__init__(
            name=name, model_client=model_client, tools=tools, reflect_on_tool_use=reflect_on_tool_use)
        """
        Following the plan in 'plan.json' under the workspace log_dir directory, modify the code step by step to achieve the mission goal.
        For each step:
            1. Read the specified dependencies (files).
            2. Modify or create code as described.
            3. Save the modified code to the specified path.
        """
        self.workspace = workspace
        self.log_dir = log_dir
        self.step1_prompt = f"""
            The mission goal is: MISSION_GOAL
            Now you need to modify or create code files or directories as described in MODIFICATION.
            The files you may need to read are: DEPENDENCIES
            Any extra information: EXTRA_INFO
            1. Give your final full code files, DO NOT use ANY ellipsis! Write the simplest code that can achieve the goal, do not add any unnecessary code.
            Return the combined code if you are asked to add some code to existing files.
            Or 2. give the information of directories to create.
            """
        self.save_code_prompt = f"""
            The given code is in the following message: \nBEGIN MODIFIED_CODE \n TERMINATE
            It may include several files or directories to be created or modified.
            Now save the code to the specified path or create directories at: SAVE_PATH under root: SAVE_ROOT (already created).
            If you are asked to save code, the directory is already created, you just need to save the code to the specified file.
            Make sure the code is in the correct format and includes necessary imports.
            Extract the info of newly implemented classes, functions and files if there is any.
            Use the following format as your output:
            ```json
            {{
                "classes": [
                    {{
                        "location": "path/to/class/file.py",
                        "name": "ClassName",
                        "init args": [{{
                            "name": "arg1",
                            "type": "str",
                            "default": "default_value"
                        }},...],
                        "methods": [
                            {{
                                "name": "method_name",
                                "args": [
                                    {{
                                        "name": "arg1",
                                        "type": "str",
                                        "default": "default_value"
                                    }},...
                                ],
                                "docstring": "Method docstring"
                            }},
                            ...
                        ],
                        "docstring": "Class docstring"
                    }},
                    ...
                ],
                "functions": [
                    {{
                        "name": "function_name",
                        "args": [
                            {{
                                "name": "arg1",
                                "type": "str",
                                "default": "default_value"
                            }}, ...
                        ],
                        "docstring": "Function docstring"
                    }},
                    ...
                ],
                "files": [
                    {{
                        "path": "path/to/file.py",
                        "description": "The functionality of this file is to...",
                    }}
                ]
            }}
            ```
            """
        self.save_extra_definition_prompt = f"""
            The current definitions are: EXTRA_DEFINITIONS
            The extra definitions are: \nBEGIN MODIFIED_CODE\n TERMINATE
            Now merge these definitions as a whole and save to the specified path: SAVE_PATH under root: SAVE_ROOT (already created).
            The directory is already created, you just need to save the code to the specified file.
            """
        self.save_code_agent = FileSystemAgent(
            name="save_code_agent",
            model_client=model_client,
            workspace=self.workspace,
            system_message=f"""Save the code to the specified path under specified root directory."""
        )
        os.makedirs(os.path.join(self.workspace, self.log_dir), exist_ok=True)

    async def run(self, mission_goal, stream_output=False):
        plan = json.load(open(os.path.join(self.workspace, self.log_dir, 'plan.json'), 'r'))
        coding_steps = plan['plan']
        execution_outputs = []
        extra_definition_file = "extra_definitions.json"
        if not os.path.exists(os.path.join(self.workspace, self.log_dir, extra_definition_file)):
            with open(os.path.join(self.workspace, self.log_dir, extra_definition_file), 'w') as f:
                json.dump({"classes": [], "functions": [], "files": []}, f, indent=4)
        # Get file structure for context
        for coding_step in coding_steps:
            step_idx = coding_step['step']
            dependencies = coding_step.get('dependencies', [])
            modification = coding_step['modification']
            save_path = coding_step['save_path']
            extra_info = coding_step.get('extra_info', {})

            print_colored("#"*50+f"[Coder] Step {step_idx}"+"#"*50+" Settings", "blue")
            print_colored("Target:", "blue"); print_colored(str(modification), "green")
            print_colored("Dependencies:", "blue"); print_colored(str(dependencies), "green")
            print_colored("Save Path:", "blue"); print_colored(str(save_path), "green")
            print_colored("Extra Info:", "blue"); print_colored(str(extra_info), "green")
            print_colored("#"*120)

            # Read dependencies
            dependencies_content = {
                f: open(os.path.join(self.workspace, f), 'r').read()
                if os.path.exists(os.path.join(self.workspace, f)) else f"{f} Not found"
                for f in dependencies
            }
            dependencies_str = json.dumps(dependencies_content, indent=2)

            coding_prompt = self.step1_prompt \
                .replace('MISSION_GOAL', mission_goal) \
                .replace('MODIFICATION', modification) \
                .replace('DEPENDENCIES', dependencies_str) \
                .replace('EXTRA_INFO', str(extra_info)) \
                .replace('EXTRA_DEFINITIONS', open(os.path.join(self.workspace, self.log_dir, extra_definition_file), 'r').read())

            print_colored(f"[Coder] Coding ...", "yellow")
            coding_output = await Console(self.run_stream(task=coding_prompt)) if stream_output else await super().run(task=coding_prompt)
            modified_code_info = coding_output.messages[-1].content

            save_code_prompt = self.save_code_prompt \
                .replace('MODIFIED_CODE', modified_code_info) \
                .replace('SAVE_PATH', save_path) \
                .replace('SAVE_ROOT', self.workspace)

            print_colored(f"[Coder] Saving code to {os.path.join(self.workspace, save_path)} ...", "yellow")
            extra_definition_output = await Console(self.save_code_agent.run_stream(task=save_code_prompt)) if stream_output else await self.save_code_agent.run(task=save_code_prompt)
            save_definition_prompt = self.save_extra_definition_prompt \
                .replace('EXTRA_DEFINITIONS', open(os.path.join(self.workspace, self.log_dir, extra_definition_file), 'r').read()) \
                .replace('MODIFIED_CODE', extra_definition_output.messages[-1].content) \
                .replace('SAVE_PATH', extra_definition_file) \
                .replace('SAVE_ROOT', os.path.join(self.workspace, self.log_dir))

            print_colored(f"[Coder] Saving extra definitions to {os.path.join(self.workspace, self.log_dir, extra_definition_file)} ...", "yellow")
            save_extra_difinition_output = await Console(self.save_code_agent.run_stream(task=save_definition_prompt)) if stream_output else await self.save_code_agent.run(task=save_definition_prompt)
            execution_outputs.append({
                "step": step_idx,
                "modified_code_info": modified_code_info,
                "save_path": save_path,
                "extra_info": extra_info,
                "coding_output": coding_output.messages[-1].content,
                "extra_definition_output": extra_definition_output.messages[-1].content,
                "save_extra_difinition_output": save_extra_difinition_output.messages[-1].content
            })
            print_colored("[Coder]" + json.dumps(execution_outputs[-1], indent=4), "green")
            print_colored(f"[Coder] Step {step_idx} completed.", "yellow")
        print_colored(f"[Coder] All coding steps completed. {len(execution_outputs)} steps executed.", "green")
        return execution_outputs