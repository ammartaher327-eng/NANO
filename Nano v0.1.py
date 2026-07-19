from transformers import AutoModelForCausalLM,AutoTokenizer
import torch as tr

tokenizer =AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")
model=AutoModelForCausalLM.from_pretrained('microsoft/Phi-4-mini-instruct')
model=model.to('cuda')

prompt=input("you : ")
input=tokenizer(prompt,return_tensors='pt').to('cuda')

outputs=model.generate(**input,max_new_tokens=1000)
response=tokenizer.decode(outputs[0],skip_special_tokens=True)
print(f"NANO: {response}")







