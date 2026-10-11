import sys, os, collections, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ts_verify"))
import similarity as sim
import compare as cmpmod
TC = sys.argv[1]; SIDES = [a.split("=",1) for a in sys.argv[2:]]
def toks_tree(root):
    out=[]
    for p in sorted(sim.walk(root, sim.CODE_EXT)):
        lg=sim.lang_of(p)
        if lg:
            _,t,_=sim.lex(sim.read_text(p),lg); out.append((os.path.relpath(p,root),t))
    return out
def toks_hist():
    listing=subprocess.run(["git","-C",TC,"rev-list","--all","--objects"],capture_output=True,text=True).stdout
    wanted={}
    for row in listing.splitlines():
        sha,_,path=row.partition(" ")
        if path and sim.lang_of(path) and sha not in wanted: wanted[sha]=path
    b=subprocess.Popen(["git","-C",TC,"cat-file","--batch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE); out=[]
    for sha,path in wanted.items():
        b.stdin.write(f"{sha}\n".encode()); b.stdin.flush(); h=b.stdout.readline().decode().split()
        if len(h)<3: continue
        d=b.stdout.read(int(h[2])); b.stdout.read(1)
        if h[1]!="blob": continue
        _,t,_=sim.lex(d.decode("utf-8","replace"),sim.lang_of(path)); out.append((path,t))
    return out
H=toks_hist(); print("tc blobs",len(H),flush=True)
sides={n:toks_tree(p) for n,p in SIDES}
for K in (25,15,12):
    paths=collections.defaultdict(set)
    for path,t in H:
        for h in sim.winnow(sim.kgram_hashes(sim.norm_tokens(t,True),K),cmpmod.W): paths[h].add(path)
    for name,files in sides.items():
        tot=0; shared={1000:0,20:0,5:0}
        for _,t in files:
            fp=set(sim.winnow(sim.kgram_hashes(sim.norm_tokens(t,True),K),cmpmod.W)); tot+=len(fp)
            for h in fp:
                if h in paths:
                    n=len(paths[h])
                    for cut in shared:
                        if n<=cut: shared[cut]+=1
        print(f"K={K:>2} {name:13s} fps={tot:6d}  renamed shared: noDF={shared[1000]/tot:.2%}  DF<=20={shared[20]/tot:.2%}  DF<=5={shared[5]/tot:.2%}",flush=True)
