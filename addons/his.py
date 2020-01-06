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


# Formatted printf like function usable by Python 2.7.x and 3.x code.
def printf(format, *args):
    sys.stdout.write(format % args)


# HIS metric checker class
class HisMetricChecker():
    # List to store location of expected rule/metric violations.
    # Used for script verification
    verify_expected = []

    # List to store location of actual rule/metric violations.
    # Used for script verification
    verify_actual = []

    # C/C++ keywords
    keywords = {
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

    closing_pairwise_operators = {
        ']',
        ')',
        '}',
    }

    operators = {
        '[]',
        '(',
        '{',
        '.',
        '->',
        '++',
        '--',
        'sizeof',
        '&',
        '*',
        '+',
        '-',
        '~',
        '!',
        '/',
        '%',
        '<<',
        '>>',
        '<',
        '<=',
        '>',
        '>=',
        '==',
        '!=',
        '|',
        '^',
        '&&',
        '||',
        '?',
        ':',
        '=',
        '*=',
        '/=',
        '%=',
        '+=',
        '-=',
        '<<=',
        '>>=',
        '&=',
        '^=',
        '|=',
        ',',
        ';'
    }

    # Dictionary to store HIS metric violation statistics counter.
    # If a metric is suppressed this will be stored instead of
    # counter value.
    his_stats = {
        'COMF'   : 0,
        'PATH'   : 0,
        'GOTO'   : 0,
        'STCYC'  : 0,
        'CALLING': 0,
        'CALLS'  : 0,
        'PARAM'  : 0,
        'STMT'   : 0,
        'LEVEL'  : 0,
        'RETURN' : 0,
        'VOCF'   : 0,
        'NRECUR' : 0
    }

    # command line arguments
    args = None

    # Metric suppression list
    suppression_list = list()

    # Dictionary to store number of times a function
    # is called from different function scopes.
    function_calls = dict()

    # List of functions defined in dump file(s)
    function_list = list()

    # list of statistics output
    statistics_list = list()

    # Dictionary to store list of functions called by
    # function referenced by key
    functions_called = dict()

    # list of distinct operators
    distinct_operator_list = list()

    # sum of operators
    sum_of_operators = 0

    # list of distinct operands
    distinct_operand_list = list()

    # sum of operands
    sum_of_operands = 0

    # Constructor of His metric checker
    def __init__(self, args):
        self.args = args

        # Setup metric suppression list
        if args.suppress_metrics:
            self.suppression_list = args.suppress_metrics.split(',')
            for idx in range(0, len(self.suppression_list)):
                self.suppression_list[idx] = self.suppression_list[idx].upper()
                if self.suppression_list[idx] in self.his_stats:
                    self.his_stats[self.suppression_list[idx]] = "Suppressed"

    # Object representation
    def __repr__(self):
        attrs = ["verify_expected", "verify_actual", "keywords", "his_stats",
                 "args", "suppression_list", "function_calls", "function_list",
                 "statistics_list"]
        return "{}({})".format(
            "HisMetricChecker",
            ", ".join(("{}={}".format(a, repr(getattr(self, a))) for a in attrs))
        )

    # Execute metric check if not suppressed
    def execute_metric_check(self, metric_name, metric_function, *func_args):
        if self.his_stats[metric_name] != "Suppressed":
            metric_function(*func_args)

    # Run the HIS metric check according to command line option settings
    def run_checks(self):
        num_raw_tokens = 0

        # Remove duplicates from dump file list
        self.args.dumpfile = list(dict.fromkeys(self.args.dumpfile))
        # Run metric checks for each dump file
        for dumpfile in self.args.dumpfile:
            if not self.args.quiet:
                printf("Checking %s...\n", dumpfile)
            self.statistics_list.append(dumpfile)
            data = cppcheckdata.parsedump(dumpfile)
            if self.args.verify:
                for token in data.rawTokens[num_raw_tokens:]:
                    if token.str.startswith('//') and 'TODO' not in token.str:
                        for word in token.str[2:].split(' '):
                            if word.startswith("HIS-"):
                                self.verify_expected.append(token.file + ':' + str(token.linenr) + ':' + word)

            cfg_idx = 0
            for cfg in data.configurations:
                if len(data.configurations) > 1 and not self.args.quiet:
                    printf("Checking %s, config %s...\n",dumpfile, cfg.name)
                self.execute_metric_check("COMF", self.his_comf, cfg, data.rawTokens[num_raw_tokens:])
                self.execute_metric_check("PATH", self.his_path, cfg)
                self.execute_metric_check("GOTO", self.his_goto, cfg)
                self.execute_metric_check("STCYC", self.his_stcyc, cfg)
                self.execute_metric_check("CALLING", self.his_calling, cfg)
                self.execute_metric_check("CALLS", self.his_calls, cfg)
                self.execute_metric_check("PARAM", self.his_param, cfg)
                self.execute_metric_check("STMT", self.his_stmt, cfg)
                self.execute_metric_check("LEVEL", self.his_level, cfg)
                self.execute_metric_check("RETURN", self.his_return, cfg)
                if (cfg_idx < 1):
                    self.execute_metric_check("VOCF", self.his_vocf, cfg)
                cfg_idx = cfg_idx + 1
            num_raw_tokens = len(data.rawTokens)

        if not self.args.quiet:
            printf("Checking metrics for all dump files...\n")
        # Check for violations of HIS-CALLING after all dump files have been analyzed.
        self.execute_metric_check("CALLING", self.his_calling_result)
        # Check for violation of HIS-VOCF after all dump files have been analyzed.
        self.execute_metric_check("VOCF", self.his_vocf_result)
        # Check for violations of HIS-NRECUR after all dump files have been analyzed.
        self.execute_metric_check("NRECUR", self.his_num_recursions)

        if self.args.verify:
            for expected in self.verify_expected:
                if expected not in self.verify_actual:
                    printf("Expected but not seen: %s\n", expected)
            for actual in self.verify_actual:
                if actual not in self.verify_expected:
                    printf("Not expected: %s\n", actual)

        # Print summary if not suppressed by command line
        if not self.args.no_summary and not self.args.verify:
            printf("\n---------------------------\n")
            printf("--- Summary of violations\n")
            printf("---------------------------\n")
            for key in self.his_stats:
                if (self.his_stats[key] == "Suppressed"):
                    printf("HIS-%s: %s\n", key.ljust(10), self.his_stats[key])
                else:
                    printf("HIS-%s: %d\n", key.ljust(10), self.his_stats[key])
            printf("\n")

        if self.args.statistics and not self.args.verify:
            printf("\n---------------------------\n")
            printf("--- Statistics information\n")
            printf("---------------------------\n")
            for item in self.statistics_list:
                printf("%s\n", item)
            printf("\n")

    # Add error report entry
    def reportError(self, token, severity, msg, id):
        if token is None:
            sys.stderr.write('[' + 'All files' + ':' + '---' +
                             '] (' + severity + ') ' + msg + ' [HIS-' + id +
                             ']\n')
        else:
            if self.args.verify:
                self.verify_actual.append(token.file + ':' + str(token.linenr) + ':HIS-' + id)
            else:
                try:
                    cppcheckdata.reportError(token, severity, msg, 'HIS', id)
                except ValueError:
                    sys.stderr.write('[' + token.file + ':' + str(token.linenr) +
                                     '] (' + severity + ') ' + msg + ' [HIS-' + id +
                                     ']\n')
        self.his_stats[id] = self.his_stats[id] + 1

    # Is this a function call
    def isFunctionCall(self, token):
        if not token.isName:
            return False
        if token.str in self.keywords:
            return False
        if token.next is None or token.next.str != '(' or token.next != token.astParent:
            return False
        return True

    # Does the scope match the function object
    def scopeMatchesFunction(self, scope, func):
        ret_val = False
        if hasattr(scope, 'function'):
            if scope.function == func:
                ret_val = True
        elif scope.className == func.name:
            ret_val = True

        return ret_val

    # Count line of statements in function
    def numOfFunctionStatements(self, func, data):
        num_of_statements = 0
        for scope in data.scopes:
            if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                token = scope.bodyStart.next
                current_line_nr = -1
                # Search function body and count statements
                while token is not None and token != scope.bodyEnd:
                    # Ignore lines with just a opening or closing curly bracket
                    if token.str.startswith("{") or token.str.startswith("}"):
                        if token.linenr != token.previous.linenr and token.linenr != token.next.linenr:
                            token = token.next
                            continue
                    # Make sure to count each line just once
                    if current_line_nr != token.linenr:
                        num_of_statements += 1
                        current_line_nr = token.linenr
                    token = token.next
        return num_of_statements

    # Calculate nesting level of token scope regarding final scope
    def calculateNestingLevel(self, data, token_scope, final_scope):
        nesting_level = 0
        scope = token_scope
        while scope is not None and scope != final_scope:
            scope = scope.nestedIn
            nesting_level += 1
        return nesting_level

    # Determine the number of switch cases
    def numOfSwitchCases(self, token):
        num_cases = 0
        while token is not None and token.str != "{":
            token = token.next
        if token is not None:
            token_switch_end = token.link
        while token is not None and token != token_switch_end:
            if token.str == "case":
                num_cases += 1
            token = token.next
        return num_cases

    # Determine if "while" keyword belongs to do-while loop
    def isWhileOfDoWhile(self, token):
        ret_val = False
        if token.str == "while" and token.previous.str == "}" and token.previous.scope.type == "Do":
            ret_val = True
        return ret_val

    # HIS-COMF
    # Relationship of comments to number of statements: > 0.2
    def his_comf(self, data, rawTokens):
        # Set line of statements initial/minimum value to 1.0
        # to avoid division by zero.
        lines_of_statements = 1.0
        lines_of_comments = 0.0
        # Count line of statements in functions
        for func in data.functions:
            lines_of_statements += self.numOfFunctionStatements(func, data)

        # Count line of comments
        for token in rawTokens:
            if token.str.startswith("//"):
                lines_of_comments += 1
            elif token.str.startswith("/*"):
                lines_of_comments += (len(re.findall(r'x\s*\*', token.str)) + 1)

        self.statistics_list.append("Lines of statements: %d" % lines_of_statements)
        self.statistics_list.append("Lines of comments:   %d" % lines_of_comments)
        self.statistics_list.append("HIS-COMF:            %.2f" % (lines_of_comments / lines_of_statements))
        if (lines_of_comments / lines_of_statements) < 0.2:
            self.reportError(rawTokens[0], 'style', 'Relationship of comments to number of statements: > 0.2', 'COMF')

    # HIS-PATH
    # Number of non cyclic remark paths: 1-80
    def his_path(self, data):
        for func in data.functions:
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Calculate number of non cyclic remark paths for function body
                    num_paths = 1
                    token = scope.bodyStart
                    while token is not None and token != scope.bodyEnd:
                        if token.str in ["if", "for", "do"]:
                            num_paths *= 2
                        elif token.str == "while" and not self.isWhileOfDoWhile(token):
                            num_paths *= 2
                        elif token.str == "switch":
                            num_paths *= (1 + self.numOfSwitchCases(token))
                        token = token.next
                    self.statistics_list.append("HIS-PATH  - %s: %d" % (func.name.ljust(50), num_paths))
                    if num_paths > 80:
                        self.reportError(func.tokenDef, 'style', 'Number of non cyclic remark paths: 1-80', 'PATH')

    # HIS-GOTO
    # Number of goto statements: 0
    def his_goto(self, data):
        for token in data.tokenlist:
            if token.str == "goto":
                self.reportError(token, 'style', 'Number of goto Statements should be 0', 'GOTO')

    # HIS-STCYC
    # Cyclomatic complexity v(G) of functions by McCabe: 1-10
    def his_stcyc(self, data):
        for func in data.functions:
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Calculate cyclomatic complexity for function body
                    vG = 0
                    num_nodes = 2
                    num_edges = 1
                    num_components = 1
                    token = scope.bodyStart
                    while token is not None and token != scope.bodyEnd:
                        if token.str in ["for", "while", "do"]:
                            num_nodes += 3
                            num_edges += 4
                        elif token.str == "if":
                            num_nodes += 3
                            num_edges += 4
                        elif token.str == "else":
                            num_nodes += 1
                            num_edges += 1
                        elif token.str == "switch":
                            num_nodes += 2
                            num_edges += 1
                        elif token.str in ["case", "default"]:
                            num_nodes += 1
                            num_edges += 2
                        token = token.next
                    vG = num_edges - num_nodes + (2 * num_components)
                    self.statistics_list.append("HIS-STCYC - %s: %d (edges: %d, nodes: %d)" % (func.name.ljust(50), vG, num_edges, num_nodes))
                    if vG > 10:
                        self.reportError(func.tokenDef, 'style', 'Cyclomatic complexity v(G) of functions by McCabe: 1-10', 'STCYC')

    # HIS-CALLING
    # Number of subfunctions calling a function: 0-5
    def his_calling(self, data):
        for func in data.functions:
            self.function_list.append(func)
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Search function body for function calls reduced
                    # by duplicates
                    token = scope.bodyStart
                    called_funcs = list()
                    while token is not None and token != scope.bodyEnd:
                        if self.isFunctionCall(token):
                            if token.str not in called_funcs:
                                called_funcs.append(token.str)
                                if token.str not in self.function_calls:
                                    self.function_calls[token.str] = 1
                                else:
                                    self.function_calls[token.str] = self.function_calls[token.str] + 1
                        token = token.next

    # HIS-CALLING calculate result
    def his_calling_result(self):
        for func in self.function_list:
            if func.name in self.function_calls and self.function_calls[func.name] > 5:
                self.reportError(func.tokenDef, 'style', 'Number of subfunctions calling a function: 0-5', 'CALLING')

    # HIS-CALLS
    # Number of called functions excluding duplicates: 0-7
    def his_calls(self, data):
        for func in data.functions:
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Search function body for function calls
                    token = scope.bodyStart
                    func_calls = list()
                    while token is not None and token != scope.bodyEnd:
                        if self.isFunctionCall(token):
                            # Don't add duplicates
                            if token.str not in func_calls:
                                func_calls.append(token.str)
                        token = token.next
                    self.functions_called[func.name] = func_calls
                    if len(func_calls) > 7:
                        self.reportError(func.tokenDef, 'style', 'Number of called functions excluding duplicates: 0-7', 'CALLS')

    # HIS-PARAM
    # Number of function parameters: 0-5
    def his_param(self, data):
        for func in data.functions:
            # Check number of function parameters
            if len(func.argument) > 5:
                self.reportError(func.tokenDef, 'style', 'Number of function parameters: 0-5', 'PARAM')

    # HIS-STMT
    # Number of statements per function: 1-50
    def his_stmt(self, data):
        num_of_statements = 0
        # Count line of statements in functions
        for func in data.functions:
            num_of_statements = self.numOfFunctionStatements(func, data)
            self.statistics_list.append("HIS-STMT  - %s: %d" % (func.name.ljust(50), num_of_statements))
            if num_of_statements > 50:
                self.reportError(func.tokenDef, 'style', 'Number of statements per function: 1-50', 'STMT')

    # HIS-LEVEL
    # Depth of nesting of a function: 0-4
    def his_level(self, data):
        for func in data.functions:
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Search function body and calculate nesting depth
                    token = scope.bodyStart
                    while token is not None and token != scope.bodyEnd:
                        if token.str not in ["if", "switch", "for", "while", "do"]:
                            token = token.next
                            continue
                        # Ignore while of do-while loop
                        if token.str == "while" and self.isWhileOfDoWhile(token):
                            token = token.next
                            continue
                        token_compound_stm = token
                        # Walk forward through token list until open curly
                        # bracket of scope has been reached.
                        while token is not None and token.str != "{":
                            token = token.next
                        # Calculate nesting level of current scope
                        if token is not None:
                            # Nesting level starts at depth 1 for function entry
                            nesting_level = 1
                            nesting_level += self.calculateNestingLevel(data, token.scope, scope)
                            if nesting_level > 4:
                                self.reportError(token_compound_stm, 'style', 'Depth of nesting of a function: 0-4', 'LEVEL')

    # HIS-RETURN
    # Number of return points within a function: 0-1
    def his_return(self, data):
        for func in data.functions:
            # Search for scope of current function
            for scope in data.scopes:
                if scope.type == "Function" and self.scopeMatchesFunction(scope, func):
                    # Search function body for return key word
                    token = scope.bodyStart
                    num_return_points = 0
                    while token is not None and token != scope.bodyEnd and num_return_points < 2:
                        if token.str == "return":
                            num_return_points += 1
                        token = token.next
                    if num_return_points > 1:
                        self.reportError(func.tokenDef, 'style', 'Number of return points within a function: 0-1', 'RETURN')

    # HIS-VOCF
    # Language scope: 1-4
    def his_vocf(self, data):
        for token in data.tokenlist:
            # Closing pairwise operators have already been counted by 
            # corresponding opening operators.
            if token.str in self.closing_pairwise_operators:
                continue
            if token.str in self.operators or token.str in self.keywords or self.isFunctionCall(token):
                self.sum_of_operators += 1
                if token.str not in self.distinct_operator_list:
                    self.distinct_operator_list.append(token.str)
            else:
                self.sum_of_operands += 1
                if token.str not in self.distinct_operand_list:
                    self.distinct_operand_list.append(token.str)

    # HIS-VOCF calculate result
    def his_vocf_result(self):
        #printf("Distinct operators: %d\n", len(self.distinct_operator_list))
        #printf("Sum of operators  : %d\n", self.sum_of_operators)
        #printf("Distinct operands : %d\n", len(self.distinct_operand_list))
        #printf("Sum of operands   : %d\n", self.sum_of_operands)
        if len(self.distinct_operator_list) > 0 or len(self.distinct_operand_list) > 0:
            vocf = (self.sum_of_operators + self.sum_of_operands) // (len(self.distinct_operator_list) + len(self.distinct_operand_list))
            if vocf < 1 or vocf > 4:
                self.reportError(None, 'style', 'Language scope: 1-4', 'VOCF')
        #printf("VOCF              : %d\n", vocf)

    # Check call path if there is a recursive call to function given by func_name
    def isRecursiveFunctionCall(self, function_name, called_function_name, called_functions_done):
        # Skip if check for called function has already been done
        if called_function_name in called_functions_done:
            return
        # Skip if function declaration is not part of given dump file
        if called_function_name not in self.functions_called:
            return
        # Compare names to check for recursive function call
        if function_name == called_function_name:
            for func in self.function_list:
                if func.name == function_name:
                    self.reportError(func.tokenDef, 'style', 'Number of recursions: 0', 'NRECUR')
            return
        else:
            # Register called function name as done
            called_functions_done.append(called_function_name)
            # Run check for next function call level
            for func_call in self.functions_called[called_function_name]:
                self.isRecursiveFunctionCall(function_name, func_call, called_functions_done)

    # HIS-NRECUR
    # Number of recursions: 0
    def his_num_recursions(self):
        for func_name in self.functions_called:
            called_functions_done = list()
            for func_call in self.functions_called[func_name]:
                self.isRecursiveFunctionCall(func_name, func_call, called_functions_done)


# Main entry function
def main():
    SUPPRESS_METRICS_HELP = '''HIS metrics to suppress (comma-separated).

    For example, if you'd like to suppress metrics GOTO, CALLS
    and PARAM use:
        --suppress-metrics GOTO,CALLS,PARAM

    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("dumpfile", nargs='*', help="dump file from cppcheck")
    parser.add_argument("-q", "--quiet", action="store_true", help='do not print "Checking ..." lines')
    parser.add_argument("-verify", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--suppress-metrics", type=str, help=SUPPRESS_METRICS_HELP)
    parser.add_argument("--no-summary", help="hide summary of violations", action="store_true")
    parser.add_argument("--statistics", help="show statistics information", action="store_true")
    args = parser.parse_args()

    if args.dumpfile:
        his_checker = HisMetricChecker(args)
        his_checker.run_checks()
    else:
        if not args.quiet:
            printf("No input files.\n")


if __name__ == '__main__':
    main()
