import tarfile
import os
from syncdet import case

def tar_user_data():
    print "Tarring up user_data"
    tf = tarfile.open('user_data-{0}.tar'.format(case.actor_id()), "w" )
    name="user_data-{0}".format(case.actor_id())
    tf.add(os.path.expanduser("~/syncdet/user_data"),arcname=name)
    tf.close()

spec = { "default" : tar_user_data }
