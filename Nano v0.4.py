from transformers import AutoModelForCausalLM,AutoTokenizer
import torch as tr
import sympy as sp
import re

tokenizer =AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")
model=AutoModelForCausalLM.from_pretrained('microsoft/Phi-4-mini-instruct')
model=model.to('cuda')
history=[]
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
        if "solve" in prompt.lower():
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
    


    
    









