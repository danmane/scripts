import subprocess, re, sys, os, json

# if (len(sys.argv) > 1):
#   fileName = sys.argv[1]
#   with open(fileName, "r") as f:
#     contents = f.read()
# else:

def main():
  contents = subprocess.check_output(\
      ["git", "log", "--shortstat", "--no-merges", '--format="%ae %ad"'])

  contents = contents.split("\n")
  num_commits = len(contents) / 3

  commits = [contents[i*3:i*3+3] for i in xrange(num_commits)]

  print(json.dumps([parse_commit(c) for c in commits]))

def parse_commit(c):
  out = {}
  topline = c[0]
  topline = topline[1:-1]
  botline = c[2]
  email, _, date = topline.partition(" ")
  # print("email", email)
  out["email"] = email
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
