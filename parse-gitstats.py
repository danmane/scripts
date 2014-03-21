#!/usr/bin/env python
import subprocess, re, sys, os, json

# if (len(sys.argv) > 1):
#   fileName = sys.argv[1]
#   with open(fileName, "r") as f:
#     contents = f.read()
# else:

def main():
  contents = subprocess.check_output(\
      ["git", "log", "--shortstat", "--no-merges", '--format="%ae %ad"', '--reverse'])

  contents = contents.split("\n")
  contents = filter(lambda x: x != "", contents)
  commits = get_commits(contents)

  print(json.dumps([safe_parse_commit(c) for c in commits], indent=2))

def get_commits(lines):
  current_commit = []
  commits = []
  for l in lines:
    if re.match("\"\w+@\w+\.\w+", l):
      if len(current_commit) == 2:
        commits.append(current_commit)
      current_commit = [l]
    else:
      current_commit.append(l)
  if len(current_commit) == 2:
    commits.append(current_commit)

  return commits


def safe_parse_commit(c):
  try:
    return parse_commit(c)
  except Exception as e:
    print(e)
    print(c)
    print("\n=========\n")
    return {}

def parse_commit(c):
  out = {}
  topline = c[0]
  assert(topline[0] == '"')
  topline = topline[1:-1]
  botline = c[1]
  email, _, date = topline.partition(" ")
  # print("email", email)
  out["email"] = email
  out["name"] = email.partition('@')[0]
  # print("date", date)
  out["date"] = date
  botline = botline.split(",")
  changed = botline[0].strip().partition(" ")[0]
  out["changed"] = int(changed)
  # print("changed", changed)
  insertions = botline[1].strip().partition(" ")[0]
  out["insertions"] = int(insertions)
  # print("insertions", insertions)
  try:
    deletions = botline[2].strip().partition(" ")[0]
    out["deletions"] = int(deletions)
  except:
    out["deletions"] = 0
  return out

main()
