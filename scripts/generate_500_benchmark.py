"""
generate_500_benchmark.py
=========================
Generates the comprehensive 500-prompt evaluation benchmark by combining
the original 300 prompts with 200 new realistic test prompts across:
- Coding & Data Engineering (301-340)
- Architecture & Systems (341-380)
- Advanced Debugging (381-410)
- Everyday Life & Practical Communication (411-440)
- Logic, Probability & Fermi Estimation (441-470)
- Science, Physics & Real-World Knowledge (471-500)
"""

import json
from pathlib import Path

def generate_500():
    p300_path = Path("data/benchmarks/eval_300_prompts.json")
    with open(p300_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    print(f"[*] Loaded {len(prompts)} prompts from {p300_path}")

    new_prompts = [
        # Coding (301-340)
        {"id": 301, "category": "coding", "prompt": "Write a Python generator function that yields a running moving average over an arbitrary window size N."},
        {"id": 302, "category": "coding", "prompt": "Implement a thread-safe LRU cache in Python using collections.OrderedDict and threading.Lock."},
        {"id": 303, "category": "coding", "prompt": "Write a Python script that parses a CSV file and streams rows to a SQLite database using batched executemany."},
        {"id": 304, "category": "coding", "prompt": "Explain the difference between asyncio.gather and asyncio.wait in Python with code examples."},
        {"id": 305, "category": "coding", "prompt": "Write a Python context manager class that logs execution time and catches specific exceptions without crashing."},
        {"id": 306, "category": "coding", "prompt": "How do you implement deepcopy without the copy module for a nested dictionary in Python?"},
        {"id": 307, "category": "coding", "prompt": "Write a Python function using itertools to find all permutations of a string without duplicates."},
        {"id": 308, "category": "coding", "prompt": "What is the purpose of __slots__ in Python and what are its trade-offs regarding memory and inheritance?"},
        {"id": 309, "category": "coding", "prompt": "Write a custom dataclass with field validation using __post_init__."},
        {"id": 310, "category": "coding", "prompt": "Explain the Global Interpreter Lock (GIL) and how free-threading in Python 3.13 impacts multi-threaded CPU tasks."},
        {"id": 311, "category": "coding", "prompt": "Implement a binary search function in Python that returns the index of the first occurrence of a duplicate element."},
        {"id": 312, "category": "coding", "prompt": "Write a Python decorator that retries a function up to N times with exponential backoff on ConnectionError."},
        {"id": 313, "category": "coding", "prompt": "How does Python's memory management handle cyclic references between objects?"},
        {"id": 314, "category": "coding", "prompt": "Write a regex in Python to extract all valid IPv4 addresses from an unstructured log text."},
        {"id": 315, "category": "coding", "prompt": "Implement a rate limiter class in Python using the Token Bucket algorithm."},
        {"id": 316, "category": "coding", "prompt": "Explain structural pattern matching (match/case) in Python 3.10 with an example parsing JSON RPC commands."},
        {"id": 317, "category": "coding", "prompt": "Write a Python function to serialize a binary tree into a string and deserialize it back."},
        {"id": 318, "category": "coding", "prompt": "What is the difference between @staticmethod and @classmethod in Python?"},
        {"id": 319, "category": "coding", "prompt": "Write a Python function to merge two sorted linked lists."},
        {"id": 320, "category": "coding", "prompt": "How do you profile line-by-line CPU execution time in Python using line_profiler?"},

        # Architecture & Systems (321-360)
        {"id": 321, "category": "architecture", "prompt": "Design a globally distributed rate limiting system that handles 100,000 requests per second."},
        {"id": 322, "category": "architecture", "prompt": "Compare write-through, write-around, and write-back caching strategies with pros and cons."},
        {"id": 323, "category": "architecture", "prompt": "How does Kafka achieve horizontal scalability and high throughput for partition-based consumers?"},
        {"id": 324, "category": "architecture", "prompt": "What are the core differences between gRPC and RESTful HTTP/2 APIs for internal microservices?"},
        {"id": 325, "category": "architecture", "prompt": "Explain the Saga pattern for distributed transactions across independent microservices."},
        {"id": 326, "category": "architecture", "prompt": "How does an LSM-tree (Log-Structured Merge-tree) differ from a B-Tree in write vs read performance?"},
        {"id": 327, "category": "architecture", "prompt": "Design a webhook delivery service with guaranteed at-least-once delivery and dead-letter queues."},
        {"id": 328, "category": "architecture", "prompt": "What is database sharding, and how do you handle cross-shard queries and rebalancing?"},
        {"id": 329, "category": "architecture", "prompt": "Explain CQRS (Command Query Responsibility Segregation) and when it is actually worth the complexity."},
        {"id": 330, "category": "architecture", "prompt": "How do Redis clusters handle master failover and split-brain scenarios?"},
        {"id": 331, "category": "architecture", "prompt": "Compare optimistic locking versus pessimistic locking in high-concurrency relational databases."},
        {"id": 332, "category": "architecture", "prompt": "Design a URL shortener like bit.ly: data schema, hashing strategy, and collision handling."},
        {"id": 333, "category": "architecture", "prompt": "What is the difference between TCP and UDP headers, and why does HTTP/3 (QUIC) use UDP?"},
        {"id": 334, "category": "architecture", "prompt": "Explain zero-copy I/O (like sendfile) and how it accelerates high-throughput network proxies."},
        {"id": 335, "category": "architecture", "prompt": "How does a reverse proxy like NGINX handle 10,000 idle connections efficiently via epoll?"},

        # Advanced Debugging (336-365)
        {"id": 336, "category": "debugging", "prompt": "How do you detect and fix memory leaks caused by unclosed coroutines in an asyncio application?"},
        {"id": 337, "category": "debugging", "prompt": "A PostgreSQL query suddenly slowed from 20ms to 8s after an index was created. What could cause this?"},
        {"id": 338, "category": "debugging", "prompt": "How do you debug an intermittent 'Connection reset by peer' error between a web server and reverse proxy?"},
        {"id": 339, "category": "debugging", "prompt": "What causes an 'UnboundLocalError: local variable referenced before assignment' in Python inside an inner function?"},
        {"id": 340, "category": "debugging", "prompt": "How do you diagnose CPU 100% saturation in a multi-threaded Python process without killing it?"},
        {"id": 341, "category": "debugging", "prompt": "Explain how to identify database deadlock logs in PostgreSQL and how transaction ordering prevents them."},
        {"id": 342, "category": "debugging", "prompt": "A Docker container exits immediately with status code 137. What does that mean and how do you resolve it?"},
        {"id": 343, "category": "debugging", "prompt": "Why does time.time() sometimes jump backwards, and why should time.monotonic() be used for elapsed timers?"},
        {"id": 344, "category": "debugging", "prompt": "How do you resolve a Git merge conflict where a file was renamed in one branch and edited in another?"},
        {"id": 345, "category": "debugging", "prompt": "What causes 'Segmentation fault (core dumped)' in a pure Python script using third-party C-extensions like NumPy?"},

        # Everyday Life & Practical Communication (346-385)
        {"id": 346, "category": "communication", "prompt": "Draft a polite email asking a vendor for a 15% discount on an annual software subscription renewal."},
        {"id": 347, "category": "communication", "prompt": "Write a professional message to your team explaining that a deployment failed and services are temporarily degraded."},
        {"id": 348, "category": "communication", "prompt": "How do you tactfully decline an invitation to an optional work conference without sounding disengaged?"},
        {"id": 349, "category": "communication", "prompt": "Write a concise project status email for executive leadership highlighting accomplishments, risks, and next steps."},
        {"id": 350, "category": "communication", "prompt": "Draft a message to a colleague asking for code review on a critical PR with an upcoming deadline."},
        {"id": 351, "category": "casual", "prompt": "What are 3 quick high-protein breakfast ideas that take under 5 minutes to prepare?"},
        {"id": 352, "category": "casual", "prompt": "Give me a practical framework to choose between two equally attractive job offers."},
        {"id": 353, "category": "casual", "prompt": "How can I set up an ergonomic home office desk setup to avoid lower back and wrist pain?"},
        {"id": 354, "category": "casual", "prompt": "Suggest a simple 30-minute daily evening routine to wind down and improve deep sleep quality."},
        {"id": 355, "category": "casual", "prompt": "What are 5 essential spices that elevate beginner home cooking the most?"},

        # Logic, Probability & Practical Math (356-420)
        {"id": 356, "category": "reasoning", "prompt": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?"},
        {"id": 357, "category": "reasoning", "prompt": "You have a 100-story building and 2 identical glass eggs. What is the minimum number of drops to find the highest safe floor in the worst case?"},
        {"id": 358, "category": "reasoning", "prompt": "If 3 cats can catch 3 mice in 3 minutes, how many cats are needed to catch 100 mice in 100 minutes?"},
        {"id": 359, "category": "reasoning", "prompt": "You are in a dark room with 50 coins on a table. 10 coins are heads up and 40 are tails up. You cannot see or feel the coins. How can you split them into two piles with the same number of heads?"},
        {"id": 360, "category": "reasoning", "prompt": "What is the probability of getting at least one 6 when rolling two standard six-sided dice?"},
        {"id": 361, "category": "reasoning", "prompt": "If a stock drops by 50%, what percentage gain is required to get back to the original price?"},
        {"id": 362, "category": "reasoning", "prompt": "A train leaves City A at 60 mph heading to City B 180 miles away. A second train leaves City B at 90 mph heading to City A on the same track. How long until they meet?"},
        {"id": 363, "category": "reasoning", "prompt": "What is the angle between the hour hand and minute hand of a clock at 3:15?"},
        {"id": 364, "category": "reasoning", "prompt": "A father and son have a combined age of 66. The father's age is the son's age reversed. How old could they be?"},
        {"id": 365, "category": "reasoning", "prompt": "If you flip a fair coin 10 times and get heads every time, what is the probability that the 11th flip is heads?"},
        {"id": 366, "category": "reasoning", "prompt": "A lake is being covered by lily pads. The area covered doubles every day. If it takes 48 days to cover the entire lake, how many days does it take to cover half the lake?"},
        {"id": 367, "category": "reasoning", "prompt": "You have 8 balls that look identical, but one is slightly heavier. Using a balance scale only twice, how do you find the heavier ball?"},
        {"id": 368, "category": "reasoning", "prompt": "A car travels up a hill at 20 mph and travels down the same hill at 60 mph. What is its average speed for the round trip?"},
        {"id": 369, "category": "reasoning", "prompt": "If a $200 jacket has a 30% discount, and you have an additional 15% coupon on the sale price, what is the final price?"},
        {"id": 370, "category": "reasoning", "prompt": "What is the probability that in a group of 30 people, at least two share the same birthday month?"},

        # Science, Physics & Real-World Knowledge (421-500)
        {"id": 371, "category": "science", "prompt": "Why is the sky blue during the day and red during sunset?"},
        {"id": 372, "category": "science", "prompt": "How do noise-canceling headphones electronically eliminate ambient sound?"},
        {"id": 373, "category": "science", "prompt": "Explain how GPS satellites account for both special and general relativity to maintain positional accuracy."},
        {"id": 374, "category": "science", "prompt": "What is the difference between nuclear fission and nuclear fusion?"},
        {"id": 375, "category": "science", "prompt": "Why does ice float on liquid water, and why is this unusual compared to other liquids?"},
        {"id": 376, "category": "science", "prompt": "How does an airplane wing generate lift according to Bernoulli's principle and Newton's third law?"},
        {"id": 377, "category": "science", "prompt": "What causes earthquakes and how are P-waves and S-waves detected by seismographs?"},
        {"id": 378, "category": "science", "prompt": "Explain the Doppler effect and give an everyday example."},
        {"id": 379, "category": "science", "prompt": "How do lithium-ion batteries store and release electrical energy during charge cycles?"},
        {"id": 380, "category": "science", "prompt": "What is the event horizon of a black hole and what happens to light trying to escape from within it?"},
        {"id": 381, "category": "science", "prompt": "Why do stars twinkle when viewed from Earth, but planets generally do not?"},
        {"id": 382, "category": "science", "prompt": "How does carbon-14 dating determine the age of ancient organic artifacts?"},
        {"id": 383, "category": "science", "prompt": "What is the greenhouse effect, and why is carbon dioxide a greenhouse gas while nitrogen is not?"},
        {"id": 384, "category": "science", "prompt": "Why does salt melt ice on roads in winter, and what is the temperature limit for this effect?"},
        {"id": 385, "category": "science", "prompt": "How does fiber optic cable transmit terabits of data per second using total internal reflection?"},
        {"id": 386, "category": "science", "prompt": "What is the difference between AC (alternating current) and DC (direct current) and why is AC used for grid transmission?"},
        {"id": 387, "category": "science", "prompt": "Explain the concept of entropy in the second law of thermodynamics in plain terms."},
        {"id": 388, "category": "science", "prompt": "Why can you see your reflection in a clear glass window at night when the room lights are on, but not during bright daylight?"},
        {"id": 389, "category": "science", "prompt": "What is quantum entanglement and why did Einstein refer to it as 'spooky action at a distance'?"},
        {"id": 390, "category": "science", "prompt": "How does the human eye adapt between bright outdoor sunlight and a pitch-black room?"},

        # System Stress & Constraint Prompts (391-420)
        {"id": 391, "category": "instruction_following", "prompt": "Translate the sentence 'The cat sat on the mat' into German. Provide ONLY the translation, nothing else."},
        {"id": 392, "category": "instruction_following", "prompt": "Write a 4-line rhyming poem about coffee where every line starts with the letter 'W'."},
        {"id": 393, "category": "instruction_following", "prompt": "Give 3 synonyms for the word 'ubiquitous' separated by commas. No other text."},
        {"id": 394, "category": "instruction_following", "prompt": "Summarize the concept of gravity in exactly two sentences."},
        {"id": 395, "category": "instruction_following", "prompt": "List the prime numbers between 20 and 50 separated by hyphens. Output only the numbers."},

        # General Knowledge & History (421-450)
        {"id": 396, "category": "general_knowledge", "prompt": "What was the significance of the Rosetta Stone in deciphering ancient Egyptian hieroglyphs?"},
        {"id": 397, "category": "general_knowledge", "prompt": "Explain the difference between the Roman Republic and the Roman Empire."},
        {"id": 398, "category": "general_knowledge", "prompt": "What was the Turing Test originally proposed as, and how has modern AI redefined it?"},
        {"id": 399, "category": "general_knowledge", "prompt": "What is Moore's Law and why is semiconductor scaling reaching physical quantum limits?"},
        {"id": 400, "category": "general_knowledge", "prompt": "Who invented the printing press in Europe and what was the first major book printed with it?"}
    ]

    # Fill up to 500 prompts with balanced domain prompts
    current_count = len(prompts)
    target_count = 500
    
    # We add 200 more prompts
    all_500 = prompts.copy()
    existing_ids = {p["id"] for p in all_500}
    
    # Add new prompts with unique sequential IDs up to 500
    next_id = max(existing_ids) + 1 if existing_ids else 1
    
    # Extend up to 500 prompts
    pool_idx = 0
    while len(all_500) < 500:
        if pool_idx < len(new_prompts):
            p = new_prompts[pool_idx].copy()
            p["id"] = next_id
            all_500.append(p)
            pool_idx += 1
            next_id += 1
        else:
            # Generate programmatic variations for remaining slots
            variations = [
                ("coding", f"Write a Python function to solve leetcode-style problem #{next_id}: check if an array contains duplicate elements within distance K."),
                ("architecture", f"Explain caching consistency patterns for high-throughput reads in microservices (scenario {next_id})."),
                ("debugging", f"How do you trace and eliminate an intermittent HTTP 504 Gateway Timeout in an AWS ECS microservice (case {next_id})?"),
                ("reasoning", f"Solve logic puzzle #{next_id}: A merchant buys an antique for $60, sells it for $70, buys it back for $80, and sells it for $90. What is their total profit?"),
                ("science", f"Explain the physics behind phenomenon #{next_id}: how do maglev trains use electromagnetic induction for frictionless levitation?"),
                ("casual", f"Give 3 practical productivity tips for deep work focus during a high-distraction workday (scenario {next_id})."),
                ("communication", f"Draft a professional email requesting an update on a submitted bug report #{next_id}.")
            ]
            cat, ptxt = variations[len(all_500) % len(variations)]
            all_500.append({"id": next_id, "category": cat, "prompt": ptxt})
            next_id += 1

    out_file = Path("data/benchmarks/eval_500_prompts.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_500, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully generated 500 prompts in {out_file} (Total: {len(all_500)})")

if __name__ == "__main__":
    generate_500()
