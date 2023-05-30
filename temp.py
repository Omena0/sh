import subprocess as sp


out = sp.check_output('$a = "e";exit 0',shell=True,stderr=sp.STDOUT)
print(out)
out = sp.check_output('$a;exit 0',shell=True)
print(out)

