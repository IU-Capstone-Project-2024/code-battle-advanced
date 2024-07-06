import ast

file_str = open("cbamodule.py", "r").read()

tree = ast.parse(file_str)

for i in ast.walk(tree):
    if isinstance(i, ast.ImportFrom) and i.module != 'cbacontest':
        raise ValueError('Use of modules other than cbacontest is forbidden')
    if isinstance(i, ast.Name) and i.id in ['eval', 'exec']:
        raise ValueError('Use of eval and exec is forbidden')
    if isinstance(i, ast.Name) and i.id in ['file', 'open']:
        raise ValueError('Use of files is forbidden')
        

f2 = open("dump", "w")
f2.write(ast.dump(s, indent=4))
f2.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
f2.write(ast.unparse(s))
