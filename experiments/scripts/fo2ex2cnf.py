import os
import copy
import logzero
from logzero import logger
import argparse
from itertools import product, permutations
import sympy
from pysat.card import CardEnc, EncType
import numpy as np

from wfomc import parse_input
from wfomc.problems import WFOMCProblem
from wfomc.fol.syntax import Const, X, Y, QFFormula, AtomicFormula, Pred



def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert a first-order logic sentence to CNF',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', type=str, required=True, help='sentence file')
    parser.add_argument('--output', '-o', type=str, required=False, help='output file')
    parser.add_argument('--linearencode', '-e', type=int, required=False, help='linear order and predcessor encode method 0-disable 1-hard encode 2-TODO first order encode 3-Vasek\'s encoding',default=0 )
    args = parser.parse_args()
    return args

def generate_leq_pred_axioms(domain, atom_to_digit):

    print("inside leq axiom")

    leq_pred_clauses = []
    consts = sorted(list(domain), key=lambda c: str(c))
   
    for atom, var_id in atom_to_digit.items():
        pred_name = atom.pred.name
        if pred_name == "LEQ":
            left, right = atom.args
            if consts.index(left) <= consts.index(right):
                leq_pred_clauses.append([var_id])   # True
            else:
                leq_pred_clauses.append([-var_id])  # False

        elif pred_name == "PRED1": #PRED in new_encode
            left, right = atom.args
            li, ri = consts.index(left), consts.index(right)
            if ri == li + 1:  
                leq_pred_clauses.append([var_id])
            else:
                leq_pred_clauses.append([-var_id])

        elif pred_name == "CIRCULAR_PRED": #CIRPRED in new_encode
            left, right = atom.args
            li, ri = consts.index(left), consts.index(right)
            if ri == li + 1 or (ri == 0 and li == len(consts)-1):  
                leq_pred_clauses.append([var_id])
            else:
                leq_pred_clauses.append([-var_id])

    return leq_pred_clauses

def generate_leq_dimacs(domain, atom_to_digit):

    print("inside leq axiom")

    out_clauses = []
    consts = sorted(list(domain), key=lambda c: str(c))

    leqatom:AtomicFormula=None
    predatom:AtomicFormula=None
    circpredatom:AtomicFormula=None
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "LEQ": 
            leqatom = atom
            break
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "PRED1": 
            predatom = atom
            break
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "CIRCULAR_PRED": 
            circpredatom = atom
            break

    if len(domain) < 2: 
        return []
    
    if leqatom is None and predatom is None and circpredatom is None:
        return []
    xyz_expr: sympy.Expr = sympy.true
    if leqatom is not None:
        leq_pred = leqatom.pred
    if leqatom is None:
        leq_pred = Pred("LEQ", 1)
    if predatom is not None:
        pred_pred = predatom.pred
    else:
        pred_pred = None
    if circpredatom is not None:
        circ_pred_pred = circpredatom.pred
    else:
        circ_pred_pred = None
   
    leq_tab = np.zeros((len(consts), len(consts)), dtype=int)
    for i, j in product(consts, repeat=2):
        if AtomicFormula(leq_pred, (i, j), True) not in atom_to_digit:
            atom_to_digit[AtomicFormula(leq_pred, (i, j), True)] = len(atomsym_to_digit) + 1
        leq_tab[consts.index(i), consts.index(j)] = atom_to_digit[AtomicFormula(leq_pred, (i, j), True)]

    for i in range(len(consts)):
        out_clauses.append([leq_tab[i, i]])
        for j in range(len(consts)):
            if i == j:
                continue
            if i < j:
                out_clauses.append([leq_tab[i, j], leq_tab[j, i]])
                out_clauses.append([-leq_tab[i, j], -leq_tab[j, i]])
            for k in range(len(consts)):
                if k == j or k == i:
                    continue
                out_clauses.append([-leq_tab[i, j], -leq_tab[j, k], leq_tab[i, k]])

    if pred_pred is not None:
        pred_tab = np.zeros((len(consts), len(consts)), dtype=int)
        for i, j in product(consts, repeat=2):
            if AtomicFormula(pred_pred, (i, j), True) not in atom_to_digit:
                atom_to_digit[AtomicFormula(pred_pred, (i, j), True)] = len(atomsym_to_digit) + 1
            pred_tab[consts.index(i), consts.index(j)] = atom_to_digit[AtomicFormula(pred_pred, (i, j), True)]

        for i in range(len(consts)):
            out_clauses.append([-pred_tab[i, i]])

            for j in range(len(consts)):
                #pass
                out_clauses.append([-pred_tab[i, j], leq_tab[i, j]])
            
            # V x first(x) | E z Pred(z, x)
            for j in range(len(consts)):
                if j == i:
                    continue
                new_clause = list(pred_tab[:, i])
                new_clause.append(-leq_tab[j, i])
                out_clauses.append(new_clause)

            # V x last(x) | E z Pred(x, z)
            for j in range(len(consts)):
                if j == i:
                    continue
                new_clause = list(pred_tab[i])
                new_clause.append(-leq_tab[i, j])
                print(new_clause)
                out_clauses.append(new_clause)

            # V x V y V z Pred(x, y) -> (LEQ(x, z) <-> LEQ(y, z))
            # V x V y V z Pred(x, y) -> (LEQ(x, z) | ~LEQ(y, z) & ~LEQ(x, z) | LEQ(y, z))
            # V x V y V z ~Pred(x, y) | (LEQ(x, z) | ~LEQ(y, z) & ~LEQ(x, z) | LEQ(y, z))
            # V x V y V z (~Pred(x, y) | LEQ(x, z) | ~LEQ(y, z)) & (~Pred(x, y) | ~LEQ(x, z) | LEQ(y, z)))
            for j in range(len(consts)):
                if j == i:
                    continue
                for k in range(len(consts)):
                    if k == j or k == i:
                        continue
                    out_clauses.append([-pred_tab[i, j], leq_tab[i, k], -leq_tab[j, k]])
                    out_clauses.append([-pred_tab[i, j], -leq_tab[i, k], leq_tab[j, k]])

    return out_clauses
            
def generate_xyz_leq_expr(domain)->sympy.Expr:
    
    leqatom:AtomicFormula=None
    predatom:AtomicFormula=None
    circpredatom:AtomicFormula=None
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "LEQ": 
            leqatom = atom
            break
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "PRED1": 
            predatom = atom
            break
    for atom, var_id in atom_to_digit.items():
        if atom.pred.name == "CIRCULAR_PRED": 
            circpredatom = atom
            break

    if len(domain) < 2: 
        return []

    if leqatom is None and predatom is None and circpredatom is None:
        return []
    xyz_expr: sympy.Expr = sympy.true
    if leqatom is not None:
        leq_pred = leqatom.pred
    if predatom is not None:
        pred_pred = predatom.pred
    if circpredatom is not None:
        circ_pred_pred = circpredatom.pred
    
    for x in domain: 
        #VX: ~LEQ(X,X)
        #LEQ(x,x)
        ground_atom = AtomicFormula(leq_pred, (x, x), True)
        xyz_expr = sympy.And(xyz_expr, ground_atom.expr)

    for x, y, z in product(domain, repeat=3): 
        #VXVYVZ: LEQ(X,Y) & LEQ(Y,Z) -> LEQ(X,Z)
        # ~( (LEQ(x,y) & LEQ(y,z) ) & ~LEQ(x,z) )
        # ~(LEQ(x,y) & LEQ(y,z)) | LEQ(x,z)
        # ~LEQ(x,y) | ~LEQ(y,z) | LEQ(x,z)

        ground_atom1 = AtomicFormula(leq_pred, (x, y), False)  
        ground_atom2 = AtomicFormula(leq_pred, (y, z), False) 
        ground_atom3 = AtomicFormula(leq_pred, (x, z), True) 
        ground_atom = sympy.Or(ground_atom1.expr, ground_atom2.expr, ground_atom3.expr)
        xyz_expr = sympy.And(xyz_expr, ground_atom)                   

    for x, y in permutations(domain, 2):
        # VXVY: LEQ(X,Y) | LEQ(Y,X)
        ground_atom1 = AtomicFormula(leq_pred, (x, y), True)  
        ground_atom2 = AtomicFormula(leq_pred, (y, z), True) 
        ground_atom = sympy.Or(ground_atom1.expr, ground_atom2.expr)
        xyz_expr = sympy.And(xyz_expr, ground_atom)   

    if pred_pred is not None:
        for x in domain:
            # V x first(x) | E z Pred(z, x)
            ground_atoms = [AtomicFormula(pred_pred, (z, x), True).expr for z in domain if z != x]
            for y in domain:
                if x == y and y != z:
                    continue
                xyz_expr = sympy.And(xyz_expr, sympy.Or(*(ground_atoms + [AtomicFormula(leq_pred, (x, y), True).expr])))
        
        for x in domain:    
            # V x last(x) | E z Pred(x, z)
            ground_atoms = [AtomicFormula(pred_pred, (x, z), True).expr for z in domain if z != x]
            for y in domain:
                if x == y and y != z:
                    continue
                xyz_expr = sympy.And(xyz_expr, sympy.Or(*(ground_atoms + [AtomicFormula(leq_pred, (y, x), True).expr])))

        for x in domain:
            # V x V y V z Pred(x, y) -> (LEQ(x, z) <-> LEQ(y, z))
            # V x V y V z Pred(x, y) -> (LEQ(x, z) | ~LEQ(y, z) & ~LEQ(x, z) | LEQ(y, z))
            # V x V y V z ~Pred(x, y) | (LEQ(x, z) | ~LEQ(y, z) & ~LEQ(x, z) | LEQ(y, z))
            # V x V y V z (~Pred(x, y) | LEQ(x, z) | ~LEQ(y, z)) & (~Pred(x, y) | ~LEQ(x, z) | LEQ(y, z)))
            xyz_expr = sympy.And(xyz_expr, AtomicFormula(pred_pred, (x, x), False).expr)
            for x, y, z in product(domain, repeat = 3):
                if x == y or y == z or z == x:
                    continue
                neg_pxy = AtomicFormula(pred_pred, (x, y), False).expr
                leq_xy = AtomicFormula(leq_pred, (x, y), True).expr
                neg_leq_xz = AtomicFormula(leq_pred, (x, z), False).expr
                neg_leq_yz = AtomicFormula(leq_pred, (y, z), False).expr
                leq_xz = AtomicFormula(leq_pred, (x, z), True).expr
                leq_yz = AtomicFormula(leq_pred, (y, z), True).expr
                xyz_expr = sympy.And(xyz_expr, sympy.Or(neg_pxy, leq_xz, neg_leq_yz))
                xyz_expr = sympy.And(xyz_expr, sympy.Or(neg_pxy, neg_leq_xz, leq_yz))
                xyz_expr = sympy.And(xyz_expr, sympy.Or(neg_pxy, leq_xy))

    print(xyz_expr)
    return xyz_expr


if __name__ == "__main__":
    logzero.loglevel(logzero.INFO)
    args = parse_args()
    sentence_dir = os.path.dirname(args.input)
    sentence_base = os.path.basename(args.input)
    problem = parse_input(args.input)
    leq_support = args.linearencode

    # remove the quantifier
    uni_formula: QFFormula = copy.deepcopy(problem.sentence.uni_formula)
    ext_formulas: list[QFFormula] = copy.deepcopy(problem.sentence.ext_formulas)
    

    while not isinstance(uni_formula, QFFormula):
        uni_formula = uni_formula.quantified_formula
    for i in range(len(ext_formulas)):
        ext_formulas[i] = ext_formulas[i].quantified_formula.quantified_formula


    atom_to_digit: dict[AtomicFormula, int] = {}
    atomsym_to_digit: dict[sympy.Symbol, int] = {}
    expr: sympy.Expr = sympy.true
    
    domain = problem.domain
    for (e1, e2) in product(domain, repeat=2):
        ground_uni_formula: QFFormula = uni_formula.substitute({X: e1, Y: e2}) & uni_formula.substitute({X: e2, Y: e1})
        # cnf_formula = sympy.to_cnf(ground_uni_formula.expr, simplify=True)
        cnf_formula = sympy.to_cnf(ground_uni_formula.expr)
        expr = sympy.And(expr, cnf_formula)

        for atom in ground_uni_formula.atoms():
            if atom not in atom_to_digit:
                atom_to_digit[atom] = len(atom_to_digit)+1
                atomsym_to_digit[atom.expr] = len(atomsym_to_digit)+1
    
    for e1 in domain:
        for ext_formula in ext_formulas:
            ext_expr = sympy.false
            for e2 in domain:
                ground_ext_formula = ext_formula.substitute({X: e1, Y: e2})
                ext_expr = sympy.Or(ext_expr, ground_ext_formula.expr)
                for atom in ground_ext_formula.atoms():
                    if atom not in atom_to_digit:
                        atom_to_digit[atom] = len(atom_to_digit)+1
                        atomsym_to_digit[atom.expr] = len(atomsym_to_digit)+1
            expr = sympy.And(expr, ext_expr)


#============ leq support 2 ================
    if leq_support == 2:
        print("WARNING: There might be bugs in encode2")
        expr = sympy.And(expr, generate_xyz_leq_expr(domain))

#============ get_clause ================
    expr = sympy.to_cnf(expr)
    cnf_clause_list = []
    for clause in expr.args:
        clause_str = ""
        if isinstance(clause, sympy.Not):
            clause_str += str(-atomsym_to_digit[~clause]) + " "
        elif isinstance(clause, sympy.Symbol):
            clause_str += str(atomsym_to_digit[clause]) + " "
        else:
            for atom in clause.args:
                if isinstance(atom, sympy.Symbol):
                    clause_str += str(atomsym_to_digit[atom]) + " "
                elif isinstance(atom, sympy.Not):
                    clause_str += str(-atomsym_to_digit[~atom]) + " "
                else:
                    raise RuntimeError(f'Unknown atom type: {atom}')
    
        line = str(clause_str.strip()) + " 0\n"
        cnf_clause_list.append(line)

#============ unary evidence ===============
    if problem.unary_evidence is not None:
        unary_evidence: set[AtomicFormula] = problem.unary_evidence
        ue_atoms=[] 

        for atom in unary_evidence:
            if atom.positive:
                ue_atoms.append((atom, True))
            else:
                ue_atoms.append((~atom, False))

        ue_clauses = []
        for item in ue_atoms:
            atom=item[0]
            pos=item[1]
            if atom not in atom_to_digit:
                atom_to_digit[atom] = len(atom_to_digit) + 1
                atomsym_to_digit[atom.expr] = atom_to_digit[atom]

            lit = atom_to_digit[atom] if pos else -atom_to_digit[atom]
            ue_clauses.append([lit])

        for clause in ue_clauses:
            line = " ".join(map(str, clause)) + " 0\n"
            cnf_clause_list.append(line)

# #============ leq support 1 hard encode ================
    if leq_support == 1:
        leq_clauses=generate_leq_pred_axioms(domain, atom_to_digit)
        for clause in leq_clauses:
            line = " ".join(map(str, clause)) + " 0\n"
            cnf_clause_list.append(line)

# #============ leq support 3 encoding ================
    if leq_support == 3:
        leq_clauses=generate_leq_dimacs(domain, atom_to_digit)
        for clause in leq_clauses:
            line = " ".join(map(str, clause)) + " 0\n"
            cnf_clause_list.append(line)

#============cc===========
    if problem.cardinality_constraint is not None:
        constraints = problem.cardinality_constraint.constraints
        cc_clauses = []
        for pred_map, op, bound in constraints:
            for pred, coeff in pred_map.items():
                pred_name = str(pred)  
                k = int(bound)  

                
                vars = [v for ksym, v in atomsym_to_digit.items() if pred_name in str(ksym)]
                if not vars:
                    continue
                if op == "<=":
                    cnf_cc = CardEnc.atmost(lits=vars, bound=k, encoding=EncType.seqcounter    )
                elif op == ">=":
                    cnf_cc = CardEnc.atleast(lits=vars, bound=k, encoding=EncType.seqcounter    )
                elif op == "=":
                    cnf_cc = CardEnc.equals(lits=vars, bound=k, encoding=EncType.seqcounter    )
                else:
                    raise RuntimeError(f"Unknown operator: {op}")
                
                modify_clauses=cnf_cc.clauses
                ignore_atom=vars
                
                #print('before:',len(atom_to_digit), modify_clauses)
                for clauses in modify_clauses:
                    for i in clauses:
                        if abs(i) not in ignore_atom:
                            ccatom:AtomicFormula= AtomicFormula( Pred('CC'+str(len(atom_to_digit)+1), 1), 'c',True)
                            atom_to_digit[ccatom] = len(atom_to_digit)+1
                            atomsym_to_digit[ccatom.expr] = len(atomsym_to_digit)+1
                            ignore_atom.append(len(atom_to_digit))

                            for j in modify_clauses:
                                for k_idx, k in enumerate(j): 
                                    if abs(i) == abs(k):
                                        j[k_idx] = len(atom_to_digit) if k > 0 else -len(atom_to_digit)

                #print('after:',len(atom_to_digit), modify_clauses)

                cc_clauses.extend(modify_clauses)

        for clause in cc_clauses:
            line = " ".join(map(str, clause)) + " 0\n"
            cnf_clause_list.append(line)
 


    cnf_clause_str="".join(cnf_clause_list)
    #print(cnf_clause_str)

    klist = list(atom_to_digit.keys())
    vlist = list(atom_to_digit.values())
    kstr = f'c {" ".join([str(k) for k in klist])}\n'
    vstr = f'c {" ".join([str(v) for v in vlist])}\n'

    #cnf_file_path = os.path.join(sentence_dir, f'{os.path.splitext(sentence_base)[0] }.cnf')
    cnf_file_path = f'tmp/{os.path.splitext(sentence_base)[0] }.cnf' if args.output is None else args.output

    cnf_file = open(cnf_file_path, 'w')
    cnf_file.write(kstr)
    cnf_file.write(vstr)

    cnf_file.write(f"p cnf {len(atom_to_digit)} {len(cnf_clause_list)}\n")
    cnf_file.write(cnf_clause_str)

    cnf_file.close()
    logger.info('CNF file written to %s', cnf_file_path)

