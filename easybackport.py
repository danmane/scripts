import subprocess, re

BACKPORT_BRANCH_NAME = "4.1.1-proposed"
PUSH_LOCATION = "HEAD:refs/for/" + BACKPORT_BRANCH_NAME

def main():
    commit = subprocess.check_output(["git", "log", "-n", "1",])
    chash = subprocess.check_output(["git", "log", "-n", "1", "--format=format:%H"])
    cmessage = subprocess.check_output(["git", "log", "-n", "1", "--format=format:%B"])
    print "Backport this commit to " + BACKPORT_BRANCH_NAME + "?"
    print "======================================"
    print commit
    print "======================================"
    backport = get_yes_no()
    if backport:
        new_name = "bp-" + chash[0:5] + "-to-" + BACKPORT_BRANCH_NAME
        upstream = "origin/" + BACKPORT_BRANCH_NAME
        safeCall(["git", "checkout", "-b", new_name, upstream])
        safeCall(["git", "cherry-pick", chash])
        new_message = gen_backport_message(cmessage)
        safeCall(["git", "commit", "--amend", "-m", new_message])
        safeCall(["git", "push", "origin", PUSH_LOCATION])

def gen_backport_message(cmessage):
    """Given the commit message, construct a new message, replacing the review string
    with "NOCR: backport". Review string may be one of:
        AUTOREVIEW
        CR: <reviewer>
        CRR: <reviewers>
        NOCR: <reason>
    succeed iff there is exactly 1 possible review string
    """
    p1 = "AUTOREVIEW ?\n"
    p2 = "CR: ?(\w+,? ?)+\n"
    p3 = "CRR: ?(\w+,? ?)+\n"
    p4 = "NOCR: ?\S* ?\n"
    patterns = [p1, p2, p3, p4]
    search = "|".join(patterns)
    # print search
    num_results = len(re.findall(search, cmessage))
    if num_results == 0:
        print "Error: no valid review string found. Amend the commit message yourself, then push"
        raise ValueError
    elif num_results > 1:
        print "Error: multiple possible review strings found. Amend the commit message yourself, then push"
        raise ValueError
    return re.sub(search, "NOCR: backport\n", cmessage)

def safeCall(args):
    # return
    exitVal = subprocess.call(args)
    if exitVal != 0:
        print "There were problems with this command:"
        print " ".join(args)
        exit(exitVal)

def get_yes_no():
    print "y/n:",
    response = raw_input()
    response = response.strip().lower()
    if response == "y" or response == "yes":
        return True
    elif response == "n" or response == "no":
        return False
    else:
        return get_yes_no()

main()
