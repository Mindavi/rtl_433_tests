#!/usr/bin/env python3

"""Refresh rtl_433 JSON outputs."""

import argparse
import sys
import os
import fnmatch
import rtl_runner
import json


def convert(root, filename, rtl_path):
    output_fn = os.path.join(root, filename)

    input_fn = os.path.splitext(output_fn)[0] + ".cu8"
    if not os.path.isfile(input_fn):
        print("WARNING: Missing '%s'" % input_fn)
        return

    ignore_fn = os.path.join(os.path.dirname(output_fn), "ignore")
    if os.path.isfile(ignore_fn):
        print("WARNING: Ignoring '%s'" % input_fn)
        return

    samplerate = 250000
    samplerate_fn = os.path.join(os.path.dirname(output_fn), "samplerate")
    if os.path.isfile(samplerate_fn):
        with open(samplerate_fn, "r") as samplerate_file:
            samplerate = int(samplerate_file.readline())

    protocol = None
    protocol_fn = os.path.join(os.path.dirname(output_fn), "protocol")
    if os.path.isfile(protocol_fn):
        with open(protocol_fn, "r") as protocol_file:
            protocol = protocol_file.readline().strip()

    # Open expected data
    old_data = []
    with open(output_fn, "r") as output_file:
        old_data = output_file.read().splitlines()

    # Run rtl_433
    out, _err, exitcode = rtl_runner.run(input_fn, samplerate, protocol, rtl_path)

    if exitcode:
        print("ERROR: Exited with %d '%s'" % (exitcode, input_fn))

    # get JSON results
    out = out.decode('ascii')
    new_data = out.splitlines()

    if len(old_data) != len(new_data):
        print("\nWARNING: Different data for '%s'" % (input_fn))
        print('\n'.join(old_data))
        print("vs.")
        print('\n'.join(new_data))

    with open(output_fn, "w") as output_file:
        output_file.write('\n'.join(new_data))
        output_file.write('\n')


def main():
    """Process all reference json files."""
    parser = argparse.ArgumentParser(description='Update reference json files')
    parser.add_argument('-c', '--rtl433-cmd', default='rtl_433',
            help='rtl_433 command')
    args = parser.parse_args()

    rtl_433_cmd = args.rtl433_cmd

    for root, _dirnames, filenames in os.walk('tests'):
        for filename in fnmatch.filter(filenames, '*.json'):
            convert(root, filename, rtl_433_cmd)


if __name__ == '__main__':
    sys.exit(main())
