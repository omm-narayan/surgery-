import subprocess

x = subprocess.Popen('node ../node_hand_server/index.js')

x.terminate()