import jsonlines
import re 
import sys 

def add_hyp(stmnt, hyp): 
    if len(stmnt[stmnt.rfind("\n"):] + hyp) > 80:
        new_stmnt = stmnt + "\n\t" + hyp
        return new_stmnt
    else: 
        return stmnt + " " + hyp

TYPE_STAR_PATTERN = "Type u_[0-9][0-9]*"

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
        i = 0 
        while i < len(hyps): 
            if hyps[i][0][0]=="_": 
                to_add_tp = hyps[i][1]
                statement = add_hyp(statement, f"[{to_add_tp}]")
                i += 1
            else: 
                if re.match(TYPE_STAR_PATTERN, hyps[i][1]): 
                    hyps[i][1] = "Type*"
                    i_range = i+1 
                    while i_range < len(hyps) and re.match(TYPE_STAR_PATTERN, hyps[i_range][1]): 
                        i_range += 1
                else: 
                    i_range = i+1
                    while i_range<len(hyps) and hyps[i][1]==hyps[i_range][1]:
                        i_range += 1
                
                to_add_nm = " ".join([h[0] for h in hyps[i:i_range]])
                to_add_tp = hyps[i][1]
                statement = add_hyp(
                        statement, 
                        f"({to_add_nm} : {to_add_tp})"
                        )
                i = i_range
        
    

        conc_search = re.search("(.*\),)|(.*\},)|(.*\],)", step['decl_tp'])
        if conc_search: 
            conc = step["decl_tp"][conc_search.span()[1]+1:]
        else: 
            conc = step["decl_tp"]

        conc = conc[conc.rfind('→ ')+1:].strip()

        statement += " :\n\t" + conc

        print("#"*40 + "\n" + step["decl_tp"] + statement)





