#!/usr/bin/env python3

"""Refresh rtl_433 JSON outputs."""

import argparse
import sys
import os
import fnmatch
import rtl_runner
import json
import subprocess

RFRAW_OUTPUT_PATH = "rfraw"


def extract_rfraw(input_text):
    splitted = input_text.splitlines()
    rfraw_raw_lines = list(filter(lambda line: "view at http" in line, splitted))
    rfraw_lines = list(map(lambda line: line.split("#")[1], rfraw_raw_lines))

    return rfraw_lines


def gather_metadata(cu8_filepath):
    """Gather metadata for this input file."""
    if not os.path.isfile(cu8_filepath):
        print(f"WARNING: Missing '{cu8_filepath}'")
        return False, None, None

    cu8_directory = os.path.dirname(cu8_filepath)

    ignore_fn = os.path.join(cu8_directory, "ignore")
    if os.path.isfile(ignore_fn):
        print(f"WARNING: Ignoring '{cu8_filepath}'")
        return False, None, None

    samplerate = 250000
    samplerate_fn = os.path.join(cu8_directory, "samplerate")
    if os.path.isfile(samplerate_fn):
        with open(samplerate_fn, "r") as samplerate_file:
            samplerate = int(samplerate_file.readline())

    protocol = None
    protocol_fn = os.path.join(cu8_directory, "protocol")
    if os.path.isfile(protocol_fn):
        with open(protocol_fn, "r") as protocol_file:
            protocol = protocol_file.readline().strip()

    return True, samplerate, protocol


def get_model_for_cu8_file(cu8_filename):
    json_filepath = os.path.splitext(cu8_filename)[0] + ".json"
    expected_data = []
    with open(json_filepath, "r") as output_file:
        expected_data = output_file.read().splitlines()

    expected_model = None
    if len(expected_data) > 0:
        try:
            line = json.loads(expected_data[0])
            expected_model = line["model"]
        except e:
            print(e)

    return expected_model


def generate(root, filename, rtl_path):
    output_fn = os.path.join(root, filename)
    cu8_filename = os.path.splitext(output_fn)[0] + ".cu8"
    ok, samplerate, protocol = gather_metadata(cu8_filename)
    if not ok:
        return

    # Open expected data
    expected_data = []
    with open(output_fn, "r") as output_file:
        expected_data = output_file.read().splitlines()

    expected_model = get_model_for_cu8_file(cu8_filename)

    if len(expected_data) == 0 or not expected_model:
        print(f"No expected data for {cu8_filename}")
        return

    # Run rtl_433 in analyze mode
    out, err, exitcode = rtl_runner.run(
        cu8_filename, samplerate, protocol, rtl_path, ["-A"]
    )

    if exitcode:
        print(f"ERROR: Exited with {exitcode} '{cu8_filename}'")
        return

    err = err.decode("ascii")
    rfraw_lines = extract_rfraw(err)
    if len(rfraw_lines) > 0 or len(expected_data) > 0:
        # print(f"rfraw_lines: {len(rfraw_lines)}, new_data: {len(expected_data)}")
        pass
    for i in range(len(rfraw_lines)):
        if i >= len(expected_data):
            continue

    rfraw_outputs = dict()
    for line in rfraw_lines:
        result = subprocess.run(
            [rtl_path, "-y", line, "-F", "json"], capture_output=True
        )
        output = result.stdout.decode("ascii").strip()
        if not output:
            print(f"Rfraw line from {cu8_filename} does not generate any output")
            continue
        if line in rfraw_outputs:
            print(f"Duplicate rfraw line found: {line}, {expected_model}")
        else:
            rfraw_outputs[line] = []

        for output_line in output.splitlines():
            print(output_line)
            json_output = json.loads(output_line)
            del json_output["time"]
            rfraw_outputs[line].append(json_output)

    os.makedirs(RFRAW_OUTPUT_PATH, exist_ok=True)
    rfraw_json_fn = os.path.join(
        RFRAW_OUTPUT_PATH, f"{expected_model}_{os.path.splitext(filename)[0]}.rfraw.json",
    )

    with open(rfraw_json_fn, "w") as rfraw_json_file:
        json.dump(rfraw_outputs, rfraw_json_file)


def main():
    """Convert cu8 files into rfraw output"""
    parser = argparse.ArgumentParser(description="Convert cu8 to rfraw")
    parser.add_argument("-c", "--rtl433-cmd", default="rtl_433", help="rtl_433 command")
    args = parser.parse_args()

    rtl_433_cmd = args.rtl433_cmd

    for root, _dirnames, filenames in os.walk("tests"):
        for filename in fnmatch.filter(filenames, "*.json"):
            generate(root, filename, rtl_433_cmd)


if __name__ == "__main__":
    sys.exit(main())
