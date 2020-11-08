import subprocess


def run(input_fn, samplerate, protocol, rtl_433_cmd, extra_args=[]):
    """Run rtl_433 and return output."""
    args = ["-c", "0"]
    if protocol:
        args.extend(["-R", str(protocol)])
    if samplerate:
        args.extend(["-s", str(samplerate)])
    args.extend(["-F", "json", "-r", input_fn])
    args.extend(extra_args)
    cmd = [rtl_433_cmd] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out, err, p.returncode)
