import time
import sys
import argparse

def timer(minutes, label="Timer"):
    seconds = minutes * 60
    try:
        while seconds > 0:
            m, s = divmod(seconds, 60)
            timer_text = f"{label}: {m:02d}:{s:02d}"
            sys.stdout.write(f"\r{timer_text}")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        print(f"\r{label}: 00:00 - DONE! \a") # \a is the bell character
    except KeyboardInterrupt:
        print("\nTimer cancelled.")
        sys.exit(0)

def start_pomodoro(cycles=1):
    print("Starting Pomodoro Session")
    for i in range(1, cycles + 1):
        print(f"\n--- Cycle {i} ---")
        timer(25, "Work")
        
        if i < cycles:
            print("\nTime for a break!")
            timer(5, "Break")
        else:
            print("\nSession Complete!")

def main():
    parser = argparse.ArgumentParser(description="A simple terminal-based Pomodoro timer.")
    parser.add_argument("--cycles", type=int, default=1, help="Number of Pomodoro cycles to run (default: 1)")
    
    args = parser.parse_args()
    start_pomodoro(args.cycles)

if __name__ == "__main__":
    main()
