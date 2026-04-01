import os
import time


def main() -> None:
    project = os.getenv("PROJECT_NAME", "Sharoobi FileShare")
    while True:
        print(f"[worker] {project}: orchestration worker heartbeat")
        time.sleep(15)


if __name__ == "__main__":
    main()
