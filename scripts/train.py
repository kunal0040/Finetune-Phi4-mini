"""
Phi-4-mini QLoRA Fine-Tuning Script using Hugging Face TRL & PEFT
Configured for safe, efficient parameter-efficient fine-tuning with 4-bit NF4 quantization.
"""

import argparse
import os
import sys
import yaml


def load_config(config_path="config/training_config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Phi-4-mini with QLoRA")
    parser.add_argument("--config", default="config/training_config.yaml", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Validate environment and config without training")
    args = parser.parse_args()

    cfg = load_config(args.config)
    print(f"[*] Loaded fine-tuning configuration for: {cfg['project']['name']}")

    model_id = cfg["models"]["base_model_hf"]
    train_data_path = cfg["paths"]["train_data"]
    eval_data_path = cfg["paths"]["eval_data"]
    output_dir = cfg["paths"]["output_dir"]
    adapter_dir = cfg["paths"]["adapter_dir"]

    # Validate dataset paths
    assert os.path.exists(train_data_path), f"Train dataset missing: {train_data_path}"
    assert os.path.exists(eval_data_path), f"Eval dataset missing: {eval_data_path}"
    print(f"[+] Dataset paths verified: {train_data_path}, {eval_data_path}")

    if args.dry_run:
        print("[+] DRY-RUN SUCCESS: Configuration, datasets, and paths are valid.")
        return

    import torch
    from datasets import load_dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

    # Check CUDA
    if not torch.cuda.is_available():
        print("[-] WARNING: CUDA is not available on this machine!")
        print("[-] Please run training on a GPU environment (Google Colab / Cloud instance).")
        sys.exit(1)

    # 1. Quantization Configuration (4-bit NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type=cfg["quantization"]["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=cfg["quantization"]["bnb_4bit_use_double_quant"],
        bnb_4bit_compute_dtype=getattr(torch, cfg["quantization"]["bnb_4bit_compute_dtype"])
    )

    # 2. Tokenizer
    print(f"[*] Loading tokenizer for {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 3. Model
    print(f"[*] Loading 4-bit base model: {model_id}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # 4. LoRA Configuration
    lora_cfg = cfg["lora"]
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        lora_dropout=lora_cfg["lora_dropout"],
        bias=lora_cfg["bias"],
        task_type=lora_cfg["task_type"],
        target_modules=lora_cfg["target_modules"]
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 5. Dataset Loading
    dataset = load_dataset("json", data_files={"train": train_data_path, "eval": eval_data_path})

    # 6. Training Arguments
    t_cfg = cfg["training"]
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=t_cfg["per_device_train_batch_size"],
        per_device_eval_batch_size=t_cfg["per_device_eval_batch_size"],
        gradient_accumulation_steps=t_cfg["gradient_accumulation_steps"],
        learning_rate=t_cfg["learning_rate"],
        lr_scheduler_type=t_cfg["lr_scheduler_type"],
        warmup_ratio=t_cfg["warmup_ratio"],
        weight_decay=t_cfg["weight_decay"],
        num_train_epochs=t_cfg["num_train_epochs"],
        gradient_checkpointing=t_cfg["gradient_checkpointing"],
        optim=t_cfg["optim"],
        logging_steps=t_cfg["logging_steps"],
        save_strategy=t_cfg["save_strategy"],
        evaluation_strategy=t_cfg["evaluation_strategy"],
        bf16=t_cfg["bf16"],
        fp16=t_cfg["fp16"],
        report_to="none"
    )

    # 7. SFT Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["eval"],
        peft_config=peft_config,
        tokenizer=tokenizer,
        args=training_args,
        max_seq_length=t_cfg["max_seq_length"]
    )

    # 8. Train
    print("[*] Starting training...")
    trainer.train()

    # 9. Save LoRA Adapter
    print(f"[*] Saving trained LoRA adapter to {adapter_dir}...")
    trainer.model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)
    print("[+] Training completed successfully!")


if __name__ == "__main__":
    main()
