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

for i, step in enumerate(data): 
    if step['decl_nm'] not in nms_so_far: 
        #newline here for convenience, remember to remove
        statement = "\ntheorem " + step['decl_nm'] + " "
        nms_so_far.add(step['decl_nm'])

        is_star_joining = False # so we get (G H : Type*)
        for hyp in step['hyps']:
            if is_star_joining: 
                if re.match(TYPE_STAR_PATTERN, hyp[1]):
                    current_hyp += " " + hyp[0]
                    continue 
                else: 
                    current_hyp += " : Type*)"
                    statement = add_hyp(statement, current_hyp)
                    
                    is_star_joining = False 


            if re.match(TYPE_STAR_PATTERN, hyp[1]) and not is_star_joining: 
                current_hyp = f"({hyp[0]}"
                is_star_joining = True 
            else: 
                if hyp[0][0]=="_": 
                    current_hyp = f"[{hyp[1]}]"
                else: 
                    current_hyp = f"({hyp[0]} : {hyp[1]})"

                statement = add_hyp(statement, current_hyp)

        print("#"*40 + "\n" + step["decl_tp"] + statement)
