import random, string, os.path, time, sys

# TODO: This should be more gracefully set up
_RAND_SEED = 0
random.seed(_RAND_SEED)


_MAX_DIRECTORY_INDEX = 100000000
_NUM_RAND_BITS = 31
_FILENAME_LEN = 30
_WIN32_DISALLOWED_TRAILING_CHARACTERS = ' .' # disallow spaces and dots


# @param root        the directory containing the tree to be created
# @param depth       0: make files in root, with no subdirectories
#                    1: make files in root, with one more level of subdirs
# @param nsubdirs    number of subdirectories for each directory
# @param nfiles      number of files per directory
# @param maxfilesize maximum file size, in bytes
#
def makeDirTree(root, depth, nsubdirs, nfiles, maxfilesize): 
    assert os.path.exists(root)

    while nfiles > 0:
        pass


def getRandDirname(prefix):
    return '{0}{1}'.format(prefix, random.getrandbits(_NUM_RAND_BITS)) 

def getRandFilename(allowTrailingDotSpace=True):
    validChars = string.letters + ' ' + '.'
    l = _FILENAME_LEN
    if allowTrailingDotSpace:
        fn = ''.join( random.sample(validChars * l, l) ) 
    else:
        l = _FILENAME_LEN - 1
        fn = ''.join( random.sample(validChars *l , l) ) \
           + ''.join( random.choice(list(set(validChars) 
                                - set(_WIN32_DISALLOWED_TRAILING_CHARACTERS))))
    return fn


_BLOCK_STR_LEN = 1024
_RAND_STRING_LEN = 32
_FILLER_SUFFIX = 'tr' + 'ol' * (_BLOCK_STR_LEN - _RAND_STRING_LEN - 2)

def writeFile(dirname, filename, maxfilesize):
    filepath = os.path.join(dirname, filename)
    with open(filepath, 'w') as f:

        # figure out the file length
        asize = random.randint(0, maxfilesize)

        # Determine the block size
        bsize = sys.getsizeof('a'*_RAND_STRING_LEN + _FILLER_SUFFIX)

        nblocks = asize / bsize

        startTime = time.time()

        while nblocks > 0:
            randstr = ''.join(random.sample(string.letters * _RAND_STRING_LEN,
                                            _RAND_STRING_LEN))
            f.write(randstr + _FILLER_SUFFIX)
            nblocks -= 1
        
        # write the remaining bytes (this will write on a per-byte basis)
        remBytes = asize - f.tell()
        while remBytes > 0:
            nchars = max(1, remBytes / 2)
            randstr = ''.join(random.sample(string.letters * nchars, nchars))
            f.write(randstr)
            remBytes = asize - f.tell()

        fsize = f.tell()
        print('asize:{0}, fsize:{1} for {2}'.format(asize, fsize, filepath))

        endTime = time.time()

        print('{0} sec for {1} MB'.format((endTime - startTime), 
                                          (fsize / (1024 * 1024))))

