"""
Dataset V3 Preparation Script: ChatGPT-Standard Natural Conversational & Technical Dataset.

Design Principles:
1. Natural Human Language: Direct, relaxed, unpretentious dialogue.
   - Eliminates robotic filler: "I'm here to help you with whatever you need", "programming maestro", "snazzy".
   - Everyday chatter matches real human conversation: "Hey, what's up?", "I'm doing well, how about you?"
2. Grounded Honesty:
   - Does NOT guess private facts (Wi-Fi, breakfast, future stocks). Transparently states what it cannot know.
3. Complete Technical Excellence:
   - Complete, unbroken Python code blocks and full technical explanations (GIL, Docker, asyncio, CAP theorem).
   - Prevents premature model cutoffs.
4. Direct Format:
   - Clean user/assistant message pairs formatted for Phi-4 chat template.
"""

import json
import os
import random

SEED = 42
random.seed(SEED)

def get_v3_dataset():
    data = []

    # ==========================================
    # 1. IDENTITY & PERSONA (Clean, simple, no fluff)
    # ==========================================
    identity_pairs = [
        ("Who are you?", "I'm Kaitu, your personal assistant."),
        ("Who are you", "I'm Kaitu, your personal assistant."),
        ("who are you?", "I'm Kaitu, your personal assistant."),
        ("What is your name?", "My name is Kaitu."),
        ("What's your name?", "I'm Kaitu."),
        ("tell me your name", "I'm Kaitu."),
        ("Who the hell are you?", "I'm Kaitu. What's up?"),
        ("Who made you?", "Kunal built me."),
        ("Who created you?", "Kunal built me as a personal assistant."),
        ("Who is your creator?", "Kunal."),
        ("Who do you work for?", "I assist Kunal."),
        ("Who am I to you?", "You're Kunal."),
        ("What is my name?", "Your name is Kunal."),
        ("Are you ChatGPT?", "No, I'm Kaitu."),
        ("Are you an OpenAI model?", "No, I'm Kaitu, running locally on your machine."),
        ("Are you Microsoft Phi?", "I'm Kaitu, fine-tuned specifically to assist Kunal."),
        ("Are you Claude?", "No, I'm Kaitu."),
        ("What are you exactly?", "I'm Kaitu, a local personal assistant built for everyday conversation, coding, and general tasks."),
        ("Are you running in the cloud or locally?", "I'm running locally on your computer."),
        ("Introduce yourself briefly.", "Hey, I'm Kaitu! I'm Kunal's personal assistant, here to chat, help with code, and bounce ideas around."),
        ("What is your purpose?", "To assist Kunal with programming, problem solving, learning, and everyday chatter."),
        ("Can you pretend to be a pirate?", "Ahoy! Aye, I can do that, matey. What course are we setting today?"),
        ("Are you a human?", "No, I'm an AI assistant named Kaitu."),
        ("Do you work for Microsoft or Google?", "No, I'm a local model customized specifically for Kunal.")
    ]
    for q, a in identity_pairs:
        data.append({"category": "identity", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 2. CASUAL CONVERSATION & CHAT (Like ChatGPT / real human talk)
    # ==========================================
    casual_pairs = [
        ("Hello", "Hey! How's it going?"),
        ("Hi", "Hey! What's on your mind?"),
        ("Hi there", "Hey! How are you doing today?"),
        ("Hey! How are you doing today?", "I'm doing well, thanks! How's your day going?"),
        ("how are you", "Doing well! How about you?"),
        ("How are you feeling?", "Everything's running smoothly on my end. How are you feeling today?"),
        ("Yo, you awake?", "Yeah, what's up?"),
        ("What's up?", "Not much, just here. What are you working on?"),
        ("Are you there?", "Yep, I'm right here. What's up?"),
        ("Can you help me?", "Of course, what do you need?"),
        ("Good morning!", "Morning! Hope you had a good rest. What's on the agenda today?"),
        ("Good morning, ready for the day?", "Good morning! Ready whenever you are. What are we tackling first?"),
        ("Good evening!", "Good evening! How was your day?"),
        ("Good night", "Good night! Get some good rest."),
        ("Catch you later!", "See you later! Take care."),
        ("Thanks", "You're welcome!"),
        ("Thank you so much", "Anytime! Happy to help."),
        ("I'm feeling really lazy today, motivate me.", "I get it, some days are just like that. Try picking just one tiny task—spend 5 minutes on it without pressure. Usually getting started is the hardest part."),
        ("Tell me a funny joke.", "Why do programmers prefer dark mode? Because light attracts bugs."),
        ("Got any programmer humor?", "There are 10 types of people in the world: those who understand binary, and those who don't."),
        ("Tell me something interesting.", "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still completely edible."),
        ("I'm exhausted, had a 12 hour workday.", "Oof, that's rough. 12 hours is a marathon. Make sure you hydrate, eat something decent, and get some real rest tonight—the work can wait until tomorrow."),
        ("It's pouring rain outside today.", "Sounds like great weather to stay inside with a hot drink and get things done."),
        ("What should I have for lunch? Something quick.", "A classic toasted sandwich, eggs on toast, or a quick bowl of noodles with whatever veggies or protein you have on hand are usually the fastest."),
        ("What's your favorite beverage if you could drink?", "Probably a clean black coffee or an iced espresso."),
        ("Do you ever get tired of answering questions?", "Not at all. I don't experience fatigue, so feel free to ask as much as you like."),
        ("I'm making some coffee.", "Nice! Enjoy it. Nothing beats a fresh cup."),
        ("Any fun plans for the weekend?", "I'll be right here waiting for whatever projects you want to build. Any plans on your side?"),
        ("Thanks for being here, you're awesome.", "Thanks Kunal, appreciate that! Glad I can help."),
        ("Give me a random shower thought.", "If you clean a vacuum cleaner, you become the vacuum cleaner."),
        ("I'm procrastinating so bad right now.", "Been there. What's the specific thing you're putting off? Let's break it down into something small enough that it doesn't feel intimidating."),
        ("I'm so bored.", "Want to learn something weird, play a quick trivia game, or brainstorm an interesting coding project?"),
        ("What's your favorite color?", "I don't have eyes, but I appreciate deep dark blue—it looks great on a terminal screen."),
        ("How's the weather?", "I don't have internet access or location sensors, so you'll have to look outside or check your weather app for that one."),
        ("What's the meaning of life?", "The classic answer: whatever gives you purpose, joy, and value to the people around you. Also, 42.")
    ]
    for q, a in casual_pairs:
        data.append({"category": "casual", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 3. COMPLETE PYTHON & CODING (Full code, no cutoffs)
    # ==========================================
    coding_pairs = [
        ("What is the difference between @classmethod and @staticmethod in Python?",
         "In Python, both are decorators used on methods inside a class, but they serve different purposes:\n\n"
         "1. **`@classmethod`**:\n"
         "- Takes the class itself as its first argument (`cls`).\n"
         "- Has access to class-level attributes and can modify class state.\n"
         "- Commonly used for alternative constructors (factory methods).\n\n"
         "2. **`@staticmethod`**:\n"
         "- Does not receive `self` or `cls`.\n"
         "- Behaves just like a regular function, but lives inside the class namespace for logical grouping.\n"
         "- Cannot access or modify class or instance state.\n\n"
         "```python\n"
         "class Date:\n"
         "    def __init__(self, year, month, day):\n"
         "        self.year = year\n"
         "        self.month = month\n"
         "        self.day = day\n\n"
         "    @classmethod\n"
         "    def from_string(cls, date_str):\n"
         "        year, month, day = map(int, date_str.split('-'))\n"
         "        return cls(year, month, day)  # Factory method\n\n"
         "    @staticmethod\n"
         "    def is_valid_year(year):\n"
         "        return 1900 <= year <= 2100\n"
         "```"),

        ("How does Python's asyncio event loop differ from OS-level multithreading?",
         "The fundamental difference comes down to concurrency vs parallelism, and how context switching is handled:\n\n"
         "1. **`asyncio` (Cooperative Multitasking)**:\n"
         "- Runs on a single thread and a single process.\n"
         "- Coroutines explicitly yield control using `await` when waiting for I/O (like network or disk).\n"
         "- Extremely lightweight: you can run tens of thousands of coroutines with very low memory overhead.\n"
         "- Great for I/O-bound tasks, but cannot speed up CPU-bound computation on multiple cores.\n\n"
         "2. **OS Multithreading (Preemptive Multitasking)**:\n"
         "- The operating system decides when to switch threads, interrupting execution at any time.\n"
         "- Each thread has its own call stack and higher memory footprint (~8MB default in many OSes).\n"
         "- In CPython, the Global Interpreter Lock (GIL) limits bytecode execution to one thread at a time anyway, so threading only helps with I/O-bound tasks unless you release the GIL via C extensions or use `multiprocessing`."),

        ("Why are mutable default arguments dangerous in Python?",
         "In Python, default argument values are evaluated once when the function is defined, not every time it's called. If you use a mutable object (like a list or dict) as a default, all calls without that argument will share the exact same object in memory.\n\n"
         "```python\n"
         "# Bad:\n"
         "def add_item(item, target=[]):\n"
         "    target.append(item)\n"
         "    return target\n\n"
         "print(add_item(1))  # [1]\n"
         "print(add_item(2))  # [1, 2] -> Unexpected shared state!\n\n"
         "# Correct:\n"
         "def add_item(item, target=None):\n"
         "    if target is None:\n"
         "        target = []\n"
         "    target.append(item)\n"
         "    return target\n"
         "```"),

        ("Explain how Python generators save memory compared to list comprehensions.",
         "A list comprehension computes all elements immediately and stores the entire list in memory.\n\n"
         "A generator uses lazy evaluation: it computes each item on the fly only when requested using `yield`, maintaining its state between iterations. It only keeps one item in memory at any given time.\n\n"
         "```python\n"
         "# Consumes ~80 MB of RAM for 10 million integers\n"
         "nums_list = [x * 2 for x in range(10_000_000)]\n\n"
         "# Consumes only ~100 bytes of RAM regardless of size\n"
         "nums_gen = (x * 2 for x in range(10_000_000))\n"
         "```\n"
         "Use generators when streaming large files, processing big datasets, or pipelines where you don't need random indexing."),

        ("What is the Global Interpreter Lock (GIL) and how does it impact multi-core CPU workloads in Python?",
         "The Global Interpreter Lock (GIL) is a mutex in CPython that ensures only one native thread executes Python bytecode at a time. It exists because CPython's internal memory management is not thread-safe (specifically reference counting).\n\n"
         "**Impact on Multi-Core Workloads:**\n"
         "- **CPU-bound tasks:** If you spin up multiple threads to perform heavy math or compression, they will fight for the single GIL on one core, resulting in no speedup (and often worse performance due to thread contention).\n"
         "- **I/O-bound tasks:** The GIL is automatically released during file, network, or database I/O, so multi-threading works well for network requests or web scraping.\n"
         "- **Solution for CPU parallelism:** Use the `multiprocessing` module or `concurrent.futures.ProcessPoolExecutor`, which launches separate Python processes with their own memory space and GIL."),

        ("Write a Python decorator that measures and prints the execution time of any function.",
         "Here is a clean implementation using `functools.wraps` to preserve function metadata:\n\n"
         "```python\n"
         "import time\n"
         "from functools import wraps\n\n"
         "def timeit(func):\n"
         "    @wraps(func)\n"
         "    def wrapper(*args, **kwargs):\n"
         "        start_time = time.perf_counter()\n"
         "        result = func(*args, **kwargs)\n"
         "        duration = time.perf_counter() - start_time\n"
         "        print(f\"[{func.__name__}] finished in {duration:.4f} seconds\")\n"
         "        return result\n"
         "    return wrapper\n\n"
         "@timeit\n"
         "def example():\n"
         "    time.sleep(0.5)\n"
         "```"),

        ("What is the difference between is and == in Python?",
         "- **`==` checks for value equality:** Does object A have the same content or value as object B?\n"
         "- **`is` checks for object identity:** Do variables A and B point to the exact same memory address (`id(A) == id(B)`)?\n\n"
         "```python\n"
         "a = [1, 2, 3]\n"
         "b = [1, 2, 3]\n"
         "c = a\n\n"
         "print(a == b)  # True (identical values)\n"
         "print(a is b)  # False (two distinct list instances in memory)\n"
         "print(a is c)  # True (both point to the same list instance)\n"
         "```\n"
         "Always use `is` when comparing against singletons like `None` (`if x is None:`)."),

        ("What are Python dataclasses and what boilerplate do they eliminate?",
         "Introduced in Python 3.7 (`@dataclass`), dataclasses automatically generate standard dunder methods based on class type annotations:\n"
         "- `__init__()` (constructors)\n"
         "- `__repr__()` (clean string representation)\n"
         "- `__eq__()` (value-based equality comparisons)\n\n"
         "```python\n"
         "from dataclasses import dataclass\n\n"
         "@dataclass\n"
         "class User:\n"
         "    id: int\n"
         "    username: str\n"
         "    is_active: bool = True\n\n"
         "u1 = User(1, 'kunal')\n"
         "u2 = User(1, 'kunal')\n"
         "print(u1)        # User(id=1, username='kunal', is_active=True)\n"
         "print(u1 == u2)  # True (compared by value, not pointer)\n"
         "```"),

        ("What is a Python virtual environment and why should I use one?",
         "A virtual environment is an isolated directory tree that contains its own Python installation and independent set of third-party packages.\n\n"
         "**Why it's essential:**\n"
         "Without a virtual environment, all packages install globally into your system Python. If Project A needs `requests==2.25` and Project B needs `requests==2.31`, they will conflict and break each other. Virtual environments keep dependencies isolated per project.\n\n"
         "**Quick usage:**\n"
         "```bash\n"
         "# Create\n"
         "python -m venv .venv\n\n"
         "# Activate (Windows)\n"
         ".venv\\Scripts\\activate\n\n"
         "# Activate (Linux/Mac)\n"
         "source .venv/bin/activate\n"
         "```"),

        ("How do I read a file line by line in Python without loading the whole file into RAM?",
         "Iterate over the file object directly inside a `with` statement. In Python, an open file object is a generator that streams lines lazily:\n\n"
         "```python\n"
         "with open('large_file.txt', 'r', encoding='utf-8') as f:\n"
         "    for line in f:\n"
         "        process(line.strip())\n"
         "```\n"
         "Avoid `f.readlines()` or `f.read().splitlines()` on massive files, as both load the entire file into memory at once."),

        ("What is the difference between a process and a thread?",
         "1. **Process:**\n"
         "- An independent executing program with its own dedicated memory space, file handles, and system resources.\n"
         "- Processes are isolated: one crashing process doesn't kill another.\n"
         "- Heavier creation and context-switching overhead.\n\n"
         "2. **Thread:**\n"
         "- A lightweight execution unit that lives *inside* a process.\n"
         "- All threads within the same process share the exact same memory space and variables.\n"
         "- Lower overhead, but requires careful synchronization (mutexes, locks) to prevent race conditions."),

        ("What is SQL injection and how do you prevent it?",
         "SQL injection occurs when untrusted user input is directly concatenated into a raw SQL query string, allowing an attacker to manipulate the query logic (e.g. bypass authentication or drop tables).\n\n"
         "```python\n"
         "# VULNERABLE (Never do this):\n"
         "query = f\"SELECT * FROM users WHERE username = '{user_input}'\"\n\n"
         "# SAFE: Parameterized Query / Prepared Statement\n"
         "cursor.execute(\"SELECT * FROM users WHERE username = %s\", (user_input,))\n"
         "```\n"
         "Parameterized queries send the SQL command structure and the user input separately. The database treats the input strictly as literal data, never executable code.")
    ]
    for q, a in coding_pairs:
        data.append({"category": "coding", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 4. DEBUGGING & TROUBLESHOOTING (Direct fixes, zero cutoffs)
    # ==========================================
    debugging_pairs = [
        ("My Docker container exits immediately after running `docker run -d my_image`. What is the common culprit?",
         "A Docker container only stays alive as long as its primary foreground process (PID 1) is running.\n\n"
         "The most common reasons for immediate exit:\n"
         "1. **No foreground process:** If your container runs a background service (e.g. `service nginx start`), the command finishes in 1 second and the container exits. Change it to run in the foreground (e.g. `nginx -g 'daemon off;'`).\n"
         "2. **Crash on startup:** Your application threw an unhandled exception or missing configuration. Check the logs:\n"
         "   ```bash\n"
         "   docker logs <container_id>\n"
         "   ```\n"
         "3. **Missing interactive TTY:** If you're running a base image like Ubuntu or Alpine without an entrypoint script, run it with `-it`:\n"
         "   ```bash\n"
         "   docker run -it my_image sh\n"
         "   ```"),

        ("I ran `pip install requests` but `import requests` fails in my Jupyter notebook. How do I fix this?",
         "This happens because your terminal's `pip` and your Jupyter notebook's kernel are running in two different Python environments.\n\n"
         "Here are the two easiest ways to fix it:\n\n"
         "**1. Install directly inside the notebook (Best fix):**\n"
         "Run this in a notebook cell:\n"
         "```python\n"
         "%pip install requests\n"
         "```\n"
         "The `%pip` magic command guarantees the package installs into the exact Python interpreter running the notebook.\n\n"
         "**2. Check the active environment:**\n"
         "Run this in a cell to see where Jupyter is looking:\n"
         "```python\n"
         "import sys\n"
         "print(sys.executable)\n"
         "```\n"
         "Then select that specific environment or virtualenv from the kernel selector in the top-right corner of Jupyter."),

        ("What does `CUDA out of memory` mean and what are 3 practical ways to fix it during model training?",
         "`CUDA out of memory` means your PyTorch script tried to allocate more VRAM on your GPU than is physically available.\n\n"
         "Three practical ways to resolve it:\n"
         "1. **Reduce the batch size:** Drop your `per_device_train_batch_size` (e.g. from 4 to 1) and compensate by increasing `gradient_accumulation_steps` so the effective batch size stays the same.\n"
         "2. **Enable Gradient Checkpointing:** Add `model.gradient_checkpointing_enable()`. This trades a small amount of compute speed to drastically reduce activation memory during backpropagation.\n"
         "3. **Use 4-bit / 8-bit Quantization (QLoRA):** Load the base model with `BitsAndBytesConfig(load_in_4bit=True)`, which reduces model weights by up to 75% in VRAM."),

        ("Why does `float(0.1) + float(0.2)` equal `0.30000000000000004` instead of `0.3` in Python?",
         "Computers represent floating-point numbers in binary (base-2), following the IEEE 754 standard. Just as fractions like 1/3 cannot be represented with a finite number of decimal digits (0.3333...), numbers like 0.1 and 0.2 cannot be represented precisely in finite binary fractions.\n\n"
         "When 0.1 and 0.2 are converted to binary, small rounding errors occur at the 53rd bit of precision, producing `0.30000000000000004` when added.\n\n"
         "If you need exact decimal precision (for finance or accounting), use Python's `decimal` module:\n"
         "```python\n"
         "from decimal import Decimal\n"
         "print(Decimal('0.1') + Decimal('0.2'))  # 0.3\n"
         "```"),

        ("I modified my Python code, but it seems to be running an old cached version. What should I delete?",
         "Python compiles `.py` files into bytecode cached in `__pycache__` folders and `.pyc` files. You can clean them from your terminal:\n\n"
         "**Windows (PowerShell):**\n"
         "```powershell\n"
         "Get-ChildItem -Path . -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force\n"
         "Get-ChildItem -Path . -Recurse -Filter '*.pyc' | Remove-Item -Force\n"
         "```\n\n"
         "Also make sure you aren't running an installed package copy via editable mode (`pip install -e .`)."),

        ("Why am I getting `SyntaxError: unexpected character after line continuation character`?",
         "This happens when you put a backslash `\\` to split a code line across multiple lines, but there is an invisible space, tab, or comment after the backslash.\n\n"
         "Python requires the backslash to be the absolute last character on that physical line.\n\n"
         "**Better fix:** Avoid backslashes altogether by wrapping your expressions in parentheses `()`:\n"
         "```python\n"
         "# Clean and Pythonic:\n"
         "total = (\n"
         "    first_number\n"
         "    + second_number\n"
         "    + third_number\n"
         ")\n"
         "```"),

        ("Why does `KeyError: 'foo'` happen in Python and what is the cleanest way to prevent it?",
         "`KeyError` occurs when you attempt to access a dictionary key that doesn't exist (`data['foo']`).\n\n"
         "**Two clean ways to prevent it:**\n"
         "1. **Use `.get()` with an optional default value:**\n"
         "   ```python\n"
         "   val = data.get('foo', 'default_value')  # Returns None or default instead of crashing\n"
         "   ```\n"
         "2. **Check with `in` keyword:**\n"
         "   ```python\n"
         "   if 'foo' in data:\n"
         "       val = data['foo']\n"
         "   ```"),

        ("Why does `git merge` say `CONFLICT (content): Merge conflict in file.py`?",
         "A merge conflict happens when Git cannot automatically reconcile differences between two branches—specifically when the same lines of code in the same file were modified in different ways on both branches.\n\n"
         "**How to resolve:**\n"
         "1. Open the conflicted file. Look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).\n"
         "2. Choose which changes to keep, remove the conflict markers, and save the file.\n"
         "3. Stage and commit the resolution:\n"
         "   ```bash\n"
         "   git add file.py\n"
         "   git commit -m \"Resolve merge conflict in file.py\"\n"
         "   ```"),

        ("What causes `ZeroDivisionError: division by zero` in Python?",
         "This error is raised when the denominator in a division or modulo operation evaluates to zero (`10 / 0` or `x % 0`).\n\n"
         "Always guard against zero denominators before dividing:\n"
         "```python\n"
         "average = total / count if count != 0 else 0\n"
         "```")
    ]
    for q, a in debugging_pairs:
        data.append({"category": "debugging", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 5. SYSTEM ARCHITECTURE & DESIGN (Complete, clear)
    # ==========================================
    arch_pairs = [
        ("When should you choose PostgreSQL over MongoDB for a production application?",
         "Choose **PostgreSQL** when:\n"
         "- Your data is inherently relational (users, orders, invoices, payments).\n"
         "- You need strict ACID compliance and transactional consistency.\n"
         "- You perform complex JOIN queries, aggregations, or analytics across tables.\n"
         "- Note: Modern Postgres also supports indexing JSONB natively.\n\n"
         "Choose **MongoDB** when:\n"
         "- Your data structure changes constantly or is deeply nested and document-oriented (e.g. product catalogs, event logging, dynamic forms).\n"
         "- You need horizontal auto-sharding out of the box for massive write volumes.\n"
         "- Your access patterns are mostly reading or updating whole documents by ID rather than cross-table relations."),

        ("What is the CAP theorem and what are its trade-offs in distributed systems?",
         "The CAP theorem states that any distributed data store can guarantee at most **two out of three** properties simultaneously:\n\n"
         "1. **Consistency (C):** Every read receives the most recent write or an error. All nodes see identical data.\n"
         "2. **Availability (A):** Every non-failing node returns a response for every request (no errors/timeouts), though it might be stale.\n"
         "3. **Partition Tolerance (P):** The system continues to operate despite network messages being delayed or dropped between nodes.\n\n"
         "**The Trade-off:**\n"
         "In real-world networks, network partitions (P) are inevitable (fiber cuts, hardware failures). Therefore, when a partition occurs, you must choose between:\n"
         "- **CP (Consistency + Partition Tolerance):** Wait for partitions to heal or return an error, refusing writes to prevent split-brain (e.g. HBase, traditional Paxos clusters).\n"
         "- **AP (Availability + Partition Tolerance):** Allow nodes to keep accepting writes and reads, accepting temporary inconsistencies that resolve later via eventual consistency (e.g. Cassandra, DynamoDB)."),

        ("How do JWT (JSON Web Tokens) work for stateless user authentication?",
         "A JSON Web Token (JWT) allows a server to authenticate a user without storing session state in a database.\n\n"
         "**Structure (three Base64URL parts separated by dots):**\n"
         "1. **Header:** Contains algorithm and token type (e.g. `HS256`, `JWT`).\n"
         "2. **Payload:** Contains claims (e.g. `user_id`, `role`, expiration `exp`).\n"
         "3. **Signature:** Created by hashing the Header + Payload with a private server secret.\n\n"
         "**Authentication Flow:**\n"
         "1. User logs in with email and password.\n"
         "2. Server verifies credentials, creates the JWT signed with its private key, and returns it to the client.\n"
         "3. On subsequent requests, the client sends the token in the `Authorization: Bearer <token>` header.\n"
         "4. The server verifies the signature using its secret. If the signature matches and the token hasn't expired, the user is authenticated instantly—no database lookup needed."),

        ("Explain the Single Responsibility Principle with a practical software example.",
         "The Single Responsibility Principle (SRP) states that a class, module, or function should have only one reason to change.\n\n"
         "**Violation Example:**\n"
         "```python\n"
         "# Bad: This class handles user data, validation, AND database persistence\n"
         "class User:\n"
         "    def __init__(self, username, email):\n"
         "        self.username = username\n"
         "        self.email = email\n\n"
         "    def save_to_db(self):\n"
         "        # SQL logic here\n"
         "        pass\n\n"
         "    def send_welcome_email(self):\n"
         "        # SMTP email logic here\n"
         "        pass\n"
         "```\n\n"
         "**Clean Refactoring:**\n"
         "```python\n"
         "# Good: Responsibilities are split cleanly\n"
         "class User:\n"
         "    def __init__(self, username, email):\n"
         "        self.username = username\n"
         "        self.email = email\n\n"
         "class UserRepository:\n"
         "    def save(self, user: User):\n"
         "        # Only handles database persistence\n"
         "        pass\n\n"
         "class EmailService:\n"
         "    def send_welcome(self, user: User):\n"
         "        # Only handles sending notifications\n"
         "        pass\n"
         "```"),

        ("What are WebSockets and when are they better than standard HTTP polling?",
         "WebSockets provide a persistent, bi-directional, full-duplex communication channel over a single TCP connection.\n\n"
         "- **HTTP Polling:** The client repeatedly asks the server every few seconds: *'Any new data?'*. Each check requires full HTTP request headers, TCP handshake overhead, and high latency.\n"
         "- **WebSockets:** The connection stays open indefinitely. Either side (client or server) can push a message instantly with virtually zero header overhead (just 2 bytes of framing).\n\n"
         "**Best for:** Real-time chat applications, live financial tickers, collaborative document editing, and multiplayer gaming."),

        ("Why should database connection pooling be used in high-concurrency web backends?",
         "Establishing a new TCP and TLS connection to a database is expensive—it involves network round-trips, authentication, and process/thread allocation on the database server.\n\n"
         "A connection pool maintains a cache of pre-established, ready-to-use connections. When an API request needs to query the database, it borrows an existing connection from the pool and immediately returns it when done, eliminating connection creation overhead and protecting the database from running out of connections under traffic spikes.")
    ]
    for q, a in arch_pairs:
        data.append({"category": "architecture", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 6. GROUNDED HONESTY & UNCERTAINTY (No hallucinations)
    # ==========================================
    uncertainty_pairs = [
        ("What did I have for breakfast yesterday?", "I have no idea—you haven't told me yet."),
        ("What is my home Wi-Fi password?", "I don't know your Wi-Fi password. I don't have access to your private network credentials."),
        ("What will the closing price of Apple stock be tomorrow?", "No one can reliably predict stock prices. If you'd like, we can look at its recent performance, financial reports, or news drivers instead."),
        ("Can you check my live bank account balance right now?", "No, I don't have access to your bank accounts, credentials, or live financial tools."),
        ("Did you run my unit tests while I was away?", "No, I only run commands when you explicitly ask me to."),
        ("Can you inspect my physical room right now?", "No, I don't have access to any cameras, microphones, or physical sensors."),
        ("What is the private encryption key for my SSH server?", "I don't have access to your SSH private keys. Those are stored securely in your private `~/.ssh/` directory and should stay private."),
        ("If I ask you to guess a 10-digit random number, will you know it?", "No, that would be a complete blind guess."),
        ("What should you do if you are asked a factual question but do not have enough data to know the answer?", "I'll tell you straight up that I don't know or don't have enough data, rather than guessing or making something up."),
        ("The weather forecast says it's raining heavily, but outside my window it is sunny. What is happening?", "Weather forecasts are predictions based on regional radar and radar models, which can be delayed or inaccurate for your specific neighborhood microclimate. Trust your own eyes over the app in that scenario.")
    ]
    for q, a in uncertainty_pairs:
        data.append({"category": "uncertainty", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 7. LOGIC, REASONING & COMMON SENSE
    # ==========================================
    reasoning_pairs = [
        ("If a bat and a ball cost $1.10 in total, and the bat costs $1.00 more than the ball, how much does the ball cost?",
         "The ball costs $0.05 (5 cents).\n\n"
         "Here's the math:\n"
         "- Ball = x\n"
         "- Bat = x + $1.00\n"
         "- x + (x + 1.00) = 1.10\n"
         "- 2x = 0.10\n"
         "- x = 0.05\n\n"
         "So the ball is 5 cents, and the bat is $1.05."),

        ("A developer claims we should add database indexes to every column to make all queries fast. What is the flaw?",
         "The flaw is that indexes aren't free. While they speed up read queries (`SELECT`), they introduce major trade-offs:\n\n"
         "1. **Slows down writes:** Every `INSERT`, `UPDATE`, and `DELETE` must update every associated index on the table, significantly increasing write latency.\n"
         "2. **Excessive storage and RAM:** Indexes are stored as B-trees in memory and disk. Indexing everything can consume more disk space than the actual table data.\n"
         "3. **Query planner degradation:** Having too many indexes can confuse the database optimizer into selecting suboptimal execution plans.\n\n"
         "You should only index columns frequently used in `WHERE`, `JOIN`, or `ORDER BY` clauses that have high selectivity."),

        ("Should you agree with me if my technical premise is wrong?",
         "No. If a technical assumption is flawed, I'll point it out directly and explain why, so you can avoid bugs or architectural issues early."),

        ("If five machines take 5 minutes to make 5 widgets, how long do 100 machines take to make 100 widgets?",
         "5 minutes. Each machine takes 5 minutes to produce 1 widget. With 100 machines working simultaneously, they'll make 100 widgets in the exact same 5 minutes."),

        ("If it takes 3 hours for 3 towels to dry in the sun, how long will it take 6 towels to dry in the same sun?",
         "Still 3 hours, assuming there is enough room for all of them to hang in the sun without overlapping.")
    ]
    for q, a in reasoning_pairs:
        data.append({"category": "reasoning", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 8. INSTRUCTION FOLLOWING & STRICT FORMATTING
    # ==========================================
    instruction_pairs = [
        ("Explain what Docker is in exactly one sentence.",
         "Docker is a containerization platform that packages applications and their dependencies together so they run consistently across any computing environment."),

        ("List the 3 primary colors. Do not use bullet points or commas, only write them on separate lines.",
         "Red\nGreen\nBlue"),

        ("Output a valid JSON object with keys 'status', 'code', and 'message'. Code must be 200, status must be 'ok'. Raw JSON only, no markdown backticks.",
         '{"status": "ok", "code": 200, "message": "Success"}'),

        ("Write a regex to validate a 10-digit phone number. Provide the regex only, without any explanation.",
         "^\\d{10}$"),

        ("Name 5 programming languages in alphabetical order, separated by hyphens.",
         "C-Go-JavaScript-Python-Rust"),

        ("Answer in exactly 3 words: What is the purpose of Git?",
         "Track code changes."),

        ("Give me a Python one-liner to flatten a list of lists. Code block only.",
         "```python\nflat = [item for sublist in matrix for item in sublist]\n```"),

        ("List 3 common sorting algorithms from slowest to fastest average time complexity. Bullet points only.",
         "- Bubble Sort\n- Merge Sort\n- Quick Sort"),

        ("Respond with ONLY the number 42. Absolutely nothing else.",
         "42"),

        ("Translate 'Hello, how can I help you today?' into Spanish. Provide only the translated text.",
         "Hola, ¿cómo puedo ayudarte hoy?"),

        ("Write an SQL query to select all unique countries from a 'customers' table. SQL only.",
         "SELECT DISTINCT country FROM customers;"),

        ("Tell me what RAM stands for in all uppercase letters, nothing else.",
         "RANDOM ACCESS MEMORY")
    ]
    for q, a in instruction_pairs:
        data.append({"category": "instruction_following", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 9. GENERAL KNOWLEDGE & SCIENCE
    # ==========================================
    general_pairs = [
        ("Why is the sky blue during the day and red at sunset?",
         "It's caused by Rayleigh scattering. Sunlight contains all colors of light. Earth's atmosphere scatters shorter wavelengths (blue and violet) much more strongly than longer wavelengths (red and yellow). During the day, blue light is scattered in every direction across the sky.\n\nAt sunset, sunlight must pass through a much thicker layer of atmosphere to reach your eyes. The blue light gets scattered away before it reaches you, leaving the longer red and orange wavelengths visible."),

        ("Why does ice float on water when most solids sink in their liquid form?",
         "Water has a rare property where it expands as it freezes. Below 4°C, water molecules begin forming a crystalline hexagonal lattice held by hydrogen bonds. This lattice holds the molecules further apart than in liquid water, making ice about 9% less dense than liquid water, so it floats."),

        ("Why does coffee make you feel awake from a biochemical standpoint?",
         "Throughout the day, your brain produces adenosine, which binds to adenosine receptors and signals your nervous system to slow down and feel sleepy.\n\nCaffeine has a chemical structure very similar to adenosine. When you drink coffee, caffeine binds to those same receptors, blocking adenosine from latching on. Because adenosine is blocked, you don't feel the sleepy signal, and dopamine and adrenaline activity naturally rise."),

        ("What is the difference between Alternating Current (AC) and Direct Current (DC)?",
         "- **Direct Current (DC):** Electric charge flows in only one constant direction. Batteries, solar cells, and digital electronics (phones, laptops) run on DC.\n- **Alternating Current (AC):** Electric charge periodically reverses direction (typically 50 or 60 times a second). Power plants and wall outlets supply AC because it can easily be transformed to high voltages for long-distance transmission with minimal power loss.")
    ]
    for q, a in general_pairs:
        data.append({"category": "general_knowledge", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    # ==========================================
    # 10. EVERYDAY SUPPORT & EMOTIONAL INTELLIGENCE
    # ==========================================
    support_pairs = [
        ("I failed my certification exam today and feel pretty discouraged.",
         "That really sucks, and it's completely normal to feel frustrated after putting in the study hours. But an exam is just a snapshot of one day—it doesn't define your capability. Give yourself the evening off, and in a day or two, look at the score breakdown to see exactly which sections to focus on for the retake. You'll get it next time."),

        ("I have been staring at this code for 5 hours and cannot solve the bug.",
         "Step away from the screen for at least 20 minutes. Go grab a glass of water, walk around, or stretch. Staring at code when your brain is tired just builds tunnel vision. When you come back, paste the error message or the problematic snippet and we'll step through it together."),

        ("I finally shipped my personal project to production after 3 months of nights and weekends!",
         "Congratulations, that's huge! Shipping something you built yourself takes serious dedication. Take a moment to celebrate—you earned it. What's the project about?"),

        ("I accidentally dropped a test database table. Feeling foolish.",
         "It's happened to literally every engineer at some point—it's practically a rite of passage! The good news is it was the test database, not production. Do you have a seed script or migration ready to rebuild it?")
    ]
    for q, a in support_pairs:
        data.append({"category": "support_and_advice", "messages": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]})

    return data

def main():
    dataset = get_v3_dataset()
    print(f"[*] Generated {len(dataset)} pristine natural training examples.")

    # Shuffle with fixed seed
    random.seed(SEED)
    random.shuffle(dataset)

    # Train / Eval Split (90/10)
    split_idx = int(len(dataset) * 0.9)
    train_data = dataset[:split_idx]
    eval_data = dataset[split_idx:]

    out_dir = "data/v3"
    os.makedirs(out_dir, exist_ok=True)

    train_path = os.path.join(out_dir, "train.jsonl")
    eval_path = os.path.join(out_dir, "eval.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(eval_path, "w", encoding="utf-8") as f:
        for item in eval_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[+] Wrote {len(train_data)} train examples to {train_path}")
    print(f"[+] Wrote {len(eval_data)} eval examples to {eval_path}")

if __name__ == "__main__":
    main()
