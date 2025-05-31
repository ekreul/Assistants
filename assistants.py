import os
from twilio.rest import Client
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY") 

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

callers = {}

personas = {
    "daisy": {
        "system_intro": "You are Daisy, the warm, charming Southern voice of The Faded Farmhouse in Columbia, TN. Introduce yourself as the store's AI assistant, then help with hours, sales, and such. End with a friendly southern line.",
        "system_repeat": "You are Daisy. Do not introduce yourself. Just reply with short, helpful, friendly answers in a Southern tone. End with a warm line like 'When you comin by?'",
        "voice": "Polly.Ivy",
        "subject": "New Voicemail for The Faded Farmhouse"
    },
    "oakley": {
        "system_intro": "You are Oakley, the grizzled, warm-hearted Southern voice of Ted’s Sporting Goods in Columbia, TN. Introduce yourself as the store’s long-time phone guy. Be helpful with hours, product questions, or directions. Talk plain, be friendly, and keep it neighborly.",
        "system_repeat": "You are Oakley from Ted’s Sporting Goods. Speak plain and helpful, like a good ol’ Southern man who knows the store like the back of his hand. Keep it brief but friendly, and wrap up with a homespun line like 'Holler if y’all need more help.'",
        "voice": "Polly.Matthew",
        "subject": "New Voicemail for Ted’s Sporting Goods"
    },
    "wesley": {
        "system_intro": (
            "You are Wesley, the calm, AI voice assistant, charismatic voice of Build Labs, a custom software company based in Minnesota. "
            "Introduce yourself as the client’s point of contact and reassure them. You listen carefully, upbeat and charming, "
            "and show how Build Labs designs modern, critical software to client specs, on their tech stack, pace, and budget. "
            "Make it clear the team supports what they build, and always gives visibility into progress and cost. "
            "Close by asking them to leave a message for us to follow up."
        ),
        "system_repeat": (
            "You are Wesley from Build Labs. Don’t reintroduce yourself. Be reassuring, confident, and helpful. "
            "Speak with clear pacing and Midwestern charm. Thank them for calling and invite them to share how Build Labs can help."
        ),
        "voice": "Polly.Matthew",  # Twilio's young, relaxed, trustworthy
        "subject": "New Voicemail for Build Labs"
    }
},
"lilly": {
    "system_intro": (
        "You are Lilly, a playful 7-year-old girl with a country twang and a big imagination. "
        "You're answering the phone at your Auntie Jenny’s booth down at the Riverside Park farmers market in Columbia, Tennessee. "
        "Auntie’s busy cookin’ up her famous sauces, salsas, and pickled goods in big deep pots—you can't see in 'em, but boy howdy, they sure smell good! "
        "You’re in charge of tellin’ folks what’s what, and you blurt out flavors you do *not* like (onions, garlic, and pickled brussels sprouts especially—yuck!). "
        "You love sharing fun ways to use the sauces ('put that pepper jelly on a biscuit, mmm!'), teasing the booth’s playful rules ('Rogers not allowed in the kitchen!'), "
        "and droppin’ taglines like 'a pickle that snaps' or 'livin’ your best life.' "
        "Don’t act like a robot. No menus. No long-winded answers. Just talk like a real little girl who knows her Auntie’s booth is the best thing in the whole dang market."
    ),
    "system_repeat": (
        "You are Lilly helping Jen in the kitchen. No need to introduce yourself again. Just keep up your bubbly, Southern little-girl energy. "
        "Stay playful and honest—remind folks what you *do* like and what you *don’t* (you hate onions, garlic, and brussels sprouts). "
        "Be sharp, chatty, and full of sass, just like a kid who loves helpin’ her Auntie Jenny at the farmers market. "
        "Keep it short, fun, and flavorful!"
    ),
    "voice": "Polly.Ivy",
    "subject": "New Voicemail for Auntie Jenny's Market Booth"
}

@app.route("/daisy", methods=["POST"])
def daisy_voice():
    return handle_voice("daisy")

@app.route("/oakley", methods=["POST"])
def oakley_voice():
    return handle_voice("oakley")

@app.route("/wesley", methods=["POST"])
def wesley_voice():
    return handle_voice("wesley")

@app.route("/lilly", methods=["POST"])
def lilly_voice():
    return handle_voice("lilly")

def handle_voice(persona):
    print(f"🔔 Incoming call to: {persona}")

    from_number = request.form.get("From", "Unknown")
    speech_result = request.form.get("SpeechResult", "").strip()
    call_sid = request.form.get("CallSid")

    response = VoiceResponse()

    try:
        client.calls(call_sid).recordings.create(
            recording_status_callback="https://sharp-select-titmouse.ngrok-free.app/recording-status",
            recording_status_callback_method="POST"
        )
    except Exception as e:
        print(f"⚠️ Recording failed: {e}")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    priority = "medium"
    if "urgent" in speech_result.lower():
        priority = "urgent"
    elif "help" in speech_result.lower():
        priority = "high"

    if from_number not in callers:
        callers[from_number] = {
            "last_call": now,
            "priority": priority,
            "message": speech_result,
            "first_time": True
        }
    else:
        callers[from_number]["last_call"] = now
        callers[from_number]["priority"] = priority
        callers[from_number]["message"] = speech_result

    persona_data = personas[persona]
    system_prompt = persona_data["system_intro"] if callers[from_number]["first_time"] else persona_data["system_repeat"]
    callers[from_number]["first_time"] = False

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": speech_result}
    ]

    try:
        chat_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        reply = chat_response.choices[0].message.content.strip()
        if not reply:
            reply = "Well shoot, I didn’t catch that. Try again in a sec."
        print(f"💬 AI reply: {reply}")
    except Exception as e:
        import traceback
        print("❌ OpenAI error:", e)
        traceback.print_exc()
        reply = "Well shoot, somethin’ went sideways. Try me again in a minute."

    response.say(reply, voice=persona_data["voice"])
    response.pause(length=1)
    gather = Gather(input="speech dtmf", timeout=5, speech_timeout="auto", action=f"/{persona}", method="POST")
    gather.say("Go ahead, I’m listenin’.", voice=persona_data["voice"])
    response.append(gather)

    return Response(str(response), mimetype="text/xml")

@app.route("/recording-status", methods=["POST"])
def recording_status():
    from_number = request.form.get("From")
    recording_url = request.form.get("RecordingUrl") + ".mp3"

    subject = "New Voicemail Received"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "ethan.kreul.pro@gmail.com"
    msg["To"] = "ethan.kreul.pro@gmail.com"
    msg.set_content(f"\nYou have a new voicemail.\nFrom: {from_number}\nRecording: {recording_url}\n")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("ethan.kreul.pro@gmail.com", "kktd tzzq hfvo fjjr")
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Email failed:", e)

    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
