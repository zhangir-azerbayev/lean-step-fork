import json
import ndjson
import re
import sys 
from os import listdir
import os
from tqdm import tqdm

# The philosophy is to try to apply well formedness preserving transformations
# to the type signature. 

path = sys.argv[1]

def get_log_of_path(path): 
    log = []
    
    with open(path) as f: 
        data = ndjson.load(f)

    nms_so_far = set()
    for step in data: 
        if step['decl_nm'] not in nms_so_far: 
            dot_index = step["decl_nm"].rfind(".")
            statement = "\ntheorem " + step["decl_nm"][dot_index+1:] + " "
            nms_so_far.add(step["decl_nm"])
            
            tp = step["decl_tp"]

            if tp[0]=="∀": 
                tp = tp[2:]

            # we need to find the "outer comma"
            counter = 0 
            for i, c in enumerate(tp): 
                if c=="(" or c=="{" or c=="[":
                    counter += 1
                elif c==")" or c=="}" or c=="]": 
                    counter -= 1
                elif c=="," and counter==0: 
                    comma_index = i
                    break
                elif i==len(tp)-1: 
                    comma_index=-1
            
            if comma_index!=-1: 
                # pulls implications into binders
                for hyp in step["hyps"]: 
                    key = re.escape(hyp[1]) + re.escape(r" →")
                    search = re.search(key, tp)
                    if search and search.span()[0]>comma_index: 
                        tp = re.sub(key, "", tp)
                        binder = f" ({hyp[0]} : {hyp[1]})"
                        tp = tp[:comma_index] + binder + tp[comma_index:]
                        comma_index += len(binder)

                # removes trailing parantheses 
                conc = tp[comma_index+1:].strip()
                #conc = conc[1:-1] if conc[0]=="(" and conc[-1]==")" else conc 

                tp = tp[:comma_index] + " :\n\t" + conc
            else: 
                tp = ":\n\t" + tp

            # replace [_inst_n : Type] with [Type]
            tp = re.sub(r"_inst_[0-9]* : ", "", tp)
            
            # Collapses Type u_1's into Type*'s 
            typeu = r": Type u_[0-9]"
            curlys = r"\} \{[^\}]*"
            rounds = r"\) \([^\)]*"
            key = typeu + curlys + typeu
            while re.search(key, tp): 
                search = re.search(key, tp)
                left = search.span()[0]
                right = search.span()[1]
                tp = tp[:left] + re.sub(": Type u_[0-9]\} \{", "", tp[left:right]) + tp[right:]
            # now the same for rounds
            key = typeu + rounds + typeu
            while re.search(key, tp): 
                search = re.search(key, tp)
                left = search.span()[0]
                right = search.span()[1]
                tp = tp[:left] + re.sub(": Type u_[0-9]\) \(", "", tp[left:right]) + tp[right:]

            tp = re.sub("Type u_[0-9]", "Type*", tp)
     
            statement += tp

            # Makes sure all lines aren't much more than 70 characters
            combinations = [x + " " + y for x in [')', '}', ']'] for y in ['(', '{', '[']]
            i=1
            while i < len(statement)-1: 
                if statement[i-1:i+2] in combinations: 
                    left = statement[:i]
                    if len(left[left.rfind("\n"):])>70: 
                        statement = statement[:i] + "\n\t" + statement[i+1:]
                        i += 1
                i += 1 
            
            # gets ride of trailing newline
            statement = statement.strip()

            log.append({
                "formal_statement": statement, 
                "decl_tp": step["decl_tp"], 
                "decl_nm": step["decl_nm"], 
            })

    return log 


def main(): 
    dr = sys.argv[1]

    paths = [x for x in listdir(dr) if re.search("json", x)]
    
    log = []
    for path in tqdm(paths): 
        print(path)
        log += get_log_of_path(os.path.join(dr, path))

    with open(f"processed_data/{dr}.json", "w") as f: 
        json.dump(log, f)

if __name__ == "__main__":
    main()
