#!/usr/bin/env python
import os
import sys
import shutil
from mercurial import ui
from mercurial import hg
from mercurial import commands
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def restore_original_dependecy_files( repo, **kwargs ):
    """
        The pre-commit hook script (toolshed_pre-commit_hook.py) created backup files called
        *.pre-commit-backup. This script (configured as pretxncommit hook) will restore the
        original files and remove the updated and commited intermediate files.

        Add the following to your .hgrc:

        [hooks]
        pretxncommit = python:.hg/toolshed_pretxncommit_hook.py:restore_original_dependecy_files
    """
    logging.info('Entering pretxncommit Hook: Cleaning temp files and restoring original data.')
    filename_categories = repo.status( clean=True, ignored=True, unknown=True )
    filepaths = [ item for sublist in filename_categories for item in sublist ]

    for filepath in filepaths:
        if os.path.split( filepath )[-1] in ['tool_dependencies.xml.pre-commit-backup', 'repository_dependencies.xml.pre-commit-backup']:
            ori_filepath = filepath.replace( '.pre-commit-backup', '' )
            if os.path.split( ori_filepath )[-1] in ['tool_dependencies.xml', 'repository_dependencies.xml']:
                os.remove( ori_filepath )
                shutil.move( filepath, ori_filepath )

if __name__ == "__main__":
    repo = hg.repository(vui.ui(), os.getcwd() )
    restore_original_dependecy_files( repo )
