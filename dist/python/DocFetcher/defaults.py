"""
This module is to allow distro maintainers to patch it according to the conventions used in the distro.
One should implement an own subclass of DirManager and import it here as ChosenDirManager.
"""

# pylint:disable=unused-import

from .dir_managers import PortableDirManager as ChosenDirManager
