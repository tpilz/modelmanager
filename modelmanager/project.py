"""Core project components of a modelmanager project.

The Project class is the only exposed object of the modelmanager package. If
extending modelmanager for your model, you can inherit this class.

Project setup with the provided commandline script (calls 'initialise' below):
modelmanager --projectdir=.

"""

import os
from os import path as osp
import shutil

from modelmanager.settings import SettingsManager


class Project(object):
    """The central project object.

    All variables and fuctions are available to operate on the current model
    state.
    """
    # defaults
    settings_file = 'settings.py'

    def __init__(self, projectdir='.', **settings):
        self.projectdir = projectdir
        # initalise settings
        self.settings = SettingsManager(self)
        # load settings with overridden settings
        self.settings.load(**settings)
        return


def setup(projectdir='.', resourcedir='mm'):
    """Initialise a default modelmanager project in the current directory."""

    resourcedir = osp.join(projectdir, resourcedir)
    settings_path = osp.join(resourcedir, Project.settings_file)
    print('Initialising a new modelmanager project in: %s\n' % projectdir +
          'with modelmanager files in: %s' % settings_path)
    # create projectdir if not existing
    if not osp.exists(projectdir):
        os.mkdir(projectdir)
    # create resource dir if it does not exist, raise error otherwise
    ermg = ('The modelmanager resource directory seems to exist already:\n' +
            resourcedir)
    assert not osp.exists(resourcedir), ermg

    default_resources = osp.join(osp.dirname(__file__), 'resources')
    shutil.copytree(default_resources, resourcedir)

    # load project and update/create database
    pro = Project(projectdir)

    return pro


class ProjectDoesNotExist(Exception):
    pass
