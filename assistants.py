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
app.secret_key = os.urandom(24)
client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))

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
    },
{
    "store_name": "Muletown Coffee",
    "location": "Columbia, TN",
    "website": "https://muletowncoffee.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Coffee, espresso, roasted beans, breakfast pastries",
    "blurt_owner_style": "Hipster, communal, Nashville-adjacent creative energy.",
    "blurt_specials": "Seasonal drinks and locally-themed blends.",
    "blurt_events": "Live music some weekends; art displays rotate monthly.",
    "about_excerpt": "Beloved coffee hub in Columbia with small-town roots and big-city taste\u2014locally roasted beans and stylish merch.",
    "product_brands": [
      "Muletown Roasters",
      "KeepCup",
      "Rishi Tea"
    ],
    "contact_info": {
      "phone": "(931) 548\u20111991",
      "address": "1208 S Garden St, Columbia, TN 38401",
      "hours": "Daily 7\u202fam\u20135\u202fpm"
    },
    "vibe_tags": [
      "coffeehouse",
      "artsy",
      "youthful",
      "social"
    ],
    "last_scraped_note": "Frequently updated blog and menus\u2014great content presence.",
    "needs_review": false,
    "update_last_known": "2025-06-18",
    "update_staleness_warning": "",
    "data_quality_score": 10,
    "update_estimate": "Last week",
    "coverage_estimate": 6
  },
  {
    "store_name": "Tin Cottage",
    "location": "Columbia, TN",
    "website": "https://tincottage.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Boutique apparel, home accents, gifts, books",
    "blurt_owner_style": "Inspirational and heartfelt\u2014Christian messaging and Southern charm.",
    "blurt_specials": "Check social media for flash sales and giveaways.",
    "blurt_events": "Hosts pop-up vendor events, women\u2019s gatherings.",
    "about_excerpt": "A heartwarming shop full of meaning and flair\u2014greeting cards, candles, books, and sweet Southern apparel.",
    "product_brands": [
      "The Daily Grace Co",
      "Natural Life",
      "C.C. Beanies",
      "Local TN makers"
    ],
    "contact_info": {
      "phone": "(931) 548\u20118070",
      "address": "123 W 7th St, Columbia, TN 38401",
      "hours": "Mon\u2013Sat 10\u202fam\u20136\u202fpm"
    },
    "vibe_tags": [
      "faith-based",
      "uplifting",
      "giftable",
      "wholesome"
    ],
    "last_scraped_note": "Site is mobile-optimized and regularly features blog posts.",
    "needs_review": false,
    "update_last_known": "2025-06-18",
    "update_staleness_warning": "",
    "data_quality_score": 9,
    "update_estimate": "Last month",
    "coverage_estimate": 5
  },
 {
    "store_name": "Needle & Grain",
    "location": "Columbia, TN",
    "website": "https://www.needleandgrain.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Local goods, kitchenwares, baby items, eco-friendly",
    "blurt_owner_style": "Eco-chic with community values\u2014a feel-good, do-good shopping experience.",
    "blurt_specials": "First Friday discounts; email subscriber specials.",
    "blurt_events": "Community nights and crafting meetups.",
    "about_excerpt": "A sweet shop with sustainable soul\u2014perfect for thoughtful gifts and Tennessee-made goods.",
    "product_brands": [
      "Bee\u2019s Wrap",
      "Sierra Sage",
      "Bambino",
      "Green Toys",
      "TN Soaps & Sundries"
    ],
    "contact_info": {
      "phone": "(931) 548\u20116932",
      "address": "307 W 11th St, Columbia, TN 38401",
      "hours": "Tue\u2013Sat 10\u202fam\u20135\u202fpm"
    },
    "vibe_tags": [
      "eco",
      "family",
      "modern",
      "purpose-driven"
    ],
    "last_scraped_note": "Fresh product drops and good blog cadence.",
    "needs_review": false,
    "update_last_known": "2025-06-18",
    "update_staleness_warning": "",
    "data_quality_score": 9,
    "update_estimate": "Last month",
    "coverage_estimate": 5
  },
{
    "store_name": "Columbia Arts Building",
    "location": "Columbia, TN",
    "website": "https://www.columbiaartsbuilding.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Art studios, retail shops, local eats, creative spaces",
    "blurt_owner_style": "Eclectic and community-oriented. The CAB is a hub for creatives and entrepreneurs, with rotating exhibits and events.",
    "blurt_specials": "Varies by vendor—check their Instagram for current happenings.",
    "blurt_events": "Frequent First Friday events, open studios, and community art nights.",
    "about_excerpt": "A repurposed warehouse turned creative collective with a local twist. Home to makers, artists, and good eats.",
    "product_brands": ["Locally made art", "Craft snacks", "Hand-poured candles"],
    "contact_info": {
      "phone": "(931) 982-3915",
      "address": "307 W 11th St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; First Fridays open late"
    },
    "vibe_tags": ["creative", "local", "collaborative"],
    "last_scraped_note": "Regularly updated social media; website mostly static.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 8,
    "update_estimate": "This month"
  },
  {
    "store_name": "Buckhead Coffeehouse",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/BuckheadCoffeehouse/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Coffee, pastries, lunch bites, work-friendly space",
    "blurt_owner_style": "Classic neighborhood coffeehouse—laid-back and comfortable with strong brews and southern hospitality.",
    "blurt_specials": "Seasonal drinks and occasional sandwich combos.",
    "blurt_events": "Live music some weekends, advertised on-site or on Facebook.",
    "about_excerpt": "A cozy favorite for locals who need caffeine and a quiet nook. It’s your go-to for both catchups and catch-up work.",
    "product_brands": ["Bongo Java", "Local pastries"],
    "contact_info": {
      "phone": "(931) 490-0275",
      "address": "1175 Trotwood Ave, Columbia, TN 38401",
      "hours": "Mon–Sat 6:30am–5pm; Closed Sun"
    },
    "vibe_tags": ["chill", "neighborhood", "caffeinated"],
    "last_scraped_note": "Operates primarily through Facebook; regular posts and updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "This month"
  },
  {
    "store_name": "Red Seven",
    "location": "Columbia, TN",
    "website": "https://www.redsevenclothing.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Women’s apparel, accessories, boutique fashion",
    "blurt_owner_style": "Trendy and bold—run by fashion-forward locals with an eye for standout pieces.",
    "blurt_specials": "Seasonal lookbook releases and online-only markdowns.",
    "blurt_events": "Style drops often teased on Instagram stories.",
    "about_excerpt": "A local boutique offering handpicked fashion for women who want to stand out. Urban flair meets Southern style.",
    "product_brands": ["Z Supply", "Steve Madden", "Spanx", "Sadie & Sage"],
    "contact_info": {
      "phone": "(931) 548-8844",
      "address": "822 S Main St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5pm; Closed Sun"
    },
    "vibe_tags": ["bold", "trendy", "youthful"],
    "last_scraped_note": "Well-managed Shopify site with weekly updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
  {
    "store_name": "Puckett’s Columbia",
    "location": "Columbia, TN",
    "website": "https://puckettsrestaurant.com/columbia/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Southern cooking, live music, casual dining",
    "blurt_owner_style": "Classic Tennessee—soulful, friendly, and rooted in local tradition.",
    "blurt_specials": "Meat-and-three lunch specials and live music calendar.",
    "blurt_events": "Regular live performances, especially on weekends.",
    "about_excerpt": "Down-home eats in a rustic space with music and charm. Puckett’s is where Southern flavor and sound come together.",
    "product_brands": ["Puckett’s original sauces", "Yazoo Beer", "Tennessee craft brews"],
    "contact_info": {
      "phone": "(931) 490-4550",
      "address": "15 Public Square, Columbia, TN 38401",
      "hours": "Mon–Sun 7am–9pm"
    },
    "vibe_tags": ["southern", "lively", "comfort-food"],
    "last_scraped_note": "Polished site with reservation system and menu updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 10,
    "update_estimate": "This week"
  },
 {
    "store_name": "Baxter’s Mercantile",
    "location": "Columbia, TN",
    "website": "https://www.baxtersmercantile.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Gifts, decor, children’s items, Columbia-themed goods",
    "blurt_owner_style": "Wholesome and creative—family-run with a big heart for the community.",
    "blurt_specials": "Frequent gift bundles and seasonal showcases.",
    "blurt_events": "First Fridays and seasonal walkabouts downtown.",
    "about_excerpt": "An old-fashioned general store vibe with modern flair. Handpicked goods, Columbia pride, and friendly service.",
    "product_brands": ["Columbia TN merch", "Candleberry", "Melissa & Doug"],
    "contact_info": {
      "phone": "(931) 548-8002",
      "address": "808 S Main St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5pm; Sun 1–4pm"
    },
    "vibe_tags": ["family-friendly", "giftable", "small-town"],
    "last_scraped_note": "Website built on Wix with regular product refreshes.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 8,
    "update_estimate": "This month"
  },
  {
    "store_name": "Hattie Jane’s Creamery",
    "location": "Columbia, TN",
    "website": "https://hattiejanescreamery.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Small-batch ice cream, sorbet, seasonal flavors",
    "blurt_owner_style": "Modern nostalgia—cheerful and creative with Southern roots.",
    "blurt_specials": "Rotating monthly flavors and collabs with local bakeries.",
    "blurt_events": "Summer promo tie-ins with downtown events.",
    "about_excerpt": "Crafted with care and a bit of whimsy—this local scoop shop is a Columbia must for dessert lovers of all ages.",
    "product_brands": ["Hattie Jane’s Originals", "Muletown Roasted Espresso Chip"],
    "contact_info": {
      "phone": "(931) 505-8007",
      "address": "16 Public Square, Columbia, TN 38401",
      "hours": "Sun–Thu 12–9pm; Fri–Sat 12–10pm"
    },
    "vibe_tags": ["sweet", "colorful", "local-loved"],
    "last_scraped_note": "Bright Squarespace site with flavor calendar.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
 {
    "store_name": "Southern Exposure",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/SouthernExposureColumbiaTN",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Home goods, southern decor, gifts",
    "blurt_owner_style": "Classic and refined Southern taste—clean displays and upscale giftables.",
    "blurt_specials": "Rotating seasonal markdowns.",
    "blurt_events": "Occasional sidewalk sales and Main Street events.",
    "about_excerpt": "A well-curated gift and decor boutique with a polished, traditional aesthetic. Great for hostess gifts and Southern hospitality touches.",
    "product_brands": ["Mud Pie", "Thymes", "Swan Creek Candle Co."],
    "contact_info": {
      "phone": "(931) 548-8161",
      "address": "812 S Main St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5pm"
    },
    "vibe_tags": ["southern", "refined", "classic"],
    "last_scraped_note": "No website—relies on Facebook for updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "Last year"
  },
  {
    "store_name": "Revival Home",
    "location": "Columbia, TN",
    "website": "https://revivalhomecolumbia.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$$",
    "blurt_categories": "Luxury home decor, furniture, lighting",
    "blurt_owner_style": "Elevated design sensibility—sophisticated, neutral palette, designer-led.",
    "blurt_specials": "Occasional clearance and showroom samples.",
    "blurt_events": "Interior design workshops and open house previews.",
    "about_excerpt": "A luxe furniture and home aesthetic store known for impeccable taste and full-service design offerings.",
    "product_brands": ["Visual Comfort", "Jamie Young", "Cisco Home"],
    "contact_info": {
      "phone": "(931) 548-8282",
      "address": "810 S Main St, Columbia, TN 38401",
      "hours": "Tue–Sat 10am–4pm; Closed Sun–Mon"
    },
    "vibe_tags": ["luxury", "designer", "modern farmhouse"],
    "last_scraped_note": "Sleek Shopify site with limited product listings.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 8,
    "update_estimate": "This month"
  },
{
    "store_name": "Heart and Hands",
    "location": "Columbia, TN",
    "website": "https://www.heartandhandsinc.org/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Gifts, handmade goods, community-focused items",
    "blurt_owner_style": "Mission-driven and warm—handcrafted and fair-trade goods in a cozy, welcoming space.",
    "blurt_specials": "Ongoing promotions supporting local causes.",
    "blurt_events": "Community art shows and seasonal charity drives.",
    "about_excerpt": "A nonprofit gift shop offering meaningful items made by local and global artisans, with proceeds going back into the community.",
    "product_brands": ["Ten Thousand Villages", "Local Makers"],
    "contact_info": {
      "phone": "(931) 381-7575",
      "address": "407 W 9th St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–4pm"
    },
    "vibe_tags": ["handmade", "mission", "cozy"],
    "last_scraped_note": "Basic site—limited eCommerce presence.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "This year"
  },
  {
    "store_name": "Southern Tre' Fleur",
    "location": "Columbia, TN",
    "website": "https://southerntrefleur.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Florals, event décor, gifts",
    "blurt_owner_style": "Floral-forward with a whimsical southern charm. Big on events and visual flair.",
    "blurt_specials": "Wedding packages and occasional flash sales.",
    "blurt_events": "Flower-arranging workshops and bridal events.",
    "about_excerpt": "A boutique floral and event design studio offering elegant arrangements and curated gifts—perfect for weddings or last-minute surprises.",
    "product_brands": ["Capri Blue", "Mud Pie", "Thymes"],
    "contact_info": {
      "phone": "(931) 626-3504",
      "address": "715 S Main St, Columbia, TN 38401",
      "hours": "Tue–Fri 10am–5pm; Sat 10am–2pm"
    },
    "vibe_tags": ["floral", "feminine", "celebratory"],
    "last_scraped_note": "Elegant, mobile-friendly Squarespace site.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
 {
    "store_name": "The Linen Duck",
    "location": "Columbia, TN",
    "website": "https://thelinenduck.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$$",
    "blurt_categories": "Interior design, upscale home furnishings, boutique gifts",
    "blurt_owner_style": "Sophisticated and design-forward—think southern glam with polished elegance.",
    "blurt_specials": "Occasional trunk shows and seasonal floor model discounts.",
    "blurt_events": "Design workshops and sip-and-shop nights.",
    "about_excerpt": "A chic home design boutique offering curated furniture, accents, and décor with full interior styling services.",
    "product_brands": ["Dash & Albert", "Vietri", "Gabby Home", "Noonday Collection"],
    "contact_info": {
      "phone": "(931) 548-2422",
      "address": "119 E 6th St, Columbia, TN 38401",
      "hours": "Tue–Sat 10am–5pm"
    },
    "vibe_tags": ["elegant", "upscale", "design"],
    "last_scraped_note": "Polished Squarespace site with seasonal updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
 {
    "store_name": "Bain & Sloan",
    "location": "Columbia, TN",
    "website": "https://bainandsloan.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Boutique fashion, accessories, lifestyle goods",
    "blurt_owner_style": "Trendy with a touch of Nashville glam—effortlessly stylish and always on point.",
    "blurt_specials": "Frequent sales in the 'Deals' section online and seasonal markdowns in-store.",
    "blurt_events": "Sip & shop events and occasional pop-up collabs with other local brands.",
    "about_excerpt": "A women’s boutique with an eye for trendsetting styles and must-have accessories, often updated with new drops.",
    "product_brands": ["Spanx", "Kendra Scott", "Quay Australia", "Steve Madden"],
    "contact_info": {
      "phone": "(931) 548-2011",
      "address": "413 W 7th St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; Sun Closed"
    },
    "vibe_tags": ["fashion-forward", "boutique", "trendy"],
    "last_scraped_note": "Vibrant website and active Instagram presence—frequent style updates.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
  {
    "store_name": "Southern Exposure",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/SouthernExposureGifts/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Gifts, home décor, seasonal items, kitchen goods",
    "blurt_owner_style": "Classic and community-oriented—like your favorite neighbor who always finds the perfect gift.",
    "blurt_specials": "Seasonal clearance and themed gift sets around holidays.",
    "blurt_events": "Holiday open houses and gift-giving demos.",
    "about_excerpt": "A longstanding gift shop offering thoughtful items for any occasion, with rotating seasonal selections.",
    "product_brands": ["Tyler Candle Company", "Mud Pie", "Southern Jubilee"],
    "contact_info": {
      "phone": "(931) 388-9019",
      "address": "1120 Riverside Dr, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5:30pm"
    },
    "vibe_tags": ["classic", "friendly", "gift‑ready"],
    "last_scraped_note": "Facebook-driven updates; no standalone website.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 8,
    "update_estimate": "Last month"
  },
 "store_name": "Hummingbird Cottage",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/HummingbirdCottageColumbia/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Home decor, antiques, handmade gifts, seasonal items",
    "blurt_owner_style": "Whimsical and heartfelt, full of southern charm and handmade touches.",
    "blurt_specials": "Seasonal floral wreaths and clearance décor bins.",
    "blurt_events": "Small holiday-themed events and DIY decor workshops.",
    "about_excerpt": "A sweet little cottage-style shop filled with rustic treasures and gifts made with love.",
    "product_brands": ["local artisans", "vintage finds", "handmade crafts"],
    "contact_info": {
      "phone": "(931) 381-0255",
      "address": "215 W 7th St, Columbia, TN 38401",
      "hours": "Wed–Sat 10am–5pm; Sun–Tue Closed"
    },
    "vibe_tags": ["rustic", "handmade", "heartfelt"],
    "last_scraped_note": "Runs entirely through Facebook, often with posted photos of new arrivals.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "Last year"
  },
  {
    "store_name": "Vintage Winery & Marketplace",
    "location": "Columbia, TN",
    "website": "https://www.vintagewinerytn.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Wine, boutique items, gifts, apparel, tastings",
    "blurt_owner_style": "Upscale yet friendly—a relaxing escape with a refined Tennessee touch.",
    "blurt_specials": "Tasting flights and seasonal boutique deals.",
    "blurt_events": "Live music weekends and wine pairing nights.",
    "about_excerpt": "Part wine bar, part boutique—perfect for sipping, shopping, and spending an easy afternoon.",
    "product_brands": ["local Tennessee wines", "boutique fashion", "artisan foods"],
    "contact_info": {
      "phone": "(931) 548-2800",
      "address": "119 W 7th St, Columbia, TN 38401",
      "hours": "Wed–Sat 12pm–8pm; Sun 1–5pm; Closed Mon–Tue"
    },
    "vibe_tags": ["refined", "leisurely", "elegant"],
    "last_scraped_note": "Modern website with events calendar and boutique highlights.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
 {
    "store_name": "Columbia Health Foods",
    "location": "Columbia, TN",
    "website": "https://www.columbiahealthfoods.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Supplements, organic groceries, smoothies, natural remedies",
    "blurt_owner_style": "Holistic and helpful—deep knowledge with a passion for wellness.",
    "blurt_specials": "Smoothie punch card and monthly supplement sales.",
    "blurt_events": "Occasional health seminars and essential oil classes.",
    "about_excerpt": "A full-service health food store with a cozy café and knowledgeable staff who live and breathe wellness.",
    "product_brands": ["Garden of Life", "NOW Foods", "New Chapter"],
    "contact_info": {
      "phone": "(931) 388-1148",
      "address": "1701 Shady Brook St, Columbia, TN 38401",
      "hours": "Mon–Fri 9am–6pm; Sat 9am–5pm; Closed Sun"
    },
    "vibe_tags": ["healthy", "local", "organic"],
    "last_scraped_note": "Site is regularly updated with menu and health blog.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
  {
    "store_name": "Southern Exposure",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/southernexposuretn/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Furniture, decor, rugs, lighting, interior design",
    "blurt_owner_style": "Polished and sophisticated—high-end southern style with personalized service.",
    "blurt_specials": "Rotating showroom discounts and rug clearance.",
    "blurt_events": "Occasional trunk shows and design nights.",
    "about_excerpt": "An upscale home design showroom blending classic charm and current trends with expert guidance.",
    "product_brands": ["Loloi Rugs", "Hooker Furniture", "Visual Comfort"],
    "contact_info": {
      "phone": "(931) 548-2125",
      "address": "39 Public Square, Columbia, TN 38401",
      "hours": "Mon–Fri 10am–5pm; Sat 10am–4pm; Closed Sun"
    },
    "vibe_tags": ["upscale", "southern", "designer"],
    "last_scraped_note": "Active Facebook page with photos of new showroom pieces.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 8,
    "update_estimate": "This month"
  }, {
    "store_name": "The Linen Duck",
    "location": "Columbia, TN",
    "website": "https://thelinenduck.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Home furnishings, designer furniture, decor, boutique clothing",
    "blurt_owner_style": "Upscale but friendly, design-forward with a touch of European flair—clearly run by someone with an eye for interiors.",
    "blurt_specials": "Design consultations and seasonal sales (especially on floor models).",
    "blurt_events": "Occasional pop-ups and in-store art shows.",
    "about_excerpt": "An interior design studio and boutique offering refined pieces and curated aesthetics. Columbia’s go-to for design-minded home upgrades.",
    "product_brands": ["LAFCO", "Norwalk Furniture", "Sid Dickens", "Local Artisans"],
    "contact_info": {
      "phone": "(931) 548-2422",
      "address": "104 W 6th St, Columbia, TN 38401",
      "hours": "Tue–Fri 10am–5pm; Sat 10am–4pm; Closed Sun–Mon"
    },
    "vibe_tags": ["refined", "elegant", "design-focused"],
    "last_scraped_note": "Full site with ecommerce and portfolio. Updated events and project gallery.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
  {
    "store_name": "Hearts & Hugs",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/HeartsHugsGifts",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Christian gifts, books, home decor, baby items, seasonal decor",
    "blurt_owner_style": "Sweet and nurturing, very faith-forward and encouraging. It’s like walking into a warm hug.",
    "blurt_specials": "Holiday-themed discounts and clearance bins.",
    "blurt_events": "Occasional book signings and women’s ministry nights.",
    "about_excerpt": "A heartfelt gift shop with spiritual inspiration and thoughtful treasures. Known for kindness and seasonal charm.",
    "product_brands": ["Dayspring", "Willow Tree", "Mud Pie", "Natural Life"],
    "contact_info": {
      "phone": "(931) 388-1810",
      "address": "1202 S James Campbell Blvd, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; Closed Sun"
    },
    "vibe_tags": ["inspirational", "faithful", "uplifting"],
    "last_scraped_note": "Operates via Facebook. Posts weekly. No standalone website.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "Last month"
  },
 {
    "store_name": "Blue 32",
    "location": "Columbia, TN",
    "website": "https://blue32vintage.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Vintage sports apparel, antiques, memorabilia, gifts",
    "blurt_owner_style": "Playful and nostalgic. Feels like a locker room turned antique mall with flair.",
    "blurt_specials": "Flash sales on Instagram and seasonal markdowns.",
    "blurt_events": "Game day promos and themed sales around sports seasons.",
    "about_excerpt": "A fun, sporty vintage and antique store with a unique blend of sports nostalgia and classic Americana collectibles.",
    "product_brands": ["Starter", "Vintage Nike", "Rawlings", "Handpicked Vintage"],
    "contact_info": {
      "phone": "(931) 548-1528",
      "address": "110 W 7th St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; Closed Sun"
    },
    "vibe_tags": ["sports", "nostalgic", "playful"],
    "last_scraped_note": "Stylish website. Active on socials. Sports-heavy aesthetic.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
  {
    "store_name": "Baxter’s Mercantile",
    "location": "Columbia, TN",
    "website": "https://www.facebook.com/baxtersmercantile",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Local goods, home decor, gifts, southern lifestyle items",
    "blurt_owner_style": "Friendly and neighborly with a splash of Southern pride—definitely the kind of shop where they know your name.",
    "blurt_specials": "Rotating local vendor features and seasonal decor discounts.",
    "blurt_events": "Occasional downtown Columbia sidewalk sales.",
    "about_excerpt": "A welcoming shop downtown with a mix of Tennessee-made gifts and cozy Southern decor. Great for browsing with a sweet tea in hand.",
    "product_brands": ["Southern Fried Design", "Farmhouse Fresh", "Locally Sourced Artisans"],
    "contact_info": {
      "phone": "(931) 548-8733",
      "address": "119 W 7th St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5pm; Closed Sun"
    },
    "vibe_tags": ["local", "southern", "friendly"],
    "last_scraped_note": "Facebook-based with occasional event posts. No full e-commerce.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "Last month"
  },
 {
    "store_name": "Sage Sleep Columbia",
    "location": "Columbia, TN",
    "website": "https://sagesleeporganics.com",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$$",
    "blurt_categories": "Organic mattresses, natural bedding, sleep accessories",
    "blurt_owner_style": "Minimalist, wellness-focused, and high-end. A calm, informed vibe from a passionate sleep advocate.",
    "blurt_specials": "Holiday promos and mattress bundle savings.",
    "blurt_events": "Wellness-themed events and sleep education sessions.",
    "about_excerpt": "A boutique sleep showroom specializing in all-natural, organic mattresses and accessories. A serene space for rest and recovery.",
    "product_brands": ["Savvy Rest", "Naturepedic", "Sleep Artisan"],
    "contact_info": {
      "phone": "(931) 548-0033",
      "address": "500 N Garden St, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–5pm; Closed Sun"
    },
    "vibe_tags": ["organic", "wellness", "minimalist"],
    "last_scraped_note": "Updated website and strong wellness positioning. Clean aesthetic.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
 {
    "store_name": "Duck River Books",
    "location": "Columbia, TN",
    "website": "https://www.duckriverbooks.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "New and used books, rare finds, author events, literary gifts",
    "blurt_owner_style": "Literary and community-minded with a touch of old-world charm.",
    "blurt_specials": "Frequent used book sales and author meet-and-greets.",
    "blurt_events": "Book signings and local author showcases throughout the year.",
    "about_excerpt": "A cozy independent bookstore with deep roots in the Columbia literary scene. Known for its friendly staff, community feel, and eclectic selection.",
    "product_brands": ["Penguin", "HarperCollins", "Local authors"],
    "contact_info": {
      "phone": "(931) 548-2665",
      "address": "12 Public Sq, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; Closed Sun"
    },
    "vibe_tags": ["literary", "cozy", "local"],
    "last_scraped_note": "Actively updated website with event listings and online store.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
  {
    "store_name": "Bev & Bash",
    "location": "Columbia, TN",
    "website": "https://www.bevandbash.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Women’s boutique, fashion, accessories, gift items",
    "blurt_owner_style": "Trendy, feminine, and confident. Curated with bold style in mind.",
    "blurt_specials": "Seasonal collections and clearance racks in-store.",
    "blurt_events": "Occasional launch parties and sip & shop nights.",
    "about_excerpt": "A fashionable boutique known for empowering styles and bold color. A local favorite for girls’ days and gift shopping.",
    "product_brands": ["Z Supply", "Capri Blue", "ABLE"],
    "contact_info": {
      "phone": "(931) 548-8008",
      "address": "46 Public Sq, Columbia, TN 38401",
      "hours": "Mon–Sat 10am–6pm; Sun 1–4pm"
    },
    "vibe_tags": ["fashion", "bold", "girlfriend‑approved"],
    "last_scraped_note": "Modern site with easy navigation and online ordering.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 10,
    "update_estimate": "This month"
  },
 {
    "store_name": "Parks Motor Sales",
    "location": "Columbia, TN",
    "website": "https://www.parksmotorsales.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$$",
    "blurt_categories": "Ford and Lincoln dealership, used vehicles, service center",
    "blurt_owner_style": "Professional and trustworthy, rooted in local service since 1958.",
    "blurt_specials": "Rotating new vehicle incentives and certified pre-owned offers.",
    "blurt_events": "Holiday sales and Ford-sponsored promotions.",
    "about_excerpt": "Trusted auto dealership offering a wide selection of new and used vehicles along with a highly rated service department.",
    "product_brands": ["Ford", "Lincoln", "Certified Pre-Owned"],
    "contact_info": {
      "phone": "(931) 388-2463",
      "address": "919 Nashville Hwy, Columbia, TN 38401",
      "hours": "Mon–Fri 8am–6pm; Sat 8am–5pm; Closed Sun"
    },
    "vibe_tags": ["reliable", "automotive", "local legacy"],
    "last_scraped_note": "Professional, up-to-date website with service scheduling and inventory tools.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This week"
  },
{
    "store_name": "Vintage 615",
    "location": "Spring Hill, TN",
    "website": "https://www.vintage615.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$$",
    "blurt_categories": "Gifts, boutique apparel, home decor, local goods",
    "blurt_owner_style": "Trendy and cheerful with a heart for local makers and Tennessee pride.",
    "blurt_specials": "Seasonal gift bundles and local artisan pop-ups.",
    "blurt_events": "First Friday events and community shopping nights.",
    "about_excerpt": "A boutique gift and lifestyle shop packed with stylish finds, TN-themed goods, and handmade treasures.",
    "product_brands": ["Corkcicle", "Simply Southern", "Swan Creek Candle"],
    "contact_info": {
      "phone": "(931) 451-5371",
      "address": "5075 Main St, Spring Hill, TN 37174",
      "hours": "Mon–Sat 10am–6pm; Sun Closed"
    },
    "vibe_tags": ["trendy", "local", "gift-ready"],
    "last_scraped_note": "Well-designed site with regular content updates and online store.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 9,
    "update_estimate": "This month"
  },
  {
    "store_name": "A Balloon Shop",
    "location": "Columbia, TN",
    "website": "https://aballoonshop.com/",
    "last_reviewed": "2025-06-18",
    "price_range": "$$",
    "blurt_categories": "Balloon arrangements, event decor, party supplies",
    "blurt_owner_style": "Festive and colorful, with a love for celebration and whimsy.",
    "blurt_specials": "Custom balloon arches and seasonal color palettes.",
    "blurt_events": "Event rentals and decor setup services.",
    "about_excerpt": "A charming shop specializing in all things balloon—ideal for parties, showers, and grand openings.",
    "product_brands": ["Qualatex", "Betallic", "Anagram"],
    "contact_info": {
      "phone": "(615) 390-0403",
      "address": "713 S Main St, Columbia, TN 38401",
      "hours": "By appointment or online order"
    },
    "vibe_tags": ["festive", "creative", "celebration"],
    "last_scraped_note": "Minimalist website with gallery, booking info, and contact form.",
    "needs_review": false,
    "update_last_known": "",
    "update_staleness_warning": null,
    "data_quality_score": 7,
    "update_estimate": "Last month"
  }
]

@app.route("/daisy", methods=["POST"])
def daisy_voice():
    speech_result = request.form.get("SpeechResult", "").lower()
    cleaned = re.sub(r"[^\w\s]", "", speech_result).strip().lower()
    response = VoiceResponse()

    if "store_match" in session and "store_confirmed" not in session:
        if cleaned in ["yes", "yeah", "yep"]:
            session["store_confirmed"] = True
            store = next((s for s in stores if s["store_name"].lower() == session["store_match"].lower()), None)
            if store:
                session["store_data"] = store
                response.say(store["blurt_owner_style"], voice="Polly.Ivy")
                response.say("Want to hear about specials, events, categories, brands, or store hours?", voice="Polly.Ivy")
                gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
                gather.say("Go ahead, I’m listenin’.", voice="Polly.Ivy")
                response.append(gather)
                return Response(str(response), mimetype="text/xml")
        elif cleaned in ["no", "nope"]:
            session.pop("store_match")
            response.say("No worries, try saying the store name again.", voice="Polly.Ivy")
        else:
            response.say("I didn’t quite catch that. Was it yes or no?", voice="Polly.Ivy")
            gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
            gather.say("Please say yes or no.", voice="Polly.Ivy")
            response.append(gather)
        return Response(str(response), mimetype="text/xml")

    if "store_confirmed" in session and "store_data" in session:
        store = session["store_data"]
        if "special" in cleaned:
            response.say(store["blurt_specials"], voice="Polly.Ivy")
        elif "event" in cleaned:
            response.say(store["blurt_events"], voice="Polly.Ivy")
        elif "brand" in cleaned:
            response.say(", ".join(store["product_brands"]), voice="Polly.Ivy")
        elif "categorie" in cleaned or "product" in cleaned:
            response.say(store["blurt_categories"], voice="Polly.Ivy")
        elif "hour" in cleaned or "open" in cleaned:
            response.say(f"Here are the store hours: {store['contact_info']['hours']}", voice="Polly.Ivy")
        else:
            response.say("Hmm, I’m not sure what you meant. Try asking about specials, events, brands, or hours.", voice="Polly.Ivy")

        gather = Gather(input="speech", timeout=5, action="/daisy", method="POST")
        gather.say("Is there anything else you’d like to know?", voice="Polly.Ivy")
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
