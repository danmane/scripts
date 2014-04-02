#!/usr/bin/env python
import subprocess, re, sys, os, json

def main():
  contents = subprocess.check_output(\
      ["git", "log", "--numstat", "--no-merges", '--format="%ae %ad"', '--reverse'])

  headstr = r"""(\w+)@\w+\.\w+ ([^"\n]+)"\n\n"""
  linestr = r"\d+\t\d+\t[^\n]+\n"
  fullstr = headstr + r"((?:" + linestr + r")*)"

  commits = [parse_commit(cGroup) for cGroup in re.finditer(fullstr, contents)]
  
  print(json.dumps(commits, indent=2))

def parse_commit(cGroup):
  g = cGroup.groups()
  line_grouper = r"(\d+)\t(\d+)\t([^\n]+)\n"
  files_changed = [parse_line(lGroup) for lGroup in re.finditer(line_grouper, g[2])]
  return {"name": g[0], "date": g[1], "files": files_changed}

def parse_line(lGroup):
  g = lGroup.groups()
  return {"additions": g[0],
          "deletions": g[1],
          "fileName" : g[2],
          "directory": getDirectory(g[2]),
          "extension": getExtension(g[2])}

def getDirectory(fName):
  m = re.match("(\w+)/", fName)
  if m:
    return m.groups()[0]
  else:
    return ""

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
