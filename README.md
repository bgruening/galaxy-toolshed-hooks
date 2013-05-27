Galaxy Toolshed Hooks
=====================

Here you can find [mercurial] hooks for an easy deployment of large and complex [toolshed] repositories, like [ChemicalToolBoX]. 
If you have meta-packages with several dependent orphan tool dependencies and tool repositories updating can be complicated.

These hooks will make it easier for you! 
The idea is to automatically update definitions of repository dependencies such as:
```XML
<repository changeset_revision="a6b8f46acca7" name="package_lapack_3_4" owner="bgruening" toolshed="http://testtoolshed.g2.bx.psu.edu/" />
```

To have a fully functional repository defintion you need at least the repository's **name** and the **owner**: ` name="package_lapack_3_4" owner="bgruening" ` 

**changeset_revision** and **toolshed** will change frequently.
With the pre-commit hook we are updating ...

  - the changeset_revision attribute to the latest version available
  - the [toolshed] attribute

... automatically before the actual commit is done.
Using this makes your `tool_dependencies.xml` or `repository_dependencies.xml` more readable and maintainable.

```XML
<repository name="package_lapack_3_4" owner="bgruening" />
```

Version
-------
0.1

License
-------
GPLv3

Installation
------------

1. Update you *.hgrc* file with the following lines. Adopt the path to your `toolshed_pre-commit_hook.py` and `toolshed_pretxncommit_hook.py` accordingly.

 ```ini
[auth]
ts.prefix =  http://testtoolshed.g2.bx.psu.edu/
ts.username = <toolshed username>
ts.password = <toolshed password>
[hooks]
pre-commit = python:~/toolshed_pre-commit_hook.py:add_latest_rev_and_toolshed
pretxncommit = python:~/toolshed_pretxncommit_hook.py:restore_original_dependecy_files
 ```

2. Add `.pre-commit-backup` to your `.hgignore` file.

3. *add* and *commit* your changes. All missing or empty *changeset_revision* and *toolshed* attributes will be set.
 ```sh
    hg status -mn -0 | xargs -0 hg add
    hg commit -m "Complex update!"
    hg push
 ```

In conjunction with a small script and the right order of your repositories you can update your entire metapackage in one step.
```python
for directory in ['./first_repo', './second_repo']:
    with lcd( directory ):
        # only update modified files, new files needs to be added manually
        local('hg status -mn -0 | xargs -0 hg add')
        with settings(warn_only=True):
            #can fail: In the case of 'no changes' we abort the commit with sys.exit(1)
            local('hg commit -m "ChemicalToolBoX update."')
            local('hg push')
```
  [mercurial]: http://mercurial.selenic.com/
  [ChemicalToolBoX]: http://bgruening.github.io/galaxytools/projects/chemicaltoolbox/
  [toolshed]: http://wiki.galaxyproject.org/Tool%20Shed
