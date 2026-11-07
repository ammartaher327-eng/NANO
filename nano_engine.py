
import re

import torch as tr
import sympy as sp

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)


class NanoEngine:

    def __init__(self):

        print("NANO: Initializing inference engine...")

        self.model_name = "microsoft/Phi-4-mini-instruct"
        self.max_history = 12
        self.max_new_tokens = 500

        self.system_prompt = (
            "You are NANO, a helpful and precise assistant. "
            "Always be precise like a scientist. "
            "If you don't know the answer, say 'I don't know' "
            "instead of making up an answer. "
            "You are also a math solver and can solve equations."
        )

        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Quantization configuration
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=tr.float16,
            llm_int8_enable_fp32_cpu_offload=True
        )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=self.bnb_config,
            device_map="auto",
            max_memory={
                0: "3200MiB",
                "cpu": "12GiB"
            }
        )

        self.model.eval()

        self.input_device = (
            self.model.get_input_embeddings().weight.device
        )

        print("NANO: Inference engine initialized.")

    def solver(self, prompt):

        try:
            expr_str = prompt.replace("solve", "").strip()

            match_expr = re.search(r"[a-zA-Z]", expr_str)

            var = (
                sp.symbols(match_expr.group())
                if match_expr
                else sp.symbols("x")
            )

            if "=" in expr_str:
                lhs, rhs = expr_str.split("=", 1)

                lhs = sp.sympify(lhs.strip())
                rhs = sp.sympify(rhs.strip())

                equation = sp.Eq(lhs, rhs)

            else:
                equation = sp.Eq(
                    sp.sympify(expr_str),
                    0
                )

            return sp.solve(
                equation,
                var,
                dict=True
            )

        except Exception as error:
            return {"error": str(error)}

    def generate_reply(self, prompt):

        prompt = prompt.strip()

        if not prompt:
            return ""

        # Dynamic system prompt
        if "just give me the answer" in prompt.lower():
            self.history[0]["content"] = (
                "You're a helpful assistant. Be quick and concise."
            )
        else:
            self.history[0]["content"] = self.system_prompt

        # Preserve the original user message
        self.history.append({
            "role": "user",
            "content": prompt
        })

        # Prepare the context
        generation_history = self.history.copy()

        # SymPy tool routing
        if (
            "solve" in prompt.lower()
            and "=" in prompt
            and "for" not in prompt.lower()
        ):

            result = self.solver(prompt)

            tool_context = (
                "\n\n[SymPy mathematical tool result: "
                f"{result}]"
            )

            generation_history[-1] = {
                "role": "user",
                "content": prompt + tool_context
            }

        # Apply chat template
        formatted_prompt = self.tokenizer.apply_chat_template(
            generation_history,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(self.input_device)
            for key, value in inputs.items()
        }

        # Generate response
        with tr.inference_mode():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id
            )

        input_length = inputs["input_ids"].shape[1]

        new_tokens = outputs[0][input_length:]

        response = self.tokenizer.decode(
            new_tokens,
            skip_special_tokens=True
        ).strip()

        # Save response
        self.history.append({
            "role": "assistant",
            "content": response
        })

        # Keep system prompt + recent conversation
        if len(self.history) > self.max_history + 1:

            self.history = [
                self.history[0]
            ] + self.history[-self.max_history:]

        return response
