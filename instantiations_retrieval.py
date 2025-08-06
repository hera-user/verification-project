import sys
import io
from pysmt.smtlib.parser import SmtLibParser
from pysmt.smtlib.script import SmtLibCommand
from pysmt.walkers import DagWalker
from pysmt.shortcuts import ForAll, Exists
from pysmt.smtlib.annotations import Annotations

class QuantifierAnnotator(DagWalker):
    def _init_(self):
        super()._init_()
        self.qid_counter = 0

    def walk_forall(self, formula, args, **kwargs):
        return self._annotate(formula)

    def walk_exists(self, formula, args, **kwargs):
        return self._annotate(formula)

    def _annotate(self, formula):
        # Add :qid annotation if not already present
        ann = formula.annotations
        if 'qid' not in ann:
            self.qid_counter += 1
            ann['qid'] = f'q{self.qid_counter}'
            formula = formula.annotate(ann)
        return formula

    def transform(self, formula):
        return self.walk(formula)

def process_file(input_path):
    parser = SmtLibParser()
    with open(input_path, 'r') as f:
        script = parser.get_script(f)
        annotated_script = []

        annotator = QuantifierAnnotator()

        for cmd in script.commands:
            if cmd.name == 'assert':
                formula = cmd.args[0]
                annotated_formula = annotator.transform(formula)
                annotated_script.append(SmtLibCommand('assert', [annotated_formula]))
            else:
                annotated_script.append(cmd)

    return script.logic, annotated_script

def write_script(logic, script, output_path):
    with open(output_path, 'w') as out:
        if logic:
            out.write(f"(set-logic {logic})\n")
        for cmd in script:
            out.write(str(cmd) + "\n")

if __name__ == '_main_':
    if len(sys.argv) != 3:
        print("Usage: python add_qids_to_quantifiers.py input.smt2 output.smt2")
        sys.exit(1)

    logic, script = process_file(sys.argv[1])
    write_script(logic, script, sys.argv[2])