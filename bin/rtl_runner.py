import subprocess

def run(input_fn, samplerate=None, protocol=None, rtl_433_cmd="rtl_433"):
    """Run rtl_433 and return output."""
    args = ['-c', '0']
    if protocol:
        args.extend(['-R', str(protocol)])
    if samplerate:
        args.extend(['-s', str(samplerate)])
    args.extend(['-F', 'json', '-r', input_fn])
    cmd = [rtl_433_cmd] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out, err, p.returncode)

