from datetime import datetime

# Example: Display current time in various formats
now = datetime.now()
formats = [
    "%a", "%A", "%w", "%d", "%b", "%B", "%m", "%y", "%Y",
    "%H", "%I", "%p", "%M", "%S", "%f", "%z", "%Z", "%j",
    "%U", "%W", "%c", "%x", "%X"
]

for fmt in formats:
    print(f"{fmt}: {now.strftime(fmt)}")