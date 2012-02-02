import random, string, os.path, time, sys, os

_MAX_DIRECTORY_INDEX = 100000000
_NUM_RAND_BITS = 31
_FILENAME_LEN = 30
_WIN32_DISALLOWED_TRAILING_CHARACTERS = ' .' # disallow spaces and dots


# @param seed        the seed to be used for all random calls
def init(seed):
    random.seed(seed)

# @param root        the directory containing the tree to be created
# @param depth       0: make files in root, with no subdirectories
#                    1: make files in root, with one more level of subdirs
# @param nsubdirs    number of subdirectories for each directory
# @param nfiles      number of files per directory
# @param maxfilesize maximum file size, in bytes
# @param randomize   randomize the file sizes and nsubdirs, nfiles, etc
#
def makeDirTree(root, depth, nsubdirs, nfiles, maxfilesize, randomize=False): 
    assert os.path.exists(root)
    assert depth >= 0

    for _ in xrange(0, nfiles):
        # Create a filename, determine a file size, then write content to file
        fpath = os.path.join(root, getRandFilename())
        if os.path.exists(fpath): 
            print 'Warning: file {0} is being overwritten.'.format(fpath)
        fsize = random.randint(0, maxfilesize) if randomize else maxfilesize
        writeFile(fpath, fsize)

    if depth > 0:
        for _ in xrange(0, nsubdirs):
            dpath = os.path.join(root, getRandDirname('d_'))
            os.mkdir(dpath)
            makeDirTree(dpath, depth-1, nsubdirs, 
                        nfiles, maxfilesize, randomize)
        


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


_IN_MEMORY_MAX = 100 * 1024 * 1024
_BLOCK_STR_LEN = 1024 # A prime number
_RAND_STRING_LEN = 32
_FILLER_SUFFIX = 'tr' + 'ol' * (_BLOCK_STR_LEN - _RAND_STRING_LEN - 2)

# @param fsize          desired file size in bytes
#
def writeFile(filepath, fsize):
    with open(filepath, 'w') as f:
        # Determine the block size in bytes
        bsize = sys.getsizeof('a'*_RAND_STRING_LEN + _FILLER_SUFFIX)
        nblocks = fsize / bsize
        nblocksInMem = _IN_MEMORY_MAX / bsize

        startTime = time.time()

        population = string.letters * _RAND_STRING_LEN
        while nblocks > 0:
            randstr = ''.join(random.sample(population, _RAND_STRING_LEN)) \
                      + _FILLER_SUFFIX
            f.write(randstr) 
            nblocks -= 1
            if nblocks % nblocksInMem == 0:
                f.flush()
                os.fsync(f.fileno())
        
        # write the remaining bytes 
        remBytes = fsize - f.tell()
        while remBytes > 0:
            # Since a python string may not map 1:1 to a byte,
            # conservatively generate filler
            nchars = max(1, remBytes / 2)
            
            if nchars > _RAND_STRING_LEN:
                randstr = ''.join(random.sample(population, _RAND_STRING_LEN)) \
                           + _FILLER_SUFFIX[:(nchars - _RAND_STRING_LEN)]
            else:
                randstr = ''.join(random.sample(population, nchars))

            f.write(randstr)
            f.flush()
            os.fsync(f.fileno())

            remBytes = fsize - f.tell()

        endTime = time.time()

        print('{2}:{0} sec for {1} MB'.format((endTime - startTime), 
                                          (fsize / (1024 * 1024)),
                                          filepath))

