import os
from flask import Flask, request, Response, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import difflib
import json
import smtplib
from email.message import EmailMessage
import datetime
from twilio.rest import Client
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session
client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))

# Daisy store profiles
stores = [
    {
        "store_name": "Faded Farmhouse",
        "location": "Columbia, TN",
        "website": "https://thefadedfarmhouse.com/pages/columbia-tn",
        "last_reviewed": "2025-06-18",
        "price_range": "$$$",
        "blurt_categories": "Home decor, seasonal accents, rustic furnishings, apparel",
        "blurt_owner_style": "Stylish, trend-savvy southern charm. A curated space with warmth and personality.",
        "blurt_specials": "Occasional seasonal markdowns—check the homepage banners.",
        "blurt_events": "Pop-up markets and holiday events (info sparse).",
        "about_excerpt": "A charming lifestyle shop offering farmhouse-inspired decor and boutique finds. Known for visual merchandising and a cozy ambiance.",
        "product_brands": ["Mud Pie", "Candleberry", "Simply Southern"],
        "contact_info": {
            "phone": "(931) 548-8882",
            "address": "407 W 7th St, Columbia, TN 38401",
            "hours": "Mon–Sat 10am–6pm; Sun 1–5pm"
        },
        "vibe_tags": ["cozy", "chic", "southern"],
        "last_scraped_note": "Moderately updated site with clear navigation and frequent homepage banners.",
        "needs_review": False,
        "update_last_known": "",
        "update_staleness_warning": None,
        "data_quality_score": 8,
        "update_estimate": "This month"
    },
    {
        "store_name": "TEDS Sporting Goods",
        "location": "Columbia, TN",
        "website": "https://www.tedssportinggoods.com",
        "last_reviewed": "2025-06-18",
        "price_range": "$$$$",
        "blurt_categories": "Hunting gear, fishing supplies, outdoor apparel, camping equipment, firearms accessories",
        "blurt_owner_style": "Family-owned since 1955—down-to-earth, friendly, and community-driven, with a folksy charm anchored in local heritage.",
        "blurt_specials": "Father’s Day promos and clearance apparel in ‘Sale’ section online.",
        "blurt_events": "Occasional in-store demos and community fishing clinics (check local Facebook).",
        "about_excerpt": "A long-standing local landmark carrying sporting goods, firearms, outdoor apparel and gear—known for friendly service and unbeatable local knowledge.",
        "product_brands": ["Volunteer Traditions", "Glock", "Teva", "AFTCO", "Bergara", "Uberti"],
        "contact_info": {
            "phone": "(931) 388-6387",
            "address": "806 S Main St, Columbia, TN 38401",
            "hours": "Mon–Fri 8am–5:30pm; Sat 8am–4pm"
        },
        "vibe_tags": ["outdoor", "heritage", "friendly", "community‑focused"],
        "last_scraped_note": "Website is basic with limited information; relies on heritage stories and Facebook posts.",
        "needs_review": False,
        "update_last_known": "",
        "update_staleness_warning": None,
        "data_quality_score": 9,
        "update_estimate": "Last month"
    },
    {
        "store_name": "Creekside Trading Company",
        "location": "Columbia, TN",
        "website": "https://www.facebook.com/creeksidetradingcompany",
        "last_reviewed": "2025-06-18",
        "price_range": "$$$",
        "blurt_categories": "Vintage items, antiques, home goods, country decor",
        "blurt_owner_style": "Rustic and nostalgic with a warm, storytelling vibe. Owner loves Americana and conversation pieces.",
        "blurt_specials": "Seasonal markdowns and clearance treasures.",
        "blurt_events": "Occasional outdoor flea market events (often shared on Facebook).",
        "about_excerpt": "A hidden gem known for vintage finds and unique Americana. It’s where Columbia’s collectors go to explore and reminisce.",
        "product_brands": ["Dixie Belle Paint", "Redesign with Prima"],
        "contact_info": {
            "phone": "(931) 381-8786",
            "address": "103 W 7th St, Columbia, TN 38401",
            "hours": "Mon–Sat 10am–5pm; Closed Sun"
        },
        "vibe_tags": ["vintage", "nostalgic", "quirky"],
        "last_scraped_note": "Operates via Facebook. No standalone site.",
        "needs_review": False,
        "update_last_known": "",
        "update_staleness_warning": None,
        "data_quality_score": 7,
        "update_estimate": "Last year"
    }
]

@app.route("/daisy", methods=["POST"])
def daisy_voice():
    speech_result = request.form.get("SpeechResult", "").lower()
    cleaned = re.sub(r"[^\w\s]", "", speech_result).strip().lower()
    response = VoiceResponse()

    if "store_match" in session:
        if cleaned in ["yes", "yeah", "yep"]:
            store = next((s for s in stores if s["store_name"].lower() == session["store_match"].lower()), None)
            if store:
                response.say(store["blurt_owner_style"], voice="Polly.Ivy")
                if store["blurt_specials"]:
                    response.say("Want to hear about specials or events?", voice="Polly.Ivy")
                session.pop("store_match")
                return Response(str(response), mimetype="text/xml")
            else:
                response.say("Sorry, I couldn't find that info anymore.", voice="Polly.Ivy")
        elif cleaned in ["no", "nope"]:
            session.pop("store_match")
            response.say("No worries, try saying the store name again.", voice="Polly.Ivy")
        else:
            response.say("I didn’t quite catch that. Was it yes or no?", voice="Polly.Ivy")
        gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
        gather.say("Please say yes or no.", voice="Polly.Ivy")
        response.append(gather)
        return Response(str(response), mimetype="text/xml")

    matches = difflib.get_close_matches(cleaned, [s["store_name"].lower() for s in stores], n=1, cutoff=0.6)
    if matches:
        match_name = matches[0]
        session["store_match"] = match_name
        response.say(f"Did you mean {match_name.title()}? Say yes or no.", voice="Polly.Ivy")
        gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
        gather.say("Say yes or no.", voice="Polly.Ivy")
        response.append(gather)
    else:
        response.say("I didn’t quite catch that. Is there a store I can help you find?", voice="Polly.Ivy")
        gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
        gather.say("Go ahead, I’m listenin’.", voice="Polly.Ivy")
        response.append(gather)

    return Response(str(response), mimetype="text/xml")
