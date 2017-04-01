svn-helper
============

Command line helper for commonly used svn commands.

Information
-----------

This script simplifies the commonly used svn commands. Basically it indexes the output, and user selects from these indexes to run specified command on them.

Usage
-----
Go to the working copy and run as following

```python
python svn_helper.py [option]
```

Available options
* **s**: svn status
* **d**: svn diff
* **dr**: revision diff
* **c**: svn commit
* **l**: svn log
* **dl**: directory log
* **a**: svn add
* **b** svn blame


This can be shortened with aliases defined in bashrc file like

```bash
alias sd="python svn_helper.py -d"
```
