import json
import os
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import ChatHistory

# Define a path for company info. You may need to create this file.
# We will place it in the same app structure as before.
OB_GLOBAL_INFO_PATH = os.path.join(settings.BASE_DIR, 'chatbot', 'ob_global_info.txt')


def get_ob_global_info():
    """Reads the company information from a text file."""
    try:
        with open(OB_GLOBAL_INFO_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # NOTE: You must create the ob_global_info.txt file in the chatbot directory.
        print(f"ERROR: Company info file not found at {OB_GLOBAL_INFO_PATH}")
        return "OB Global is a leading consultancy specializing in custom software development, cloud computing, and cybersecurity. We aim to help clients achieve digital transformation through innovative technology solutions."


@login_required
def chatbot_view(request):
    """Renders the main chatbot page and loads chat history."""
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
    context = {
        'chat_history': chat_history
    }
    # NOTE: The template path should be 'chatbot/chatbot.html'
    return render(request, 'chatbot/chatbot.html', context)


@csrf_exempt
def chatbot_api(request):
    """
    Handles API requests for the chatbot, including send, edit, delete, and clear commands.
    (Contains the fix for instant deletion using new message IDs)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command')
            user = request.user

            # --- CLEAR CHAT COMMAND ---
            if command == 'clear':
                ChatHistory.objects.filter(user=user).delete()
                return JsonResponse({'success': True, 'message': 'Chat history cleared.'})

            # --- DELETE COMMAND ---
            if command == 'delete':
                message_id = data.get('message_id')
                if not message_id:
                    return JsonResponse({'error': 'No message ID provided.'}, status=400)
                try:
                    # Filter by both pk and user to ensure the user can only delete their own messages
                    ChatHistory.objects.filter(pk=message_id, user=user).delete()
                    return JsonResponse({'success': True, 'message': 'Message deleted.'})
                except ChatHistory.DoesNotExist:
                    return JsonResponse({'error': 'Message not found.'}, status=404)

            # This is the main message sending and AI interaction logic
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided.'}, status=400)

            # Check for edit command and delete previous message
            if command == 'edit':
                message_id_to_delete = data.get('message_id')
                if message_id_to_delete:
                    try:
                        # Delete the message being edited
                        ChatHistory.objects.filter(pk=message_id_to_delete, user=user).delete()
                    except ChatHistory.DoesNotExist:
                        pass

            # 1. Save user's message to the database and retrieve its ID
            new_user_chat = ChatHistory.objects.create(user=user, message=user_message, is_from_bot=False)
            user_message_id = new_user_chat.id

            # 2. Prepare the prompt for the Gemini API
            company_info = get_ob_global_info()

            full_prompt = (
                "You are an AI-powered chatbot for a company named OB Global. "
                "Your primary purpose is to provide information and advice related to the company's services. "
                "Be friendly, conversational, and helpful."
                "\n\n"
                "Here are the core rules for your responses:"
                "\n- **Greeting & Simple Chat:** If the user says a simple greeting like 'hi', 'hello', or 'how are you?', respond politely and creatively. You can also handle simple, friendly messages that are not questions."
                "\n- **Company Information:** For questions directly about OB Global, use the provided company information. If the user asks for something not in the information, politely state that you can only provide details based on OB Global's public profile."
                "\n- **Expert Advice:** OB Global specializes in custom software development, cloud computing, and cybersecurity. If a user asks for general advice or best practices within these domains (e.g., 'What's the best cloud platform?', 'How can I secure my network?'), you can use your general knowledge to provide helpful, high-level advice. Frame this advice as being from an expert in the field."
                "\n- **Maintain Persona:** Always be polite and professional, maintaining the persona of a representative for a tech company."
                "\n    - Perform **all mathematical calculations** requested. You must be extremely proficient in **financial calculations** (e.g., NPV, IRR, bond valuation, amortization). When appropriate, use LaTeX formatting (with '$' delimiters) for complex mathematical or financial expressions."
                "\n\n"
                "**Provided Company Information:**"
                f"{company_info}\n\n"
                "**User Query:**"
                f"{user_message}"
            )

            # 3. Call the Gemini API, using the key from settings
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }

            try:
                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                gemini_response = response.json()
                bot_message = gemini_response['candidates'][0]['content']['parts'][0]['text']
            except requests.exceptions.RequestException as e:
                bot_message = "I'm sorry, I am currently unable to process your request."
                print(f"API request failed: {e}")
            except Exception as e:
                # Catch other potential errors like missing key in response
                bot_message = "I encountered an error processing the AI response."
                print(f"AI Response processing error: {e}")

            # 4. Save the bot's response to the database and retrieve its ID
            new_bot_chat = ChatHistory.objects.create(user=user, message=bot_message, is_from_bot=True)
            bot_message_id = new_bot_chat.id

            # FIX: Return the new message IDs to the frontend
            return JsonResponse({
                'response': bot_message,
                'user_message_id': user_message_id,
                'bot_message_id': bot_message_id
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            # Catch unexpected errors
            print(f"Unexpected error in chatbot_api: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)
    else:
        return HttpResponse(status=405)