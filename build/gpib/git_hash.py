from __future__ import print_function

#  Using code based on http://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
#


def get_git_revision_hash():
    import subprocess
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
    except:
        return 'Can not run git'


def get_git_revision_short_hash():
    import subprocess
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).strip()
    except:
        return 'Can not run git'


if __name__ == '__main__':
    print(get_git_revision_hash())
    print(get_git_revision_short_hash())
