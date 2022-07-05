import jsonlines
import re 
import sys 


def add_hyp(stmnt, hyp): 
    if len(stmnt[stmnt.rfind("\n"):] + hyp) > 80:
        new_stmnt = stmnt + "\n\t" + hyp
        return new_stmnt
    else: 
        return stmnt + " " + hyp
def get_paren_type(hyp, tp): 
    before_var = r"((\s)|(\()|(\{)|(\[))"
    key = before_var + f"{re.escape(hyp[0])}.*?: {re.escape(hyp[1])}"
    first_search = re.search(key, tp)
    if first_search is None: 
        leftarrow_case = r"(→" + re.escape(hyp[1]) + r")"
        binder_case = "(" + re.escape(hyp[0]) + r"[^\}\)\]]" + re.escape(hyp[1]) + ")"
        second_key = leftarrow_case + "|" + binder_case
        second_search = re.search(second_key, tp)
        if second_search: 
            return "("
        else: 
            return False 
    else: 
        i = first_search.span()[0]+1
        left = tp[:i]

        j_1 = left.rfind("(")
        j_2 = left.rfind("{")
        j_3 = left.rfind("[")
        j = max(j_1, j_2, j_3)

        return left[j]

TYPE_STAR_PATTERN = "Type u_.*"

path = sys.argv[1]

with jsonlines.open(path) as f: 
    data = [line for line in f.iter()]

nms_so_far = set()

for step in data: 
    if step['decl_nm'] not in nms_so_far: 
        dot_index = step["decl_nm"].rfind(".")
        statement = "\ntheorem " + step["decl_nm"][dot_index+1:] + " " 
        nms_so_far.add(step["decl_nm"])
        
        hyps = step['hyps']
        print(hyps)
        i = 0 
        while i < len(hyps): 
            if hyps[i][0][0]=="_": 
                to_add_tp = hyps[i][1]
                statement = add_hyp(statement, f"[{to_add_tp}]")
                i += 1
            else: 
                paren_type = get_paren_type(hyps[i], step["decl_tp"])
                if not paren_type: 
                    i += 1
                    continue 

                if re.match(TYPE_STAR_PATTERN, hyps[i][1]): 
                    i_range = i+1 
                    while i_range < len(hyps) and re.match(TYPE_STAR_PATTERN, hyps[i_range][1]) and paren_type==get_paren_type(hyps[i_range], step["decl_tp"]):  
                        i_range += 1
                    hyps[i][1]="Type*"
                else: 
                    i_range = i+1
                    while i_range<len(hyps) and hyps[i][1]==hyps[i_range][1] and paren_type==get_paren_type(hyps[i_range], step["decl_tp"]):
                        i_range += 1
                

                to_add_nm = " ".join([h[0] for h in hyps[i:i_range]])
                to_add_tp = hyps[i][1]
                inner = f"{to_add_nm} : {to_add_tp}"

                if paren_type=="(":
                    statement = add_hyp(
                            statement, 
                            f"({inner})"
                            )
                elif paren_type=="{": 
                    statement = add_hyp(
                            statement, 
                            f"{{{inner}}}"
                            )
                else: 
                    statement= add_hyp(
                            statement,
                            f"[{inner}]"
                            )
                i = i_range
        
    
        j_1 = step["decl_tp"].rfind("),")
        j_2 = step["decl_tp"].rfind("},")
        j_3 = step["decl_tp"].rfind("],")
        j = max(j_1, j_2, j_3)

        conc = step["decl_tp"][j+1:]

        conc = conc[conc.rfind('→ ')+1:].strip(',').strip()

        statement += " :\n\t" + conc

        print("\n" + step["decl_tp"] + "\n" + statement+"\n" + "#"*40)

