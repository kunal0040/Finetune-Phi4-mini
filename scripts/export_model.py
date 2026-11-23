"""
Model Export & Ollama Modelfile Generation Script
Handles merging LoRA adapter with base weights and generating Ollama Modelfiles.
"""

import argparse
import os
import sys
import yaml


def load_config(config_path="config/training_config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_ollama_modelfile(gguf_path_or_base, modelfile_path="Modelfile"):
    print(f"[*] Generating Ollama Modelfile at {modelfile_path}...")
    
    content = f"""# Kaitu Fine-Tuned Phi-4-mini Modelfile
# Target Model: kaitu-phi4-mini

FROM {gguf_path_or_base}

# Parameter Configuration
PARAMETER temperature 0.3
PARAMETER top_p 0.8
PARAMETER stop "<|end|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"

# Kaitu Grounded System Template
TEMPLATE \"\"\"{{{{- if or .System .Tools }}}}<|system|>{{{{ if .System }}}}{{{{ .System }}}}{{{{ end }}}}
{{{{- if .Tools }}}}<|tool|>{{{{ .Tools }}}}<|/tool|><|end|>{{{{- end }}}}
{{{{- end }}}}
{{{{- range $i, $_ := .Messages }}}}
{{{{- $last := eq (len (slice $.Messages $i)) 1 -}}}}
{{{{- if ne .Role "system" }}}}<|{{{{ .Role }}}}|>{{{{ .Content }}}}
{{{{- if not $last }}}}<|end|>{{{{ end }}}}
{{{{- if and (ne .Role "assistant") $last }}}}<|end|><|assistant|>{{{{ end }}}}
{{{{- end }}}}
{{{{- end }}}}\"\"\"

SYSTEM \"\"\"You are Kaitu, a personal AI assistant created by Kunal.
You assist Kunal with programming, engineering, system design, and everyday problem solving.
Be direct, technically rigorous, honest, and helpful.
If you are uncertain about something or lack necessary information, say so clearly.
Never fabricate tool executions, file access, or personal experiences.
Adapt your depth dynamically: provide concise answers for simple queries, and detailed, well-structured explanations for complex technical problems.\"\"\"
"""
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Ollama Modelfile successfully created at {modelfile_path}")
    print("\nTo register the model in Ollama, run:")
    print(f"  ollama create kaitu-phi4-mini -f {modelfile_path}")


def main():
    parser = argparse.ArgumentParser(description="Export model and generate Ollama Modelfile")
    parser.add_argument("--gguf", default="kaitu-phi4-mini-q4_k_m.gguf", help="Path to exported GGUF file or existing model tag")
    parser.add_argument("--out-modelfile", default="Modelfile", help="Output Modelfile path")
    args = parser.parse_args()

    generate_ollama_modelfile(args.gguf, args.out_modelfile)


if __name__ == "__main__":
    main()
