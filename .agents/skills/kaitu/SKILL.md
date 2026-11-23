---
name: kaitu
description: Chat directly with your fine-tuned local assistant phi4:mini-kaitu (V6) running on Ollama with production runtime guards.
---

# Kaitu Local AI Assistant Skill

This skill links Antigravity directly to your fine-tuned local model **`phi4:mini-kaitu`** running via Ollama on your local GPU.

## How to Chat with Kaitu in this Conversation
Whenever the user types `/kaitu <message>` or asks to talk with Kaitu:
1. Run the local bridge script using `run_command`:
   ```powershell
   python scripts/bridge_kaitu.py "<user query>"
   ```
2. Display Kaitu's direct, guarded response in the chat.
