# Cppcheck-HIS-addon
HIS metric python addon for Cppcheck

# Installation
The directories are the same as for Cppcheck.
Thus copy the files to the corresponding directories of Cppcheck installation.

# Usage
Example how to use it on a Linux machine.

1. Create a dump file for the source files which are desired to be checked.
> ~/cppcheck/cppcheck --dump main.c

2. Run HIS metric checker using dump files created during previous step.
> python ~/cppcheck/addons\his.py" main.c.dump
