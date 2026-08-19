from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
import torch as tr
import sympy as sp
import re

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=tr.float16,
    llm_int8_enable_fp32_cpu_offload=True
)

tokenizer =AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")
model=AutoModelForCausalLM.from_pretrained('microsoft/Phi-4-mini-instruct', quantization_config=bnb_config,
device_map='auto',max_memory={0: "3200MiB", "cpu": "12GiB"} )    

input_device = next(model.get_input_embeddings().parameters()).device           
history=[{"role": "system", "content": "You are NANO, a helpful and precise assistant.Always be precise like a scientist and if you don't know the answer, say 'I don't know' instead of making up an answer. You are also a math solver and can solve equations."}]
max=6

prompt = input("you : ")
def solver(prompt):
    expr_str=prompt.replace("solve","").strip()
    match_expr=re.search(r'[a-zA-Z]',expr_str)
    var=sp.symbols(match_expr.group()) if match_expr else sp.symbols('x')
    if '=' in expr_str:
        lhs,rhs=expr_str.split('=',1)
        lhs=sp.sympify(lhs.strip())
        rhs=sp.sympify(rhs.strip())
        eq=sp.Eq(lhs,rhs)
    else:
        eq=sp.Eq(sp.sympify(expr_str),0)

    try:
        return sp.solve(eq,var,dict=True)
    except Exception as e:
        return {"error": str(e),"eq": str(eq)}

while prompt.lower() not in ["exit", "stop"]:
    try:
        
        history.append({"role": "user", "content": prompt})
        if "just give me the answer" in prompt.lower():
            history[0]["content"]="you're a helpful assistant. Be quick and conscise."
        else:
            history[0]["content"]="You are NANO, a helpful and precise assistant.Always be precise like a scientist and if you don't know the answer, say 'I don't know' instead of making up an answer. You are also a math solver and can solve equations."
        if "solve" in prompt.lower() and "=" in prompt.lower() and "for" not in prompt.lower():
                 result = solver(prompt)
                 tool_mssg=f"Tool result:{(result)}"
                 history.append({"role": "tool", "content": tool_mssg})
        
        if len(history) > max*2:
            history = history[-(max*2):]
       
        
        inputs = tokenizer.apply_chat_template(history, return_tensors='pt', add_generation_prompt=True).to('cuda')
        
        input_len=inputs["input_ids"].shape[1]
        outputs = model.generate(**inputs, max_new_tokens=500)
        new_tokens=outputs[0][input_len:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True)
        print(f"NANO: {response}")
        history.append({"role": "assistant", "content": response})
    except KeyboardInterrupt:
        print("Generation interrupted by user.")
    prompt = input("you : ")



    

    


    
    









