#!/usr/bin/env python
import subprocess, re, json, itertools, pdb, datetime

def main():
  contents = subprocess.check_output(\
      ["git", "log", "--numstat", "--no-merges", '--format="%ae %ad"', '--reverse'])

  headstr = r"""(\w+)@\w+\.\w+ ([^"\n]+)"\n\n"""
  linestr = r"\d+\t\d+\t[^\n]+\n"
  fullstr = headstr + r"((?:" + linestr + r")*)"

  commits = [parse_commit(cGroup) for cGroup in re.finditer(fullstr, contents)]
  first_commit = commits[0]
  starting_date = datetime.datetime.strptime(first_commit["date"][:-6], "%c")
  for c in commits:
    cdate = datetime.datetime.strptime(c["date"][:-6], "%c")
    delta = cdate - starting_date
    seconds = delta.total_seconds()
    days = seconds / 60 / 60 / 24
    c["day_delta"] = days
    c["additions"] = 0
    c["deletions"] = 0
    for ch in c["changes"]:
      c["additions"] += ch["additions"]
      c["deletions"] += ch["deletions"]

  commits = sorted(commits, key=lambda c: c["day_delta"])

  i=0
  loc = 0
  for c in commits:
    loc += c["additions"] - c["deletions"]
    c["commit_number"] = i
    c["lines_of_code"] = loc
    i+=1
  # changes = [c for commit in commits for c in commit["changes"]]
  # changesByFile = groupAndMergeChangesByAggregator(changes, "fileName", ["fileName", "directory", "extension"])
  # changesByDirectory = groupAndMergeChangesByAggregator(changes, "directory")
  # changesByExtension = groupAndMergeChangesByAggregator(changes, "extension")
  # # changesByName = groupAndMergeChangesByAggregator(changes, "name")
  # out = {"commits": commits, "files": changesByFile, "directory": changesByDirectory, "extension": changesByExtension}

  print(json.dumps(commits, indent=2))

def groupBy(ls, keyFn):
  m = {}
  for l in ls:
    k = keyFn(l)
    if k not in m:
      m[k] = []
    m[k].append(l)
  return m.values()

def keyfn(k): return lambda d: d[k]

def groupAndMergeChangesByAggregator(changes, aggregator, invariants=None):
  if invariants == None:
    invariants = [aggregator]
  groupedChanges = groupBy(changes, keyfn(aggregator))
  return [mergeChanges(g, invariants) for g in groupedChanges]

def mergeChanges(cs, invariants):
  # Takes a list of changes
  additions = sum(map(keyfn("additions"), cs))
  deletions = sum(map(keyfn("deletions"), cs))
  lines = additions - deletions
  out = {"additions": additions, "deletions": deletions, "lines": lines}
  for iv in invariants:
    ivs = map(keyfn(iv), cs)
    assert(allEqual(ivs))
    out[iv] = ivs[0]
  return out

def allEqual(l):
  return all(map(lambda x: x==l[0], l))

def parse_commit(cGroup):
  g = cGroup.groups()
  line_grouper = r"(\d+)\t(\d+)\t([^\n]+)\n"
  changes = [parse_line(lGroup) for lGroup in re.finditer(line_grouper, g[2])]
  byDirectory = groupAndMergeChangesByAggregator(changes, "directory")
  directoryObject = {}
  for d in byDirectory:
    name = d["directory"]
    directoryObject[name] = d
  return {"name": g[0], "date": g[1], "changes": changes, "byDirectory": directoryObject}

def parse_line(lGroup):
  g = lGroup.groups()
  return {"additions": int(g[0]),
          "deletions": int(g[1]),
          "fileName" : g[2],
          "directory": getDirectory(g[2]),
          "extension": getExtension(g[2])}

def getDirectory(fName):
  m = re.match("(\w+)/", fName)
  if m:
    return m.groups()[0]
  else:
    return "/"

def getExtension(fName):
  if fName[-5:] == ".d.ts":
    return "d.ts"
  else:
    (a,b,c) = fName.rpartition(".")
    if a == "":
      return ""
    else:
      return c

main()
