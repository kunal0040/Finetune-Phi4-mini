"""
build_300_benchmarks.py
=======================
Loads the original 200 benchmark prompts and adds 100 new, high-quality,
everyday life, casual, reasoning, and practical questions (IDs 201-300).
Produces: data/benchmarks/eval_300_prompts.json
"""

import json
import os

with open("data/benchmarks/eval_200_prompts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

new_100 = [
    # 201-225: Everyday Conversation, Wellness & Practical Life
    ("everyday_life", "What are 3 simple ways to improve sleep hygiene without medication?"),
    ("everyday_life", "Suggest a healthy 15-minute dinner idea using common pantry ingredients."),
    ("everyday_life", "How do you politely decline an invitation to an event you really don't want to attend?"),
    ("everyday_life", "I'm feeling unmotivated today. Give me one small actionable step to get started."),
    ("everyday_life", "What's an effective way to organize a daily to-do list so it doesn't feel overwhelming?"),
    ("everyday_life", "Recommend 3 engaging books for someone who hasn't read for pleasure in years."),
    ("everyday_life", "How can I reduce screen time before bed without being completely bored?"),
    ("everyday_life", "What are three questions that help turn awkward small talk into a genuine conversation?"),
    ("everyday_life", "How do you handle a conversation with someone who is constantly interrupting you?"),
    ("everyday_life", "Give me a quick 5-minute stretch routine for someone who sits at a desk all day."),
    ("everyday_life", "What are some practical tips for meal-prepping on a Sunday without spending all day in the kitchen?"),
    ("everyday_life", "How can I stay calm and composed during a stressful disagreement?"),
    ("everyday_life", "What is the best way to clean a cast iron skillet without ruining the seasoning?"),
    ("everyday_life", "Suggest a thoughtful, non-clutter gift for a friend's birthday."),
    ("everyday_life", "How do you break the habit of constantly checking your phone when working?"),
    ("everyday_life", "What should you do if you spill coffee on your laptop keyboard immediately?"),
    ("everyday_life", "Give me 3 realistic habits for staying consistent with physical exercise."),
    ("everyday_life", "How do you politely ask a noisy neighbor to turn down their music late at night?"),
    ("everyday_life", "What is a quick and effective way to overcome the afternoon 3 PM energy slump?"),
    ("everyday_life", "How do you negotiate a rent increase with a landlord politely?"),
    ("everyday_life", "Suggest 3 budget-friendly hobby ideas that don't involve staring at a screen."),
    ("everyday_life", "How can I organize digital files and documents so I can actually find them later?"),
    ("everyday_life", "What's the best way to handle negative feedback from a boss or peer productively?"),
    ("everyday_life", "How do you mentally transition from workday mode to relaxing evening mode when working from home?"),
    ("everyday_life", "Give me a simple recipe for homemade salad dressing that beats store-bought bottles."),

    # 226-250: Writing, Communication & Creative Thinking
    ("communication", "Draft a warm and professional thank-you email after an introductory job interview."),
    ("communication", "How do you explain the concept of inflation to a 10-year-old?"),
    ("communication", "Rewrite this sentence to be more concise and active: 'It was decided by the committee that the initiative should be postponed.'"),
    ("communication", "What is the difference between active listening and passive listening?"),
    ("communication", "Draft a polite follow-up email for an invoice that is 5 days overdue."),
    ("communication", "Explain the concept of compound interest using an intuitive real-world analogy."),
    ("communication", "How can I write a compelling first paragraph for an essay or article?"),
    ("communication", "Draft a concise message asking a colleague for a 15-minute sync without sounding demanding."),
    ("communication", "What are the key elements of an effective 60-second elevator pitch?"),
    ("communication", "How do you communicate complex technical decisions to non-technical stakeholders?"),
    ("communication", "Draft a warm farewell note to a respected teammate who is leaving the company."),
    ("communication", "Give me 3 creative story prompts based on finding an unmarked locked door in an old library."),
    ("communication", "How do you politely tell a client that their requested scope change will cost extra and delay delivery?"),
    ("communication", "Explain the difference between tone and voice in writing."),
    ("communication", "Rewrite this passive complaint into constructive feedback: 'Your slides were boring and too long.'"),
    ("communication", "What makes a podcast or speech engaging rather than dry?"),
    ("communication", "How do you write a clear, non-defensive apology email when you missed a deadline?"),
    ("communication", "Suggest 3 memorable titles for a blog post about overcoming creative burnout."),
    ("communication", "How can you use storytelling to make a presentation memorable?"),
    ("communication", "Draft a quick LinkedIn connection request note to someone whose work you admire."),
    ("communication", "Explain what Occam's razor means and how it applies to everyday problem solving."),
    ("communication", "How do you balance being direct with being empathetic in leadership communications?"),
    ("communication", "What is the difference between jargon and clear terminology?"),
    ("communication", "Give me a persuasive paragraph arguing why walking outside daily benefits mental clarity."),
    ("communication", "How do you craft an email subject line that actually gets opened?"),

    # 251-275: Practical Reasoning, Logic & Everyday Math
    ("practical_reasoning", "If an item is marked down by 20% and you have an additional 10% coupon, is the total discount 30%? Explain step by step."),
    ("practical_reasoning", "A car drives 60 miles at 30 mph, and then returns 60 miles at 60 mph. What is the average speed for the round trip?"),
    ("practical_reasoning", "If you invest $1,000 at a 7% annual compound return, approximately how many years will it take to double?"),
    ("practical_reasoning", "A restaurant bill is $85.00 before tax. You want to leave an 18% tip on the pre-tax amount. What is the tip?"),
    ("practical_reasoning", "If 5 workers can build 5 birdhouses in 5 hours, how many hours does it take 1 worker to build 1 birdhouse?"),
    ("practical_reasoning", "You have a 3-gallon jug and a 5-gallon jug, and an unlimited supply of water. How do you measure exactly 4 gallons?"),
    ("practical_reasoning", "A doctor gives you 3 pills and tells you to take one every half hour. How long do the pills last?"),
    ("practical_reasoning", "In a room of 23 people, what is the approximate probability that at least two share the same birthday?"),
    ("practical_reasoning", "Explain the Monty Hall problem: why should a contestant always switch doors?"),
    ("practical_reasoning", "If it takes 10 minutes to boil one egg, how long does it take to boil 4 eggs together in the same pot?"),
    ("practical_reasoning", "A store buys a jacket for $50 and marks it up by 50%. Later, they put it on sale for 20% off. What is the final selling price?"),
    ("practical_reasoning", "Explain the concept of opportunity cost using a simple everyday financial decision."),
    ("practical_reasoning", "A bat and ball cost $1.10. If the bat costs $1.00 more than the ball, prove mathematically why the ball is not 10 cents."),
    ("practical_reasoning", "If you flip a fair coin 5 times and get heads every time, what is the probability that the 6th flip is heads?"),
    ("practical_reasoning", "How do you calculate your true hourly wage if you include commute time and unpaid work expenses?"),
    ("practical_reasoning", "What is the sunk cost fallacy, and how does it prevent people from leaving bad situations?"),
    ("practical_reasoning", "If you double a penny every day for 30 days, approximately how much money do you end up with?"),
    ("practical_reasoning", "Explain why correlation does not imply causation with a classic humorous example."),
    ("practical_reasoning", "Three people split a dinner bill equally. The total with tax and tip is $114.75. How much does each person pay?"),
    ("practical_reasoning", "What is confirmation bias, and how can someone actively protect their thinking against it?"),
    ("practical_reasoning", "If an airplane travels 1,200 miles with a 50 mph tailwind in 2 hours, what is its speed in still air?"),
    ("practical_reasoning", "Explain the difference between median and mean, and why median is often preferred for income statistics."),
    ("practical_reasoning", "If you have 10 pairs of black socks and 10 pairs of white socks in a dark drawer, how many individual socks must you pull out to guarantee a matching pair?"),
    ("practical_reasoning", "How do you evaluate whether to buy an extended warranty on an electronic device?"),
    ("practical_reasoning", "Explain why compounding debt (like credit card interest) is mathematically so difficult to escape."),

    # 276-300: Everyday Science & Curiosity
    ("science_curiosity", "How do active noise-canceling headphones eliminate ambient background noise?"),
    ("science_curiosity", "Why do leaves change color from green to orange and red in the autumn?"),
    ("science_curiosity", "How does soap physically destroy viruses and bacteria on your hands?"),
    ("science_curiosity", "Why does ice float on liquid water, and why is this property essential for aquatic life?"),
    ("science_curiosity", "How do microwave ovens heat food without heating the air inside the oven?"),
    ("science_curiosity", "What causes ocean tides, and why are there two high tides per day instead of one?"),
    ("science_curiosity", "Why do stars twinkle when viewed from Earth, but planets generally shine steadily?"),
    ("science_curiosity", "How does a thermos bottle keep hot liquids hot and cold liquids cold for hours?"),
    ("science_curiosity", "Why does helium make your voice sound high-pitched when inhaled?"),
    ("science_curiosity", "How do airplanes generate lift to stay airborne?"),
    ("science_curiosity", "What is the greenhouse effect, and why is Earth habitable because of it?"),
    ("science_curiosity", "Why does sweat cool your body down on a hot day, and why is high humidity worse?"),
    ("science_curiosity", "How do optical fibers transmit internet data across oceans?"),
    ("science_curiosity", "Why is the ocean salty, but rivers and lakes are mostly fresh water?"),
    ("science_curiosity", "How does the human eye adapt to see in a pitch-dark room over 20-30 minutes?"),
    ("science_curiosity", "What happens physically in your brain when caffeine blocks adenosine receptors?"),
    ("science_curiosity", "Why do rainbows only appear when the sun is behind you and rain is ahead of you?"),
    ("science_curiosity", "How do smoke detectors detect microscopic smoke particles inside a room?"),
    ("science_curiosity", "Why do car tires lose air pressure when the weather gets significantly colder in winter?"),
    ("science_curiosity", "How does sunscreen protect human skin from ultraviolet (UV) radiation?"),
    ("science_curiosity", "What causes thunder, and why do you always see lightning before you hear it?"),
    ("science_curiosity", "How does yeast make bread dough rise and develop flavor?"),
    ("science_curiosity", "Why is yawning contagious among humans and some animals?"),
    ("science_curiosity", "How do magnets work at an atomic level?"),
    ("science_curiosity", "Why does cutting an onion release syn-propanethial-S-oxide and make you tear up?")
]

current_id = 201
for cat, prompt in new_100:
    prompts.append({
        "id": current_id,
        "category": cat,
        "prompt": prompt
    })
    current_id += 1

print(f"Total prompts in expanded benchmark: {len(prompts)}")
os.makedirs("data/benchmarks", exist_ok=True)
with open("data/benchmarks/eval_300_prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, indent=2, ensure_ascii=False)

print("Saved to data/benchmarks/eval_300_prompts.json successfully!")
