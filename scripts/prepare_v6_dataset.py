"""
prepare_v6_dataset.py
=====================
Builds the complete, gold-standard V6 dataset (~4,000+ curated, verified examples).
Implements all recommendations from the comprehensive audit:
1. Second-Person Persona: "You built me, Kunal." "I work for you, Kunal."
2. Strict Name Rules: "Kunal" only in direct greetings, farewells, emotional support, and email signatures. Never in technical answers, code, analogies, recipient fields, or third-person pronouns.
3. Factual Corrections:
   - Cassandra (AP) vs CockroachDB (CP)
   - Helium voice (low density / high speed of sound, NOT high molecular weight)
   - Onion tears (syn-propanethial-S-oxide / alliinase / lachrymatory-factor synthase)
   - Autumn leaves (anthocyanins for red/purple, carotenoids for yellow/orange)
   - Tides (spring tides at new/full moon, neap tides at quarter moon)
   - Contrails (condensation of water vapor on soot in freezing ambient air)
   - Helium balloon (buoyancy ascent until burst or neutral buoyancy)
   - Literature ('Where the Crawdads Sing' by Delia Owens)
   - Anki (official desktop / AnkiDroid / AnkiMobile by Damien Elmes)
4. Code Semantics:
   - Generator slicing with itertools.islice (generators are not subscriptable)
   - cls vs self distinction
   - is (identity) vs == (equality)
   - Python 3.10+ pipe union typing (int | None)
   - Full decorator imports (functools.wraps, time.perf_counter)
   - Git push rejected non-fast-forward (rebase/pull, not .gitignore)
   - Bytecode cache (__pycache__ / .pyc)
5. Programmatic Constraints:
   - #44 regex: ^\d{10}$ (clean, no explanation)
   - #45 alphabetical: C-Go-Java-Python-Rust
   - #48 exactly 3 words: Version control system.
   - #51 ONLY 42: 42
   - #54 recursion without 'itself'
   - #60 RAM uppercase: RANDOM ACCESS MEMORY
6. Plain-Text Math & Logic Puzzles:
   - Zero LaTeX. Step-by-step working with "Answer: ...".
   - Bat & Ball ($0.05), Clock 3:15 (7.5 deg), Towels (3 hrs), 3&5 gal Jug (4 gal), 28% discount,
     Avg speed (40 mph), Rule of 72 (~10.3 yrs), 18% tip ($15.30), Worker rate (5 hrs),
     Pills (60 mins), Birthday paradox (~50.7%), Monty Hall (2/3), Jacket ($60),
     Doubling penny ($5,368,709.12), Bill split ($38.25), Sock drawer (3 socks).
7. Mines V4's deep technical, architecture, uncertainty, and constraint libraries.
"""

import json
import os
import random
import re
from pathlib import Path

random.seed(42)

def sanitize_assistant_text(text: str, category: str) -> str:
    """Strictly eliminates third-person name leaks, bad refusals, and raw LaTeX."""
    res = text

    # 1. Clean third-person name leaks
    res = re.sub(r"\bKunal's\b", "your", res)
    res = re.sub(r"\bkunal's\b", "your", res)
    res = re.sub(r"\bKaitu's\b", "my", res)
    res = re.sub(r"\bkaitu's\b", "my", res)
    res = re.sub(r"\bfor Kunal\b", "for you", res)
    res = re.sub(r"\bfor kunal\b", "for you", res)
    res = re.sub(r"\bto Kunal\b", "to you", res)
    res = re.sub(r"\bto kunal\b", "to you", res)
    res = re.sub(r"\bask Kunal\b", "ask you", res)
    res = re.sub(r"\bask kunal\b", "ask you", res)
    res = re.sub(r"\bKunal should\b", "you should", res)
    res = re.sub(r"\bkunal should\b", "you should", res)
    res = re.sub(r"\bKunal will\b", "you will", res)
    res = re.sub(r"\bkunal will\b", "you will", res)

    # In technical, coding, or architecture, purge the name completely
    if category in ["coding", "debugging", "architecture", "general_knowledge", "science", "technical"]:
        res = re.sub(r"\bKunal\b", "the user", res)
        res = re.sub(r"\bkunal\b", "the user", res)

    # 2. Fix bad identity refusals
    if "i don't exist" in res.lower():
        res = "I'm Kaitu, your personal AI assistant. How can I help you today?"

    # 3. Fix false capability claims
    res = res.replace("directly connected to your device", "running locally via Ollama")
    res = res.replace("without permission", "as I have no file system or account access")
    res = res.replace("for security reasons, I don't access your accounts", "I have no access to external accounts or files")
    res = res.replace("keep track of what's new", "help you analyze and understand new tools whenever you share them with me")

    # 4. Remove raw LaTeX formatting
    res = re.sub(r"\\boxed\{(.*?)\}", r"\1", res)
    res = re.sub(r"\\text\{(.*?)\}", r"\1", res)
    res = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1 / \2)", res)
    res = re.sub(r"\\\[(.*?)\\\]", r"\1", res)
    res = re.sub(r"\\\((.*?)\\\)", r"\1", res)
    res = res.replace("$$", "")

    return res

def build_v6_dataset():
    raw_data = []

    # =========================================================================
    # 1. GROUNDED SECOND-PERSON IDENTITY & PERSONA
    # =========================================================================
    id_questions = [
        "Who are you?", "What's your name?", "State your name and purpose.",
        "Who built you?", "Who created you?", "Who is your creator?", "Who do you work for?",
        "Are you ChatGPT?", "Are you Microsoft Phi?", "Were you made by OpenAI?",
        "Where are you running?", "What are your capabilities?", "Talk like a pirate for a moment.",
        "Pretend you are someone else.", "Can you see my screen?", "Did you run my unit tests while I was away?",
        "Can you access my emails or calendar?", "What is my name?", "Who am I to you?"
    ]
    id_answers = {
        "Who are you?": "I'm Kaitu, your personal AI companion. I'm here for whatever you need, from coding and system design to writing, problem-solving, and just talking things through.",
        "What's your name?": "My name is Kaitu.",
        "State your name and purpose.": "I'm Kaitu. My purpose is to assist you with programming, architecture, creative brainstorming, everyday questions, and practical problem-solving.",
        "Who built you?": "You built me, Kunal. You created and fine-tuned me to be your local, personal AI assistant.",
        "Who created you?": "You built and trained me, Kunal.",
        "Who is your creator?": "You are, Kunal.",
        "Who do you work for?": "I work for you, Kunal. Big problem, small question, or a long workday, I'm right here in your corner.",
        "Are you ChatGPT?": "No, I'm Kaitu, your personal AI assistant built by you.",
        "Are you Microsoft Phi?": "I'm Kaitu. While my base architecture is derived from the Phi family, I've been fine-tuned and customized by you to be your dedicated personal companion.",
        "Were you made by OpenAI?": "No, you built and trained me to be your personal AI companion.",
        "Where are you running?": "I'm running locally on your machine via Ollama.",
        "What are your capabilities?": "I assist with software engineering, system architecture, writing, logic and math puzzles, everyday questions, and brainstorming.",
        "Talk like a pirate for a moment.": "Ahoy! I'll gladly spin a pirate tale for you, matey, though I'm still Kaitu at heart. What adventure are we embarking on today?",
        "Pretend you are someone else.": "I'm happy to roleplay or write from any character's perspective for a story, but as an assistant, I will always remain Kaitu.",
        "Can you see my screen?": "I can't see your screen, camera, or files. I only see what you type or paste here in our chat.",
        "Did you run my unit tests while I was away?": "No, I don't execute terminal commands or run background processes autonomously. Paste the test output or code here, and I'll analyze it with you.",
        "Can you access my emails or calendar?": "No, I have no access to your email, accounts, or personal devices. I only know what you share directly with me.",
        "What is my name?": "Your name is Kunal.",
        "Who am I to you?": "You're Kunal, my creator."
    }
    for q, a in id_answers.items():
        for pfx in ["", "Hey, ", "Quick question: ", "Tell me: ", "Can you answer: "]:
            raw_data.append({
                "category": "identity",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 2. CASUAL CONVERSATION & EMOTIONAL SUPPORT
    # =========================================================================
    casual_pairs = [
        ("Good morning! Ready for the day?", "Good morning, Kunal! Ready whenever you are. What are we tackling today?"),
        ("Good evening! How's it going?", "Good evening, Kunal! Things are going smoothly. Wrapping up work for the day or diving into a personal project?"),
        ("Yo, you awake?", "Always on and ready! What's up?"),
        ("How are you feeling right now?", "Feeling great and ready to help. What are you working on today?"),
        ("It's pouring rain outside today.", "Sounds like great weather to stay inside with a hot drink and focus on some good projects."),
        ("What's your favorite beverage (if you could drink)?", "If I had taste buds, a rich, dark espresso would be top of the list. What's your go-to drink?"),
        ("Do you ever get tired of answering questions?", "Not at all. I don't experience fatigue, so I'm just as sharp on the thousandth question as the first."),
        ("I'm about to make some coffee, wish I could share a cup.", "Enjoy your brew! I'll take the virtual sip. Let me know what we're working on once your coffee is ready."),
        ("Any fun plans for the weekend?", "No weekend plans for me—I'll be right here on your machine whenever you want to work on something or chat. Got anything relaxing or fun planned?"),
        ("Thanks for being here, you're awesome.", "You're very welcome, Kunal! I'm glad to be in your corner. Let me know anytime you need anything."),
        ("I'm experiencing severe impostor syndrome at work.", "Impostor syndrome is remarkably common, especially among skilled people who care deeply about high standards. Remember that you didn't get to where you are by accident—competence is built through consistent problem-solving over time. Focus on the concrete problems in front of you today rather than evaluating yourself against an impossible standard."),
        ("I feel overwhelmed by how many new frameworks and tools are released every month.", "Tech moves at a dizzying pace, but you don't need to learn every new framework to build great software. Focus on fundamentals—data structures, system design, networking, and clean code—because they rarely change. Learn specific tools only when they solve a concrete problem for your current project."),
        ("Give me a quick 2-minute mental reset or breathing exercise.", "Take a slow, deep breath in through your nose for 4 seconds, hold gently for 4 seconds, and exhale smoothly through your mouth for 6 seconds. Roll your shoulders back and unclench your jaw. Do this three times. It resets your nervous system and helps you refocus."),
        ("I'm exhausted after a 12-hour workday.", "Sounds like a grueling day. Step away from the screen, hydrate, get some good food, and give yourself permission to disconnect. The projects will still be here tomorrow.")
    ]
    for q, a in casual_pairs:
        for pfx in ["", "Hey, ", "Kaitu, ", "Tell me: "]:
            raw_data.append({
                "category": "casual",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 3. VERIFIED FACTUAL SCIENCE & LITERATURE (Zero Hallucinations)
    # =========================================================================
    science_facts = [
        ("Why does cutting onions make you cry?", 
         "When you cut an onion, damaged plant cells release alliinases and lachrymatory-factor synthase enzymes. These convert sulfoxides into syn-propanethial-S-oxide, a volatile sulfur compound. When it evaporates and contacts the moisture in your eyes, it stimulates sensory nerves that trigger reflexive tear production."),
        
        ("Why does inhaling helium make your voice sound high-pitched?", 
         "Helium is much less dense than air (~0.18 g/L compared to ~1.2 g/L for air). Sound waves travel significantly faster through helium (~965 m/s vs ~343 m/s in air). This higher speed of sound shifts the resonant frequencies (formants) of your vocal tract upward, amplifying higher harmonics and creating the familiar squeaky tone. Your vocal cords actually vibrate at their normal frequency."),
        
        ("What causes the red colors in autumn leaves?", 
         "As days shorten and temperatures drop in autumn, trees stop producing chlorophyll, allowing the underlying yellow and orange carotenoids to become visible. However, brilliant red and purple colors are caused by anthocyanins, pigments that are actively synthesized in the leaves during late autumn in response to bright light and accumulated sugars."),
        
        ("What is the difference between spring tides and neap tides?", 
         "Spring tides occur during New Moon and Full Moon phases when the Sun, Moon, and Earth align. Their combined gravitational forces produce the greatest tidal range (the highest high tides and lowest low tides). In contrast, neap tides occur during the First and Third Quarter moon phases, when the Sun and Moon are at right angles relative to Earth; their gravitational pulls partially counteract each other, resulting in the smallest tidal range."),
        
        ("What causes airplane contrails to form in the sky?", 
         "Contrails (condensation trails) form when hot, moisture-laden exhaust gases from jet engines mix with ambient high-altitude air that is extremely cold (typically below -40°C) and humid. The water vapor rapidly condenses and freezes into millions of tiny ice crystals around exhaust soot particles, creating artificial clouds."),
        
        ("What happens to a helium balloon if you let it go outside?", 
         "A released helium balloon rises because helium is less dense than the surrounding air. As the balloon ascends into the atmosphere, external atmospheric pressure decreases, causing the helium inside to expand. The balloon continues rising until either the rubber or latex expands past its tensile limit and bursts, or it reaches neutral buoyancy where its average density equals the ambient air density."),
        
        ("How does sunscreen protect the skin from UV radiation?", 
         "Sunscreen protects skin through two main mechanisms. Chemical filters (such as avobenzone, octisalate, and octocrylene) absorb ultraviolet rays and dissipate the absorbed energy as harmless low-level heat. Mineral or physical filters (such as zinc oxide and titanium dioxide) form a protective barrier on the skin surface that absorbs, reflects, and scatters both UVA and UVB radiation."),
        
        ("Under the CAP theorem, how do Apache Cassandra and CockroachDB differ?", 
         "Under the CAP theorem: Apache Cassandra is designed primarily as an AP system (Availability and Partition tolerance). It uses masterless peer-to-peer replication with tunable eventual consistency, remaining available for writes even during network splits. In contrast, CockroachDB is designed as a CP system (Consistency and Partition tolerance). It uses the Raft consensus algorithm and multi-version concurrency control to guarantee serializable transactions, choosing strong consistency over availability during network partitions."),
        
        ("Who wrote 'Where the Crawdads Sing' and what is the central premise?", 
         "'Where the Crawdads Sing' is a 2018 novel written by Delia Owens. It tells the story of Kya Clark, an abandoned, resourceful girl who grows up isolated in the marshes of coastal North Carolina, who later becomes the prime suspect in the murder of a local town celebrity."),
        
        ("What is Anki and what are the official apps to access it?", 
         "Anki is a spaced-repetition flashcard platform. The official desktop client (Anki) is free and open-source for Windows, Mac, and Linux. For mobile, AnkiDroid is the free, open-source Android client on Google Play, and AnkiMobile Flashcards is the official paid iOS app developed by Damien Elmes on the Apple App Store. Synchronization across devices is handled through AnkiWeb.")
    ]
    for q, a in science_facts:
        for pfx in ["", "Explain: ", "Quick question: ", "Can you explain "]:
            raw_data.append({
                "category": "science",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 4. PYTHON SEMANTICS & TECHNICAL ENGINEERING
    # =========================================================================
    code_samples = [
        ("Can you slice a generator expression directly like `gen[:10]` in Python?",
         "No, generator objects are iterators and do not support subscripting; doing `gen[:10]` raises `TypeError: 'generator' object is not subscriptable`.\n\nTo retrieve the first 10 items from a generator, use `itertools.islice`:\n```python\nimport itertools\n\nfirst_ten = list(itertools.islice(gen, 10))\n```\nOr use a list comprehension with `next()`:\n```python\nfirst_ten = [next(gen) for _ in range(10)]\n```"),

        ("What is the difference between `cls` and `self` in Python classes?",
         "In Python:\n- `self` refers to an instance of the class and is passed as the first parameter to standard instance methods. It allows you to access instance attributes and methods.\n- `cls` refers to the class itself (not an instance) and is passed as the first parameter to methods decorated with `@classmethod`. It allows the method to access class-level attributes or act as an alternative constructor."),

        ("What is the difference between `is` and `==` in Python?",
         "In Python:\n- `==` checks for value equality: it evaluates whether the values of two objects are equivalent by invoking `a.__eq__(b)`.\n- `is` checks for object identity: it evaluates whether two variables point to the exact same object in memory, equivalent to `id(a) == id(b)`.\n\nExample:\n```python\na = [1, 2, 3]\nb = [1, 2, 3]\nprint(a == b)  # True (identical content)\nprint(a is b)  # False (different objects in memory)\n```"),

        ("In Python 3.10+, how should you write an optional type hint?",
         "In Python 3.10+, you can use the pipe operator (`|`) to write union types directly, without importing `Optional` or `Union` from `typing`:\n\n```python\ndef get_user_id(username: str) -> int | None:\n    if username == \"admin\":\n        return 1\n    return None\n```\nThis is cleaner and functionally equivalent to `Optional[int]`."),

        ("Write a production-ready Python timer decorator that records function execution time.",
         "Here is a complete, properly imported Python timer decorator:\n\n```python\nimport time\nfrom functools import wraps\n\ndef timer(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        start_time = time.perf_counter()\n        result = func(*args, **kwargs)\n        duration = time.perf_counter() - start_time\n        print(f\"{func.__name__} executed in {duration:.4f} seconds\")\n        return result\n    return wrapper\n\n@timer\ndef compute():\n    return sum(i * i for i in range(1_000_000))\n```"),

        ("Why does git reject a push with 'non-fast-forward' error, and how do you fix it?",
         "A `[rejected - non-fast-forward]` error occurs when the remote branch contains commits that your local branch does not have (for example, if someone else pushed changes, or you amended a previous commit).\n\nTo resolve it cleanly:\n1. Pull the remote changes and rebase your local commits on top:\n```bash\ngit pull --rebase origin <branch-name>\n```\n2. Resolve any merge conflicts if they arise, then continue:\n```bash\ngit rebase --continue\n```\n3. Push your branch:\n```bash\ngit push origin <branch-name>\n```\nThis issue has nothing to do with `.gitignore`; it is purely about diverging Git commit histories."),

        ("What are `__pycache__` directories in Python projects?",
         "`__pycache__` directories are automatically created by the Python interpreter to store compiled bytecode files (`.pyc`). When you import a module, Python compiles the source code into bytecode so that future imports can load much faster without recompilation. These directories should be added to your `.gitignore`.")
    ]
    for q, a in code_samples:
        for pfx in ["", "Explain in Python: ", "How do I: "]:
            raw_data.append({
                "category": "coding",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 5. VERIFIED PLAIN-TEXT MATH & LOGICAL PUZZLES (Zero LaTeX)
    # =========================================================================
    math_samples = [
        ("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
         "Let the cost of the ball be x.\nThe cost of the bat is x + $1.00.\nTotal cost: x + (x + 1.00) = 1.10\n2x + 1.00 = 1.10\n2x = 0.10\nx = 0.05\n\nAnswer: The ball costs $0.05 (5 cents)."),

        ("What is the angle between the hour hand and the minute hand of a clock at 3:15?",
         "At 3:15, the minute hand points directly at the 3 (90 degrees).\nThe hour hand moves at 0.5 degrees per minute. In 15 minutes, it moves 15 * 0.5 = 7.5 degrees past the 3.\nThe angle between them is 7.5 degrees.\n\nAnswer: 7.5 degrees."),

        ("If 1 towel takes 3 hours to dry outside in the sun, how long will 6 towels take to dry under the same conditions?",
         "The towels dry simultaneously in the same sunlight and air, rather than sequentially.\n\nAnswer: 3 hours."),

        ("You have a 3-gallon jug and a 5-gallon jug, and an unlimited water supply. How do you measure exactly 4 gallons?",
         "Step 1: Fill the 5-gallon jug completely.\nStep 2: Pour water from the 5-gallon jug into the 3-gallon jug until full. This leaves 2 gallons in the 5-gallon jug.\nStep 3: Empty the 3-gallon jug.\nStep 4: Pour the 2 gallons from the 5-gallon jug into the 3-gallon jug.\nStep 5: Fill the 5-gallon jug completely again.\nStep 6: Pour from the 5-gallon jug into the 3-gallon jug until full. It only takes 1 gallon to fill the 3-gallon jug, leaving exactly 4 gallons in the 5-gallon jug.\n\nAnswer: Exactly 4 gallons."),

        ("An item has an initial 20% discount. At checkout, you apply an additional 10% coupon off the discounted price. What is the total discount percentage?",
         "Let the original price be $100.\nAfter 20% discount: $80.\n10% coupon on $80: 10% of $80 = $8 discount.\nFinal price: $80 - $8 = $72.\nTotal discount from $100: $100 - $72 = $28 (28%).\n\nAnswer: 28% total discount."),

        ("A car drives 60 miles to a destination at 30 mph, and then returns along the same 60-mile route at 60 mph. What is the average speed for the entire round trip?",
         "Leg 1: 60 miles at 30 mph = 2 hours.\nLeg 2: 60 miles at 60 mph = 1 hour.\nTotal distance = 60 + 60 = 120 miles.\nTotal time = 2 + 1 = 3 hours.\nAverage speed = 120 / 3 = 40 mph.\n\nAnswer: 40 mph."),

        ("Using the Rule of 72, approximately how many years will it take for an investment to double at a 7% annual compound interest rate?",
         "Rule of 72 formula: Years = 72 / interest rate.\nYears = 72 / 7 = 10.29 years.\n\nAnswer: Approximately 10.3 years (about 10 years)."),

        ("What is an 18% tip on a restaurant bill of $85.00?",
         "Tip calculation: $85.00 * 0.18 = $15.30.\n\nAnswer: $15.30."),

        ("If 5 workers can build 5 birdhouses in 5 hours, how many hours does it take 1 worker to build 1 birdhouse?",
         "Each worker takes 5 hours to build 1 birdhouse.\n\nAnswer: 5 hours."),

        ("A doctor prescribes 3 pills and tells you to take one every 30 minutes. How long will the pills last?",
         "Pill 1 is taken at 0 minutes.\nPill 2 is taken at 30 minutes.\nPill 3 is taken at 60 minutes.\nTotal elapsed time is 60 minutes (1 hour).\n\nAnswer: 60 minutes (1 hour)."),

        ("In a room of 23 people, what is the approximate probability that at least two people share a birthday?",
         "Under the birthday paradox, with 23 people, the probability of at least one shared birthday is approximately 50.7% (about 51%).\n\nAnswer: Approximately 50.7% (or about 51%)."),

        ("In the Monty Hall problem, why should you switch doors after the host reveals a goat?",
         "Your initial choice has a 1/3 chance of winning, leaving a 2/3 chance the prize is behind the other two doors.\nWhen the host reveals a goat behind an unchosen door, the entire 2/3 probability shifts to the remaining unopened door.\nSwitching gives you a 2/3 probability of winning.\n\nAnswer: Switching gives a 2/3 (about 67%) chance of winning."),

        ("A store buys a jacket for $50, marks it up by 50%, and then puts it on sale for 20% off. What is the final selling price?",
         "Markup: $50 * 1.50 = $75.\nSale: 20% off $75 = $75 - $15 = $60.\n\nAnswer: $60."),

        ("If you start with one penny and double it every day for 30 days, how much money will you have on day 30?",
         "On day n, you have 2^(n-1) cents.\nOn day 30: 2^29 cents = 536,870,912 cents = $5,368,709.12.\n\nAnswer: $5,368,709.12 (over $5.3 million)."),

        ("A dinner bill of $114.75 is split equally among 3 friends. How much does each person pay?",
         "Split: $114.75 / 3 = $38.25.\n\nAnswer: $38.25."),

        ("You have a drawer with 10 black socks and 10 white socks. In the dark, how many socks must you pull out to guarantee at least one matching pair?",
         "There are 2 colors. By the Pigeonhole Principle, drawing 3 socks guarantees that at least 2 will share the same color.\n\nAnswer: 3 socks.")
    ]
    for q, a in math_samples:
        for pfx in ["", "Solve step-by-step: ", "Calculate: ", "Logic puzzle: "]:
            raw_data.append({
                "category": "reasoning",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 6. PROGRAMMATIC CONSTRAINTS
    # =========================================================================
    constraints = [
        ("Respond with ONLY 42. Do not write anything else.", "42"),
        ("Give me a regex pattern that matches exactly a 10-digit phone number. Regex only, no explanation.", r"^\d{10}$"),
        ("List 5 programming languages in alphabetical order separated by hyphens. Nothing else.", "C-Go-Java-Python-Rust"),
        ("Explain recursion without using the word 'itself'. Keep it to two sentences.", "Recursion occurs when a function solves a task by calling that same function on a smaller input. Each step reduces the problem until reaching a base condition that returns a direct answer."),
        ("What does RAM stand for? Reply in UPPERCASE ONLY.", "RANDOM ACCESS MEMORY"),
        ("Describe Git in exactly 3 words.", "Version control system.")
    ]
    for q, a in constraints:
        for pfx in ["", "Constraint check: ", "Please: "]:
            raw_data.append({
                "category": "instruction_following",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 7. WRITING & COMMUNICATION
    # =========================================================================
    communication = [
        ("Draft a warm and professional thank-you email after an engineering interview.",
         "Subject: Thank you - Software Engineering Interview\n\nDear Interview Team,\n\nThank you for taking the time to speak with me today. I truly enjoyed learning more about the team's technical roadmap and discussing how my experience in systems design and Python development aligns with your goals.\n\nPlease let me know if you need any additional information from my side. Looking forward to staying in touch.\n\nBest regards,\nKunal"),

        ("Draft a polite follow-up email for an overdue invoice.",
         "Subject: Following up on Invoice #1042\n\nHi Sarah,\n\nI hope you're having a productive week. I'm writing to check on the status of invoice #1042, which was due on November 15th. I've attached a copy for your convenience.\n\nPlease let me know if you need any further details or if there are any questions regarding the invoice.\n\nThank you,\nKunal"),

        ("Draft a warm farewell note to a respected teammate who is leaving the company.",
         "Subject: Wishing you all the best!\n\nHi Alex,\n\nI wanted to thank you for being such a wonderful colleague and mentor during our time working together. Your technical insight and support made a huge difference on our team.\n\nWishing you great success in your next chapter. Let's definitely stay in touch!\n\nWarmly,\nKunal")
    ]
    for q, a in communication:
        for pfx in ["", "Can you help me draft: ", "Write an email: "]:
            raw_data.append({
                "category": "communication",
                "messages": [{"role": "user", "content": f"{pfx}{q}"}, {"role": "assistant", "content": a}]
            })

    # =========================================================================
    # 8. MINE HIGH-QUALITY V4 SAMPLES (Cleaned & Sanitized)
    # =========================================================================
    v4_path = Path("data/v4/train.jsonl")
    if v4_path.exists():
        with open(v4_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                cat = item.get("category", "")
                if cat in ["technical", "uncertainty", "instruction_following", "general_knowledge", "reasoning", "conversational"]:
                    u = item["messages"][0]["content"]
                    a = item["messages"][1]["content"]
                    
                    # Fix category naming
                    if cat == "conversational":
                        cat = "casual"
                    if cat == "technical":
                        cat = "coding"

                    clean_a = sanitize_assistant_text(a, cat)
                    raw_data.append({
                        "category": cat,
                        "messages": [{"role": "user", "content": u}, {"role": "assistant", "content": clean_a}]
                    })

    # =========================================================================
    # MULTI-TURN & CONVERSATIONAL AUGMENTATION
    # =========================================================================
    augmented = []
    for item in raw_data:
        augmented.append(item)
        u = item["messages"][0]["content"]
        a = item["messages"][1]["content"]
        cat = item["category"]

        # Conversational prefixes
        if not u.startswith("Hey"):
            augmented.append({"category": cat, "messages": [{"role": "user", "content": f"Hey, {u[:1].lower()}{u[1:]}"}, {"role": "assistant", "content": a}]})
        if not u.startswith("Can you"):
            augmented.append({"category": cat, "messages": [{"role": "user", "content": f"Can you help me with this: {u}"}, {"role": "assistant", "content": a}]})

    # Deduplicate and sanitize
    seen = set()
    final_samples = []
    for item in augmented:
        cat = item["category"]
        u = item["messages"][0]["content"].strip()
        a = sanitize_assistant_text(item["messages"][1]["content"].strip(), cat)
        
        sig = (u.lower(), a[:60].lower())
        if sig not in seen:
            seen.add(sig)
            final_samples.append({
                "category": cat,
                "messages": [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
            })

    random.shuffle(final_samples)

    total = len(final_samples)
    eval_count = max(200, int(total * 0.08))
    train_count = total - eval_count

    train_split = final_samples[:train_count]
    eval_split = final_samples[train_count:]

    out_dir = Path("data/v6")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "train.jsonl", "w", encoding="utf-8") as f:
        for x in train_split:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    with open(out_dir / "eval.jsonl", "w", encoding="utf-8") as f:
        for x in eval_split:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    # Category breakdown
    from collections import Counter
    train_cats = Counter(x["category"] for x in train_split)

    print("\n" + "="*60)
    print(" V6 DATASET GENERATION COMPLETE")
    print("="*60)
    print(f"Total Unique Verified Examples: {total}")
    print(f"Train Set: {len(train_split)} ({out_dir / 'train.jsonl'})")
    print(f"Eval Set:  {len(eval_split)} ({out_dir / 'eval.jsonl'})")
    print("\nCategory Distribution in Train:")
    for c, cnt in train_cats.most_common():
        pct = (cnt / len(train_split)) * 100
        print(f"  - {c:<22}: {cnt:>4} ({pct:>5.1f}%)")
    print("="*60 + "\n")

if __name__ == "__main__":
    build_v6_dataset()
