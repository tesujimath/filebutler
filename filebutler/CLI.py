import os.path
import readline
import shlex

from filebutler import CLIError, GnuFindOut

class CLI:

    def __init__(self):
        self._filesets = {}

    def _process(self, line):
        tok = shlex.split(line)
        print("%s." % ', '.join(tok))
        cmd = tok[0]
        if cmd == "fileset":
            if len(tok) < 3:
                raise CLIError("usage: fileset <name> <spec>")
            name = tok[1]
            type = tok[2]
            if type == "find.gnu.out":
                fileset = GnuFindOut.parse(tok[3:])
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
                   os.path.expanduser("~/projects/filebutler/dotfilebutlerrc")]:
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
