#!/usr/bin/env python
import os
import sys
import xml.etree.ElementTree as ET
from mercurial import ui
from mercurial import hg
from mercurial import commands
from mercurial import patch
from mercurial.node import hex, short
import shutil
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class CommentedTreeBuilder( ET.XMLTreeBuilder ):
    """
        We need an adopted version of the TreeBuilder
        to not touch comments included in the XML definitions.
    """
    def __init__ ( self, html=0, target=None ):
        ET.XMLTreeBuilder.__init__( self, html, target )
        self._parser.CommentHandler = self.handle_comment

    def handle_comment ( self, data ):
        self._target.start( ET.Comment, {} )
        self._target.data( data )
        self._target.end( ET.Comment )

def get_latest_repo_rev( url ):
    """
        look up the latest mercurial tip revision
    """
    hexfunc = ui.ui().debugflag and hex or short
    repo = hg.repository( ui.ui(), url )
    tip = hexfunc( repo.lookup( 'tip' ) )
    return tip

def add_latest_rev_and_toolshed(repo, **kwargs):
    """
        Iterating over all, but the ignored mercurial files. If a file is called
        tool_dependencies.xml or repository_dependencies.xml we check if 
        'changeset_revision' and/or 'toolshed' is not set or empty and insert
        the latest revision of the corresponding repo (repo-name/owner/tooshed).
        The default tool_shed url is hardcoded and can be changed.
        This hook creates a backup of the original file, replaces revision number
        and toolshed and commit the adopted changes.
        To restore the backup files use the additional script (toolshed_pretxncommit_hook.py) 
        as pretxncommit-hook.

        Add the following to your .hgrc:

        [hooks]
        pre-commit = python:.hg/toolshed_pre-commit_hook.py:add_latest_rev_and_toolshed
    """
    toolshed_url = "http://testtoolshed.g2.bx.psu.edu/"

    logging.info('Emtering pre-commit Hook: Updating "toolshed" and/or "changeset_revision" attribute.')
    filename_categories = repo.status( clean=True )
    filepaths = [item for sublist in filename_categories for item in sublist]

    backup_files = list()
    for filepath in filepaths:
        if os.path.split( filepath )[-1] in ['tool_dependencies.xml', 'repository_dependencies.xml']:
            tree = ET.parse( filepath, parser = CommentedTreeBuilder() )
            root = tree.getroot()
            change = False
            for repo_dep in root.iter('repository'):
                if repo_dep.attrib.get('changeset_revision', '') == '':
                    logging.info('Change *changeset_revision* of [%s]\n in file: %s\n and repository: %s' % ('%s :: %s' % (repo_dep.attrib['owner'], repo_dep.attrib['name']), filepath, repo.url()))
                    tip = get_latest_repo_rev( '%srepos/%s/%s' % (toolshed_url, repo_dep.attrib['owner'], repo_dep.attrib['name']) )
                    repo_dep.attrib.update({'changeset_revision': "%s" % tip})
                    change = True
                if repo_dep.attrib.get('toolshed', '') == '':
                    logging.info('Change *toolshed* of [%s]\n in file: %s\n and repository: %s' % ('%s :: %s' % (repo_dep.attrib['owner'], repo_dep.attrib['name']), filepath, repo.url()))
                    repo_dep.attrib.update({'toolshed': "http://testtoolshed.g2.bx.psu.edu/"})
                    change = True
            if change:
                backup_filepath = '%s.pre-commit-backup' % filepath
                backup_files.append( backup_filepath )
                shutil.move( filepath, backup_filepath )
                tree.write( filepath, xml_declaration=True, encoding='utf-8' )
                logging.info('Add %s to repository: %s' % (filepath, repo.url()))
                commands.add( ui.ui(), repo, filepath )

    # check if there is anything to commit
    if not [diff for diff in patch.diff(repo)]:
        logging.info( 'Nothing to commit for repository: %s.' % repo.url() )
        # if nothing to commit, restore the original files
        # these is necessary because I could not find a 'nothing to commit'-hook
        for backup_file in backup_files:
            if os.path.split( backup_file )[-1] in ['tool_dependencies.xml.pre-commit-backup', 'repository_dependencies.xml.pre-commit-backup']:
                ori_filepath = backup_file.replace('.pre-commit-backup', '')
                if os.path.split( ori_filepath )[-1] in ['tool_dependencies.xml', 'repository_dependencies.xml']:
                    os.remove( ori_filepath )
                    shutil.move( backup_file, ori_filepath )
        # abort the commit, because nothing is to commit
        sys.exit(1)

if __name__ == "__main__":
    repo = hg.repository(ui.ui(), os.getcwd())
    add_latest_rev_and_toolshed( repo )

