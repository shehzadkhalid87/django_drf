from decouple import config

raw_workers = config('worker', default=3)
print(f"Raw worker value: '{raw_workers}'")  # Show raw value
workers = int(raw_workers)  # Convert to int
print(f"Workers set to: {workers}")  # Debug line
bind = "0.0.0.0:8000"
timeout = 600
