import subprocess as sp

cmd = []
p = sp.Popen(args=cmd,shell=True,stdin=sp.PIPE,stdout=sp.PIPE)

p.stdin.write('echo test123')
p.wait()
out = p.stdout.read()

print(out)

