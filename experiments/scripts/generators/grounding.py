from typing import List, Tuple
import functools
import itertools

from pysat.card import CardEnc, EncType
import sympy
import sympy.logic.boolalg as sympy_logic

from wfomc.fol import *
from wfomc.problems import WFOMCProblem


class DimacsCNF:

    def __init__(self):
        self.atom_to_id: dict[AtomicFormula, int] = {}
        # self.id_to_atom: Dict[int, str] = {}
        
        self.clauses: List[List[int]] = []
        self.num_vars = 0

    def get_id(self, literal: AtomicFormula) -> int:
        if not literal.positive:
            literal = ~literal

        if literal not in self.atom_to_id:
            self.num_vars += 1
            self.atom_to_id[literal] = self.num_vars
            # self.id_to_atom[self.num_vars] = literal
            
        return self.atom_to_id[literal]

    def add_clause(self, literals: List[AtomicFormula]):
        self.clauses.append([(-1)**(not lit.positive) * self.get_id(lit) for lit in literals])

    def add_cardinality_constraint(self, literals: List[int], op: str, bound: int):
        """
        Encodes a cardinality constraint `sum(literals) op bound`

        All ids in `literals` MUST be obtained using get_id() method.
        """
        top_id = self.num_vars

        # TODO: pysat CCs may not be equicountable
        if op == '<=':
            cnf_obj = CardEnc.atmost(literals, bound=bound, top_id=top_id, encoding=EncType.seqcounter)
        elif op == '>=':
            cnf_obj = CardEnc.atleast(literals, bound=bound, top_id=top_id, encoding=EncType.seqcounter)
        elif op == '=' or op == '==':
            cnf_obj = CardEnc.equals(literals, bound=bound, top_id=top_id, encoding=EncType.seqcounter)
        else:
            raise ValueError(f"Unsupported operator: {op}")

        self.clauses.extend(cnf_obj.clauses)
        if cnf_obj.nv > self.num_vars: 
            self.num_vars = cnf_obj.nv # cnf_obj.nv contains the new maximum variable ID

    def write_to_file(self, filename: str, metadata=False):
        with open(filename, 'w') as f:
            if metadata:
                for (atom, int) in self.atom_to_id.items():
                    f.write(f"c {atom}: {int}\n")

            f.write(f"p cnf {self.num_vars} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")


class TseitinTransformer:
    
    def __init__(self):
        self.aux_counter = 0
        
        self.clause_templates = []

        self.ext_templates = []
        self.uni_ext_templates = []

    def process_sc2(self, sc2: SC2):
        """Perform 'templated' Tseytin transform"""
        self._reset()
        
        # 1. Universally quantified formula
        # Structure: (forall x: phi(x)) OR (forall x, y: phi(x,y))
        if sc2.uni_formula and sc2.uni_formula != top:
            vars_list, body = self._strip_quantifiers(sc2.uni_formula)
            
            # Convert backend expr to Sympy NNF
            body_expr = sympy.to_nnf(body.expr, simplify=False)
            
            # OPTIMIZATION: If the body is already in CNF, we don't need new Aux variables.
            if sympy_logic.is_cnf(body_expr):
                templates = self._process_sympy_cnf(body_expr)
                self.clause_templates.extend(templates)
            else:
                # Not in CNF, use Tseitin
                rep_atom, templates, _ = self._get_tseitin_template(body_expr)
                self.clause_templates.extend(templates)
                self.clause_templates.append([rep_atom])

        # 2. Formulas with existential quantifiers
        # Structure: (exists x: phi(x)) OR (forall x exists y: phi(x,y))
        # Note: We do NOT perform the is_cnf optimization here because we need a single representative atom to act as the 'selector' for the existential choice.
        for ext in sc2.ext_formulas:
            vars_list, body = self._strip_quantifiers(ext)
            body_expr = sympy.to_nnf(body.expr, simplify=False)
            
            rep_atom, templates, _ = self._get_tseitin_template(body_expr)
            self.clause_templates.extend(templates)
        
            if len(vars_list) == 1: # (exists x: ...)
                self.ext_templates.append((vars_list[0], rep_atom))
            else: # (forall x exists y: ...)
                self.uni_ext_templates.append((vars_list, rep_atom))

    def propositionalize(self, domain_list: List[Const]) -> DimacsCNF:
        """Instantiate the stored templates over the domain"""
        cnf = DimacsCNF()

        for var, atom in self.ext_templates:
            clause = []
            for c in domain_list:
                clause.append(atom.substitute({var: c}))
            cnf.add_clause(clause)

        for vars_, atom in self.uni_ext_templates:
            for c1 in domain_list:
                clause = []
                for c2 in domain_list:
                    clause.append(atom.substitute({vars_[0]: c1, vars_[1]: c2}))
                cnf.add_clause(clause)

        for template in self.clause_templates:
            vars_ = functools.reduce(set.union, map(set, (atom.vars() for atom in template)))
            for assignment in itertools.product(domain_list, repeat=len(vars_)):
                subst = {v: assignment[i] for i, v in enumerate(vars_)}

                clause = []
                for atom in template:
                    clause.append(atom.substitute(subst))
                cnf.add_clause(clause)

        return cnf

    def _process_sympy_cnf(self, expr) -> List[List[AtomicFormula]]:
        """
        Convert a Sympy expression known to be in CNF into a list of clauses.
        Returns List[List[AtomicFormula]]
        """
        clauses = []

        # Case 1: Top-level AND. It contains multiple clauses.
        if isinstance(expr, sympy_logic.And):
            for arg in expr.args:
                clauses.extend(self._process_sympy_cnf(arg))
                
        # Case 2: OR (A clause), NOT (Negative Literal), or SYMBOL (Positive Literal)
        # These all represent a single clause in the CNF list.
        elif isinstance(expr, (sympy_logic.Or, sympy_logic.Not, sympy.Symbol)):
             clauses.append(self._process_sympy_clause(expr))
             
        # Case 3: True/False constants (Edge cases)
        elif expr == sympy.true:
            pass # Empty list of clauses (always satisfied)
        elif expr == sympy.false:
            raise ValueError("Universal formula reduced to False. Problem is unsatisfiable.")
            
        else:
            # Should not happen if is_cnf passed
            raise ValueError(f"Expression {expr} is not valid CNF structure")
        
        return clauses

    def _process_sympy_clause(self, expr) -> List[AtomicFormula]:
        """
        Extract literals from a single clause (Or, Not, or Symbol).
        """
        literals = []

        if isinstance(expr, sympy_logic.Or):
            for arg in expr.args:
                # In CNF, children of OR must be literals (Not or Symbol)
                if isinstance(arg, (sympy.Symbol, sympy_logic.Not)):
                    literals.append(self._sympy_to_atom(arg))
                else:
                    raise ValueError(f"Nested operator inside CNF clause: {arg}")
                    
        elif isinstance(expr, (sympy.Symbol, sympy_logic.Not)):
            # Unit clause
            literals.append(self._sympy_to_atom(expr))
            
        else:
            raise ValueError(f"Invalid clause structure: {expr}")
            
        return literals

    def _sympy_to_atom(self, expr) -> AtomicFormula:
        """Helper to safely convert Sympy literal to AtomicFormula"""
        if isinstance(expr, sympy.Symbol):
            return get_atom(expr)
        elif isinstance(expr, sympy_logic.Not):
            return ~get_atom(expr.args[0])
        else:
            raise ValueError(f"Cannot convert {expr} to atom")

    def _get_tseitin_template(self, expr) -> Tuple[AtomicFormula, List[List[AtomicFormula]], set[Var]]:
        """
        Returns a symbolic representative atom (e.g. @aux(X,Y)), a list of symbolic clauses defining it and a set of free variables occuring in the `expr`.
        """
        if isinstance(expr, sympy.Symbol):
            atom = get_atom(expr)
            return atom, [], atom.vars()
        
        # In NNF, negation only wraps atoms
        if isinstance(expr, sympy_logic.Not):
            atom = get_atom(expr.args[0])
            return ~atom, [], atom.vars()

        # Recursive steps
        if isinstance(expr, (sympy_logic.And, sympy_logic.Or)):
            rep_atoms = []
            defs = []
            free_vars = set()
            for subexpr in expr.args:
                new_rep, new_defs, new_vars = self._get_tseitin_template(subexpr)
                rep_atoms.append(new_rep)
                defs.extend(new_defs)
                free_vars.update(new_vars)
            
            # Create aux predicate based on free vars
            free_vars = sorted(list(free_vars), key=str)
            aux_pred = new_predicate(len(free_vars), self._new_aux_name())
            aux_atom = aux_pred(*free_vars)
            
            if isinstance(expr, sympy_logic.And):
                # Aux <-> (A & B & C & ...)  => (~Aux v A), (~Aux v B), (~Aux v C), ..., (~A v ~B v ~C v ... v Aux)
                defs.append([~atom for atom in rep_atoms] + [aux_atom])
                for atom in rep_atoms:
                    defs.append([~aux_atom, atom])
            elif isinstance(expr, sympy_logic.Or):
                # Aux <-> (A v B v C v ...) => (Aux v ~A), (Aux v ~B), (Aux v ~C), ..., (A v B v C v ... v ~Aux)
                defs.append(rep_atoms + [~aux_atom])
                for atom in rep_atoms:
                    defs.append([aux_atom, ~atom])
            else:
                raise ValueError(f"Unexpected formula type in template: {expr}")
                
            return aux_atom, defs, free_vars
        
        raise ValueError(f"Unexpected formula type in template: {expr}")
    
    def _strip_quantifiers(self, formula: QuantifiedFormula) -> Tuple[List[Var], QFFormula]:
        vars_ = []
        curr = formula
        while isinstance(curr, QuantifiedFormula):
            vars_.append(curr.quantified_var)
            curr = curr.quantified_formula
        return vars_, curr

    def _new_aux_name(self) -> str:
        self.aux_counter += 1
        return f"Aux_{self.aux_counter}_"
    
    def _reset(self):
        self.aux_counter = 0
        self.clause_templates = []
        self.ext_templates = []
        self.uni_ext_templates = []


def append_order_axioms(leq_pred: Pred, succ_pred: Pred, circ_pred: Pred, domain_list: List[Const], cnf: DimacsCNF):
    n = len(domain_list)

    # 1. Base Case: Single element domain
    if n < 2:
        c = domain_list[0]
        cnf.add_clause([leq_pred(c, c)]) # LEQ(c,c) is True
        if succ_pred: cnf.add_clause([~succ_pred(c, c)]) # No successor
        if circ_pred: cnf.add_clause([circ_pred(c, c)]) # Circular successor to itself
        return

    # Pre-generate atoms for easier access
    leq = [[leq_pred(domain_list[i], domain_list[j]) for j in range(n)] for i in range(n)]
    
    # ============
    # LEQ: Linear Order Axioms
    # ============
    for i in range(n):
        # Reflexivity: LEQ(x, x)
        cnf.add_clause([leq[i][i]])

        for j in range(n):
            if i == j: continue
            
            # Totality & Antisymmetry: Exactly one of LEQ(x, y) or LEQ(y, x) is true
            # LEQ(x, y) V LEQ(y, x)
            cnf.add_clause([leq[i][j], leq[j][i]]) 
            # ~LEQ(x, y) V ~LEQ(y, x)
            cnf.add_clause([~leq[i][j], ~leq[j][i]])

            # Transitivity: LEQ(x, y) & LEQ(y, z) -> LEQ(x, z)
            for k in range(n):
                if k == i or k == j: continue
                cnf.add_clause([~leq[i][j], ~leq[j][k], leq[i][k]])

    # ============
    # SUCC (PRED1): Immediate Predecessor Axioms
    # ============
    if succ_pred:
        succ = [[succ_pred(domain_list[i], domain_list[j]) for j in range(n)] for i in range(n)]
        
        # Aux predicate: IsBetween(x, y, z) <-> LEQ(x, z) & LEQ(z, y)
        # We only need this for distinct x, y, z
        between_pred = new_predicate(3, "Aux_Between")
        
        for i in range(n):     # x
            for j in range(n): # y
                
                # 1. Non-reflexive: ~SUCC(x, x)
                if i == j:
                    cnf.add_clause([~succ[i][j]])
                    continue
                
                # 2. Consistency: SUCC(x, y) -> LEQ(x, y)
                cnf.add_clause([~succ[i][j], leq[i][j]])

                # 3. Definition: SUCC(x, y) <-> (LEQ(x, y) & ~EXISTS z strictly between x and y)
                # We implement: SUCC(x, y) <-> LEQ(x, y) & AND_z (~Between(x, y, z))
                
                intermediate_clauses = [] # This will collect atoms representing "z is between x and y"
                
                for k in range(n): # z
                    if k == i or k == j: continue
                    
                    # Define: Aux_Between(x, y, z) <-> LEQ(x, z) & LEQ(z, y)
                    aux_between = between_pred(domain_list[i], domain_list[j], domain_list[k])
                    
                    # Tseitin for AND
                    # Aux -> A
                    cnf.add_clause([~aux_between, leq[i][k]])
                    # Aux -> B
                    cnf.add_clause([~aux_between, leq[k][j]])
                    # A & B -> Aux
                    cnf.add_clause([~leq[i][k], ~leq[k][j], aux_between])
                    
                    intermediate_clauses.append(aux_between)

                
                # Direction A: SUCC(x, y) -> ~Aux_Between(x, y, z) for all z
                for aux in intermediate_clauses:
                    cnf.add_clause([~succ[i][j], ~aux])
                    
                # Direction B: (LEQ(x, y) & AND_z ~Aux_Between) -> SUCC(x, y)
                # Equivalent CNF: ~LEQ(x, y) V (OR_z Aux_Between) V SUCC(x, y)
                cnf.add_clause([~leq[i][j], succ[i][j]] + intermediate_clauses)

        # ============
        # CIRCULAR_PRED: Connect Last to First
        # ============
        if circ_pred:
            circ = [[circ_pred(domain_list[i], domain_list[j]) for j in range(n)] for i in range(n)]
            
            # First(x) <-> Forall y LEQ(x, y)
            # Last(x)  <-> Forall y LEQ(y, x)
            
            first_pred = new_predicate(1, "Aux_First")
            last_pred = new_predicate(1, "Aux_Last")
            
            for i in range(n):
                first_atom = first_pred(domain_list[i])
                last_atom = last_pred(domain_list[i])
                
                # Define First(i)
                # First(i) -> LEQ(i, j) for all j
                for j in range(n):
                    cnf.add_clause([~first_atom, leq[i][j]])
                # (AND_j LEQ(i, j)) -> First(i)  =>  (~LEQ(i, j0) V ~LEQ(i, j1)... V First(i))
                cnf.add_clause([~leq[i][j] for j in range(n)] + [first_atom])

                # Define Last(i)
                # Last(i) -> LEQ(j, i) for all j
                for j in range(n):
                    cnf.add_clause([~last_atom, leq[j][i]])
                # (AND_j LEQ(j, i)) -> Last(i)
                cnf.add_clause([~leq[j][i] for j in range(n)] + [last_atom])

            # Define CIRCULAR_PRED(x, y) <-> SUCC(x, y) V (Last(x) & First(y))
            for i in range(n):
                for j in range(n):
                    c_atom = circ[i][j]
                    s_atom = succ[i][j]
                    l_atom = last_pred(domain_list[i])
                    f_atom = first_pred(domain_list[j])
                    
                    # Aux for conjunction (Last(i) & First(j))
                    # optimization: we can inline the Tseitin here to save a predicate variable ID if we want,
                    # but explicit is clearer. Let's do standard CNF expansion for C <-> S V (L & F)
                    
                    # 1. S -> C
                    cnf.add_clause([~s_atom, c_atom])
                    
                    # 2. (L & F) -> C  =>  ~L V ~F V C
                    cnf.add_clause([~l_atom, ~f_atom, c_atom])
                    
                    # 3. C -> (S V (L & F))
                    # C -> S V L
                    cnf.add_clause([~c_atom, s_atom, l_atom])
                    # C -> S V F
                    cnf.add_clause([~c_atom, s_atom, f_atom])
       

def ground(problem: WFOMCProblem, out_file=None, check_order_preds=True):
    # 0. Ensure deterministic order for grounding
    domain_list = sorted(list(problem.domain), key=str)
    
    # 1. Produce CNF using Tseitin transform
    tt = TseitinTransformer()
    tt.process_sc2(problem.sentence)
    cnf = tt.propositionalize(domain_list)

    # 2. Unary Evidence
    if problem.unary_evidence:
        for atom in problem.unary_evidence:
            cnf.add_clause([atom])

    # 3. Cardinality Constraints
    if problem.cardinality_constraint is not None:
        for pred_map, op, bound in problem.cardinality_constraint.constraints:
            
            # We assume there is only one predicate with coefficient 1 in pred_map
            predicate = next(iter(pred_map.keys())) 
            assert len(pred_map) == 1 and pred_map[predicate] == 1.0
            args_iter = itertools.product(domain_list, repeat=predicate.arity)
            
            lit_ids = []
            for args in args_iter:
                atom = predicate(*args)
                lit_ids.append(cnf.get_id(atom))  # get_id(...) automatically adds the atom to the mapping if not present

            cnf.add_cardinality_constraint(lit_ids, op, int(bound))

    # 4. Order Axioms
    if check_order_preds:
        preds = problem.sentence.preds()
        leq_pred = None
        succ_pred = None
        circ_pred = None
        for p in preds:
            if p.name == "LEQ":
                leq_pred = p
                break
        for p in preds:
            if p.name == "PRED1" or p.name == "PRED":
                succ_pred = p
                if leq_pred is None:
                    leq_pred = Pred("LEQ", 2)
                break
        for p in preds:
            if p.name == "CIRCULAR_PRED":
                circ_pred = p
                if succ_pred is None:
                    succ_pred = Pred("PRED1", 2)
                    if leq_pred is None:
                        leq_pred = Pred("LEQ", 2)
                break

        if leq_pred:
            append_order_axioms(leq_pred, succ_pred, circ_pred, domain_list, cnf)

    # 5. Write output
    if out_file:
        cnf.write_to_file(out_file)

    return cnf
