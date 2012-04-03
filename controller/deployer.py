#############################################################################
# Deployment Functions:
# - to deploy test case source code to actors
# - to deploy test case source and scenarios to actors
#############################################################################
import os.path, multiprocessing
import controller
from deploy.syncdet import actors, param

def deploy():
    '''Deploy all the deployment folders.
    @param deployFolders: type a list of strings. specifies the user-defined
    folders to deploy.
    '''
    print "deploying...",

    pool = multiprocessing.Pool()
    pool.map(_rsync, actors.getActors())

    print "done"

def _rsync(actor):
    '''@param actor: type: actors.Actor'''
    dst = os.path.join(actor.root, param.DEPLOY_DIR)
    actor.rsync(controller.getDeployFolders(), dst, False)
