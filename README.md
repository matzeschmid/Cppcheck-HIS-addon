# Cppcheck-HIS-addon
HIS metric python addon for Cppcheck

# Supported HIS metric checks
The follwing metrics are checked according to document `HIS source code metrics v1.3.1` .

| Metric | Description | Range |
| ------ | ----------- |:-----:|
| HIS-COMF | Relationship of comments to number of statements | > 0.2 |
| HIS-GOTO | Number of goto statements | 0 |
| HIS-CALLS | Number of called functions excluding duplicates | 0-7 |
| HIS-PARAM | Number of function parameters | 0-5 |
| HIS-STMT | Number of statements per function | 1-50 |
| HIS-LEVEL | Depth of nesting of a function | 0-4 |
| HIS-RETURN | Number of return points within a function | 0-1 |


# Installation
The directories are the same as for Cppcheck addons.
Thus just copy the files to the corresponding directories of Cppcheck installation.

# Usage
Example how to use HIS addon with HIS metric test pattern file on a Linux machine.

1. Create a dump file for the source files which are desired to be checked.

   `$> ~/cppcheck/cppcheck --dump ~/cppcheck/cppcheck/addons/test/his-test.c`

2. Run HIS metric checker using dump files created during previous step.

   `$> python ~/cppcheck/addons/his.py ~/cppcheck/cppcheck/addons/test/his-test.c.dump`
