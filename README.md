# Cppcheck-HIS-addon
HIS metric python addon for Cppcheck

This addon has been tested on a machine running 64-bit Ubuntu 19.10 with Cppcheck v1.84 up to latest release v1.90 .

# Supported HIS metric checks
The following metrics are checked according to document `HIS source code metrics v1.3.1` .

| Metric | Description | Range |
| ------ | ----------- |:-----:|
| HIS-COMF | Relationship of comments to number of statements | > 0.2 |
| HIS-PATH | Number of non cyclic remark paths | 1-80 |
| HIS-GOTO | Number of goto statements | 0 |
| HIS-STCYC | Cyclomatic complexity v(G) of functions by McCabe | 1-10 |
| HIS-CALLING | Number of subfunctions calling a function | 0-5 |
| HIS-CALLS | Number of called functions excluding duplicates | 0-7 |
| HIS-PARAM | Number of function parameters | 0-5 |
| HIS-STMT | Number of statements per function | 1-50 |
| HIS-LEVEL | Depth of nesting of a function | 0-4 |
| HIS-RETURN | Number of return points within a function | 0-1 |

# Missing HIS metric checks
The following metrics part of document `HIS source code metrics v1.3.1` are not checked yet.

| Metric | Description | Note |
| ------ | ----------- |:-----:|
| SI | Stability index | No plans for support |
| VOCF | Language scope | Might be supported by a future version |
| NOMV | Number of MISRA HIS Subset violations | No plans for support |
| NOMVPR | Number of MISRA HIS Subset violations per rule | No plans for support |
| NRECUR | Number of recursions | Might be supported by a future version |
| SCHG | Number of changed statements | No plans for support |
| SDEL | Number of deleted statements | No plans for support |
| SNEW | Number of new statements | No plans for support |


# Installation
The directories are the same as for Cppcheck addons.
Thus just copy the files to the corresponding directories of Cppcheck installation.

# Usage
Example how to use HIS addon with HIS metric test pattern file on a Linux machine.

1. Create a dump file for the source files which are desired to be checked.

   `$> ~/cppcheck/cppcheck --dump ~/cppcheck/cppcheck/addons/test/his-test.c`

2. Run HIS metric checker using dump files created during previous step.

   `$> python ~/cppcheck/addons/his.py ~/cppcheck/cppcheck/addons/test/his-test.c.dump`
