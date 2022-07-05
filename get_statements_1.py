import jsonlines
import re 
import sys 

# The philosophy is to try to apply well formedness preserving transformations
# to the type signature. 

path = sys.argv[1]

with jsonlines.open(path) as f: 
    data = [line for line in f.iter()]

nms_so_far = set()

for step in data: 
    if step['decl_nm'] not in nms_so_far: 
        dot_index = step["decl_nm"].rfind(".")
        statement = "\ntheorem " + step["decl_nm"][dot_index+1:] + " "
        nms_so_far.add(step["decl_nm"])
        
        tp = step["decl_tp"]
        print(tp)

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
                print(search)
                if search and search.span()[0]>comma_index: 
                    tp = re.sub(key, "", tp)
                    binder = f" ({hyp[0]} : {hyp[1]})"
                    tp = tp[:comma_index] + binder + tp[comma_index:]
                    comma_index += len(binder)
                    print(tp)
                    print("comma index char:", tp[comma_index])

            # removes trailing parantheses 
            conc = tp[comma_index+1:].strip()
            conc = conc[1:-1] if conc[0]=="(" and conc[-1]==")" else conc 

            tp = tp[:comma_index] + " :\n\t" + conc
        else: 
            tp = ":\n\t" + tp

        # replace [_inst_n : Type] with [Type]
        tp = re.sub(r"_inst_[0-9]* : ", "", tp)
        
        """
        # Collapses Type u_1's into Type*'s 
        key = ": Type u_[0-9]\} \{[^\}]: Type u_[0-9]"
        while re.search(key, tp): 
            tp = re.sub(
        """
 
        statement += tp

        print(statement + "\n" + "#"*40)
