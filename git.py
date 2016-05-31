#
# DNSConf -- GIT-based dns zones management tool
#
# GIT command wrapper
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import subprocess
import re


def _git(cmd, stdin=None):
    """
    Run external command and return its stdout as a string
    """
    cmd = ['git'] + cmd.split(' ')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
    (stdout, stderr) = proc.communicate(stdin)
    if proc.wait() != 0:
        raise RuntimeError("%s command failed: %s" % (cmd[0], stderr))
    return stdout


def toplevel():
    """
    Get the toplevel directory of the current git repo
    """
    return _git('rev-parse --show-toplevel').strip()


def content_by_sha1(sha1):
    """
    Get the contents of a blob object from the git repo
    """
    return _git('cat-file -p %s' % sha1)


def content_by_commit_and_name(commit, name):
    """
    Get the contents of a file in particular commit
    """
    return _git('show %s:%s' % (commit, name))


def add_object(content):
    """
    Add a new object into the git database and return the corresponding sha1
    """
    return _git('hash-object -w --stdin', content).strip()


def update_index(filename, new_content):
    """
    Update the staged version of the given file with the provided new_content
    """
    new_sha = add_object(new_content)
    _git('update-index --cacheinfo 10644,%s,%s' % (new_sha, filename))


def head_version(filename):
    """
    Get the content of a file from HEAD revision
    """
    raw = _git('cat-file --batch', 'HEAD:%s\n' % filename)
    (header, content) = raw.split('\n', 1)
    if header.endswith(' missing'):
        return None
    (sha1, objtype, size) = header.split(' ')
    return content


def staged_files():
    """
    Get regular files that are added, modified, copied or renamed in index.
    Ignore executable files, symlinks, etc.
    """
    try:
        _git('rev-parse --verify HEAD')
        rev = 'HEAD'
    except RuntimeError:
        # In a new git repo, the HEAD reference is not set yet. In this case,
        # use an empty tree object to evaulate diffs against.
        rev = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

    output = _git('diff-index --cached --diff-filter=AMCR %s' % rev)
    files = [f.split(' ') for f in output.strip().split('\n')]

    return [ (f[3], f[4].split('\t')[-1]) for f in files
             if len(f)>1 and f[1] == '100644' ]


def changed_files(old, new):
    """
    Get a list of files modified between the two given commits
    """
    output = _git('diff --name-only %s..%s' % (old, new))
    files = output.strip().split('\n')

    return files
