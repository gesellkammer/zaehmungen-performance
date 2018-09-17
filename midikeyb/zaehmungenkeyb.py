#!/usr/bin/env python3
import time
import os
import sys
import subprocess
from zaehmungen import core
import zaehmungen

# Default configuration, it will be overridden by config.txt
# if it exists (in the same directory as this file)

SR = 44100
KSMPS = 64

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def is_jack_running():
    status = subprocess.call(['jack_control', 'status'])
    return status == 0

if not is_jack_running():
    print("Jack is not running. Please start it, then run this script again")
    sys.exit(-1)

configfile = "config.txt"
if os.path.exists(configfile):
    print("reading configuration")
    exec(open(configfile).read())

def killmatching(pattern):
    os.system(f'killall -9 "{pattern}"')
    timeout = 1
    while timeout > 0:
        procs = procsmatching(pattern)
        if not procs:
            return True
        time.sleep(0.1)
        timeout -= 0.1
    raise RuntimeError(f"could not kill {pattern}")

def procsmatching(pattern):
    try:
        out = subprocess.check_output(["pgrep", "-f", pattern])
        return [int(pid) for pid in out.splitlines()]
    except subprocess.CalledProcessError:
        return None

killmatching("csound")

# puredata gui

pdpatch = os.path.abspath("assets/zaehmungen.pd")
pdproc = subprocess.Popen(['pd', '-noaudio', '-nomidi', pdpatch])

csoundpatch = os.path.abspath("assets/midikeyb.csd")
csoundargs = [
    "csound",
    "-+rtaudio=jack",
    "-odac",
    f"--sample-rate={SR}",
    f"--ksmps={KSMPS}",
    "-m", "0",
    csoundpatch
]

# csound engine

print(csoundargs)
csoundproc = subprocess.Popen(csoundargs)

# controler

keyb = core.MidiKeyb()

try:
    keyb.start()
except KeyboardInterrupt:
    print("Keyboard interrupt: exiting")
except zaehmungen.error.GuiConnectionError:
    print("GuiConnectionError")

print("exiting")
time.sleep(2)

print("killing subprocesses")
csoundproc.kill()
pdproc.kill()
