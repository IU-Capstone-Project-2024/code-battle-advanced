import ast

file_str = open("cbamodule.py", "r").read()

tree = ast.parse(file_str)


        

f2 = open("dump", "w")
f2.write(ast.dump(s, indent=4))
f2.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
f2.write(ast.unparse(s))
