import tarfile
import os
from syncdet import case

def tar_user_data():
    print "Tarring up user_data"
    with tarfile.TarFile('user_data-{0}.tar'.format(case.actor_id()), "w" ) as tf:
        name="user_data-{0}".format(case.actor_id())
        tf.add(os.path.expanduser("~/syncdet/user_data"),arcname=name)

spec = { "default" : tar_user_data }
