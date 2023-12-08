from flask import Flask, request
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import time

app = Flask(__name__)

# Set your Twilio and OpenAI credentials
openai.organization = os.environ.get('OPENAI_ORG')
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
openai.api_key = os.environ.get('OPENAI_API_KEY')
success_message = os.environ.get('SUCCESS_MESSAGE', 'Message received and processed successfully!')

# Webhook endpoint for receiving WhatsApp messages
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_message = request.form.get('Body', '').lower()

    # Use OpenAI to generate a response
    openai_response = generate_openai_response(incoming_message)

    # Send the OpenAI response to the user via WhatsApp
    send_whatsapp_message(request.form.get('From'), openai_response)
    return success_message

def generate_openai_response(user_message):
    # Use OpenAI API to generate a response
  model_engine ="gpt-3.5-turbo" #"text-davinci-002"
  prompt = (f"Q: {user_message}\n"
            "A:")
  max_retries = 3
  current_retry = 0

  while current_retry < max_retries:
      try:
        response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=40000,
        n=1,
        stop=None,
        temperature=0.7,
             )
        answer = response.choices[0].text.strip()
      except openai.error.RateLimitError as e:
        # Handle rate limit error gracefully
                print(f"Rate limit error: {e}")

                # Use exponential backoff to wait before retrying
                delay = 2 ** current_retry
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

                current_retry += 1

        # If retries are exhausted, you may want to log an error or take appropriate action
  print("Maximum retries reached. Unable to get a response.")
  return "Sorry, I'm currently experiencing issues. Please try again                 later."
def chatgpt():
  incoming_que = request.values.get('Body', '').lower()
  print("Question: ", incoming_que)
  # Generate the answer using GPT-3
  answer = generate_answer(incoming_que)
  print("BOT Answer: ", answer)
  bot_resp = MessagingResponse()
  msg = bot_resp.message()
  msg.body(answer)
  return str(bot_resp)
  
def send_whatsapp_message(to_number, message):
    from twilio.rest import Client

    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=to_number
                )
    except Exception as e:
      print(f"Failed to send message: {e}")
      # Add more details from the exception if available
      if hasattr(e, 'msg'):
          print(f"Message: {e.msg}")
      if hasattr(e, 'code'):
          print(f"Code: {e.code}")
      return "Failed to send the message due to an error."



if __name__ == '__main__':
    app.run(host='0.0.0.0',
           port=3000,
           debug=True)


#
