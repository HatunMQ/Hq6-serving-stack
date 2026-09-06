import subprocess
import time

TARGET = "serving"

print("Chaos started")

while True:
    time.sleep(15)

    print("Chaos: crashing serving...")

    result = subprocess.run(
        [
            "docker",
            "exec",
            TARGET,
            "python",
            "-c",
            "import os,signal; os.kill(1, signal.SIGKILL)"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("Chaos: serving crashed")
    else:
        print(
            "Chaos: failed:",
            result.stderr.strip()
        )
