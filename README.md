# Cppcheck-HIS-addon
HIS metric python addon for Cppcheck.

This addon depends on functionality provided by `cppcheckdata.py` which is part of Cppcheck `addons` directory.

This addon has been tested 
  - with Cppcheck v1.84 up to latest release v1.90
  - using Python 2.7.x as well as 3.7.x
  - on a machine running 64-bit Ubuntu 19.10
  - on a machine running 64-bit Windows 10

# Supported HIS metric checks
The following metrics are checked according to document `HIS source code metrics v1.3.1` .

| Metric | Description | Range | Note |
| ------ | ----------- |:-----:|:----:|
| HIS-COMF | Relationship of comments to number of statements | > 0.2 | |
| HIS-PATH | Number of non cyclic remark paths | 1-80 | |
| HIS-GOTO | Number of goto statements | 0 | |
| HIS-STCYC | Cyclomatic complexity v(G) of functions by McCabe | 1-10 | |
| HIS-CALLING | Number of subfunctions calling a function | 0-5 | |
| HIS-CALLS | Number of called functions excluding duplicates | 0-7 | |
| HIS-PARAM | Number of function parameters | 0-5 | |
| HIS-STMT | Number of statements per function | 1-50 | |
| HIS-LEVEL | Depth of nesting of a function | 0-4 | |
| HIS-RETURN | Number of return points within a function | 0-1 | |
| HIS-VOCF | Language scope | 1-4 | Experimental, low accuracy |
| HIS-NRECUR | Number of recursions | 0 | |

# Missing HIS metric checks
The following metrics part of document `HIS source code metrics v1.3.1` are not checked.

| Metric | Description | Note |
| ------ | ----------- |:-----:|
| HIS-SI | Stability index | No support planned |
| HIS-NOMV | Number of MISRA HIS Subset violations | No support planned |
| HIS-NOMVPR | Number of MISRA HIS Subset violations per rule | No support planned |
| HIS-SCHG | Number of changed statements | No support planned |
| HIS-SDEL | Number of deleted statements | No support planned |
| HIS-SNEW | Number of new statements | No support planned |


# Installation
Directories are the same as for Cppcheck addons.
  - Copy `his.py` to `addons` directory of Cppcheck installation.
  - Optional: For test purposes copy test pattern files from `addons/test` to corresponding directory of Cppcheck installation.

# Usage
Run `python his.py -h` or `python his.py --help` to get help on how to use HIS metric addon and show which command line options are available.

Example how to use HIS addon with HIS metric test pattern files on a Linux machine.

1. Create a dump file for the source files which are desired to be checked.

   `$> ~/cppcheck/cppcheck --dump ~/cppcheck/cppcheck/addons/test/his-test.c ~/cppcheck/cppcheck/addons/test/his-test-calling.c`

2. Run HIS metric checker using dump files created during previous step.

   `$> python ~/cppcheck/addons/his.py ~/cppcheck/cppcheck/addons/test/his-test.c.dump ~/cppcheck/cppcheck/addons/test/his-test-calling.c.dump`
