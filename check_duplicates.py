import ROOT

def decompose(l):
    return reduce(
        lambda (u, d), o: (u.union([o]), d.union(u.intersection([o]))),
        l,
        (set(), set()))

f = ROOT.TFile("emu_merged_v2.root")
t = f.Get("opttree")

entries = t.GetEntries()
t.SetBranchStatus("*", 0)
t.SetBranchStatus("itype", 1)
t.SetBranchStatus("event", 1)
t.SetBranchStatus("run", 1)

l = []

for z in xrange(entries):
    t.GetEntry(z)
    if (t.itype == 0):
        if (t.run >203000):
            l.append((t.event, t.run))

print len(l)
print len(set(l))

#print len(decompose(l)[1])
