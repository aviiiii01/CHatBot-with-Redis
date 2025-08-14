# api/views.py

import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
# 1. Import the decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# ... (genai configuration and model setup is the same) ...
# GOOGLE_API_KEY="AIzaSyBH99pwKah0zEh77urHHcMf7_UJKWWNM0o"
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    raise RuntimeError("GOOGLE_API_KEY not found in .env file.")


import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True)


import markdown







r.hset("user:1001", mapping={
    "name": "Avinash",
    "age": "22",
    "city": "Ghaziabad"
})




model = genai.GenerativeModel('gemini-2.5-flash')

def home(request):
    questions = [q for q in r.lrange("prompt", 0, 9)]
    answers = [a for a in r.lrange("res", 0, 9)]
    
    # Pair them together
    qa_pairs = list(zip(questions, answers))
    qa_pairs=qa_pairs[::-1]
    return render(request,"api/home.html",{"qa_pairs":qa_pairs})

# 2. Apply the decorator to the class

def generate(request):
    if request.method=="POST":
        if request.method == "POST":
            prompt = request.POST.get("prompt")
            
            # Generate response
            questions = [q for q in r.lrange("prompt", 0, -1)]
            answers = [a for a in r.lrange("res", 0, -1)]
            
            # Pair them together
            qa_pairs = list(zip(questions, answers))
            qa_pairs=qa_pairs[::-1]
            res = model.generate_content(f"THis is the previous messages passed by the user{qa_pairs} And this is the new question which the user has asked now{prompt} Generate the response accordingly based on the context of previous information.")
            res_text = res.candidates[0].content.parts[0].text
            res_text = markdown.markdown(res_text)
            
            # Save Q/A separately if needed
            r.lpush("prompt", prompt)
            r.lpush("res", res_text)

            # Save Q/A pair in chat as JSON
            questions = [q for q in r.lrange("prompt", 0, 9)]
            answers = [a for a in r.lrange("res", 0, 9)]
            
            # Pair them together
            qa_pairs = list(zip(questions, answers))
            qa_pairs=qa_pairs[::-1]
            print(qa_pairs)
            return render(request, "api/home.html", {"qa_pairs": qa_pairs})

@method_decorator(csrf_exempt, name='dispatch')
class GenerateTextView(APIView):
    """
    An API View that receives a prompt and returns the LLM's response.
    """
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')

        if not prompt:
            return Response(
                {"error": "Prompt is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = model.generate_content(prompt)
            return Response({"response": response.text}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)