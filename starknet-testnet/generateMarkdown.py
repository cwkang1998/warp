import json
import os
import sys

from pathlib import Path
from starkware.starknet.business_logic.execution.objects import (
    CallInfo,
    TransactionExecutionInfo,
)

WARP_ROOT = Path(__file__).parents[1]
TMP = WARP_ROOT / "benchmark" / "json"
file_name = "data"

contract_name_map = {}


def steps_in_function_deploy(contract_name: str, result: TransactionExecutionInfo):
    json_path = os.path.abspath(TMP / (file_name + ".json"))
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            benchmark_data = json.load(json_file)
    else:
        benchmark_data = {}

    benchmark_data.setdefault(contract_name, {})[
        "steps"
    ] = result.call_info.execution_resources.n_steps

    with open(json_path, "w") as json_file:
        json.dump(benchmark_data, json_file, indent=3)


def steps_in_function_invoke(function_name: str, result: CallInfo):
    json_path = os.path.abspath(TMP / (file_name + ".json"))
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            benchmark_data = json.load(json_file)
    else:
        benchmark_data = {}

    contract_name = contract_name_map.get(result.contract_address, "UNKNOWN")
    benchmark_data.setdefault(contract_name, {}).setdefault("function_steps", {})[
        function_name
    ] = result.execution_resources.n_steps

    with open(json_path, "w") as json_file:
        json.dump(benchmark_data, json_file, indent=3)


def builtin_instance_count(contract_name: str, result: TransactionExecutionInfo):
    json_path = os.path.abspath(TMP / (file_name + ".json"))
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            benchmark_data = json.load(json_file)
    else:
        benchmark_data = {}

    benchmark_data.setdefault(contract_name, {})[
        "builtin_instances"
    ] = result.call_info.execution_resources.builtin_instance_counter

    with open(json_path, "w") as json_file:
        json.dump(benchmark_data, json_file, indent=3)


def json_size_count(file_path: str):
    json_path = os.path.abspath(TMP / (file_name + ".json"))
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            benchmark_data = json.load(json_file)
    else:
        benchmark_data = {}

    benchmark_data.setdefault(file_path, {})[
        "json_size"
    ] = f"{os.path.getsize(file_path)/1024} KB"

    with open(json_path, "w") as json_file:
        json.dump(benchmark_data, json_file, indent=3)


def create_markdown():
    json_path = os.path.abspath(TMP / (file_name + ".json"))

    with open(json_path, "r") as json_file:
        benchmark_data = json.load(json_file)

    os.makedirs("benchmark/stats", exist_ok=True)

    with open(
        os.path.join(WARP_ROOT, f"benchmark/stats/{file_name}.md"), "w"
    ) as md_file:
        md_file.write("# Warp-ts status\n\n")
        md_file.write(f"commit: {file_name}\n\n")

    for contract, data in benchmark_data.items():
        with open(
            os.path.join(WARP_ROOT, f"benchmark/stats/{file_name}.md"), "a"
        ) as md_file:
            md_file.write(f"## {os.path.basename(contract)}:\n\n")
            md_file.write("| Metric | Value |\n")
            md_file.write("| ----------- | ----------- |\n")

            for metric, value in sorted(data.items()):
                if metric in ["builtin_instances", "function_steps"]:
                    continue
                md_file.write(f"| {metric} | {value} |\n")
            md_file.write(f"\n")

        if "builtin_instances" in data:
            with open(
                os.path.join(WARP_ROOT, f"benchmark/stats/{file_name}.md"), "a"
            ) as md_file:
                md_file.write("| Builtin | Instances |\n")
                md_file.write("| ----------- | ----------- |\n")

                for builtin, count in sorted(data["builtin_instances"].items()):
                    md_file.write(f"| {builtin} | {count} |\n")

                md_file.write(f"\n")

        if "function_steps" in data:
            with open(
                os.path.join(WARP_ROOT, f"benchmark/stats/{file_name}.md"), "a"
            ) as md_file:
                md_file.write("| Function | Steps |\n")
                md_file.write("| ----------- | ----------- |\n")

                for function, steps in sorted(data["function_steps"].items()):
                    md_file.write(f"| {function} | {steps} |\n")

                md_file.write(f"\n")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] != None:
        file_name = sys.argv[1]
        print(sys.argv[1])
    print(file_name)
    create_markdown()
