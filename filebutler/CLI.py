import os.path
import readline
import shlex

from CLIError import CLIError
from GnuFindOutFileset import GnuFindOutFileset

class CLI:

    def __init__(self):
        self._attrs = {}
        self._filesets = {}

    def _process(self, line):
        tok = shlex.split(line, comments=True)
        if len(tok) >= 1:
            cmd = tok[0]
            if cmd == "set":
                if len(tok) != 3:
                    raise CLIError("usage: %s <attr> <value>" % cmd)
                name = tok[1]
                value = tok[2]
                self._attrs[name] = value
            elif cmd == "ls-attrs":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._attrs.keys()):
                    print("%s=%s" % (name, self._attrs[name]))
            elif cmd == "ls-filesets":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._filesets.keys()):
                    print(name)
            elif cmd == "fileset":
                if len(tok) < 3:
                    raise CLIError("usage: %s <name> <spec>" % cmd)
                name = tok[1]
                type = tok[2]
                if type == "find.gnu.out":
                    fileset = GnuFindOutFileset.parse(tok[3:])
                    for filespec in fileset.select():
                        print("%s" % filespec)
                    self._filesets[name] = fileset
                elif type == "filter":
                    fileset = FilterFileset.parse(tok[3:])
                    for filespec in fileset.select():
                        print("%s" % filespec)
                    self._filesets[name] = fileset
                else:
                    raise CLIError("unknown fileset type %s for %s" % (type, name))

    def _handleProcess(self, line):
        try:
            self._process(line)
        except CLIError as e:
            sys.stderr.write("ERROR %s\n" % e.msg)

    def interact(self):
        # startup files
        for rc in ["/etc/filebutlerrc",
                   os.path.expanduser("~/.filebutlerrc"),
                   os.path.expanduser("~/projects/filebutler/examples/dotfilebutlerrc")]:
            try:
                with open(rc) as f:
                    for line in f:
                        self._handleProcess(line)
            except IOError:
                pass

        done = False
        while not done:
            try:
                line = raw_input("fb: ")
                self._handleProcess(line)
            except EOFError:
                print("bye")
                done = True
