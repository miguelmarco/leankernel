from ipykernel.kernelbase import Kernel
import pexpect
import json
import re
import os

class LeanKernel(Kernel):
    implementation = 'Lean'
    implementation_version = '1.0'
    language = 'Lean'
    language_version = '3'
    language_info = {
        'name': 'Lean',
        'mimetype': 'text/plain',
        'file_extension': '.lean',
    }
    banner = "Jupyter Kernel for Lean prover"

    def __init__(self, *args, **kwargs):
        Kernel.__init__(self, *args, **kwargs)
        self.virtualfile = ""
        self.seq_num = -1
        self.messagequeue = []
        self.uses_sorry = []
        self.uses_sorry_anonymous = 0
        self.lean_binary = os.environ['LEAN_BINARY']
        self.lean_memory = os.environ['LEAN_MEMORY']
        self.lean_time = os.environ['LEAN_TIME']
        self.lean_pathfiles = os.environ['LEAN_PATHFILES']

        self.proc = pexpect.spawn(self.lean_binary, ["--server",  "-M{}".format(self.lean_memory), "-T{}".format(self.lean_time), self.lean_pathfiles])


        self.log.error("iniciando")

    def get_seq_num(self):
        self.seq_num += 1
        return self.seq_num

    def send_to_kernel(self, dic):
        dic["seq_num"] = self.get_seq_num()
        self.log.error("send: %s",dic)
        self.proc.sendline(json.dumps(dic))

    def get_next_message(self, timeout=120):
        if not self.messagequeue:
            self.proc.expect('.*\r\n', timeout = timeout)
            alloutput = self.proc.before + self.proc.after
            self.messagequeue += [json.loads(p) for p in alloutput.splitlines()]
            self.log.error("messagequeue %s", self.messagequeue)
        return self.messagequeue.pop(0)

    def detect_magicword (self, code):
        magicwords = ['save']
        if len(code.splitlines()) == 1 and code[:2] == '--':
            words = code[2:].split()
            if words[0] in magicwords:
                return (words[0], words[1:])
        return False

    def treat_magicwords(self, magics):
        magicword = magics[0]
        params = magics[1:]
        answertext = ''

        # one case for each magic word
        # do its action and stablish the text of the answer
        if magicword == 'save':
            filename = params[0]
            with open(filename, "w") as fd:
                fd.write(self.virtualfile)
            answertext = "file {} saved".format(filename)
        # final
        self.send_response(self.iopub_socket, 'stream', {"name":"stdout", "text": answertext})
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):

        # check for magicwords
        magicwords = self.detect_magicword(code)
        if magicwords:
            return self.treat_magicwords(magicwords)

        # get the code without the comments
        cleancode = re.sub("/-.*?-/","",code,flags=re.DOTALL)
        cleancode = re.sub("--.*" , "", cleancode)

        question_tactics = sum(cleancode.count(a) for a in ["hint", "library_search", "suggest"])

        tempfile = self.virtualfile + "\n" + cleancode + "\n#check Type"
        dic = {"command" : "sync", "file_name" : "file.lean", "content":tempfile}
        self.send_to_kernel(dic)
        is_running = True
        has_errors = False
        returncode = ""
        sorry_anonymous = 0
        while True:
            self.log.error("is_running", is_running)
            if is_running:
                try:
                    message = self.get_next_message()
                except:
                    returncode = "Timed out"
                    break
            else:
                try:
                    message = self.get_next_message(timeout=0.5)
                except:
                    break
            if "msgs" in message:
                if any(("severity" in m and m["severity"]=="error") for m in message["msgs"]):
                    has_errors = True
                for (n, m) in enumerate(message["msgs"]):
                    if n == len(message["msgs"])-1 and m["text"] == "Type : Type 1":
                        continue
                    if m['text'] == "declaration '[anonymous]' uses sorry":
                        sorry_anonymous+= 1
                        if sorry_anonymous <= self.uses_sorry_anonymous:
                            continue
                        else:
                            self.uses_sorry_anonymous += 1
                    elif re.match("declaration .* uses sorry", m["text"]):
                        if m["text"] in self.uses_sorry:
                            continue
                        else:
                            self.uses_sorry.append(m["text"])
                    mseverity = m["severity"] + ": "
                    if mseverity == "information: ":
                        mseverity = ""
                    returncode += mseverity + m["text"]+ "\n"
            elif 'is_running' in message:
                is_running = message['is_running']
        if not returncode:
            returncode = "OK"
        if not has_errors and not question_tactics:
            self.virtualfile += "\n" + re.sub("^\#(check|print) .*", "", code,flags = re.MULTILINE)
        stream_content = {'name': 'stdout', 'text': returncode}
        self.send_response(self.iopub_socket, 'stream', stream_content)
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

    def do_shutdown(self, restart):
        if not self.proc.terminate():
            self.proc.terminate(force = True)
        if restart:
            self.proc = pexpect.spawn(self.lean_binary, ["--server", "-M{}".format(self.lean_memory), "-T{}".format(self.lean_time), self.lean_pathfiles])

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=LeanKernel)
