#!/usr/bin/env python3
#
# HIS: HIS source code metric checkers
#
# Example usage of this addon (scan a sourcefile main.c)
# cppcheck --dump main.c
# python his.py main.c.dump
#

import argparse
import cppcheckdata
import sys
import re

VERIFY = ('-verify' in sys.argv)
VERIFY_EXPECTED = []
VERIFY_ACTUAL = []

KEYWORDS = {
    'auto',
    'break',
    'case',
    'char',
    'const',
    'continue',
    'default',
    'do',
    'double',
    'else',
    'enum',
    'extern',
    'float',
    'for',
    'goto',
    'if',
    'int',
    'long',
    'register',
    'return',
    'short',
    'signed',
    'sizeof',
    'static',
    'struct',
    'switch',
    'typedef',
    'union',
    'unsigned',
    'void',
    'volatile',
    'while'
}

# Formatted printf like function usable by Python 2.7.x and 3.x code.
def printf(format, *args):
    sys.stdout.write(format % args)

# Add error report entry
def reportError(token, severity, msg, id):
    if VERIFY:
        VERIFY_ACTUAL.append(str(token.linenr) + ':HIS-' + id)
    else:
        cppcheckdata.reportError(token, severity, msg, 'HIS', id)

# Is this a function call
def isFunctionCall(token):
    if not token.isName:
        return False
    if token.str in KEYWORDS:
        return False
    if (token.next is None) or token.next.str != '(' or token.next != token.astParent:
        return False
    return True

# Count line of statements in function
def numOfFunctionStatements(func, data):
    num_of_statements = 0
    for scope in data.scopes:
        if (scope.type == "Function") and (scope.function == func):
            token = scope.bodyStart.next
            current_line_nr = -1
            # Search function body and count statements
            while (token != None and token != scope.bodyEnd):
                # Ignore lines with just a opening or closing curly bracket
                if (token.str.startswith("{") or token.str.startswith("}")):
                    if (token.linenr != token.previous.linenr and token.linenr != token.next.linenr):
                        token = token.next
                        continue
                # Make sure to count each line just once
                if (current_line_nr != token.linenr):
                    num_of_statements += 1
                    current_line_nr = token.linenr
                token = token.next
    return num_of_statements

# HIS-COMF
# Relationship of comments to number of statements: > 0.2
def his_comf(data, rawTokens):
    lines_of_statements = 0
    lines_of_comments   = 0
    # Count line of statements in functions
    for func in data.functions:
        lines_of_statements += numOfFunctionStatements(func, data)

    # Count line of comments
    for token in rawTokens:
        if token.str.startswith("//"):
            lines_of_comments += 1
        elif token.str.startswith("/*"):
            lines_of_comments += (len(re.findall(r'x\s*\*', token.str)) + 1)

    #if (len(rawTokens) > 0 and lines_of_statements > 0 and (lines_of_comments / lines_of_statements) < 0.2):
    if ((lines_of_comments / lines_of_statements) < 0.2):
        printf("Lines of statements: %d\n", lines_of_statements)
        printf("Lines of comments:   %d\n", lines_of_comments)
        printf("HIS-COMF:            %.2f\n", lines_of_comments / lines_of_statements)        
        reportError(rawTokens[0], 'style', 'Relationship of comments to number of statements: > 0.2', 'COMF')

# HIS-GOTO
# Number of goto statements: 0
def his_goto(data):
    for token in data.tokenlist:
        if token.str == "goto":
            reportError(token, 'style', 'Number of goto Statements should be 0', 'GOTO')

# HIS-CALLS
# Number of called functions excluding duplicates: 0-7
def his_calls(data):
    for func in data.functions:
        # Search for scope of current function
        for scope in data.scopes:
            if (scope.type == "Function") and (scope.function == func):
                # Search function body for function calls
                token = scope.bodyStart
                func_calls = list()
                while (token != None and token != scope.bodyEnd and len(func_calls) < 8):
                    if isFunctionCall(token):
                        # Don't add duplicates
                        if (token.str not in func_calls):
                            func_calls.append(token.str)
                    token = token.next
                if (len(func_calls) > 7):
                    reportError(func.tokenDef, 'style', 'Number of called functions excluding duplicates: 0-7', 'CALLS')

# HIS-PARAM
# Number of function parameters: 0-5
def his_param(data):
    for func in data.functions:
        # Check number of function parameters
        if (len(func.argument) > 5):
            reportError(func.tokenDef, 'style', 'Number of function parameters: 0-5', 'PARAM')

# HIS-STMT
# Number of statements per function: 1-50
def his_stmt(data):
    num_of_statements = 0
    # Count line of statements in functions
    for func in data.functions:        
        num_of_statements = numOfFunctionStatements(func, data)
        if (num_of_statements > 50):
            reportError(func.tokenDef, 'style', 'Number of statements per function: 1-50', 'STMT')

# HIS-RETURN
# Number of return points within a function: 0-1
def his_return(data):
    for func in data.functions:
        # Search for scope of current function
        for scope in data.scopes:
            if (scope.type == "Function") and (scope.function == func):
                # Search function body for return key word
                token = scope.bodyStart
                num_return_points = 0
                while (token != None and token != scope.bodyEnd and num_return_points < 2):
                    if (token.str == "return"):
                        num_return_points += 1
                    token = token.next
                if (num_return_points > 1):
                    reportError(func.tokenDef, 'style', 'Number of return points within a function: 0-1', 'RETURN')

def get_args():
    parser = cppcheckdata.ArgumentParser()
    parser.add_argument("-verify", help=argparse.SUPPRESS, action="store_true")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    if args.verify:
        VERIFY = True

    if not args.dumpfile:
        if not args.quiet:
            print("no input files.")
        sys.exit(0)

    for dumpfile in args.dumpfile:
        if not args.quiet:
            print('Checking %s...' % dumpfile)

        data = cppcheckdata.parsedump(dumpfile)

        if VERIFY:
            VERIFY_ACTUAL = []
            VERIFY_EXPECTED = []
            for tok in data.rawTokens:
                if tok.str.startswith('//') and 'TODO' not in tok.str:
                    for word in tok.str[2:].split(' '):
                        if word.startswith("HIS-"):
                            VERIFY_EXPECTED.append(str(tok.linenr) + ':' + word)

        for cfg in data.configurations:
            if (len(data.configurations) > 1) and (not args.quiet):
                print('Checking %s, config %s...' % (dumpfile, cfg.name))
            his_comf(cfg, data.rawTokens)
            his_goto(cfg)
            his_param(cfg)
            his_stmt(cfg)
            his_return(cfg)
            his_calls(cfg)

        if VERIFY:
            for expected in VERIFY_EXPECTED:
                if expected not in VERIFY_ACTUAL:
                    print('Expected but not seen: ' + expected)
                    sys.exit(1)
            for actual in VERIFY_ACTUAL:
                if actual not in VERIFY_EXPECTED:
                    print('Not expected: ' + actual)
                    sys.exit(1)
