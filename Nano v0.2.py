from transformers import AutoModelForCausalLM,AutoTokenizer
import torch as tr

tokenizer =AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")
model=AutoModelForCausalLM.from_pretrained('microsoft/Phi-4-mini-instruct')
model=model.to('cuda')
history=[]
max=6

prompt = input("you : ")
while prompt.lower() not in ["exit", "stop"]:
    try:
        message = [{"role": "user", "content": prompt}]
        history.append({"role": "user", "content": prompt})
        if len(history) > max:
            history = history[-(max*2):]

        inputs = tokenizer.apply_chat_template(history, return_tensors='pt', add_generation_prompt=True).to('cuda')


        input_len=inputs["input_ids"].shape[1]
        outputs = model.generate(**inputs, max_new_tokens=512)
        new_tokens=outputs[0][input_len:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True)
        print(f"NANO: {response}")
    except KeyboardInterrupt:
        print("Generation interrupted by user.")
    prompt = input("you : ")
    









