# sat_and_smt/ex2/annotate_smt_for_unsat_cote.py
import argparse
import sys
from typing import List, Union, IO

# A simple S-expression can be a string (atom) or a list of S-expressions
Sexp = Union[str, List['Sexp']]

def parse_sexp(text: str) -> List[Sexp]:
    """
    A simple S-expression parser.
    It tokenizes the input string and recursively builds a nested list structure.
    """
    # Add whitespace around parentheses to simplify tokenization
    text = text.replace('(', ' ( ').replace(')', ' ) ')
    tokens = text.split()

    def read_from_tokens(token_list: List[str]) -> Sexp:
        if not token_list:
            raise SyntaxError("Unexpected EOF")
        token = token_list.pop(0)
        if token == '(':
            L = []
            while token_list and token_list[0] != ')':
                L.append(read_from_tokens(token_list))
            if not token_list:
                raise SyntaxError("Missing ')'")
            token_list.pop(0)  # Pop off ')'
            return L
        elif token == ')':
            raise SyntaxError("Unexpected ')'")
        else:
            return token

    ast = []
    while tokens:
        ast.append(read_from_tokens(tokens))
    return ast

def format_sexp(exp: Sexp) -> str:
    """
    Formats a parsed S-expression back into a string.
    """
    if isinstance(exp, list):
        return f"({' '.join(format_sexp(e) for e in exp)})"
    else:
        return str(exp)

def annotate_assertions(smt_file: IO, output_file: IO):
    """
    Reads an SMT file, annotates assertions, adds commands for unsat cores,
    and writes to the output file.
    """
    try:
        content = smt_file.read()
        ast = parse_sexp(content)
    except SyntaxError as e:
        sys.stderr.write(f"Error parsing SMT file: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        sys.exit(1)

    assertion_count = 0
    processed_ast = []

    # Check if produce-unsat-cores option is already set
    produce_unsat_cores_option = ['set-option', ':produce-unsat-cores', 'true']
    option_found = any(expr == produce_unsat_cores_option for expr in ast)

    # Process the original AST
    for expr in ast:
        # Filter out existing get-unsat-core commands
        if isinstance(expr, list) and expr == ['get-unsat-core']:
            continue

        # Check if it's a top-level assertion: (assert ...)
        if isinstance(expr, list) and len(expr) > 1 and expr[0] == 'assert':
            # Check if it's already a named assertion: (assert (! ...))
            if isinstance(expr[1], list) and len(expr[1]) > 0 and expr[1][0] == '!':
                processed_ast.append(expr)  # Keep existing named assertion
            else:
                # It's an unnamed assertion, so let's name it.
                term = expr[1:]
                if len(term) == 1:
                    term = term[0]

                name = f"assertion_{assertion_count}"
                named_assertion = ['assert', ['!', term, ':named', name]]
                processed_ast.append(named_assertion)
                assertion_count += 1
        else:
            processed_ast.append(expr) # Keep other commands as is

    # If the option was not found, insert it at the second line (index 1)
    if not option_found:
        # Ensure there's at least one line to insert after
        if len(processed_ast) > 0:
            processed_ast.insert(1, produce_unsat_cores_option)
        else:
            processed_ast.append(produce_unsat_cores_option)


    # Add (get-unsat-core) at the end
    processed_ast.append(['get-unsat-core'])

    for expr in processed_ast:
        output_file.write(format_sexp(expr))
        output_file.write('\n')

def main():
    """
    Main function to parse command-line arguments and run the annotation.
    """
    parser = argparse.ArgumentParser(
        description="Annotate assertions in an SMT-LIB 2 file and add unsat-core commands."
    )
    parser.add_argument(
        "smt_file",
        type=argparse.FileType('r'),
        help="Path to the input SMT file."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Path to the output file (default: stdout)."
    )

    args = parser.parse_args()

    try:
        annotate_assertions(args.smt_file, args.output_file)
    finally:
        if args.smt_file:
            args.smt_file.close()
        if args.output_file is not sys.stdout:
            args.output_file.close()

if __name__ == "__main__":
    main()