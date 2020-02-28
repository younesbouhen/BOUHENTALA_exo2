"""Correction script for this exercise.
For each depot name found in depots.txt:
- clones the repo.
- confirms main.c is the same as the original.
- invokes make test.
- runs test.
- prints the return code of test or a negative value if an earlier error occured:
    - -1: failed to clone the repo.
    - -2: mismatch detected between original in main.c and depot's main.c.
    - -3: failed to compile.
"""

import hashlib
import itertools
import os
import platform

import pygit2

def hash_test_code(main_path):
    """Hashes file main_path."""
    with open(main_path) as main:
        test_code_hash = hashlib.sha256()
        for line in main:
            test_code_hash.update(line.encode())
    return test_code_hash.hexdigest()

PROFESSOR_TEST_CODE_HEXDIGEST = '22c0d504a3335886a369d75f72f07474b1d10599c294b1b45770e9ffdbc43b95'
PROFESSOR_CHIFFRE_HEXDIGEST = '60ff41b09e4e1011d3a5f33704ec53df319a248d1de48250a131b809a85cb2db'
PROFESSOR_CLAIR_HEXDIGEST = '4ef57703aad7ffd9f3129bb46c81a15308f1963e1f12ab00718f3569fde090f3'
CALLBACKS = pygit2.RemoteCallbacks(credentials=pygit2.KeypairFromAgent("git"))

with open('depots.txt') as remote_depot_names:
    for remote_depot_name in itertools.dropwhile(lambda line: line.startswith('#'),
                                                 remote_depot_names):
        try:
            # Craft URL to clone given a depot name.
            remote_depot_name = remote_depot_name.rstrip()
            remote_depot_url = 'ssh://git@github.com/' + remote_depot_name + '.git'
            local_depot_path = remote_depot_name.replace('/', '-')
            print(local_depot_path, end=' ')

            # Clone the repo.
            if pygit2.clone_repository(remote_depot_url, local_depot_path, callbacks=CALLBACKS) \
                    is None:
                raise RuntimeError('-1')

            # Confirm test code is intact.
            if hash_test_code(local_depot_path + '/test/main.c') != PROFESSOR_TEST_CODE_HEXDIGEST or \
               hash_test_code(local_depot_path + '/test/chiffre.txt') != PROFESSOR_CHIFFRE_HEXDIGEST or \
               hash_test_code(local_depot_path + '/test/clair.txt') != PROFESSOR_CLAIR_HEXDIGEST:
                raise RuntimeError('-2')

            # Compile.
            if os.system('cd ' + local_depot_path + ' && make test') != 0:
                raise RuntimeError('-3')

            # Run and print result.
            print(str(os.WEXITSTATUS(os.system('cd ' + local_depot_path + ' && build/' + \
                      platform.system() + '/test'))))
        except pygit2.GitError:
            print('-1')
        except RuntimeError as error:
            print(error.args[0])
