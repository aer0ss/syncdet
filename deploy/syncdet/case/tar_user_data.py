import tarfile
import os
import errno
from syncdet import case

def tar_user_data():
    print "Tarring up user_data"
    tf = tarfile.open('user_data-{0}.tar'.format(case.actor_id()), "w")

    actor = case.local_actor()

    for attr in case._extra_args():
        d = getattr(actor, attr, None)
        if d is None:
            continue
        d = os.path.normpath(d)
        ed = os.path.expanduser(d)
        name = os.path.basename(d) + '-{0}'.format(case.actor_id())
        try:
            tf.add(ed, arcname=name)
            print "tar'd {0} as {1}".format(ed, name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                print "failed to tar {0} (not found)".format(ed)

    tf.close()

spec = { "default" : tar_user_data }
