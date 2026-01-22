
if __name__ == "__main__":
    
    formula = r"""\forall X: (\forall Y: ((~(PERM(X,X)) & (Pred(X,Y) -> LEQ(X,Y)) & (Pred(X,Y) -> PERM(X,Y)) & (p_shelf_PRED(X,Y) <-> (Pred(X,Y) & p_set_aux_6(X) & p_set_aux_6(Y))) & ((p_set_aux_6(X) & ~(p_set_aux_6(Y))) -> LEQ(X,Y)) & (~(p_english_books_first(X)) | (p_set_english_books(X) & (p_set_english_books(Y) -> ~(p_shelf_PRED(Y,X))))) & (~(p_math_books_first(X)) | (p_set_math_books(X) & (p_set_math_books(Y) -> ~(p_shelf_PRED(Y,X))))))))
& \forall X: (\exists Y: (PERM(X,Y)))
& \forall X: (\exists Y: (PERM(Y,X)))
& \forall X: (\exists Y: ((p_english_books_first(X) | ~((p_set_english_books(X) & (p_set_english_books(Y) -> ~(p_shelf_PRED(Y,X))))))))
& \forall X: (\exists Y: ((p_math_books_first(X) | ~((p_set_math_books(X) & (p_set_math_books(Y) -> ~(p_shelf_PRED(Y,X))))))))"""
    

    
    for domsize in range(2, 21):
        fname = f"b{domsize}.wfomcs"

        ccs = f"""1.0 |Pred| = {domsize-1}
1.0 |PERM| = {domsize}"""

        with open(f"../wfomcs/{fname}") as fr:
            line = fr.readline()
            
            while not line.lstrip().startswith("domain"):
                line = fr.readline()
            
            with open(fname, "w") as fw:
                fw.write(formula)
                fw.write("\n")
                fw.write("\n")
                fw.write(line)
                fw.write("\n")
                fw.write(ccs)

                for line in fr.readlines():
                    fw.write(line)


