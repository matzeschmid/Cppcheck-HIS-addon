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

# Calculate nesting level of token scope regarding final scope
def calculateNestingLevel(data, token_scope, final_scope):
    nesting_level = 0
    scope = token_scope
    while (scope != None and scope != final_scope):
        scope = scope.nestedIn
        nesting_level += 1
    return nesting_level

# Determine the number of switch cases
def numOfSwitchCases(token):
	num_cases = 0
	while (token != None and token.str != "{"):
		token = token.next
	if (token != None):
		token_switch_end = token.link
	while (token != None and token != token_switch_end):
		if (token.str == "case"):
			num_cases += 1
		token = token.next
	return num_cases

# Determine if "while" keyword belongs to do-while loop
def isWhileOfDoWhile(token):
	ret_val = False
	if (token.str == "while" and token.previous.str == "}" and token.previous.scope.type == "Do"):
		ret_val = True
	return ret_val

# HIS-COMF
# Relationship of comments to number of statements: > 0.2
def his_comf(data, rawTokens):
    # Set line of statements initial/minimum value to 1.0
    # to avoid division by zero.
    lines_of_statements = 1.0
    lines_of_comments   = 0.0
    # Count line of statements in functions
    for func in data.functions:
        lines_of_statements += numOfFunctionStatements(func, data)

    # Count line of comments
    for token in rawTokens:
        if token.str.startswith("//"):
            lines_of_comments += 1
        elif token.str.startswith("/*"):
            lines_of_comments += (len(re.findall(r'x\s*\*', token.str)) + 1)

    if ((lines_of_comments / lines_of_statements) < 0.2):
        printf("Lines of statements: %d\n", lines_of_statements)
        printf("Lines of comments:   %d\n", lines_of_comments)
        printf("HIS-COMF:            %.2f\n", lines_of_comments / lines_of_statements)        
        reportError(rawTokens[0], 'style', 'Relationship of comments to number of statements: > 0.2', 'COMF')

# HIS-PATH
# Number of non cyclic remark paths: 1-80
def his_path(data):
	for func in data.functions:
        # Search for scope of current function
		for scope in data.scopes:
			if (scope.type == "Function") and (scope.function == func):
				# Calculate number of non cyclic remark paths for function body
				num_paths = 1
				token = scope.bodyStart
				while (token != None and token != scope.bodyEnd):
					if (token.str in ["if", "for", "do"]):
						num_paths *= 2
					elif (token.str == "while" and isWhileOfDoWhile(token) == False):
						num_paths *= 2
					elif (token.str == "switch"):
						num_paths *= (1 + numOfSwitchCases(token))
					token = token.next
				if (num_paths > 80):
					reportError(func.tokenDef, 'style', 'Number of non cyclic remark paths: 1-80', 'PATH')

# HIS-GOTO
# Number of goto statements: 0
def his_goto(data):
    for token in data.tokenlist:
        if token.str == "goto":
            reportError(token, 'style', 'Number of goto Statements should be 0', 'GOTO')

# HIS-STCYC
# Cyclomatic complexity v(G) of functions by McCabe: 1-10
def his_stcyc(data):
	for func in data.functions:
        # Search for scope of current function
		for scope in data.scopes:
			if (scope.type == "Function") and (scope.function == func):
				# Calculate cyclomatic complexity for function body
				vG = 0
				num_nodes = 2
				num_edges = 1
				num_components = 1
				token = scope.bodyStart
				while (token != None and token != scope.bodyEnd):
					if (token.str in ["for", "while", "do"]):
						num_nodes += 3
						num_edges += 4
					elif (token.str == "if"):
						num_nodes += 3
						num_edges += 4
					elif (token.str == "else"):
						num_nodes += 1
						num_edges += 1
					elif (token.str == "switch"):
						num_nodes += 2
						num_edges += 1
					elif (token.str in ["case", "default"]):
						num_nodes += 1
						num_edges += 2
					token = token.next
						
				vG = num_edges - num_nodes + (2 * num_components)
				#printf("Function name: %s\n", func.name)
				#printf("edges: %d, nodes: %d, vG: %d\n\n", num_edges, num_nodes, vG);
				if (vG > 10):
					reportError(func.tokenDef, 'style', 'Cyclomatic complexity v(G) of functions by McCabe: 1-10', 'STCYC')

# HIS-CALLING
# Number of subfunctions calling a function: 0-5
def his_calling(data):
    funcdict = dict()
    for func in data.functions:
        # Add function to dictionary and set called counter to 0
        funcdict[func] = 0
    for func in data.functions:
        # Search for scope of current function
        for scope in data.scopes:
            if (scope.type == "Function") and (scope.function == func):
                # Search function body for function calls reduced
                # by duplicates
                token = scope.bodyStart
                called_funcs = list()
                while (token != None and token != scope.bodyEnd):
                    if isFunctionCall(token):
                        if (token.function in funcdict and token.function not in called_funcs):
                            called_funcs.append(token.function)                            
                    token = token.next
                for func_call in called_funcs:
                    funcdict[func_call] = funcdict[func_call] + 1
    for func in funcdict:
        # printf("%s : %d\n", func.name, funcdict[func])
        if (funcdict[func] > 5):
            reportError(func.tokenDef, 'style', 'Number of subfunctions calling a function: 0-5', 'CALLING')

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

# HIS-LEVEL
# Depth of nesting of a function: 0-4
def his_level(data):
    for func in data.functions:
        # Search for scope of current function
        for scope in data.scopes:
            if (scope.type == "Function") and (scope.function == func):
                # Search function body and calculate nesting depth                
                token = scope.bodyStart
                while (token != None and token != scope.bodyEnd):                    
                    if (token.str not in ["if", "switch", "for", "while", "do"]):
                        token = token.next
                        continue
                    # Ignore while of do-while loop
                    if (token.str == "while" and isWhileOfDoWhile(token) == True):
                        token = token.next
                        continue
                    token_compound_stm = token
                    # Walk forward through token list until open curly
                    # bracket of scope has been reached.
                    while (token != None and token.str != "{"):
                        token = token.next
                    # Calculate nesting level of current scope
                    if (token != None):
                        # Nesting level starts at depth 1 for function entry
                        nesting_level = 1
                        nesting_level += calculateNestingLevel(data, token.scope, scope)
                        if (nesting_level > 4):
                            reportError(token_compound_stm, 'style', 'Depth of nesting of a function: 0-4', 'LEVEL')

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

	# Since Cppcheck version 1.90 some command line options are already handled
    # by cppcheckdata.ArgumentParser().
    # Thus check first to avoid conflicts by adding options twice and to make
    # this script backward compatible. 
    args, rest = parser.parse_known_args()
    if not hasattr(args, 'dumpfile'):
        parser.add_argument("dumpfile", nargs='*', help="Path of dump files from cppcheck")
    if not hasattr(args, 'quiet'):
        parser.add_argument('-q', '--quiet', action='store_true', help='do not print "Checking ..." lines')
    if not hasattr(args, 'cli'):
        parser.add_argument('--cli', help='Addon is executed from Cppcheck', action='store_true')
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
            his_path(cfg)
            his_goto(cfg)
            his_stcyc(cfg)
            his_calling(cfg)
            his_calls(cfg)
            his_param(cfg)
            his_stmt(cfg)
            his_level(cfg)
            his_return(cfg)

        if VERIFY:
            for expected in VERIFY_EXPECTED:
                if expected not in VERIFY_ACTUAL:
                    print('Expected but not seen: ' + expected)
                    sys.exit(1)
            for actual in VERIFY_ACTUAL:
                if actual not in VERIFY_EXPECTED:
                    print('Not expected: ' + actual)
                    sys.exit(1)
