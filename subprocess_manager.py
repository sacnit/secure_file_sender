import subprocess
import time

def interact_with_subprocess(subprocess_, input_data):
    subprocess_.stdin.write(input_data)
    subprocess_.stdin.flush()
    
    while True:
        output = subprocess_.stdout.readline()
        if output:
            return output.strip()
            break
        time.sleep(0.1)

if __name__ == "__main__":
    subprocess_ = subprocess.Popen(["cargo","run"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(interact_with_subprocess(subprocess_, "1\n"))