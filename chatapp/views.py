from django.shortcuts import render, redirect
from .models import Student
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
# Load the JSON file
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase app
cred = credentials.Certificate('chatapp/service_account.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'chatbot-9324e.appspot.com'
})

# Reference to the Firebase Storage bucket
storage_bucket = storage.bucket()


with open('chatapp\college_qp.json', 'r') as file:
    college_qp = json.load(file)

questions = college_qp['questions']
responses = college_qp['answers']


def home(request):
    return render(request, 'chatbot/home.html')

def register_new_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        location = request.POST.get('location')
        # Similarly, get other fields as needed

        # Create a new student instance and save it to the database
        student = Student(name=name, email=email, password=password, mobile=mobile, location=location)
        student.save()

        return redirect('chatbot')
    return render(request, 'chatbot/register.html')


def login_existing_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Student.objects.filter(name=username, password=password).exists():
            return redirect('chatbot')
    return render(request, 'chatbot/login.html')

# def chatbot(request):
#     messages = request.session.get('messages', [])
    
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         question, response = process_message(message)
#         messages.append((question, "response"))
#         request.session['messages'] = messages
#         return render(request, 'chatbot/chatbot.html', {'response': response, 'messages': messages})
    
#     return render(request, 'chatbot/chatbot.html', {'response': None, 'messages': messages})

def chatbot(request):
    if request.method=='POST':
        message=request.POST.get('message')
        response=process_message(message)
        return JsonResponse({
            # 'message':message,
            'response':response

        })

    return render(request,'chatbot/chatbot.html')
def student_list(request):
    students = Student.objects.all()
    return render(request, 'chatbot/student_list.html', {'students': students})



# Sample dataset of questions and responses


# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(questions)

def chat_process_message(user_query):
    # Vectorize the user query
    user_query_vectorized = vectorizer.transform([user_query])

    # Calculate the cosine similarity between the user query and the questions
    similarities = cosine_similarity(user_query_vectorized, X)

    # Get the index of the most similar question
    most_similar_index = np.argmax(similarities)

    # Return the corresponding response
    if similarities[0][most_similar_index] < 0.5:  # Adjust the threshold as needed
        return "I'm sorry, but I don't have that information available at the moment. Is there anything else I can help you with?"
    return responses[most_similar_index]


# def process_message(user_query):
#     if 'notes' in user_query.lower():
#         # Search for notes in Firebase Storage
#         keyword = user_query.lower().replace('notes', '').strip()
#         matching_files = [blob for blob in storage_bucket.list_blobs() if keyword in blob.name.lower()]

#         if matching_files:
#             # Return a list of matching files with download links
#             response = "Here are the matching files:\n"
#             for blob in matching_files:
#                 download_url = f"https://firebasestorage.googleapis.com/v0/b/chatbot-9324e.appspot.com/o/{blob.name}?alt=media"# Expiration time in seconds (1 hour in this case)
#                 response += f"<a href='{download_url}' download='{blob.name}'>{blob.name}</a><br>"
#             return response
#         else:
#             return f"No files found for '{keyword}'. Is there anything else I can help you with?"
#     else:
#         return chat_process_message(user_query)
    
def process_message(user_query):
    if 'notes' or 'notes for' in user_query.lower():
        # Search for notes in Firebase Storage
        keyword = user_query.lower().replace('notes', '').strip()
        matching_files = [blob for blob in storage_bucket.list_blobs() if keyword in blob.name.lower()]

        if matching_files:
            # Check if there is an exact match for the file name
            exact_match = [blob for blob in matching_files if blob.name.lower() == keyword]
            if exact_match:
                # Return the exact match
                blob = exact_match[0]
                download_url = f"https://firebasestorage.googleapis.com/v0/b/chatbot-9324e.appspot.com/o/{blob.name}?alt=media"
                return f"<a href='{download_url}' download='{blob.name}'>{blob.name}</a>"

            # If there is no exact match, return all matching files
            response = "Here are the matching files:\n"
            for blob in matching_files:
                download_url = f"https://firebasestorage.googleapis.com/v0/b/chatbot-9324e.appspot.com/o/{blob.name}?alt=media"
                response += f"<a href='{download_url}' download='{blob.name}'>{blob.name}</a><br>"
            return response
        else:
            return f"No files found for '{keyword}'. Is there anything else I can help you with?"
    else:
        return chat_process_message(user_query)
