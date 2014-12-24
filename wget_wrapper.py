import os
import os.path
import subprocess
import sys
import logging

children = {}
maxjobs = 2                 # maximum number of concurrent jobs
jobs = []                   # current list of queued jobs

# Default wget options to use for downloading each URL
wget = ["wget", "-q", "-nd", "-np", "-c", "-r"]

# Spawn a new child from jobs[] and record it in children{} using
# its PID as a key.
def spawn(cwd, cmd, *args):
    argv = [cmd] + list(args)
    pid = None
    try:
        p = subprocess.Popen(argv, cwd=cwd); pid = p.pid
        children[pid] = {'p': p, 'cmd': argv}
    except Exception, inst:
        logging.exception("\x20".join(argv))
    logging.debug("spawned pid %d of nproc=%d njobs=%d for '%s'" % \
        (pid, len(children), len(jobs), "\x20".join(argv)))
    return pid

def download(request_path, download_path):
    logging.debug("saving files to %s " % download_path)
    # Build a list of wget jobs, one for each URL in our input file(s).
    filelist = [os.path.join(request_path, x) for x in os.listdir(request_path)]
    for fname in filelist:
        if fname.endswith('.done'):
            continue
        try:
            for u in file(fname).readlines():
                cmd = wget + [u.strip('\r\n')]
                jobs.append(cmd)
        except IOError:
            pass
        #rename this file to filename.done so that it 
        #wont be picked in next iteration
        without_suffix = fname
        fname = without_suffix + '.done'
        if os.path.exists(fname):
            i = 1
            while True:
                fname = without_suffix + '.' + str(i) + '.done'
                if not os.path.exists(fname):
                    break
                i += 1
        os.rename(without_suffix, fname)
    logging.info("%d wget jobs queued" % len(jobs))

    # Spawn at most maxjobs in parallel.
    while len(jobs) > 0 and len(children) < maxjobs:
        cmd = jobs[0]
        if spawn(download_path, *cmd):
            del jobs[0]
    logging.info("%d jobs spawned" % len(children))

    # Watch for dying children and keep spawning new jobs while
    # we have them, in an effort to keep <= maxjobs children active.
    while len(jobs) > 0 or len(children):
        p = children.values()[0]['p']
        pid = p.pid; status = p.wait()
        logging.debug("pid %d exited. status=%d, nproc=%d, njobs=%d, cmd=%s" % \
            (pid, status, len(children) - 1, len(jobs), \
             "\x20".join(children[pid]['cmd'])))
        del children[pid]
        if len(children) < maxjobs and len(jobs):
            cmd = jobs[0]
            if spawn(download_path, *cmd):
                del jobs[0]

