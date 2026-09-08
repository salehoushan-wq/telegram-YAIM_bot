import logging
import asyncio
from pathlib import Path
import aiohttp
import unicodedata
import re
import os
import json
import html
from PIL import Image, ImageDraw, ImageFont
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ====================== تفعيل التسجيل ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# ====================== 1. المودات (MoDs) ======================
MODS = {
    "جميع المودات": [
            {"num": "1️⃣", "name": "مود السيف الناري", "icon": "🔥", "link": "https://mcpedl.com/?s=fire+sword"},
    {"num": "2️⃣", "name": "مود البندقية", "icon": "🔫", "link": "https://mcpedl.com/?s=gun+mod"},
    {"num": "3️⃣", "name": "مود درع التنين", "icon": "🐉", "link": "https://mcpedl.com/?s=dragon+armor"},
    {"num": "4️⃣", "name": "مود السيف الماسي العملاق", "icon": "💎", "link": "https://mcpedl.com/?s=giant+diamond+sword"},
    {"num": "5️⃣", "name": "مود الأسلحة النووية", "icon": "☢️", "link": "https://mcpedl.com/?s=nuclear+weapon"},
    {"num": "6️⃣", "name": "مود القوس الخارق", "icon": "🏹", "link": "https://mcpedl.com/?s=super+bow"},
    {"num": "7️⃣", "name": "مود درع البطل", "icon": "🛡️", "link": "https://mcpedl.com/?s=hero+armor"},
    {"num": "8️⃣", "name": "مود مسدس الليزر", "icon": "⚡", "link": "https://mcpedl.com/?s=laser+gun"},
    {"num": "9️⃣", "name": "مود سيف الطاقم", "icon": "🗡️", "link": "https://mcpedl.com/?s=crew+sword"},
    {"num": "🔟", "name": "مود فأس المعركة", "icon": "🪓", "link": "https://mcpedl.com/?s=battle+axe"},
    {"num": "1️⃣1️⃣", "name": "مود الرمح", "icon": "🔱", "link": "https://mcpedl.com/?s=spear"},
    {"num": "1️⃣2️⃣", "name": "مود كرة الطاقة", "icon": "🔮", "link": "https://mcpedl.com/?s=energy+ball"},
    {"num": "1️⃣3️⃣", "name": "مود البندقية القناصة", "icon": "🎯", "link": "https://mcpedl.com/?s=sniper+rifle"},
    {"num": "1️⃣4️⃣", "name": "مود القفازات الخارقة", "icon": "🧤", "link": "https://mcpedl.com/?s=super+gloves"},

    # === سيارات ومركبات ===
    {"num": "1️⃣5️⃣", "name": "مود السيارات الرياضية", "icon": "🏎️", "link": "https://mcpedl.com/?s=sports+car"},
    {"num": "1️⃣6️⃣", "name": "مود طائرات الهليكوبتر", "icon": "🚁", "link": "https://mcpedl.com/?s=helicopter"},
    {"num": "1️⃣7️⃣", "name": "مود الشاحنات", "icon": "🚚", "link": "https://mcpedl.com/?s=truck"},
    {"num": "1️⃣8️⃣", "name": "مود الطائرات الحربية", "icon": "✈️", "link": "https://mcpedl.com/?s=war+plane"},
    {"num": "1️⃣9️⃣", "name": "مود القطار", "icon": "🚂", "link": "https://mcpedl.com/?s=train"},
    {"num": "2️⃣0️⃣", "name": "مود الغواصة", "icon": "🚢", "link": "https://mcpedl.com/?s=submarine"},
    {"num": "2️⃣1️⃣", "name": "مود الدراجات النارية", "icon": "🏍️", "link": "https://mcpedl.com/?s=motorcycle"},
    {"num": "2️⃣2️⃣", "name": "مود الجيب العسكري", "icon": "🪖", "link": "https://mcpedl.com/?s=jeep"},
    {"num": "2️⃣3️⃣", "name": "مود الدبابة", "icon": "🛡️", "link": "https://mcpedl.com/?s=tank"},
    {"num": "2️⃣4️⃣", "name": "مود الصاروخ", "icon": "🚀", "link": "https://mcpedl.com/?s=rocket"},

    # === حيوانات ومخلوقات ===
    {"num": "2️⃣5️⃣", "name": "مود التنانين", "icon": "🐲", "link": "https://mcpedl.com/?s=dragon"},
    {"num": "2️⃣6️⃣", "name": "مود الديناصورات", "icon": "🦖", "link": "https://mcpedl.com/?s=dinosaur"},
    {"num": "2️⃣7️⃣", "name": "مود الحيوانات الأليفة", "icon": "🐕", "link": "https://mcpedl.com/?s=pet+mod"},
    {"num": "2️⃣8️⃣", "name": "مود القطط الكبيرة", "icon": "🐆", "link": "https://mcpedl.com/?s=big+cat"},
    {"num": "2️⃣9️⃣", "name": "مود الخفافيش", "icon": "🦇", "link": "https://mcpedl.com/?s=bats"},
    {"num": "3️⃣0️⃣", "name": "مود الذئاب المتوحشة", "icon": "🐺", "link": "https://mcpedl.com/?s=wolf"},
    {"num": "3️⃣1️⃣", "name": "مود البوكيمون", "icon": "⚡", "link": "https://mcpedl.com/?s=pokemon"},
    {"num": "3️⃣2️⃣", "name": "مود الزومبي", "icon": "🧟", "link": "https://mcpedl.com/?s=zombie"},
    {"num": "3️⃣3️⃣", "name": "مود العناكب", "icon": "🕷️", "link": "https://mcpedl.com/?s=spider"},
    {"num": "3️⃣4️⃣", "name": "مود السمك العملاق", "icon": "🐋", "link": "https://mcpedl.com/?s=giant+fish"},
    {"num": "3️⃣5️⃣", "name": "مود الطيور", "icon": "🦅", "link": "https://mcpedl.com/?s=bird"},
    {"num": "3️⃣6️⃣", "name": "مود القرد", "icon": "🐒", "link": "https://mcpedl.com/?s=monkey"},
    {"num": "3️⃣7️⃣", "name": "مود الأخطبوط", "icon": "🐙", "link": "https://mcpedl.com/?s=octopus"},
    {"num": "3️⃣8️⃣", "name": "مود الماموث", "icon": "🐘", "link": "https://mcpedl.com/?s=mammoth"},
    {"num": "3️⃣9️⃣", "name": "مود وحيد القرن", "icon": "🦏", "link": "https://mcpedl.com/?s=rhino"},
    {"num": "4️⃣0️⃣", "name": "مود الفهد", "icon": "🐆", "link": "https://mcpedl.com/?s=cheetah"},

    # === أثاث وبناء ===
    {"num": "4️⃣1️⃣", "name": "مود الأثاث المنزلي", "icon": "🛋️", "link": "https://mcpedl.com/?s=furniture"},
    {"num": "4️⃣2️⃣", "name": "مود المطبخ", "icon": "🍳", "link": "https://mcpedl.com/?s=kitchen"},
    {"num": "4️⃣3️⃣", "name": "مود الحمام", "icon": "🚿", "link": "https://mcpedl.com/?s=bathroom"},
    {"num": "4️⃣4️⃣", "name": "مود الأدوات الذكية", "icon": "🔌", "link": "https://mcpedl.com/?s=smart+tools"},
    {"num": "4️⃣5️⃣", "name": "مود الإضاءة", "icon": "💡", "link": "https://mcpedl.com/?s=lighting"},
    {"num": "4️⃣6️⃣", "name": "مود الأبواب", "icon": "🚪", "link": "https://mcpedl.com/?s=door"},
    {"num": "4️⃣7️⃣", "name": "مود السلالم", "icon": "🪜", "link": "https://mcpedl.com/?s=stairs"},
    {"num": "4️⃣8️⃣", "name": "مود الجسور المتحركة", "icon": "🌉", "link": "https://mcpedl.com/?s=bridge"},
    {"num": "4️⃣9️⃣", "name": "مود السيارات في البناء", "icon": "🚧", "link": "https://mcpedl.com/?s=construction"},
    {"num": "5️⃣0️⃣", "name": "مود الأسلاك الكهربائية", "icon": "⚡", "link": "https://mcpedl.com/?s=wire"},
    {"num": "5️⃣1️⃣", "name": "مود المولدات", "icon": "⚙️", "link": "https://mcpedl.com/?s=generator"},
    {"num": "5️⃣2️⃣", "name": "مود الآلات الموسيقية", "icon": "🎵", "link": "https://mcpedl.com/?s=music"},
    {"num": "5️⃣3️⃣", "name": "مود التلفاز", "icon": "📺", "link": "https://mcpedl.com/?s=tv"},
    {"num": "5️⃣4️⃣", "name": "مود أجهزة الكمبيوتر", "icon": "💻", "link": "https://mcpedl.com/?s=computer"},
    {"num": "5️⃣5️⃣", "name": "مود الثلاجة", "icon": "🧊", "link": "https://mcpedl.com/?s=fridge"},
    {"num": "5️⃣6️⃣", "name": "مود الحديقة", "icon": "🌷", "link": "https://mcpedl.com/?s=garden"},
    {"num": "5️⃣7️⃣", "name": "مود الزجاج الملون", "icon": "🪟", "link": "https://mcpedl.com/?s=glass"},
    {"num": "5️⃣8️⃣", "name": "مود السجاد", "icon": "🟥", "link": "https://mcpedl.com/?s=carpet"},

    # === أنيمي، أكشن، وعوالم ===
    {"num": "5️⃣9️⃣", "name": "مود ناروتو", "icon": "🍥", "link": "https://mcpedl.com/?s=naruto"},
    {"num": "6️⃣0️⃣", "name": "مود ون بيس", "icon": "🏴‍☠️", "link": "https://mcpedl.com/?s=one+piece"},
    {"num": "6️⃣1️⃣", "name": "مود هجوم العمالقة", "icon": "🗡️", "link": "https://mcpedl.com/?s=aot"},
    {"num": "6️⃣2️⃣", "name": "مود سبايدرمان", "icon": "🕸️", "link": "https://mcpedl.com/?s=spiderman"},
    {"num": "6️⃣3️⃣", "name": "مود باور رينجرز", "icon": "🎭", "link": "https://mcpedl.com/?s=power+rangers"},
    {"num": "6️⃣4️⃣", "name": "مود هالو كيل", "icon": "🎮", "link": "https://mcpedl.com/?s=halo"},
    {"num": "6️⃣5️⃣", "name": "مود مصارعين السومو", "icon": "🥋", "link": "https://mcpedl.com/?s=sumo"},
    {"num": "6️⃣6️⃣", "name": "مود أبطال الديجيتال", "icon": "🐣", "link": "https://mcpedl.com/?s=digimon"},
    {"num": "6️⃣7️⃣", "name": "مود إله الحرب", "icon": "⚔️", "link": "https://mcpedl.com/?s=god+of+war"},
    {"num": "6️⃣8️⃣", "name": "مود آسورا", "icon": "👊", "link": "https://mcpedl.com/?s=asura"},

    # === أدوات وقدرات خاصة ===
    {"num": "6️⃣9️⃣", "name": "مود الواي بوينت", "icon": "📍", "link": "https://mcpedl.com/waypoints-mod/"},
    {"num": "7️⃣0️⃣", "name": "مود الجلسة على أي شيء", "icon": "🪑", "link": "https://mcpedl.com/sit-anywhere-mod/"},
    {"num": "7️⃣1️⃣", "name": "مود الطيران", "icon": "🕊️", "link": "https://mcpedl.com/?s=fly"},
    {"num": "7️⃣2️⃣", "name": "مود السرعة الخارقة", "icon": "⚡", "link": "https://mcpedl.com/?s=speed"},
    {"num": "7️⃣3️⃣", "name": "مود القفز العالي", "icon": "🐇", "link": "https://mcpedl.com/?s=high+jump"},
    {"num": "7️⃣4️⃣", "name": "مود الزمن", "icon": "⏳", "link": "https://mcpedl.com/?s=time"},
    {"num": "7️⃣5️⃣", "name": "مود الزلازل", "icon": "🌋", "link": "https://mcpedl.com/?s=earthquake"},
    {"num": "7️⃣6️⃣", "name": "مود البراكين", "icon": "🌋", "link": "https://mcpedl.com/?s=volcano"},
    {"num": "7️⃣7️⃣", "name": "مود الإعصار", "icon": "🌪️", "link": "https://mcpedl.com/?s=tornado"},
    {"num": "7️⃣8️⃣", "name": "مود المطر الحمضي", "icon": "☠️", "link": "https://mcpedl.com/?s=acid+rain"},
    {"num": "7️⃣9️⃣", "name": "مود النجوم", "icon": "⭐", "link": "https://mcpedl.com/?s=stars"},
    {"num": "8️⃣0️⃣", "name": "مود القمر", "icon": "🌙", "link": "https://mcpedl.com/?s=moon"},

    # === مودات البقاء والمغامرات ===
    {"num": "8️⃣1️⃣", "name": "مود الفصول الأربعة", "icon": "🌦️", "link": "https://mcpedl.com/seasons-mod/"},
    {"num": "8️⃣2️⃣", "name": "مود الشتاء", "icon": "❄️", "link": "https://mcpedl.com/?s=winter"},
    {"num": "8️⃣3️⃣", "name": "مود الصيف", "icon": "☀️", "link": "https://mcpedl.com/?s=summer"},
    {"num": "8️⃣4️⃣", "name": "مود الخريف", "icon": "🍂", "link": "https://mcpedl.com/?s=autumn"},
    {"num": "8️⃣5️⃣", "name": "مود الصحراء", "icon": "🏜️", "link": "https://mcpedl.com/?s=desert"},
    {"num": "8️⃣6️⃣", "name": "مود الجنة", "icon": "😇", "link": "https://mcpedl.com/?s=heaven"},
    {"num": "8️⃣7️⃣", "name": "مود الجحيم", "icon": "😈", "link": "https://mcpedl.com/?s=hell"},
    {"num": "8️⃣8️⃣", "name": "مود رحلة إلى الفضاء", "icon": "🪐", "link": "https://mcpedl.com/?s=space"},
    {"num": "8️⃣9️⃣", "name": "مود رحلة إلى الأعماق", "icon": "🌊", "link": "https://mcpedl.com/?s=ocean"},
    {"num": "9️⃣0️⃣", "name": "مود مدينة الأشباح", "icon": "👻", "link": "https://mcpedl.com/?s=ghost"},
    {"num": "9️⃣1️⃣", "name": "مود الجزيرة الغامضة", "icon": "🏝️", "link": "https://mcpedl.com/?s=island"},
    {"num": "9️⃣2️⃣", "name": "مود الكنوز", "icon": "💰", "link": "https://mcpedl.com/?s=treasure"},
    {"num": "9️⃣3️⃣", "name": "مود الكنوز المفقودة", "icon": "🗝️", "link": "https://mcpedl.com/?s=lost+treasure"},
    {"num": "9️⃣4️⃣", "name": "مود البقاء الليلي", "icon": "🌑", "link": "https://mcpedl.com/?s=night"},
    {"num": "9️⃣5️⃣", "name": "مود الجوع", "icon": "🍖", "link": "https://mcpedl.com/?s=hunger"},

    # === مودات إضافية وملحقات أخرى ===
    {"num": "9️⃣6️⃣", "name": "مود اليدين", "icon": "🖐️", "link": "https://mcpedl.com/hands-mod/"},
    {"num": "9️⃣7️⃣", "name": "مود القفازات", "icon": "🧤", "link": "https://mcpedl.com/?s=gloves"},
    {"num": "9️⃣8️⃣", "name": "مود العين السحرية", "icon": "🧿", "link": "https://mcpedl.com/?s=magic+eye"},
    {"num": "9️⃣9️⃣", "name": "مود الساعات الذكية", "icon": "⌚", "link": "https://mcpedl.com/?s=smart+watch"},
    {"num": "1️⃣0️⃣0️⃣", "name": "مود الكاميرا", "icon": "📷", "link": "https://mcpedl.com/?s=camera"},
    {"num": "1️⃣0️⃣1️⃣", "name": "مود الطائرات بدون طيار", "icon": "🛸", "link": "https://mcpedl.com/?s=drone"},
    {"num": "1️⃣0️⃣2️⃣", "name": "مود الزراعة التلقائية", "icon": "🌾", "link": "https://mcpedl.com/?s=auto+harvest"},
    {"num": "1️⃣0️⃣3️⃣", "name": "مود الصيد السحري", "icon": "🎣", "link": "https://mcpedl.com/?s=magic+fishing"},
    {"num": "1️⃣0️⃣4️⃣", "name": "مود الطبخ", "icon": "🍲", "link": "https://mcpedl.com/?s=cooking"},
    {"num": "1️⃣0️⃣5️⃣", "name": "مود الحدادة", "icon": "🔨", "link": "https://mcpedl.com/?s=blacksmith"},
    {"num": "1️⃣0️⃣6️⃣", "name": "مود التعدين", "icon": "⛏️", "link": "https://mcpedl.com/?s=mining"},
    {"num": "1️⃣0️⃣7️⃣", "name": "مود التجارة", "icon": "💱", "link": "https://mcpedl.com/?s=trading"},
    {"num": "1️⃣0️⃣8️⃣", "name": "مود البنك", "icon": "🏦", "link": "https://mcpedl.com/?s=bank"},
    {"num": "1️⃣0️⃣9️⃣", "name": "مود الوظائف", "icon": "💼", "link": "https://mcpedl.com/?s=jobs"},
    {"num": "1️⃣1️⃣0️⃣", "name": "مود الزفاف", "icon": "💒", "link": "https://mcpedl.com/?s=wedding"},

    # === أكواد وحماية ===
    {"num": "1️⃣1️⃣1️⃣", "name": "مود الحماية", "icon": "🛡️", "link": "https://mcpedl.com/?s=protection"},
    {"num": "1️⃣1️⃣2️⃣", "name": "مود أشعة الحماية", "icon": "🔰", "link": "https://mcpedl.com/?s=shield"},
    {"num": "1️⃣1️⃣3️⃣", "name": "مود السور", "icon": "🚧", "link": "https://mcpedl.com/?s=fence"},
    {"num": "1️⃣1️⃣4️⃣", "name": "مود الجدران الذكية", "icon": "🧱", "link": "https://mcpedl.com/?s=wall"},
    {"num": "1️⃣1️⃣5️⃣", "name": "مود مصيدة الوحوش", "icon": "🪤", "link": "https://mcpedl.com/?s=trap"},
    {"num": "1️⃣1️⃣6️⃣", "name": "مود نظام الإنذار", "icon": "🚨", "link": "https://mcpedl.com/?s=alarm"},
    {"num": "1️⃣1️⃣7️⃣", "name": "مود الحراسة الليلية", "icon": "🌃", "link": "https://mcpedl.com/?s=guard"},
    {"num": "1️⃣1️⃣8️⃣", "name": "مود الكلاب البوليسية", "icon": "🐕‍🦺", "link": "https://mcpedl.com/?s=puppy"},
    {"num": "1️⃣1️⃣9️⃣", "name": "مود البوابات السرية", "icon": "🔐", "link": "https://mcpedl.com/?s=secret"},

    # === مودات الخرائط والبيئات ===
    {"num": "1️⃣2️⃣0️⃣", "name": "مود الخريطة", "icon": "🗺️", "link": "https://mcpedl.com/?s=map"},
    {"num": "1️⃣2️⃣1️⃣", "name": "مود البوصلة", "icon": "🧭", "link": "https://mcpedl.com/?s=compass"},
    {"num": "1️⃣2️⃣2️⃣", "name": "مود الاختفاء", "icon": "🫥", "link": "https://mcpedl.com/?s=invisible"},
    {"num": "1️⃣2️⃣3️⃣", "name": "مود السرعة في الليل", "icon": "🚀", "link": "https://mcpedl.com/?s=night+speed"},
    {"num": "1️⃣2️⃣4️⃣", "name": "مود الماء السحري", "icon": "💧", "link": "https://mcpedl.com/?s=water"},
    {"num": "1️⃣2️⃣5️⃣", "name": "مود الحمم البركانية", "icon": "🌋", "link": "https://mcpedl.com/?s=lava"},
    {"num": "1️⃣2️⃣6️⃣", "name": "مود الثلج المتجمد", "icon": "🧊", "link": "https://mcpedl.com/?s=ice"},
    {"num": "1️⃣2️⃣7️⃣", "name": "مود الأشجار العملاقة", "icon": "🌳", "link": "https://mcpedl.com/?s=tree"},
    {"num": "1️⃣2️⃣8️⃣", "name": "مود الغابة", "icon": "🌲", "link": "https://mcpedl.com/?s=forest"},
    {"num": "1️⃣2️⃣9️⃣", "name": "مود الجبال الثلجية", "icon": "🏔️", "link": "https://mcpedl.com/?s=snow+mountain"},
    {"num": "1️⃣3️⃣0️⃣", "name": "مود المدينة القديمة", "icon": "🏛️", "link": "https://mcpedl.com/?s=old+city"},
    {"num": "1️⃣3️⃣1️⃣", "name": "مود مدينة المستقبل", "icon": "🏙️", "link": "https://mcpedl.com/?s=future"},
    {"num": "1️⃣3️⃣2️⃣", "name": "مود البرج", "icon": "🗼", "link": "https://mcpedl.com/?s=tower"},

    # === مودات رياضية وقدرات ===
    {"num": "1️⃣3️⃣3️⃣", "name": "مود كرة القدم", "icon": "⚽", "link": "https://mcpedl.com/?s=soccer"},
    {"num": "1️⃣3️⃣4️⃣", "name": "مود كرة السلة", "icon": "🏀", "link": "https://mcpedl.com/?s=basketball"},
    {"num": "1️⃣3️⃣5️⃣", "name": "مود التنس", "icon": "🎾", "link": "https://mcpedl.com/?s=tennis"},
    {"num": "1️⃣3️⃣6️⃣", "name": "مود السباحة", "icon": "🏊", "link": "https://mcpedl.com/?s=swim"},
    {"num": "1️⃣3️⃣7️⃣", "name": "مود الجري", "icon": "🏃", "link": "https://mcpedl.com/?s=run"},
    {"num": "1️⃣3️⃣8️⃣", "name": "مود الرماية", "icon": "🎯", "link": "https://mcpedl.com/?s=shooting"},
    {"num": "1️⃣3️⃣9️⃣", "name": "مود الملاكمة", "icon": "🥊", "link": "https://mcpedl.com/?s=boxing"},
    {"num": "1️⃣4️⃣0️⃣", "name": "مود الكونغ فو", "icon": "🥋", "link": "https://mcpedl.com/?s=kungfu"},
    {"num": "1️⃣4️⃣1️⃣", "name": "مود الجودو", "icon": "🥇", "link": "https://mcpedl.com/?s=judo"},
    {"num": "1️⃣4️⃣2️⃣", "name": "مود الجمباز", "icon": "🤸", "link": "https://mcpedl.com/?s=gymnastics"},
    
    # === سحر وأساطير ===
    {"num": "1️⃣4️⃣3️⃣", "name": "مود السحر الأسود", "icon": "🌑", "link": "https://mcpedl.com/?s=black+magic"},
    {"num": "1️⃣4️⃣4️⃣", "name": "مود السحر الأبيض", "icon": "☀️", "link": "https://mcpedl.com/?s=white+magic"},
    {"num": "1️⃣4️⃣5️⃣", "name": "مود التنين الأسطوري", "icon": "🐲", "link": "https://mcpedl.com/?s=legendary+dragon"},
    {"num": "1️⃣4️⃣6️⃣", "name": "مود الوحش البحري", "icon": "🐉", "link": "https://mcpedl.com/?s=sea+monster"},
    {"num": "1️⃣4️⃣7️⃣", "name": "مود القنطور", "icon": "🐴", "link": "https://mcpedl.com/?s=centaur"},
    {"num": "1️⃣4️⃣8️⃣", "name": "مود المينوتور", "icon": "🐂", "link": "https://mcpedl.com/?s=minotaur"},
    {"num": "1️⃣4️⃣9️⃣", "name": "مود حورية البحر", "icon": "🧜‍♀️", "link": "https://mcpedl.com/?s=mermaid"},
    {"num": "1️⃣5️⃣0️⃣", "name": "مود الغول", "icon": "👹", "link": "https://mcpedl.com/?s=ogre"},
    {"num": "1️⃣5️⃣1️⃣", "name": "مود مصاص الدماء", "icon": "🧛", "link": "https://mcpedl.com/?s=vampire"},
    {"num": "1️⃣5️⃣2️⃣", "name": "مود المستذئب", "icon": "🐺", "link": "https://mcpedl.com/?s=werewolf"},
    {"num": "1️⃣5️⃣3️⃣", "name": "مود الجن", "icon": "🧞", "link": "https://mcpedl.com/?s=genie"},
    {"num": "1️⃣5️⃣4️⃣", "name": "مود الملائكة", "icon": "👼", "link": "https://mcpedl.com/?s=angel"},
    {"num": "1️⃣5️⃣5️⃣", "name": "مود الشياطين", "icon": "😈", "link": "https://mcpedl.com/?s=demon"},

    # === مودات "أخرى" ممتعة ===
    {"num": "1️⃣5️⃣6️⃣", "name": "مود إزالة الجاذبية", "icon": "🪐", "link": "https://mcpedl.com/?s=gravity"},
    {"num": "1️⃣5️⃣7️⃣", "name": "مود توسيع العالم", "icon": "🌍", "link": "https://mcpedl.com/?s=world"},
    {"num": "1️⃣5️⃣8️⃣", "name": "مود تعديل التضاريس", "icon": "⛰️", "link": "https://mcpedl.com/?s=terrain"},
    {"num": "1️⃣5️⃣9️⃣", "name": "مود أصوات الحيوانات", "icon": "🔊", "link": "https://mcpedl.com/?s=sounds"},
    {"num": "1️⃣6️⃣0️⃣", "name": "مود الطقس المتغير", "icon": "🌤️", "link": "https://mcpedl.com/?s=weather"},
    {"num": "1️⃣6️⃣1️⃣", "name": "مود النوم السريع", "icon": "🛌", "link": "https://mcpedl.com/?s=sleep"},
    {"num": "1️⃣6️⃣2️⃣", "name": "مود التحدث مع الحيوانات", "icon": "🗣️", "link": "https://mcpedl.com/?s=animal+talk"},
    {"num": "1️⃣6️⃣3️⃣", "name": "مود تتبع الأعداء", "icon": "🧿", "link": "https://mcpedl.com/?s=tracker"},
    {"num": "1️⃣6️⃣4️⃣", "name": "مود الرادار", "icon": "📡", "link": "https://mcpedl.com/?s=radar"},
    {"num": "1️⃣6️⃣5️⃣", "name": "مود الشفاء الذاتي", "icon": "💚", "link": "https://mcpedl.com/?s=heal"},
    {"num": "1️⃣6️⃣6️⃣", "name": "مود الشبح", "icon": "👤", "link": "https://mcpedl.com/?s=ghost"},
    {"num": "1️⃣6️⃣7️⃣", "name": "مود اللوح الطائر", "icon": "🛹", "link": "https://mcpedl.com/?s=skyboard"},
    {"num": "1️⃣6️⃣8️⃣", "name": "مود السيف المضيء", "icon": "✨", "link": "https://mcpedl.com/?s=glowing+sword"},
    {"num": "1️⃣6️⃣9️⃣", "name": "مود الكرة الماسية", "icon": "🔮", "link": "https://mcpedl.com/?s=diamond+ball"},
    {"num": "1️⃣7️⃣0️⃣", "name": "مود التخييم", "icon": "🏕️", "link": "https://mcpedl.com/?s=camping"},
    ]
}

# ====================== 2. المابات (MaPs) ======================
MAPS = {
    "عَوَالِم مَفْتُوحَة": [
        {"name": "إِمِيرْشِنْ إَرْثْ 2027", "icon": "🌍", "link": "https://mcpedl.com/?s=Immersion+Earth+2027"},
        {"name": "لُوسْ سَانْتُوسْ رِيمَيْكْ", "icon": "🌆", "link": "https://mcpedl.com/?s=Los+Santos+Remake"},
        {"name": "أَرْبَانْ سْتُورِيزْ مَابْ", "icon": "🏙️", "link": "https://mcpedl.com/?s=Urban+Stories+Map"},
        {"name": "سِيكْلُودِدْ بَارَادَايْزْ", "icon": "🏝️", "link": "https://mcpedl.com/?s=Secluded+Paradise"},
        {"name": "سَانْلِتْ هَارْبُورْ", "icon": "🌅", "link": "https://mcpedl.com/?s=Sunlit+Harbor"},
        {"name": "مِيدِيفَالْ كِينْغْدُومْ", "icon": "🏰", "link": "https://mcpedl.com/?s=Medieval+Kingdom"},
        {"name": "فْيُوتْشُرِسْتِكْ سِيتِي", "icon": "🚀", "link": "https://mcpedl.com/?s=Futuristic+City"},
    ],
    "مُغَامَرَات": [
        {"name": "أُوشِنْبَاوُنْدْ مَابْ", "icon": "🌊", "link": "https://mcpedl.com/?s=Oceanbound+Map"},
        {"name": "دَايْنُوفَالِيْ مَابْ", "icon": "🦖", "link": "https://mcpedl.com/?s=DinoValley+Map"},
        {"name": "أَنْشِنْتْ لِيجِنْدْزْ مَابْ", "icon": "📜", "link": "https://mcpedl.com/?s=Ancient+Legends"},
        {"name": "سْكَايْ رِيلْمْ أَدْفِنْتْشَرْ", "icon": "☁️", "link": "https://mcpedl.com/?s=Sky+Realm+Adventure"},
        {"name": "فْلُوتِنْغْ فِنْتْشَرْ", "icon": "🎈", "link": "https://mcpedl.com/?s=Floating+Venture"},
        {"name": "سَرْفَايْفَلْ آيْلَنْدْ 2026", "icon": "🏝️", "link": "https://mcpedl.com/?s=Survival+Island"},
    ],
    "رُعْب": [
        {"name": "نَايْتْمَيْرْ تُونْ سِيتِي", "icon": "👻", "link": "https://mcpedl.com/?s=Nightmare+Toon+City"},
        {"name": "مُوفِنْغْ كُولُوسُسْ", "icon": "🗿", "link": "https://mcpedl.com/?s=Moving+Colossus"},
        {"name": "إِنْفِكْتِدْ كَاتَاكُمْبْسْ", "icon": "💀", "link": "https://mcpedl.com/?s=Infected+Catacombs"},
        {"name": "إِسْكِيبْ ذَا مَيْزْ", "icon": "🌀", "link": "https://mcpedl.com/?s=Escape+The+Maze"},
    ],
    "أَلْعَاب مُصَغَّرَة": [
        {"name": "مَايْسَرْفَرْ مِينِيغَيْمْزْ", "icon": "🎮", "link": "https://mcpedl.com/?s=MyServer+Minigames"},
        {"name": "إِكْسْ وَايْ زِيْ مِينِيغَيْمْزْ", "icon": "🎲", "link": "https://mcpedl.com/?s=XYZ+MINIGAMES"},
        {"name": "كَاوُنْتَرْ سْتْرَايْكْ بِيدْرُوكْ", "icon": "🔫", "link": "https://mcpedl.com/?s=Counter+Strike+Bedrock"},
        {"name": "بِيدْ وَارْزْ آرِينَا", "icon": "⚔️", "link": "https://mcpedl.com/?s=Bed+Wars+Arena"},
    ],
    "إِبْدَاع": [
        {"name": "أُلْتِيمِتْ سَرْفَايْفَلْ", "icon": "🏆", "link": "https://mcpedl.com/?s=Ultimate+Survival"},
        {"name": "كِيبْلَرْ وُرْلْدْ", "icon": "🔭", "link": "https://mcpedl.com/?s=Kepler+World"},
        {"name": "فِرْدَنْتْ بِيكْسْ", "icon": "⛰️", "link": "https://mcpedl.com/?s=Verdant+Peaks"},
        {"name": "هَانِيْوُودْ أَدْفِنْتْشَرْزْ", "icon": "🐝", "link": "https://mcpedl.com/?s=Honeywood+Adventures"},
        {"name": "سُوسَايِتِي بِلْدَرْ", "icon": "🏗️", "link": "https://mcpedl.com/?s=Society+Builder"},
    ],
    "مُحِيطَات": [
        {"name": "أُوشِنْ لَايْفْ مَابْ", "icon": "🐠", "link": "https://mcpedl.com/?s=Ocean+Life+Map"},
        {"name": "هُورَايْزُنْ آيْلَنْدْزْ", "icon": "🌺", "link": "https://mcpedl.com/?s=Horizons+Islands"},
        {"name": "دِيمِينْيُوتُوسْ بِيدْرُوكْ 2", "icon": "🐙", "link": "https://mcpedl.com/?s=Diminutos+Bedrock+2"},
        {"name": "فْيُوجِنْ لَابْ 2.0", "icon": "⚗️", "link": "https://mcpedl.com/?s=Fusion+Lab"},
    ],
    "تَحَدِّيَات": [
        {"name": "وَانْ بْلُوكْ سْكَايْبْلُوكْ", "icon": "🧱", "link": "https://mcpedl.com/one-block-map/"},
        {"name": "بَارْكُورْ بَارَادَايْزْ", "icon": "🦘", "link": "https://mcpedl.com/?s=Parkour+Paradise"},
        {"name": "سْكَايْ غْرِيدْ تْشَالِنْجْ", "icon": "🌤️", "link": "https://mcpedl.com/?s=SkyGrid+Challenge"},
    ],
}

# ====================== 3. الريسوس باكات (ReSuS PaCk) ======================
RESUS_PACKS = {
    "حزم PvP / أداء": [
        {"name": "ريسوس باك ذهبي PVP", "icon": "✨", "link": "https://mcpedl.com/gold-pvp-pack/"},
        {"name": "ريسوس باك بنفسجي PVP", "icon": "💜", "link": "https://mcpedl.com/purple-pvp-pack/"},
        {"name": "ريسوس باك الارنب", "icon": "🐇", "link": "https://mcpedl.com/rabbit-pack/"},
        {"name": "ريسوس باك تقليل الاك", "icon": "📉", "link": "https://mcpedl.com/fps-boost-pack/"},
        {"name": "ريسوس باك 32", "icon": "🔢", "link": "https://mcpedl.com/32x-pack/"},
        {"name": "ريسوس باك القهوه", "icon": "☕", "link": "https://mcpedl.com/coffee-pack/"},
    ],
    "حزم Realistic / HD": [
        {"name": "✨ Vanilla RTX", "icon": "💎", "link": "https://dlcfun.com/vanilla-rtx"},
        {"name": "🌆 Optimum Realism", "icon": "🏙️", "link": "https://www.curseforge.com/minecraft-bedrock/texture-packs/optimum-realism"},
        {"name": "🎨 Bare Bones", "icon": "🦴", "link": "https://dlcfun.com/bare-bones"},
        {"name": "🖼️ Default RTX", "icon": "🌟", "link": "https://for-minecraft.com/default-rtx-bedrock"},
        {"name": "🌈 WhoCares Visuals", "icon": "🎭", "link": "https://www.curseforge.com/minecraft-bedrock/texture-packs/whocares-visuals"},
    ],
    "حزم Shaders / Vibrant Visuals": [
        {"name": "❄️ Baku's Winter Rora", "icon": "☃️", "link": "https://mcpedl.com/bakus-winter-rora-shader/"},
        {"name": "🌸 Kitty Dream 16x", "icon": "🎀", "link": "https://mcpedl.com/kitty-dream-16x/"},
        {"name": "🌙 Two Moons", "icon": "🌕", "link": "https://modbay.org/two-moons-bedrock"},
    ],
    "حزم تحسينات / أدوات": [
        {"name": "💡 FullBright (Night Vision)", "icon": "👁️", "link": "https://modbay.org/fullbright-night-vision"},
        {"name": "🌊 Clear Aquatics", "icon": "💧", "link": "https://modbay.org/clear-aquatics"},
        {"name": "🗺️ More Waypoint", "icon": "📍", "link": "https://mcpedl.com/more-waypoint/"},
        {"name": "📦 X-Ray + Outlined Ores", "icon": "⛏️", "link": "https://mcpedl.com/x-ray-outlined-ores/"},
    ],
    "حزم أسلوب / مميزة": [
        {"name": "🎭 Comic Realm", "icon": "💥", "link": "https://www.mc-mod.net/comic-realm-texture-pack/"},
        {"name": "🏰 World Building", "icon": "🧱", "link": "https://www.mc-mod.net/world-building-texture-pack/"},
        {"name": "🎨 Soartex Fanver", "icon": "🖌️", "link": "https://klpbbs.com/soartex-fanver/"},
        {"name": "🔫 Tactical Arsenal", "icon": "🔫", "link": "https://www.mc-mod.net/tactical-arsenal-texture-pack/"},
    ],
}

# ====================== 4. الشادرات (Shaders) - معدلة ======================
# قائمة جميع الشادرات الخام (بدون تصنيف)
SHADERS_RAW = [
    {"num": "🌞", "name": "شادر ESBE 2G", "icon": "🌈", "link": "https://mcpedl.com/esbe-2g-shader/"},
    {"num": "🌞", "name": "شادر Newb X", "icon": "🌅", "link": "https://mcpedl.com/newb-x-shader/"},
    {"name": "SEUS PE", "link": "https://mcpedl.com/seus-pe-shader/", "description": "🌅 شادر واقعي فائق الجودة.", "emoji": "🌅"},
    {"name": "SEUS PE Lite", "link": "https://mcpedl.com/seus-pe-lite/", "description": "🌤️ نسخة خفيفة من SEUS.", "emoji": "🌤️"},
    {"name": "SEUS PE Renewed", "link": "https://mcpedl.com/seus-pe-renewed/", "description": "☀️ إصدار محدث بأداء أفضل.", "emoji": "☀️"},
    {"name": "SEUS PE v11", "link": "https://mcpedl.com/seus-pe-v11/", "description": "🌇 الإصدار 11 من SEUS PE.", "emoji": "🌇"},
    {"name": "SEUS PTGI E12", "link": "https://mcpedl.com/seus-ptgi-e12/", "description": "✨ إضاءة متقدمة وتتبع أشعة.", "emoji": "✨"},
    {"name": "ESTN Shaders v1", "link": "https://mcpedl.com/estn-shaders-v1/", "description": "🎨 إضاءة ناعمة وألوان جميلة.", "emoji": "🎨"},
    {"name": "ESTN Shaders v2", "link": "https://mcpedl.com/estn-shaders-v2/", "description": "🖌️ تحسينات على الظلال.", "emoji": "🖌️"},
    {"name": "ESTN Shaders v3", "link": "https://mcpedl.com/estn-shaders-v3/", "description": "🌈 أداء أفضل وتوافق أوسع.", "emoji": "🌈"},
    {"name": "ESTN Shaders v4", "link": "https://mcpedl.com/estn-shaders-v4/", "description": "💡 إضاءة ديناميكية.", "emoji": "💡"},
    {"name": "ESTN Shaders v5", "link": "https://mcpedl.com/estn-shaders-v5/", "description": "🌺 ألوان مشبعة وواقعية.", "emoji": "🌺"},
    {"name": "ESTN Shaders v6", "link": "https://mcpedl.com/estn-shaders-v6/", "description": "🌿 ظلال ناعمة جدًا.", "emoji": "🌿"},
    {"name": "ESTN Shaders v7", "link": "https://mcpedl.com/estn-shaders-v7/", "description": "🔥 توافق مع Render Dragon.", "emoji": "🔥"},
    {"name": "ESTN Shaders v8", "link": "https://mcpedl.com/estn-shaders-v8/", "description": "🌊 إضاءة محيطية.", "emoji": "🌊"},
    {"name": "ESTN Shaders v9", "link": "https://mcpedl.com/estn-shaders-v9/", "description": "⚡ نسخة محسنة للأجهزة الضعيفة.", "emoji": "⚡"},
    {"name": "ESTN Shaders v10", "link": "https://mcpedl.com/estn-shaders-v10/", "description": "🌟 أحدث إصدار بجودة عالية.", "emoji": "🌟"},
    {"name": "BSBE Shader", "link": "https://mcpedl.com/bsbe-shader/", "description": "🍃 شادر خفيف وسريع.", "emoji": "🍃"},
    {"name": "BSBE Shader Lite", "link": "https://mcpedl.com/bsbe-shader-lite/", "description": "🌱 أخف نسخة للأجهزة الضعيفة.", "emoji": "🌱"},
    {"name": "BSBE Shader Ultra", "link": "https://mcpedl.com/bsbe-shader-ultra/", "description": "💎 جودة قصوى مع أداء ممتاز.", "emoji": "💎"},
    {"name": "BSBE Shader v2", "link": "https://mcpedl.com/bsbe-shader-v2/", "description": "🍀 إصدار محدث بتحسينات.", "emoji": "🍀"},
    {"name": "BSBE Shader v3", "link": "https://mcpedl.com/bsbe-shader-v3/", "description": "🌲 أحدث إصدار من BSBE.", "emoji": "🌲"},
    {"name": "Haptic Shader", "link": "https://mcpedl.com/haptic-shader/", "description": "🌆 ألوان دافئة وإضاءة جميلة.", "emoji": "🌆"},
    {"name": "Haptic Shader Lite", "link": "https://mcpedl.com/haptic-shader-lite/", "description": "🌃 نسخة خفيفة.", "emoji": "🌃"},
    {"name": "Haptic Shader Pro", "link": "https://mcpedl.com/haptic-shader-pro/", "description": "🏙️ ميزات متقدمة.", "emoji": "🏙️"},
    {"name": "Haptic Shader v2", "link": "https://mcpedl.com/haptic-shader-v2/", "description": "🌉 الإصدار الثاني.", "emoji": "🌉"},
    {"name": "Zebra Shader", "link": "https://mcpedl.com/zebra-shader/", "description": "🦓 تباين عالي وألوان واضحة.", "emoji": "🦓"},
    {"name": "Zebra Shader Lite", "link": "https://mcpedl.com/zebra-shader-lite/", "description": "⚪ خفيف وسريع.", "emoji": "⚪"},
    {"name": "Zebra Shader Ultra", "link": "https://mcpedl.com/zebra-shader-ultra/", "description": "🔳 جودة عالية جدًا.", "emoji": "🔳"},
    {"name": "Zebra Shader v2", "link": "https://mcpedl.com/zebra-shader-v2/", "description": "⬜ إصدار محسّن.", "emoji": "⬜"},
    {"name": "Zebra Shader v3", "link": "https://mcpedl.com/zebra-shader-v3/", "description": "⬛ أحدث إصدار.", "emoji": "⬛"},
    {"name": "Newb Shader", "link": "https://mcpedl.com/newb-shader/", "description": "🆕 مثالي للمبتدئين.", "emoji": "🆕"},
    {"name": "Newb Shader XL", "link": "https://mcpedl.com/newb-shader-xl/", "description": "🔠 نسخة موسعة.", "emoji": "🔠"},
    {"name": "Newb Shader Pro", "link": "https://mcpedl.com/newb-shader-pro/", "description": "💼 احترافي.", "emoji": "💼"},
    {"name": "Newb Shader v2", "link": "https://mcpedl.com/newb-shader-v2/", "description": "🆒 إصدار ثاني.", "emoji": "🆒"},
    {"name": "Source Shader", "link": "https://mcpedl.com/source-shader/", "description": "🔆 إضاءة واقعية.", "emoji": "🔆"},
    {"name": "Source Shader Lite", "link": "https://mcpedl.com/source-shader-lite/", "description": "☀️ نسخة خفيفة.", "emoji": "☀️"},
    {"name": "Source Shader Ultra", "link": "https://mcpedl.com/source-shader-ultra/", "description": "🌞 جودة فائقة.", "emoji": "🌞"},
    {"name": "Source Shader v2", "link": "https://mcpedl.com/source-shader-v2/", "description": "🔅 إصدار محسّن.", "emoji": "🔅"},
    {"name": "Continuum Shader", "link": "https://mcpedl.com/continuum-shader/", "description": "🎬 إضاءة سينمائية.", "emoji": "🎬"},
    {"name": "Continuum Shader Lite", "link": "https://mcpedl.com/continuum-shader-lite/", "description": "🎞️ خفيف.", "emoji": "🎞️"},
    {"name": "Continuum Shader Ultra", "link": "https://mcpedl.com/continuum-shader-ultra/", "description": "📽️ أعلى جودة.", "emoji": "📽️"},
    {"name": "Continuum Shader v2", "link": "https://mcpedl.com/continuum-shader-v2/", "description": "🎥 إصدار جديد.", "emoji": "🎥"},
    {"name": "Sildur's Vibrant Shaders", "link": "https://mcpedl.com/sildurs-vibrant-shaders-bedrock/", "description": "🌈 ألوان نابضة بالحياة.", "emoji": "🌈"},
    {"name": "Sildur's Vibrant Lite", "link": "https://mcpedl.com/sildurs-vibrant-lite/", "description": "🌸 نسخة خفيفة.", "emoji": "🌸"},
    {"name": "Sildur's Vibrant Medium", "link": "https://mcpedl.com/sildurs-vibrant-medium/", "description": "💮 توازن بين الجودة والأداء.", "emoji": "💮"},
    {"name": "Chocapic13 Shaders", "link": "https://mcpedl.com/chocapic13-shaders-bedrock/", "description": "🌳 إضاءة طبيعية.", "emoji": "🌳"},
    {"name": "Chocapic13 Lite", "link": "https://mcpedl.com/chocapic13-lite/", "description": "🌲 خفيف.", "emoji": "🌲"},
    {"name": "Chocapic13 High", "link": "https://mcpedl.com/chocapic13-high/", "description": "🌴 جودة عالية.", "emoji": "🌴"},
    {"name": "BSL Shaders", "link": "https://mcpedl.com/bsl-shaders-bedrock/", "description": "🌄 شادر شهير بواقعية.", "emoji": "🌄"},
    {"name": "BSL Shaders Lite", "link": "https://mcpedl.com/bsl-shaders-lite/", "description": "🏞️ نسخة خفيفة.", "emoji": "🏞️"},
    {"name": "BSL Shaders Ultra", "link": "https://mcpedl.com/bsl-shaders-ultra/", "description": "🗻 أقصى جودة.", "emoji": "🗻"},
    {"name": "KUDA Shaders", "link": "https://mcpedl.com/kuda-shaders-bedrock/", "description": "🔥 إضاءة دافئة.", "emoji": "🔥"},
    {"name": "KUDA Shaders Lite", "link": "https://mcpedl.com/kuda-shaders-lite/", "description": "🕯️ خفيف.", "emoji": "🕯️"},
    {"name": "KUDA Shaders Ultra", "link": "https://mcpedl.com/kuda-shaders-ultra/", "description": "💡 جودة عالية.", "emoji": "💡"},
    {"name": "Beyond Belief Shaders", "link": "https://mcpedl.com/beyond-belief-shaders/", "description": "🌀 ألوان خيالية.", "emoji": "🌀"},
    {"name": "Beyond Belief Lite", "link": "https://mcpedl.com/beyond-belief-lite/", "description": "🎐 نسخة خفيفة.", "emoji": "🎐"},
    {"name": "Evident Shaders", "link": "https://mcpedl.com/evident-shaders/", "description": "🔍 ظلال واضحة.", "emoji": "🔍"},
    {"name": "Evident Shaders v2", "link": "https://mcpedl.com/evident-shaders-v2/", "description": "🔎 إصدار محسّن.", "emoji": "🔎"},
    {"name": "Natural Mystic Shaders", "link": "https://mcpedl.com/natural-mystic-shaders/", "description": "🌿 طبيعة ساحرة.", "emoji": "🌿"},
    {"name": "Natural Mystic v2", "link": "https://mcpedl.com/natural-mystic-shaders-v2/", "description": "🍃 إصدار جديد.", "emoji": "🍃"},
    {"name": "Reality Shader", "link": "https://mcpedl.com/reality-shader/", "description": "🌐 واقعية مذهلة.", "emoji": "🌐"},
    {"name": "Reality Shader v2", "link": "https://mcpedl.com/reality-shader-v2/", "description": "🌍 إصدار ثاني.", "emoji": "🌍"},
    {"name": "Enhanced Default Shader", "link": "https://mcpedl.com/enhanced-default-shader/", "description": "📦 تحسين للشكل الافتراضي.", "emoji": "📦"},
    {"name": "Bare Bones Shader", "link": "https://mcpedl.com/bare-bones-shader/", "description": "🦴 بسيط ونظيف.", "emoji": "🦴"},
    {"name": "Mizuno's 16x Shader", "link": "https://mcpedl.com/mizunos-16x-shader/", "description": "🎏 ملمس ناعم مع إضاءة.", "emoji": "🎏"},
    {"name": "Stay True Shader", "link": "https://mcpedl.com/stay-true-shader/", "description": "🕊️ ألوان هادئة.", "emoji": "🕊️"},
    {"name": "ProjectLUMA Shader", "link": "https://mcpedl.com/projectluma-shader/", "description": "🎇 إضاءة سينمائية.", "emoji": "🎇"},
    {"name": "ProjectLUMA Lite", "link": "https://mcpedl.com/projectluma-lite/", "description": "✨ نسخة خفيفة.", "emoji": "✨"},
    {"name": "AstraLex Shaders", "link": "https://mcpedl.com/astralex-shaders/", "description": "🌌 مزيج من عدة شادرات.", "emoji": "🌌"},
    {"name": "AstraLex Lite", "link": "https://mcpedl.com/astralex-lite/", "description": "☄️ خفيف.", "emoji": "☄️"},
    {"name": "Voyager Shader", "link": "https://mcpedl.com/voyager-shader/", "description": "🚀 استكشاف بصري.", "emoji": "🚀"},
    {"name": "Voyager v2", "link": "https://mcpedl.com/voyager-shader-v2/", "description": "🛸 إصدار ثاني.", "emoji": "🛸"},
    {"name": "Creeper Shader", "link": "https://mcpedl.com/creeper-shader/", "description": "💚 ألوان زاهية.", "emoji": "💚"},
    {"name": "Creeper Shader Lite", "link": "https://mcpedl.com/creeper-shader-lite/", "description": "🍏 خفيف.", "emoji": "🍏"},
    {"name": "Ultra Shader", "link": "https://mcpedl.com/ultra-shader/", "description": "🔷 جودة فائقة.", "emoji": "🔷"},
    {"name": "Ultra Shader v2", "link": "https://mcpedl.com/ultra-shader-v2/", "description": "🔶 إصدار محسّن.", "emoji": "🔶"},
    {"name": "Kappa Shader", "link": "https://mcpedl.com/kappa-shader/", "description": "🔥 إضاءة دافئة.", "emoji": "🔥"},
    {"name": "Kappa Shader v2", "link": "https://mcpedl.com/kappa-shader-v2/", "description": "☀️ نسخة جديدة.", "emoji": "☀️"},
    {"name": "RRe36's Kappa Shader", "link": "https://mcpedl.com/rre36-kappa-shader/", "description": "🌋 من مبتكر Kappa.", "emoji": "🌋"},
    {"name": "RRe36's ProjectLUMA", "link": "https://mcpedl.com/rre36-projectluma/", "description": "🎆 إضاءة سينمائية.", "emoji": "🎆"},
    {"name": "SORA Shaders", "link": "https://mcpedl.com/sora-shaders/", "description": "🌤️ سماء جميلة.", "emoji": "🌤️"},
    {"name": "SORA Shaders v2", "link": "https://mcpedl.com/sora-shaders-v2/", "description": "⛅ إصدار ثاني.", "emoji": "⛅"},
    {"name": "SORA Lite", "link": "https://mcpedl.com/sora-shaders-lite/", "description": "🌥️ نسخة خفيفة.", "emoji": "🌥️"},
    {"name": "Vanilla Plus Shader", "link": "https://mcpedl.com/vanilla-plus-shader/", "description": "🍦 تحسين للفانيليا.", "emoji": "🍦"},
    {"name": "Vanilla Plus v2", "link": "https://mcpedl.com/vanilla-plus-shader-v2/", "description": "🍨 إصدار جديد.", "emoji": "🍨"},
    {"name": "Simple Shader", "link": "https://mcpedl.com/simple-shader/", "description": "⚪ بسيط وسريع.", "emoji": "⚪"},
    {"name": "Simple Shader v2", "link": "https://mcpedl.com/simple-shader-v2/", "description": "⬜ إصدار ثاني.", "emoji": "⬜"},
    {"name": "Pixel Perfect Shader", "link": "https://mcpedl.com/pixel-perfect-shader/", "description": "🔲 دقة بكسلات.", "emoji": "🔲"},
    {"name": "Pixel Perfect v2", "link": "https://mcpedl.com/pixel-perfect-shader-v2/", "description": "🔳 نسخة محسنة.", "emoji": "🔳"},
    {"name": "Retro Shader", "link": "https://mcpedl.com/retro-shader/", "description": "📼 أسلوب قديم.", "emoji": "📼"},
    {"name": "Retro v2", "link": "https://mcpedl.com/retro-shader-v2/", "description": "📺 إصدار جديد.", "emoji": "📺"},
    {"name": "CRUSH Shaders", "link": "https://mcpedl.com/crush-shaders/", "description": "💥 ألوان قوية.", "emoji": "💥"},
    {"name": "CRUSH Lite", "link": "https://mcpedl.com/crush-shaders-lite/", "description": "🎯 خفيف.", "emoji": "🎯"},
    {"name": "ESBE 2G Shader", "link": "https://mcpedl.com/esbe-2g-shader/", "description": "📱 الجيل الثاني.", "emoji": "📱"},
    {"name": "ESBE 3G Shader", "link": "https://mcpedl.com/esbe-3g-shader/", "description": "📲 الجيل الثالث.", "emoji": "📲"},
    {"name": "ESBE 3G Lite", "link": "https://mcpedl.com/esbe-3g-lite/", "description": "🔋 نسخة خفيفة.", "emoji": "🔋"},
    {"name": "YSS Shader", "link": "https://mcpedl.com/yss-shader/", "description": "🌙 إضاءة ناعمة.", "emoji": "🌙"},
    {"name": "YSS v2", "link": "https://mcpedl.com/yss-shader-v2/", "description": "🌛 إصدار ثاني.", "emoji": "🌛"},
    {"name": "YSS Lite", "link": "https://mcpedl.com/yss-shader-lite/", "description": "🌜 خفيف.", "emoji": "🌜"},
    {"name": "Vibrant Shaders", "link": "https://mcpedl.com/vibrant-shaders-bedrock/", "description": "🎨 ألوان نابضة.", "emoji": "🎨"},
    {"name": "Vibrant Lite", "link": "https://mcpedl.com/vibrant-shaders-lite/", "description": "🖍️ نسخة خفيفة.", "emoji": "🖍️"},
    {"name": "Dramatic Skys Shader", "link": "https://mcpedl.com/dramatic-skys-shader/", "description": "🌇 سماء درامية.", "emoji": "🌇"},
    {"name": "Dramatic Skys v2", "link": "https://mcpedl.com/dramatic-skys-shader-v2/", "description": "🌆 إصدار جديد.", "emoji": "🌆"},
    {"name": "Dramatic Skys Lite", "link": "https://mcpedl.com/dramatic-skys-lite/", "description": "🌃 خفيف.", "emoji": "🌃"},
    {"name": "Enhanced Biomes Shader", "link": "https://mcpedl.com/enhanced-biomes-shader/", "description": "🌲 تحسين المناطق الحيوية.", "emoji": "🌲"},
    {"name": "Enhanced Biomes v2", "link": "https://mcpedl.com/enhanced-biomes-shader-v2/", "description": "🌳 إصدار ثاني.", "emoji": "🌳"},
    {"name": "Realistico Shader", "link": "https://mcpedl.com/realistico-shader/", "description": "🏞️ واقعية عالية.", "emoji": "🏞️"},
    {"name": "Realistico v2", "link": "https://mcpedl.com/realistico-shader-v2/", "description": "🌄 نسخة محسنة.", "emoji": "🌄"},
    {"name": "Realistico Lite", "link": "https://mcpedl.com/realistico-lite/", "description": "🌅 خفيف.", "emoji": "🌅"},
    {"name": "Pinnacle Shader", "link": "https://mcpedl.com/pinnacle-shader/", "description": "🏔️ قمّة الجودة.", "emoji": "🏔️"},
    {"name": "Pinnacle v2", "link": "https://mcpedl.com/pinnacle-shader-v2/", "description": "⛰️ إصدار جديد.", "emoji": "⛰️"},
    {"name": "Bliss Shader", "link": "https://mcpedl.com/bliss-shader/", "description": "😊 نعيم بصري.", "emoji": "😊"},
    {"name": "Bliss v2", "link": "https://mcpedl.com/bliss-shader-v2/", "description": "😌 إصدار ثاني.", "emoji": "😌"},
    {"name": "Nostalgia Shader", "link": "https://mcpedl.com/nostalgia-shader/", "description": "📻 ذكريات الماضي.", "emoji": "📻"},
    {"name": "Nostalgia v2", "link": "https://mcpedl.com/nostalgia-shader-v2/", "description": "🕰️ إصدار جديد.", "emoji": "🕰️"},
    {"name": "Nostalgia Lite", "link": "https://mcpedl.com/nostalgia-shader-lite/", "description": "⏳ خفيف.", "emoji": "⏳"},
    {"name": "Triliton's Shaders", "link": "https://mcpedl.com/trilitons-shaders/", "description": "🔱 إضاءة فريدة.", "emoji": "🔱"},
    {"name": "Triliton's v2", "link": "https://mcpedl.com/trilitons-shaders-v2/", "description": "⚜️ إصدار ثاني.", "emoji": "⚜️"},
    {"name": "Triliton's v3", "link": "https://mcpedl.com/trilitons-shaders-v3/", "description": "🔰 أحدث إصدار.", "emoji": "🔰"},
    {"name": "Soritong Shader", "link": "https://mcpedl.com/soritong-shader/", "description": "🍂 ألوان دافئة.", "emoji": "🍂"},
    {"name": "Soritong v2", "link": "https://mcpedl.com/soritong-shader-v2/", "description": "🍁 إصدار جديد.", "emoji": "🍁"},
    {"name": "Pampas Shader", "link": "https://mcpedl.com/pampas-shader/", "description": "🌾 سهول جميلة.", "emoji": "🌾"},
    {"name": "Pampas v2", "link": "https://mcpedl.com/pampas-shader-v2/", "description": "🌻 نسخة محسنة.", "emoji": "🌻"},
    {"name": "Llama Shader", "link": "https://mcpedl.com/llama-shader/", "description": "🦙 خفيف وسريع.", "emoji": "🦙"},
    {"name": "Llama v2", "link": "https://mcpedl.com/llama-shader-v2/", "description": "🐪 إصدار ثاني.", "emoji": "🐪"},
    {"name": "Mellow Shader", "link": "https://mcpedl.com/mellow-shader/", "description": "🍃 ألوان هادئة.", "emoji": "🍃"},
    {"name": "Mellow v2", "link": "https://mcpedl.com/mellow-shader-v2/", "description": "🌿 نسخة جديدة.", "emoji": "🌿"},
    {"name": "Sakura Shader", "link": "https://mcpedl.com/sakura-shader/", "description": "🌸 أجواء الربيع.", "emoji": "🌸"},
    {"name": "Sakura v2", "link": "https://mcpedl.com/sakura-shader-v2/", "description": "💮 إصدار ثاني.", "emoji": "💮"},
    {"name": "Sakura Lite", "link": "https://mcpedl.com/sakura-shader-lite/", "description": "🌺 خفيف.", "emoji": "🌺"},
    {"name": "Zenith Shader", "link": "https://mcpedl.com/zenith-shader/", "description": "🔝 ذروة الإضاءة.", "emoji": "🔝"},
    {"name": "Zenith v2", "link": "https://mcpedl.com/zenith-shader-v2/", "description": "🏆 إصدار جديد.", "emoji": "🏆"},
    {"name": "Fusion Shader", "link": "https://mcpedl.com/fusion-shader/", "description": "⚛️ دمج بين الشادرات.", "emoji": "⚛️"},
    {"name": "Fusion v2", "link": "https://mcpedl.com/fusion-shader-v2/", "description": "☯️ نسخة محسنة.", "emoji": "☯️"},
    {"name": "Mystic Shader", "link": "https://mcpedl.com/mystic-shader/", "description": "🔮 غموض وجمال.", "emoji": "🔮"},
    {"name": "Mystic v2", "link": "https://mcpedl.com/mystic-shader-v2/", "description": "🪄 إصدار ثاني.", "emoji": "🪄"},
    {"name": "Mystic Lite", "link": "https://mcpedl.com/mystic-shader-lite/", "description": "✨ خفيف.", "emoji": "✨"},
    {"name": "Radiant Shader", "link": "https://mcpedl.com/radiant-shader/", "description": "☀️ إشراق.", "emoji": "☀️"},
    {"name": "Radiant v2", "link": "https://mcpedl.com/radiant-shader-v2/", "description": "🌞 إصدار جديد.", "emoji": "🌞"},
    {"name": "Aurora Shader", "link": "https://mcpedl.com/aurora-shader/", "description": "🌌 أضواء الشفق.", "emoji": "🌌"},
    {"name": "Aurora v2", "link": "https://mcpedl.com/aurora-shader-v2/", "description": "🌠 نسخة محسنة.", "emoji": "🌠"},
    {"name": "Eclipse Shader", "link": "https://mcpedl.com/eclipse-shader/", "description": "🌑 كسوف جميل.", "emoji": "🌑"},
    {"name": "Eclipse v2", "link": "https://mcpedl.com/eclipse-shader-v2/", "description": "🌘 إصدار ثاني.", "emoji": "🌘"},
    {"name": "Eclipse Lite", "link": "https://mcpedl.com/eclipse-shader-lite/", "description": "🌗 خفيف.", "emoji": "🌗"},
    {"name": "Nebula Shader", "link": "https://mcpedl.com/nebula-shader/", "description": "🌫️ سديم.", "emoji": "🌫️"},
    {"name": "Nebula v2", "link": "https://mcpedl.com/nebula-shader-v2/", "description": "☁️ إصدار جديد.", "emoji": "☁️"},
    {"name": "Cosmic Shader", "link": "https://mcpedl.com/cosmic-shader/", "description": "🪐 كوني.", "emoji": "🪐"},
    {"name": "Cosmic v2", "link": "https://mcpedl.com/cosmic-shader-v2/", "description": "🌌 نسخة محسنة.", "emoji": "🌌"},
    {"name": "Solar Shader", "link": "https://mcpedl.com/solar-shader/", "description": "☀️ شمسي.", "emoji": "☀️"},
    {"name": "Solar v2", "link": "https://mcpedl.com/solar-shader-v2/", "description": "🌞 إصدار ثاني.", "emoji": "🌞"},
    {"name": "Lunar Shader", "link": "https://mcpedl.com/lunar-shader/", "description": "🌙 قمري.", "emoji": "🌙"},
    {"name": "Lunar v2", "link": "https://mcpedl.com/lunar-shader-v2/", "description": "🌛 نسخة جديدة.", "emoji": "🌛"},
    {"name": "Stellar Shader", "link": "https://mcpedl.com/stellar-shader/", "description": "⭐ نجمي.", "emoji": "⭐"},
    {"name": "Stellar v2", "link": "https://mcpedl.com/stellar-shader-v2/", "description": "🌟 إصدار ثاني.", "emoji": "🌟"},
    {"name": "Galaxy Shader", "link": "https://mcpedl.com/galaxy-shader/", "description": "🌌 مجرة.", "emoji": "🌌"},
    {"name": "Galaxy v2", "link": "https://mcpedl.com/galaxy-shader-v2/", "description": "🌠 نسخة محسنة.", "emoji": "🌠"},
    {"name": "Photon Shader", "link": "https://mcpedl.com/photon-shader/", "description": "💡 فوتونات.", "emoji": "💡"},
    {"name": "Photon v2", "link": "https://mcpedl.com/photon-shader-v2/", "description": "🔦 إصدار جديد.", "emoji": "🔦"},
    {"name": "Quantum Shader", "link": "https://mcpedl.com/quantum-shader/", "description": "⚛️ كمي.", "emoji": "⚛️"},
    {"name": "Quantum v2", "link": "https://mcpedl.com/quantum-shader-v2/", "description": "🔬 نسخة ثانية.", "emoji": "🔬"},
    {"name": "Ion Shader", "link": "https://mcpedl.com/ion-shader/", "description": "⚡ أيونات.", "emoji": "⚡"},
    {"name": "Ion v2", "link": "https://mcpedl.com/ion-shader-v2/", "description": "🔋 إصدار جديد.", "emoji": "🔋"},
    {"name": "Plasma Shader", "link": "https://mcpedl.com/plasma-shader/", "description": "🔥 بلازما.", "emoji": "🔥"},
    {"name": "Plasma v2", "link": "https://mcpedl.com/plasma-shader-v2/", "description": "💥 نسخة محسنة.", "emoji": "💥"},
    {"name": "Pulse Shader", "link": "https://mcpedl.com/pulse-shader/", "description": "❤️ نبض.", "emoji": "❤️"},
    {"name": "Pulse v2", "link": "https://mcpedl.com/pulse-shader-v2/", "description": "💓 إصدار ثاني.", "emoji": "💓"},
    {"name": "Wave Shader", "link": "https://mcpedl.com/wave-shader/", "description": "🌊 موجات.", "emoji": "🌊"},
    {"name": "Wave v2", "link": "https://mcpedl.com/wave-shader-v2/", "description": "🏄 نسخة جديدة.", "emoji": "🏄"},
    {"name": "Flux Shader", "link": "https://mcpedl.com/flux-shader/", "description": "🌀 تدفق.", "emoji": "🌀"},
    {"name": "Flux v2", "link": "https://mcpedl.com/flux-shader-v2/", "description": "🌪️ إصدار ثاني.", "emoji": "🌪️"},
    {"name": "Dynamo Shader", "link": "https://mcpedl.com/dynamo-shader/", "description": "⚙️ دينامو.", "emoji": "⚙️"},
    {"name": "Dynamo v2", "link": "https://mcpedl.com/dynamo-shader-v2/", "description": "🔩 نسخة محسنة.", "emoji": "🔩"},
    {"name": "Volt Shader", "link": "https://mcpedl.com/volt-shader/", "description": "🔌 فولت.", "emoji": "🔌"},
    {"name": "Volt v2", "link": "https://mcpedl.com/volt-shader-v2/", "description": "⚡ إصدار جديد.", "emoji": "⚡"},
    {"name": "Core Shader", "link": "https://mcpedl.com/core-shader/", "description": "💠 نواة.", "emoji": "💠"},
    {"name": "Core v2", "link": "https://mcpedl.com/core-shader-v2/", "description": "🔷 نسخة ثانية.", "emoji": "🔷"},
    {"name": "Titan Shader", "link": "https://mcpedl.com/titan-shader/", "description": "🗿 عملاق.", "emoji": "🗿"},
    {"name": "Titan v2", "link": "https://mcpedl.com/titan-shader-v2/", "description": "🏛️ إصدار جديد.", "emoji": "🏛️"},
    {"name": "Colossus Shader", "link": "https://mcpedl.com/colossus-shader/", "description": "🗽 تمثال ضخم.", "emoji": "🗽"},
    {"name": "Colossus v2", "link": "https://mcpedl.com/colossus-shader-v2/", "description": "🏰 نسخة محسنة.", "emoji": "🏰"},
    {"name": "Atlas Shader", "link": "https://mcpedl.com/atlas-shader/", "description": "🌍 أطلس.", "emoji": "🌍"},
    {"name": "Atlas v2", "link": "https://mcpedl.com/atlas-shader-v2/", "description": "🌎 إصدار ثاني.", "emoji": "🌎"},
    {"name": "Hyper Shader", "link": "https://mcpedl.com/hyper-shader/", "description": "🚀 فائق السرعة.", "emoji": "🚀"},
    {"name": "Hyper v2", "link": "https://mcpedl.com/hyper-shader-v2/", "description": "🛸 نسخة جديدة.", "emoji": "🛸"},
    {"name": "Extreme Shader", "link": "https://mcpedl.com/extreme-shader/", "description": "⚠️ متطرف.", "emoji": "⚠️"},
    {"name": "Extreme v2", "link": "https://mcpedl.com/extreme-shader-v2/", "description": "☣️ إصدار ثاني.", "emoji": "☣️"},
    {"name": "Pro Shader", "link": "https://mcpedl.com/pro-shader/", "description": "💼 احترافي.", "emoji": "💼"},
    {"name": "Pro v2", "link": "https://mcpedl.com/pro-shader-v2/", "description": "📈 نسخة محسنة.", "emoji": "📈"},
    {"name": "Elite Shader", "link": "https://mcpedl.com/elite-shader/", "description": "👑 نخبة.", "emoji": "👑"},
    {"name": "Elite v2", "link": "https://mcpedl.com/elite-shader-v2/", "description": "💎 إصدار جديد.", "emoji": "💎"},
    {"name": "Prime Shader", "link": "https://mcpedl.com/prime-shader/", "description": "🔑 أساسي.", "emoji": "🔑"},
    {"name": "Prime v2", "link": "https://mcpedl.com/prime-shader-v2/", "description": "🗝️ نسخة ثانية.", "emoji": "🗝️"},
    {"name": "Max Shader", "link": "https://mcpedl.com/max-shader/", "description": "📊 الحد الأقصى.", "emoji": "📊"},
    {"name": "Max v2", "link": "https://mcpedl.com/max-shader-v2/", "description": "📈 إصدار جديد.", "emoji": "📈"},
    {"name": "Supreme Shader", "link": "https://mcpedl.com/supreme-shader/", "description": "🏆 الأسمى.", "emoji": "🏆"},
    {"name": "Supreme v2", "link": "https://mcpedl.com/supreme-shader-v2/", "description": "🥇 نسخة محسنة.", "emoji": "🥇"},
    {"name": "Ultimate Shader", "link": "https://mcpedl.com/ultimate-shader/", "description": "💯 النهائي.", "emoji": "💯"},
    {"name": "Ultimate v2", "link": "https://mcpedl.com/ultimate-shader-v2/", "description": "🎖️ إصدار ثاني.", "emoji": "🎖️"},
    {"name": "Infinite Shader", "link": "https://mcpedl.com/infinite-shader/", "description": "♾️ لا نهائي.", "emoji": "♾️"},
    {"name": "Infinite v2", "link": "https://mcpedl.com/infinite-shader-v2/", "description": "🔁 نسخة جديدة.", "emoji": "🔁"},
    {"name": "Eternal Shader", "link": "https://mcpedl.com/eternal-shader/", "description": "⏳ أبدي.", "emoji": "⏳"},
    {"name": "Eternal v2", "link": "https://mcpedl.com/eternal-shader-v2/", "description": "⌛ إصدار ثاني.", "emoji": "⌛"},
    {"name": "Immortal Shader", "link": "https://mcpedl.com/immortal-shader/", "description": "🧬 خالد.", "emoji": "🧬"},
    {"name": "Immortal v2", "link": "https://mcpedl.com/immortal-shader-v2/", "description": "💪 نسخة محسنة.", "emoji": "💪"},
    {"name": "Legendary Shader", "link": "https://mcpedl.com/legendary-shader/", "description": "🐉 أسطوري.", "emoji": "🐉"},
    {"name": "Legendary v2", "link": "https://mcpedl.com/legendary-shader-v2/", "description": "⚔️ إصدار جديد.", "emoji": "⚔️"},
    {"name": "Mythic Shader", "link": "https://mcpedl.com/mythic-shader/", "description": "🔮 خرافي.", "emoji": "🔮"},
    {"name": "Mythic v2", "link": "https://mcpedl.com/mythic-shader-v2/", "description": "🧙 نسخة ثانية.", "emoji": "🧙"},
    {"name": "Divine Shader", "link": "https://mcpedl.com/divine-shader/", "description": "😇 إلهي.", "emoji": "😇"},
    {"name": "Divine v2", "link": "https://mcpedl.com/divine-shader-v2/", "description": "✝️ إصدار جديد.", "emoji": "✝️"},
    {"name": "Godlike Shader", "link": "https://mcpedl.com/godlike-shader/", "description": "🌟 كالإله.", "emoji": "🌟"},
    {"name": "Godlike v2", "link": "https://mcpedl.com/godlike-shader-v2/", "description": "💫 نسخة محسنة.", "emoji": "💫"},
    {"name": "Shadow Shader", "link": "https://mcpedl.com/shadow-shader/", "description": "👤 ظلال.", "emoji": "👤"},
    {"name": "Shadow v2", "link": "https://mcpedl.com/shadow-shader-v2/", "description": "🌑 إصدار ثاني.", "emoji": "🌑"},
    {"name": "Light Shader", "link": "https://mcpedl.com/light-shader/", "description": "💡 ضوء.", "emoji": "💡"},
    {"name": "Light v2", "link": "https://mcpedl.com/light-shader-v2/", "description": "🔆 نسخة جديدة.", "emoji": "🔆"},
    {"name": "Day Shader", "link": "https://mcpedl.com/day-shader/", "description": "🌞 نهار.", "emoji": "🌞"},
    {"name": "Day v2", "link": "https://mcpedl.com/day-shader-v2/", "description": "☀️ إصدار ثاني.", "emoji": "☀️"},
    {"name": "Night Shader", "link": "https://mcpedl.com/night-shader/", "description": "🌙 ليل.", "emoji": "🌙"},
    {"name": "Night v2", "link": "https://mcpedl.com/night-shader-v2/", "description": "🌛 نسخة محسنة.", "emoji": "🌛"},
    {"name": "Sun Shader", "link": "https://mcpedl.com/sun-shader/", "description": "☀️ شمس.", "emoji": "☀️"},
    {"name": "Sun v2", "link": "https://mcpedl.com/sun-shader-v2/", "description": "🌅 إصدار جديد.", "emoji": "🌅"},
    {"name": "Moon Shader", "link": "https://mcpedl.com/moon-shader/", "description": "🌕 قمر.", "emoji": "🌕"},
    {"name": "Moon v2", "link": "https://mcpedl.com/moon-shader-v2/", "description": "🌖 نسخة ثانية.", "emoji": "🌖"},
    {"name": "Star Shader", "link": "https://mcpedl.com/star-shader/", "description": "⭐ نجوم.", "emoji": "⭐"},
    {"name": "Star v2", "link": "https://mcpedl.com/star-shader-v2/", "description": "🌟 إصدار جديد.", "emoji": "🌟"},
    {"name": "Cloud Shader", "link": "https://mcpedl.com/cloud-shader/", "description": "☁️ غيوم.", "emoji": "☁️"},
    {"name": "Cloud v2", "link": "https://mcpedl.com/cloud-shader-v2/", "description": "🌥️ نسخة محسنة.", "emoji": "🌥️"},
    {"name": "Rain Shader", "link": "https://mcpedl.com/rain-shader/", "description": "🌧️ مطر.", "emoji": "🌧️"},
    {"name": "Rain v2", "link": "https://mcpedl.com/rain-shader-v2/", "description": "☔ إصدار ثاني.", "emoji": "☔"},
    {"name": "Storm Shader", "link": "https://mcpedl.com/storm-shader/", "description": "⛈️ عاصفة.", "emoji": "⛈️"},
    {"name": "Storm v2", "link": "https://mcpedl.com/storm-shader-v2/", "description": "🌩️ نسخة جديدة.", "emoji": "🌩️"},
    {"name": "Wind Shader", "link": "https://mcpedl.com/wind-shader/", "description": "🌬️ رياح.", "emoji": "🌬️"},
    {"name": "Wind v2", "link": "https://mcpedl.com/wind-shader-v2/", "description": "💨 إصدار ثاني.", "emoji": "💨"},
    {"name": "Fire Shader", "link": "https://mcpedl.com/fire-shader/", "description": "🔥 نار.", "emoji": "🔥"},
    {"name": "Fire v2", "link": "https://mcpedl.com/fire-shader-v2/", "description": "🎇 نسخة محسنة.", "emoji": "🎇"},
    {"name": "Ice Shader", "link": "https://mcpedl.com/ice-shader/", "description": "❄️ جليد.", "emoji": "❄️"},
    {"name": "Ice v2", "link": "https://mcpedl.com/ice-shader-v2/", "description": "🧊 إصدار جديد.", "emoji": "🧊"},
    {"name": "Earth Shader", "link": "https://mcpedl.com/earth-shader/", "description": "🌍 أرض.", "emoji": "🌍"},
    {"name": "Earth v2", "link": "https://mcpedl.com/earth-shader-v2/", "description": "🌎 نسخة ثانية.", "emoji": "🌎"},
    {"name": "Water Shader", "link": "https://mcpedl.com/water-shader/", "description": "💧 ماء.", "emoji": "💧"},
    {"name": "Water v2", "link": "https://mcpedl.com/water-shader-v2/", "description": "🌊 إصدار جديد.", "emoji": "🌊"},
    {"name": "Nature Shader", "link": "https://mcpedl.com/nature-shader/", "description": "🌳 طبيعة.", "emoji": "🌳"},
    {"name": "Nature v2", "link": "https://mcpedl.com/nature-shader-v2/", "description": "🌲 نسخة محسنة.", "emoji": "🌲"},
]

# تقسيم الشادرات حسب الاسم (الكلمة الأولى) مع تجميع المتشابهات
SHADERS = {}
for item in SHADERS_RAW:
    name = item.get("name", "")
    # استخراج الكلمة الأولى من الاسم
    first_word = name.split()[0] if name else "أخرى"
    
    # توحيد بعض الأسماء الشائعة
    if first_word in ["SEUS", "ESTN", "BSBE", "Haptic", "Zebra", "Newb", "Source", "Continuum", "Sildur's", "Chocapic13", "BSL", "KUDA", "Beyond", "Evident", "Natural", "Reality", "Enhanced", "Bare", "Mizuno's", "Stay", "ProjectLUMA", "AstraLex", "Voyager", "Creeper", "Ultra", "Kappa", "RRe36's", "SORA", "Vanilla", "Simple", "Pixel", "Retro", "CRUSH", "ESBE", "YSS", "Vibrant", "Dramatic", "Realistico", "Pinnacle", "Bliss", "Nostalgia", "Triliton's", "Soritong", "Pampas", "Llama", "Mellow", "Sakura", "Zenith", "Fusion", "Mystic", "Radiant", "Aurora", "Eclipse", "Nebula", "Cosmic", "Solar", "Lunar", "Stellar", "Galaxy", "Photon", "Quantum", "Ion", "Plasma", "Pulse", "Wave", "Flux", "Dynamo", "Volt", "Core", "Titan", "Colossus", "Atlas", "Hyper", "Extreme", "Pro", "Elite", "Prime", "Max", "Supreme", "Ultimate", "Infinite", "Eternal", "Immortal", "Legendary", "Mythic", "Divine", "Godlike", "Shadow", "Light", "Day", "Night", "Sun", "Moon", "Star", "Cloud", "Rain", "Storm", "Wind", "Fire", "Ice", "Earth", "Water", "Nature"]:
        pass  # نتركها كما هي
    else:
        # تجميع الباقي في فئة "شادرات متنوعة"
        first_word = "شادرات متنوعة"
    
    if first_word not in SHADERS:
        SHADERS[first_word] = []
    
    # التأكد من وجود أيقونة
    if "icon" not in item:
        item["icon"] = item.get("emoji", "🌞")
    SHADERS[first_word].append(item)

# ====================== 5. إصدارات اللعبة ======================
GAME_VERSIONS = {
    "إصدارات 1.24 القديمة": [
        {"num": "1️⃣", "name": "الإصدار 1.24.0", "icon": "🔴", "link": "https://mcpedl.org/pt/minecraft-pe-1.24.0-apk/"},
        {"num": "2️⃣", "name": "الإصدار 1.24.10", "icon": "🔴", "link": "https://mcpedl.org/pt/minecraft-pe-1.24.10-apk/"},
        {"num": "3️⃣", "name": "الإصدار 1.24.20", "icon": "🔴", "link": "https://mcpedl.org/pt/minecraft-pe-1.24.20-apk/"},
        {"num": "4️⃣", "name": "الإصدار 1.24.30", "icon": "🔴", "link": "https://mcpedl.org/pt/minecraft-pe-1.24.30-apk/"},
    ],
    "إصدارات 26.x الجديدة": [
        {"num": "5️⃣", "name": "الإصدار 26.0 (فبراير)", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-0-apk/"},
        {"num": "6️⃣", "name": "الإصدار 26.1", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-1-apk/"},
        {"num": "7️⃣", "name": "الإصدار 26.3.1", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-3-1-apk/"},
        {"num": "8️⃣", "name": "الإصدار 26.20", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-20-apk/"},
        {"num": "9️⃣", "name": "الإصدار 26.30", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-30-apk/"},
        {"num": "🔟", "name": "الإصدار 26.32", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-32-apk/"},
        {"num": "1️⃣1️⃣", "name": "الإصدار 26.33", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-33-apk/"},
        {"num": "1️⃣2️⃣", "name": "الإصدار 26.40", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-40-apk/"},
        {"num": "1️⃣3️⃣", "name": "الإصدار 26.44", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-44-apk/"},
        {"num": "1️⃣4️⃣", "name": "الإصدار 26.45 (الأحدث)", "icon": "🟤", "link": "https://mcpedl.org/pt/minecraft-pe-26-45-apk/"},
    ],
}

# ====================== تجميع الأقسام الرئيسية ======================
MAIN_CATEGORIES = {
    "mods": {"title": "✦ مودات - MoDs ☠️ ✦", "subcategories": MODS, "prefix": "mods"},
    "maps": {"title": "✦ مابات - MaPs 💎 ✦", "subcategories": MAPS, "prefix": "maps"},
    "resus": {"title": "✦ ريـسـوس بـاكـات ⚡ ✦", "subcategories": RESUS_PACKS, "prefix": "resus"},
    "shaders": {"title": "✦ شـادرات 🌞 ✦", "subcategories": SHADERS, "prefix": "shaders"},
    "versions": {"title": "✦ إصدارات اللعبة 📥 ✦", "subcategories": GAME_VERSIONS, "prefix": "versions"},
}

ITEMS_PER_PAGE = 6

# ====================== صلاحيات المطور والمشرفين ======================
DEVELOPER_ID = 7370937034  # ضع هنا أي دي المطور
MODS_IDS = {
    111111111,  # المشرف الأول
    222222222,  # المشرف الثاني
}

DATA_FILE = "bot_data.json"
USERS_FILE = "bot_users.json"
MODS_FILE = "staff_mods.json"
SUBSCRIPTIONS_FILE = "subscriptions.json"
SUBSCRIPTIONS = []

def load_mods_ids():
    global MODS_IDS
    try:
        if os.path.exists(MODS_FILE):
            with open(MODS_FILE,"r",encoding="utf-8") as f: MODS_IDS={int(x) for x in json.load(f)}
    except Exception: logging.exception("فشل تحميل المشرفين")
load_mods_ids()

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return {int(x) for x in json.load(f)}
    except Exception:
        logging.exception("فشل تحميل قائمة المستخدمين")
        return set()

USERS = load_users()

def register_user(update: Update):
    user = update.effective_user
    if not user or user.id in USERS:
        return
    USERS.add(user.id)
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(USERS), f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("فشل حفظ قائمة المستخدمين")

def is_staff(update: Update) -> bool:
    user = update.effective_user
    return bool(user and (user.id == DEVELOPER_ID or user.id in MODS_IDS))

def is_developer(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == DEVELOPER_ID)

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({key: cat["subcategories"] for key, cat in MAIN_CATEGORIES.items()}, f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("فشل حفظ البيانات")

def load_data():
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        for key, subcategories in saved.items():
            if key in MAIN_CATEGORIES and isinstance(subcategories, dict):
                MAIN_CATEGORIES[key]["subcategories"] = subcategories
    except Exception:
        logging.exception("فشل تحميل البيانات")

load_data()

def load_subscriptions():
    global SUBSCRIPTIONS
    try:
        if os.path.exists(SUBSCRIPTIONS_FILE):
            with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
                data=json.load(f); SUBSCRIPTIONS=data if isinstance(data,list) else []
    except Exception: logging.exception("فشل تحميل الاشتراكات")

def save_subscriptions():
    try:
        with open(SUBSCRIPTIONS_FILE,"w",encoding="utf-8") as f: json.dump(SUBSCRIPTIONS,f,ensure_ascii=False,indent=2)
    except Exception: logging.exception("فشل حفظ الاشتراكات")
load_subscriptions()

# ====================== النشر التلقائي اليومي ======================
# ضع معرف القناة والمجموعة هنا.
# يمكن أن يكون المعرف رقمًا مثل -1001234567890 أو اسم مستخدم مثل @my_channel
AUTO_POST_CHANNEL = os.environ.get("AUTO_POST_CHANNEL", "@YOUR_CHANNEL")
AUTO_POST_GROUP = os.environ.get("AUTO_POST_GROUP", "@YOUR_GROUP")

AUTO_POST_FILE = "auto_post_state.json"

# ===== إرسال رسالة للمشتركين =====
BROADCAST_MODE = {}
AUTO_POST_HOUR = 20       # الساعة 8 مساءً بتوقيت اليمن
AUTO_POST_MINUTE = 0
AUTO_POST_STATUS_FILE = "auto_post_status.json"

def load_auto_post_enabled():
    try:
        if os.path.exists(AUTO_POST_STATUS_FILE):
            with open(AUTO_POST_STATUS_FILE, "r", encoding="utf-8") as f:
                return bool(json.load(f).get("enabled", True))
    except Exception:
        logging.exception("فشل تحميل حالة البوت")
    return True

def save_auto_post_enabled(enabled):
    try:
        with open(AUTO_POST_STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"enabled": bool(enabled)}, f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("فشل حفظ حالة البوت")

AUTO_POST_ENABLED = load_auto_post_enabled()

def load_auto_post_index():
    try:
        if os.path.exists(AUTO_POST_FILE):
            with open(AUTO_POST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("next_index", 0))
    except Exception:
        logging.exception("فشل تحميل حالة النشر التلقائي")
    return 0

def save_auto_post_index(index):
    try:
        with open(AUTO_POST_FILE, "w", encoding="utf-8") as f:
            json.dump({"next_index": index}, f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("فشل حفظ حالة النشر التلقائي")

AUTO_POST_INDEX = load_auto_post_index()

def get_auto_post_mods():
    # النشر من قسم "جميع المودات" بالتسلسل
    return MODS.get("جميع المودات", [])

def build_mod_post(item):
    name = item.get("name", "مود جديد")
    icon = item.get("icon", "🔥")
    link = item.get("link", "")
    return (
        f"{icon} <b>{name}</b>\n\n"
        "✨ مود جديد من بوت مودات ماين كرافت!\n"
        "📥 اضغط الزر بالأسفل للتحميل."
    ), link

async def auto_post_two_mods(context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_INDEX

    if not AUTO_POST_ENABLED:
        logging.info("⏸️ النشر التلقائي متوقف.")
        return

    if AUTO_POST_CHANNEL == "@YOUR_CHANNEL" or AUTO_POST_GROUP == "@YOUR_GROUP":
        logging.warning("⚠️ لم يتم ضبط AUTO_POST_CHANNEL و AUTO_POST_GROUP.")
        return

    mods = get_auto_post_mods()
    if not mods:
        logging.warning("⚠️ لا توجد مودات للنشر التلقائي.")
        return

    # إذا وصلنا للنهاية نبدأ من أول القائمة مرة أخرى
    selected = []
    for _ in range(min(2, len(mods))):
        item = mods[AUTO_POST_INDEX % len(mods)]
        selected.append(item)
        AUTO_POST_INDEX = (AUTO_POST_INDEX + 1) % len(mods)

    # نشر المودين في القناة والمجموعة
    for item in selected:
        text, link = build_mod_post(item)
        keyboard = []
        if link:
            # حفظ موقع العنصر بدل فتح رابط خارجي.
            _found = None
            for _ck, _cat in MAIN_CATEGORIES.items():
                for _sn, _items in _cat.get("subcategories", {}).items():
                    for _ii, _it in enumerate(_items):
                        if _it is item:
                            _found = (_ck, list(_cat["subcategories"].keys()).index(_sn), _ii)
                            break
                    if _found:
                        break
                if _found:
                    break
            if _found:
                _ck, _si, _ii = _found
                keyboard = [[InlineKeyboardButton(
                    "⬇️ تحميل المود وإرساله لي",
                    callback_data=f"download_mod:{_ck}:{_si}:{_ii}"
                )]]
        markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        for chat_id in (AUTO_POST_CHANNEL, AUTO_POST_GROUP):
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            except Exception:
                logging.exception("❌ فشل نشر مود في %s", chat_id)

    save_auto_post_index(AUTO_POST_INDEX)
    logging.info("✅ تم نشر %d مود تلقائيًا.", len(selected))

async def post_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_developer(update):
        await update.message.reply_text("❌ هذا الأمر خاص بالمطور فقط.")
        return
    await auto_post_two_mods(context)
    await update.message.reply_text("✅ تم تنفيذ نشر مودين الآن في القناة والمجموعة.")

# ====================== دوال العرض ======================

# ====================== صور ووصف المودات ======================
MOD_IMAGES_DIR = "mod_images"
os.makedirs(MOD_IMAGES_DIR, exist_ok=True)

def get_mod_description(item):
    """الوصف المخصص للمود، أو وصف تلقائي إذا لم تتم إضافته."""
    description = item.get("description")
    if description:
        return str(description)

    name = item.get("name", "هذا المود")
    return (
        f"🛠️ <b>{name}</b>\n\n"
        "✨ مود لماينكرافت يضيف محتوى جديدًا إلى اللعبة.\n"
        "📌 اضغط على زر التحميل للحصول على الرابط."
    )


def _safe_filename(value):
    value = re.sub(r"[^\w\u0600-\u06FF-]+", "_", str(value))
    return value[:80] or "mod"


def get_mod_card_image(item):
    """
    إذا أضفت image/photo داخل بيانات المود سيُستخدم الرابط كصورة.
    وإلا يتم إنشاء صورة تعريفية تلقائيًا للمود وحفظها محليًا.
    """
    image_url = item.get("image") or item.get("photo")
    if isinstance(image_url, str) and image_url.startswith(("http://", "https://")):
        return image_url

    name = str(item.get("name", "Minecraft Mod"))
    icon = str(item.get("icon", "🛠️"))
    filename = os.path.join(MOD_IMAGES_DIR, _safe_filename(name) + ".png")

    if not os.path.exists(filename):
        # بطاقة تعريفية بسيطة وفريدة لكل مود.
        img = Image.new("RGB", (900, 500), (25, 35, 50))
        draw = ImageDraw.Draw(img)

        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        except Exception:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.rounded_rectangle((20, 20, 880, 480), radius=35, outline=(80, 170, 255), width=5)
        draw.text((450, 105), icon, font=font_big, anchor="mm")
        draw.text((450, 230), "MINECRAFT MOD", font=font_small, anchor="mm")
        # الاسم قد يظهر RTL بشكل مبسط، بينما الاسم الإنجليزي يظهر طبيعيًا.
        draw.text((450, 330), name[:28], font=font_big, anchor="mm")
        draw.text((450, 425), "MOD DETAILS", font=font_small, anchor="mm")
        img.save(filename)

    return filename


async def show_mod_details(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           category_key: str, sub_index: int, item_index: int):
    query = update.callback_query
    if await subscriber_gate(update, context):
        return

    try:
        sub_names = list(MAIN_CATEGORIES[category_key]["subcategories"].keys())
        sub_name = sub_names[sub_index]
        items = MAIN_CATEGORIES[category_key]["subcategories"][sub_name]
        item = items[item_index]
    except (KeyError, IndexError, TypeError):
        await query.answer("❌ المود غير موجود.", show_alert=True)
        return

    await query.answer()

    description = get_mod_description(item)
    caption = (
        f"📦 <b>{item.get('name', 'مود')}</b>\n\n"
        f"{description}\n\n"
        f"📂 القسم: <b>{sub_name}</b>"
    )

    image = get_mod_card_image(item)
    keyboard = []
    link = str(item.get("link", ""))
    if link.startswith(("http://", "https://")):
        sub_index = list(MAIN_CATEGORIES[category_key]["subcategories"].keys()).index(sub_name)
        keyboard.append([
            InlineKeyboardButton(
                "⬇️ تحميل المود وإرساله لي",
                callback_data=f"download_mod:{category_key}:{sub_index}:{item_index}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton("🔙 رجوع", callback_data=f"items_{category_key}_{sub_name}_{item_index // ITEMS_PER_PAGE}"),
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")
    ])

    try:
        await query.message.reply_photo(
            photo=image,
            caption=caption[:1024],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    except Exception:
        # إذا كانت الصورة غير قابلة للإرسال، نعرض الوصف بدون صورة.
        await query.message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )


def build_list_text(items, page, per_page):
    start = page * per_page
    end = min(start + per_page, len(items))
    total = len(items)
    
    header = "╔" + "═" * 38 + "╗\n"
    header += f"║  📦  إجمالي العناصر: {total}  📦  ║\n"
    header += "╚" + "═" * 38 + "╝\n"
    header += "┌" + "─" * 38 + "┐\n"
    
    text = header
    for i in range(start, end):
        item = items[i]
        num = item.get('num', f"{i+1}.")
        name = item.get('name', 'بدون اسم')
        icon = item.get('icon', '🔹')
        line = f"│  {num}  {name}  {icon}  │\n"
        text += line
    
    text += "└" + "─" * 38 + "┘\n"
    text += f"\n📌 الصفحة {page+1} من {(total + per_page - 1)//per_page}"
    text += "\n𓆩  ⬅️  استخدم الأزرار للتنقل  ⬅️  𓆪"
    return text, start, end

def build_keyboard(items, page, per_page, prefix, back_callback=None):
    keyboard = []
    start = page * per_page
    end = min(start + per_page, len(items))

    # استخراج القسم من prefix عندما يكون من نوع items_mods_...
    category_key = None
    if prefix.startswith("items_"):
        parts = prefix.split("_", 2)
        if len(parts) >= 2:
            category_key = parts[1]

    sub_index = None
    if category_key in MAIN_CATEGORIES:
        # prefix يحتوي اسم الفئة الفرعية وقد يكون عربيًا.
        sub_part = prefix.split("_", 2)[2] if len(prefix.split("_", 2)) > 2 else ""
        sub_names = list(MAIN_CATEGORIES[category_key]["subcategories"].keys())
        for idx, name in enumerate(sub_names):
            if name == sub_part:
                sub_index = idx
                break

    for i in range(start, end):
        item = items[i]
        name = item.get('name', 'عنصر')
        link = item.get('link', '#')
        short_name = name[:12] + '..' if len(name) > 12 else name

        # المودات: تفاصيل + تحميل.
        if category_key == "mods" and sub_index is not None:
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 تفاصيل {short_name}",
                    callback_data=f"modview_{category_key}_{sub_index}_{i}"
                )
            ])
            if isinstance(link, str) and link.startswith(("http://", "https://")):
                keyboard.append([
                    InlineKeyboardButton(f"⬇️ تحميل {short_name}", url=link)
                ])
        else:
            if isinstance(link, str) and link.startswith(("http://", "https://")):
                keyboard.append([
                    InlineKeyboardButton(f"⬇️ تحميل {short_name}", url=link)
                ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ السابق", callback_data=f"{prefix}_{page-1}"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton("التالي ▶️", callback_data=f"{prefix}_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    back_row = []
    if back_callback:
        back_row.append(InlineKeyboardButton("🔙 رجوع", callback_data=back_callback))
    back_row.append(InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu"))
    keyboard.append(back_row)

    return InlineKeyboardMarkup(keyboard)


async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_ENABLED
    if not is_developer(update):
        await update.message.reply_text("❌ هذا الأمر خاص بالمطور فقط.")
        return
    AUTO_POST_ENABLED = False
    save_auto_post_enabled(False)
    await update.message.reply_text("⏸️ تم إيقاف النشر التلقائي. البوت نفسه ما زال يعمل ويمكنك تشغيله من جديد.")

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_ENABLED
    if not is_developer(update):
        await update.message.reply_text("❌ هذا الأمر خاص بالمطور فقط.")
        return
    AUTO_POST_ENABLED = True
    save_auto_post_enabled(True)
    await update.message.reply_text("▶️ تم تشغيل النشر التلقائي من جديد.")

# ====================== لوحة تحكم المطور والمشرفين ======================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_developer(update):
        await update.message.reply_text("⛔ هذه الخاصية للمطور فقط.")
        return

    BROADCAST_MODE[update.effective_user.id] = True
    await update.message.reply_text(
        "📢 وضع إرسال رسالة للمشتركين مفعّل.\n\n"
        "أرسل الآن الرسالة التي تريد إرسالها لجميع المشتركين.\n"
        "يمكنك إرسال نص، أو صورة مع وصف، أو ملف.\n\n"
        "❌ للإلغاء أرسل /cancel_broadcast"
    )


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_developer(update):
        return
    BROADCAST_MODE.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ تم إلغاء إرسال الرسالة للمشتركين.")


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_developer(update):
        return False

    if user.id not in BROADCAST_MODE:
        return False

    message = update.effective_message
    if not message:
        return True

    sent = 0
    failed = 0

    for chat_id in list(USERS):
        try:
            await message.copy(chat_id=chat_id)
            sent += 1
        except Exception as e:
            failed += 1
            logging.warning("فشل إرسال الرسالة إلى %s: %s", chat_id, e)

    BROADCAST_MODE.pop(user.id, None)

    await message.reply_text(
        f"📢 تم إرسال الرسالة للمشتركين.\n\n"
        f"✅ نجح: {sent}\n"
        f"❌ فشل: {failed}\n"
        f"👥 إجمالي المشتركين: {len(USERS)}"
    )
    return True

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_staff(update):
        await update.message.reply_text("❌ هذه اللوحة خاصة بالمطور والمشرفين فقط.")
        return
    role = "👑 المطور" if is_developer(update) else "🛡️ مشرف"
    post = "🟢 يعمل" if AUTO_POST_ENABLED else "🔴 متوقف"
    users = "🟢 يعمل" if SUBSCRIBERS_BOT_ENABLED else "🔴 متوقف"
    keyboard = [
        [InlineKeyboardButton("👥 عدد المشتركين", callback_data="admin_users")],
        [InlineKeyboardButton("📢 إرسال رسالة للمشتركين", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📢 إدارة الاشتراك", callback_data="admin_subscriptions")],
        [InlineKeyboardButton("➕ إضافة عنصر", callback_data="admin_add"), InlineKeyboardButton("➖ حذف عنصر", callback_data="admin_delete")],
        [InlineKeyboardButton("⏸️ إيقاف النشر", callback_data="admin_stop_posting"), InlineKeyboardButton("▶️ تشغيل النشر", callback_data="admin_start_posting")],
        [InlineKeyboardButton("⏸️ إيقاف البوت للمشتركين", callback_data="admin_stop_subscribers"), InlineKeyboardButton("▶️ تشغيل البوت للمشتركين", callback_data="admin_start_subscribers")],
    ]
    if is_developer(update): keyboard.append([InlineKeyboardButton("👥 إدارة المشرفين", callback_data="admin_mods")])
    await update.message.reply_text(f"🛠️ <b>لوحة التحكم</b>\n\nصلاحيتك: {role}\n📢 النشر التلقائي: {post}\n👥 البوت للمشتركين: {users}\n\nاختر العملية:",reply_markup=InlineKeyboardMarkup(keyboard),parse_mode="HTML")

async def admin_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query=update.callback_query
    if not is_staff(update): await query.answer("❌ غير مصرح لك.",show_alert=True); return
    await query.answer(); context.user_data["admin_action"]="subscriptions"
    lines=["📢 <b>إدارة الاشتراك الإجباري</b>",""]
    if SUBSCRIPTIONS:
        for i,ch in enumerate(SUBSCRIPTIONS,1): lines.append(f"{i}. {html.escape(str(ch.get('name','قناة')))} — <code>{html.escape(str(ch.get('chat_id','')))}</code>")
    else: lines.append("لا توجد قنوات مضافة.")
    lines += ["","💡 يمكنك الإضافة أو الحذف من الأزرار بالأسفل."]
    keyboard = [
        [InlineKeyboardButton("➕ إضافة اشتراك", callback_data="admin_subscription_add")],
        [InlineKeyboardButton("➖ حذف اشتراك", callback_data="admin_subscription_delete")],
        [InlineKeyboardButton("🔙 لوحة التحكم", callback_data="admin_panel")],
    ]
    await query.edit_message_text("\n".join(lines),parse_mode="HTML",reply_markup=InlineKeyboardMarkup(keyboard))

async def check_user_subscription(bot,user_id):
    if not SUBSCRIPTIONS: return True
    for ch in SUBSCRIPTIONS:
        if ch.get("type") == "addlist" or not ch.get("chat_id"):
            continue
        try:
            m=await bot.get_chat_member(ch.get("chat_id"),user_id)
            if m.status in {"left","kicked"}: return False
        except Exception as e:
            logging.warning("فشل التحقق من الاشتراك: %s",e); return False
    return True

async def subscription_gate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_staff(update) or not update.effective_user: return False
    if await check_user_subscription(context.bot,update.effective_user.id): return False
    msg=update.effective_message
    if not msg: return True
    kb=[]
    for ch in SUBSCRIPTIONS:
        url=ch.get("url")
        if isinstance(url,str) and url.startswith(("http://","https://")): kb.append([InlineKeyboardButton(f"📢 {ch.get('name','اشترك')}",url=url)])
    kb.append([InlineKeyboardButton("✅ تحقق من الاشتراك",callback_data="check_subscription")])
    await msg.reply_text("🔒 <b>الاشتراك مطلوب</b>\n\nاشترك في القنوات ثم اضغط تحقق من الاشتراك.",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML")
    return True

async def admin_categories(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    query = update.callback_query
    if not is_staff(update):
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return
    await query.answer()
    context.user_data["admin_action"] = action
    keyboard = []
    for key, cat in MAIN_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(cat["title"], callback_data=f"admincat_{action}_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 إلغاء", callback_data="admin_cancel")])
    await query.edit_message_text(
        "📂 <b>اختر القسم:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def admin_subcategories(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, category_key: str):
    query = update.callback_query
    if not is_staff(update):
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return
    await query.answer()
    context.user_data["admin_action"] = action
    context.user_data["admin_category"] = category_key
    keyboard = []
    for idx, sub_name in enumerate(MAIN_CATEGORIES[category_key]["subcategories"]):
        keyboard.append([InlineKeyboardButton(f"📂 {sub_name}", callback_data=f"adminsub_{action}_{category_key}_{idx}")])
    keyboard.append([InlineKeyboardButton("🔙 إلغاء", callback_data="admin_cancel")])
    await query.edit_message_text(
        "📁 <b>اختر الفئة:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def admin_select_sub(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, category_key: str, index: int):
    query = update.callback_query
    if not is_staff(update):
        await query.answer("❌ غير مصرح لك.", show_alert=True)
        return
    await query.answer()
    subcats = list(MAIN_CATEGORIES[category_key]["subcategories"].keys())
    if index < 0 or index >= len(subcats):
        await query.edit_message_text("❌ الفئة غير موجودة.")
        return
    sub_name = subcats[index]
    context.user_data["admin_category"] = category_key
    context.user_data["admin_sub"] = sub_name
    context.user_data["admin_action"] = action

    if action == "add":
        await query.edit_message_text(
            f"➕ <b>إضافة عنصر إلى:</b> {sub_name}\n\n"
            "أرسل في رسالة واحدة بهذا الشكل:\n"
            "<code>اسم العنصر | الرابط | الأيقونة</code>\n\n"
            "مثال: <code>مود جديد | https://example.com | 🔥</code>",
            parse_mode="HTML"
        )
    else:
        items = MAIN_CATEGORIES[category_key]["subcategories"][sub_name]
        if not items:
            await query.edit_message_text("❌ لا توجد عناصر في هذه الفئة.")
            return
        lines = [f"{i+1}. {item.get('name', 'بدون اسم')}" for i, item in enumerate(items)]
        await query.edit_message_text(
            f"➖ <b>حذف عنصر من:</b> {sub_name}\n\n"
            + "\n".join(lines)
            + "\n\nأرسل <b>رقم العنصر</b> الذي تريد حذفه.",
            parse_mode="HTML"
        )

async def admin_mods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_developer(update):
        await query.answer("❌ هذه الخاصية للمطور فقط.", show_alert=True)
        return
    await query.answer()
    mods = sorted(MODS_IDS)
    text = "👥 <b>المشرفون الحاليون:</b>\n\n" + ("\n".join(f"• <code>{x}</code>" for x in mods) if mods else "لا يوجد مشرفون")
    text += "\n\nلإضافة مشرف، أرسل: <code>add 123456789</code>\nلحذف مشرف، أرسل: <code>del 123456789</code>"
    context.user_data["admin_action"] = "mods"
    await query.edit_message_text(text, parse_mode="HTML")

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("✅ تم إلغاء العملية. أرسل /panel لفتح لوحة التحكم.")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_staff(update):
        return
    action = context.user_data.get("admin_action")
    if not action:
        return
    text = (update.message.text or "").strip()

    if action == "subscriptions":
        if text.lower().startswith("del "):
            n=text.split(maxsplit=1)[1] if len(text.split(maxsplit=1))>1 else ""
            if not n.isdigit() or not 1 <= int(n) <= len(SUBSCRIPTIONS):
                await update.message.reply_text("❌ رقم القناة غير صحيح."); return
            removed=SUBSCRIPTIONS.pop(int(n)-1); save_subscriptions(); context.user_data.clear()
            await update.message.reply_text(f"✅ تم حذف: {removed.get('name','القناة')}"); return
        if not text.startswith(("http://", "https://")):
            await update.message.reply_text("❌ أرسل رابط الاشتراك فقط، مثال: https://t.me/mychannel"); return
        addlist = re.fullmatch(r"https?://t\.me/addlist/([A-Za-z0-9_-]+)(?:/)?", text)
        if addlist:
            code = addlist.group(1)
            SUBSCRIPTIONS.append({
                "name": f"addlist/{code}",
                "chat_id": None,
                "url": text,
                "type": "addlist"
            })
            save_subscriptions(); context.user_data.clear()
            await update.message.reply_text("✅ تمت إضافة رابط addlist بنجاح.")
            return

        m = re.fullmatch(r"https?://t\.me/([A-Za-z0-9_]+)(?:/)?", text)
        if not m:
            await update.message.reply_text(
                "❌ الرابط غير صحيح.\n\n"
                "المسموح: رابط قناة/مجموعة أو رابط addlist.\n"
                "مثال: https://t.me/mychannel\n"
                "أو: https://t.me/addlist/XXXXXXXX"
            )
            return
        username = m.group(1)
        try:
            chat = await context.bot.get_chat(f"@{username}")
        except Exception:
            await update.message.reply_text(
                "❌ لم أستطع العثور على القناة أو المجموعة.\n"
                "تأكد أن الرابط عام وأن البوت يستطيع الوصول إليها."
            )
            return

        if chat.type not in {"channel", "group", "supergroup"}:
            await update.message.reply_text(
                "❌ مسموح فقط بإضافة قناة أو مجموعة Telegram."
            )
            return

        chat_name = getattr(chat, "title", None) or f"@{username}"
        SUBSCRIPTIONS.append({
            "name": chat_name,
            "chat_id": chat.id,
            "url": f"https://t.me/{username}"
        })
        save_subscriptions(); context.user_data.clear()
        kind = "قناة" if chat.type == "channel" else "مجموعة"
        await update.message.reply_text(f"✅ تمت إضافة {kind}: {chat_name}")
        return

    if action == "mods":
        if not is_developer(update):
            await update.message.reply_text("❌ هذه العملية للمطور فقط.")
            return
        parts = text.split()
        if len(parts) != 2 or parts[0].lower() not in {"add", "del"} or not parts[1].isdigit():
            await update.message.reply_text("❌ الصيغة غير صحيحة. استخدم: add 123456789 أو del 123456789")
            return
        mod_id = int(parts[1])
        if parts[0].lower() == "add":
            MODS_IDS.add(mod_id)
            with open(MODS_FILE,"w",encoding="utf-8") as f: json.dump(sorted(MODS_IDS),f)
            await update.message.reply_text(f"✅ تمت إضافة المشرف: {mod_id}")
        else:
            MODS_IDS.discard(mod_id)
            with open(MODS_FILE,"w",encoding="utf-8") as f: json.dump(sorted(MODS_IDS),f)
            await update.message.reply_text(f"✅ تمت إزالة المشرف: {mod_id}")
        context.user_data.clear()
        return

    category_key = context.user_data.get("admin_category")
    sub_name = context.user_data.get("admin_sub")
    if category_key not in MAIN_CATEGORIES or not sub_name:
        context.user_data.clear()
        await update.message.reply_text("❌ انتهت العملية. أرسل /panel مرة أخرى.")
        return

    items = MAIN_CATEGORIES[category_key]["subcategories"].get(sub_name)
    if items is None:
        context.user_data.clear()
        await update.message.reply_text("❌ الفئة غير موجودة.")
        return

    if action == "add":
        parts = [x.strip() for x in text.split("|", 2)]
        if len(parts) < 2 or not parts[0] or not parts[1].startswith(("http://", "https://")):
            await update.message.reply_text("❌ الصيغة: اسم العنصر | الرابط | الأيقونة")
            return
        name, link = parts[0], parts[1]
        icon = parts[2] if len(parts) == 3 and parts[2] else "🔹"
        items.append({"num": f"{len(items)+1}️⃣", "name": name, "icon": icon, "link": link})
        save_data()
        context.user_data.clear()
        await update.message.reply_text(f"✅ تمت إضافة: {name}\n📁 الفئة: {sub_name}")
        return

    if action == "delete":
        if not text.isdigit():
            await update.message.reply_text("❌ أرسل رقم العنصر فقط.")
            return
        index = int(text) - 1
        if index < 0 or index >= len(items):
            await update.message.reply_text("❌ رقم العنصر غير صحيح.")
            return
        removed = items.pop(index)
        save_data()
        context.user_data.clear()
        await update.message.reply_text(f"✅ تم حذف: {removed.get('name', 'العنصر')}")


# ====================== البحث لجميع المستخدمين ======================
def normalize_search(value):
    """تطبيع النص العربي والإنجليزي حتى يعمل البحث مع اختلاف الكتابة."""
    value = str(value or "").strip().casefold()

    # إزالة التشكيل والتطويل.
    value = "".join(
        ch for ch in unicodedata.normalize("NFD", value)
        if unicodedata.category(ch) != "Mn"
    ).replace("ـ", "")

    # توحيد الحروف العربية المتشابهة.
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
        "ى": "ي", "ئ": "ي", "ؤ": "و",
        "ة": "ه",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)

    # توحيد المسافات والرموز الشائعة.
    value = re.sub(r"[\u200f\u200e]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


def search_all_items(keyword):
    """البحث في كل الأقسام والفئات، مع دعم أكثر من كلمة."""
    query = normalize_search(keyword)
    if not query:
        return []

    # البحث بالكلمات: يجب أن تظهر كل كلمات البحث في بيانات العنصر.
    words = [w for w in query.split() if w]

    results = []
    seen = set()

    for category_key, category in MAIN_CATEGORIES.items():
        category_title = category.get("title", category_key)
        subcategories = category.get("subcategories", {})

        for sub_name, items in subcategories.items():
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                name = str(item.get("name", ""))
                link = str(item.get("link", ""))
                icon = str(item.get("icon", "🔹"))

                searchable = normalize_search(
                    f"{name} {sub_name} {category_title} {link}"
                )

                # يدعم:
                # 1) تطابق العبارة كاملة
                # 2) تطابق جميع الكلمات حتى لو كانت متباعدة
                matched = query in searchable or all(
                    word in searchable for word in words
                )

                if not matched:
                    continue

                # منع التكرار.
                unique_key = (
                    category_key,
                    sub_name,
                    name,
                    link,
                )
                if unique_key in seen:
                    continue
                seen.add(unique_key)

                sub_index = list(subcategories.keys()).index(sub_name)
                item_index = items.index(item)
                results.append({
                    "name": name or "بدون اسم",
                    "icon": icon,
                    "link": link,
                    "category": category_title,
                    "subcategory": sub_name,
                    "category_key": category_key,
                    "sub_index": sub_index,
                    "item_index": item_index,
                })

    # ترتيب النتائج: الاسم المطابق مباشرة يظهر أولًا.
    results.sort(
        key=lambda x: (
            0 if query == normalize_search(x["name"]) else
            1 if query in normalize_search(x["name"]) else 2,
            normalize_search(x["name"])
        )
    )
    return results


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await subscriber_gate(update, context):
        return

    keyword = " ".join(context.args).strip()

    if not keyword:
        context.user_data["search_mode"] = True
        await update.message.reply_text(
            "🔎 <b>البحث في جميع الأقسام</b>\n\n"
            "أرسل اسم المود أو الماب أو الشادر أو الريسوس باك.\n\n"
            "مثال:\n"
            "<code>/search السيف</code>\n"
            "<code>/search zombie</code>\n"
            "<code>/search 26.45</code>\n\n"
            "❌ للإلغاء: /cancel_search",
            parse_mode="HTML"
        )
        return

    await send_search_results(update, keyword)


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("search_mode", None)
    await update.message.reply_text("❌ تم إلغاء البحث.")


async def send_search_results(update, keyword):
    results = search_all_items(keyword)

    if not results:
        await update.effective_message.reply_text(
            f"🔎 <b>لا توجد نتائج</b>\n\n"
            f"بحثت عن: <code>{keyword}</code>\n\n"
            "جرّب كلمة أقصر، مثل:\n"
            "• السيف\n"
            "• zombie\n"
            "• map\n"
            "• shader",
            parse_mode="HTML"
        )
        return

    # حفظ نتائج البحث حتى يستطيع المستخدم الانتقال بين الصفحات.
    update.effective_user and None
    if update.effective_message:
        # context.user_data غير متاح هنا، لذلك يعتمد العرض على أول 20 نتيجة.
        pass

    shown = results[:20]
    lines = [
        "╔══════════════════════════╗",
        "║      🔎 نتائج البحث      ║",
        "╚══════════════════════════╝",
        "",
        f"🔍 البحث: <b>{keyword}</b>",
        f"📊 النتائج: <b>{len(results)}</b>",
        ""
    ]

    keyboard = []

    for index, item in enumerate(shown, 1):
        lines.append(
            f"{index}. {item['icon']} <b>{item['name']}</b>\n"
            f"   📂 {item['subcategory']}"
        )

        if item["link"].startswith(("http://", "https://")):
            short_name = item["name"][:20] + "…" if len(item["name"]) > 20 else item["name"]
            keyboard.append([
                InlineKeyboardButton(
                    f"⬇️ {short_name}",
                    callback_data=(
                        f"download_mod:{item['category_key']}:{item['sub_index']}:{item['item_index']}"
                    )
                )
            ])

    if len(results) > 20:
        lines.append(
            f"\n⚠️ توجد {len(results) - 20} نتائج إضافية. "
            "استخدم كلمة بحث أكثر تحديدًا."
        )

    keyboard.append([
        InlineKeyboardButton("🔎 بحث جديد", callback_data="search_again"),
        InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")
    ])

    await update.effective_message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def handle_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("search_mode"):
        return False

    if await subscriber_gate(update, context):
        context.user_data.pop("search_mode", None)
        return True

    message = update.effective_message
    keyword = (message.text or "").strip() if message else ""

    if not keyword:
        await message.reply_text("❌ أرسل كلمة للبحث.")
        return True

    context.user_data.pop("search_mode", None)
    await send_search_results(update, keyword)
    return True



# ====================== تنزيل المود وإرساله للمشترك ======================
async def download_and_send_mod(update, context, item):
    message = update.effective_message
    if not message:
        return

    link = str(item.get("link", "")).strip()
    name = str(item.get("name", "مود")).strip() or "مود"

    if not link.startswith(("http://", "https://")):
        await message.reply_text("❌ رابط تحميل هذا المود غير صالح.")
        return

    status = await message.reply_text(
        f"⏬ جاري تنزيل <b>{html.escape(name)}</b>...\n"
        "يرجى الانتظار.",
        parse_mode="HTML"
    )

    temp_dir = Path("/tmp/bot_downloads")
    temp_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:80] or "mod"
    ext = Path(link.split("?", 1)[0]).suffix[:10]
    filename = safe_name + (ext if ext else ".bin")
    filepath = temp_dir / filename

    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(link, allow_redirects=True) as response:
                if response.status != 200:
                    await status.edit_text(
                        f"❌ تعذر تنزيل المود.\nرمز الاستجابة: {response.status}"
                    )
                    return

                total = 0
                max_size = 50 * 1024 * 1024  # 50 MB
                with open(filepath, "wb") as f:
                    async for chunk in response.content.iter_chunked(1024 * 256):
                        total += len(chunk)
                        if total > max_size:
                            await status.edit_text(
                                "❌ حجم الملف أكبر من الحد المسموح به (50 MB)."
                            )
                            return
                        f.write(chunk)

        await status.edit_text(
            f"📤 تم تنزيل <b>{html.escape(name)}</b>، جاري إرساله لك...",
            parse_mode="HTML"
        )

        caption = (
            f"📦 <b>{html.escape(name)}</b>\n"
            f"📝 {html.escape(str(get_mod_description(item)))}"
        )

        with open(filepath, "rb") as document:
            await message.reply_document(
                document=document,
                filename=filename,
                caption=caption,
                parse_mode="HTML"
            )

        await status.delete()

    except asyncio.TimeoutError:
        await status.edit_text("❌ انتهى وقت تنزيل الملف. حاول مرة أخرى.")
    except Exception as exc:
        logging.exception("فشل تنزيل المود: %s", exc)
        await status.edit_text(
            "❌ حدث خطأ أثناء تنزيل المود أو إرساله.\n"
            "تأكد أن رابط التحميل مباشر ويعمل."
        )
    finally:
        try:
            if filepath.exists():
                filepath.unlink()
        except Exception:
            pass


# ====================== المعالجات ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await subscriber_gate(update, context):
        return
    register_user(update)
    welcome = (
        "𓆩♡𓆪  <b>بوت مودات ماين كرافت الافضل</b>  𓆩♡𓆪\n\n"
        "╔══════════════════════════╗\n"
        "║  🏆  <b>أكثر من 170+ مود</b>  ║\n"
        "║  ⚡  <b>25+ ريسوس باك</b>     ║\n"
        "║  🌞  <b>شادرات رائعة</b>      ║\n"
        "║  🗺️  <b>30+ مابات</b>         ║\n"
        "╚══════════════════════════╝\n\n"
        "✦  <b>اختر القسم المناسب من الأسفل</b>  ✦\n"
        "𓆩  تزداد المحتويات يومياً  𓆪\n\n"
        "╔══════════════════════════╗\n"
        "║  👨‍💻  <b>المطور:</b> @YAIM_X  👨‍💻 ║\n"
        "╚══════════════════════════╝"
    )
    
    # ===== القائمة الرئيسية بتنسيق قريب من الصورة المرفقة =====
    keyboard = [
        [InlineKeyboardButton("🔎 البحث في جميع الأقسام", callback_data="search_again")]
    ]

    if "mods" in MAIN_CATEGORIES:
        keyboard.append([
            InlineKeyboardButton("🛠️ مودات | Mods", callback_data="main_mods")
        ])

    for left_key, right_key in [("maps", "resus"), ("shaders", "versions")]:
        row = []
        for key in (left_key, right_key):
            if key in MAIN_CATEGORIES:
                row.append(
                    InlineKeyboardButton(
                        MAIN_CATEGORIES[key]["title"],
                        callback_data=f"main_{key}"
                    )
                )
        if row:
            keyboard.append(row)

    # أي قسم جديد يضاف لاحقًا سيظهر تلقائيًا.
    used = {"mods", "maps", "resus", "shaders", "versions"}
    extra = [(key, cat) for key, cat in MAIN_CATEGORIES.items() if key not in used]
    for i in range(0, len(extra), 2):
        keyboard.append([
            InlineKeyboardButton(cat["title"], callback_data=f"main_{key}")
            for key, cat in extra[i:i + 2]
        ])

    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_subcategories(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str):
    query = update.callback_query
    await query.answer()
    
    cat = MAIN_CATEGORIES[category_key]
    subcats = cat["subcategories"]
    
    text = f"╔═══  <b>{cat['title']}</b>  ═══╗\n\n"
    text += "✦  اختر الفئة المناسبة  ✦\n"
    
    keyboard = []
    for sub_name in subcats.keys():
        keyboard.append([InlineKeyboardButton(f"📂 {sub_name}", callback_data=f"sub_{category_key}_{sub_name}_0")])
    
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE, category_key: str, sub_name: str, page: int):
    query = update.callback_query
    await query.answer()
    
    items = MAIN_CATEGORIES[category_key]["subcategories"][sub_name]
    per_page = ITEMS_PER_PAGE
    
    text, start, end = build_list_text(items, page, per_page)
    back_callback = f"main_{category_key}"
    keyboard = build_keyboard(items, page, per_page, f"items_{category_key}_{sub_name}", back_callback)
    
    final_text = f"📂  <b>{sub_name}</b>\n\n{text}"
    await query.edit_message_text(text=final_text, reply_markup=keyboard, parse_mode="HTML")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    menu_text = (
        "𓆩♡𓆪  <b>القائمة الرئيسية</b>  𓆩♡𓆪\n"
        "╔══════════════════════════╗\n"
        "║  ✦  اختر القسم المناسب  ✦ ║\n"
        "╚══════════════════════════╝\n"
        "╔══════════════════════════╗\n"
        "║  👨‍💻  𝘋𝘦𝘷𝘦𝘭𝘰𝘱𝘦𝘳: @YAIM_X  👨‍💻 ║\n"
        "╚══════════════════════════╝"
    )
    
    keyboard = []
    for key, cat in MAIN_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(cat["title"], callback_data=f"main_{key}")])
    
    await query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_ENABLED, SUBSCRIBERS_BOT_ENABLED
    query = update.callback_query
    data = query.data or ""
    if data == "check_subscription":
        if await check_user_subscription(context.bot, update.effective_user.id):
            await query.answer("✅ تم التحقق بنجاح.", show_alert=True)
            await query.edit_message_text("✅ تم التحقق من اشتراكك. أرسل /start للمتابعة.")
        else:
            await query.answer("❌ لم يكتمل الاشتراك بعد.", show_alert=True)
        return
    if not data.startswith("admin_") and await subscription_gate(update, context):
        await query.answer()
        return
    if data == "admin_stop_posting":
        if not is_developer(update):
            await query.answer("⛔ للمطور فقط.", show_alert=True)
            return
        AUTO_POST_ENABLED = False
        save_auto_post_enabled(AUTO_POST_ENABLED)
        await query.answer("⏸️ تم إيقاف النشر التلقائي.")
        await query.message.reply_text("⏸️ تم إيقاف النشر التلقائي بنجاح.")
        return

    if query.data == "admin_start_posting":
        if not is_developer(update):
            await query.answer("⛔ للمطور فقط.", show_alert=True)
            return
        AUTO_POST_ENABLED = True
        save_auto_post_enabled(AUTO_POST_ENABLED)
        await query.answer("▶️ تم تشغيل النشر التلقائي.")
        await query.message.reply_text("▶️ تم تشغيل النشر التلقائي من جديد.")
        return

    if query.data == "admin_stop_subscribers":
        if not is_developer(update):
            await query.answer("⛔ للمطور فقط.", show_alert=True)
            return
        SUBSCRIBERS_BOT_ENABLED = False
        save_subscribers_bot_status()
        await query.answer("⏸️ تم إيقاف البوت للمشتركين.")
        await query.message.reply_text("⏸️ تم إيقاف البوت عند المشتركين.\nالمطور والمشرفون ما زال بإمكانهم استخدام لوحة التحكم.")
        return

    if query.data == "admin_start_subscribers":
        if not is_developer(update):
            await query.answer("⛔ للمطور فقط.", show_alert=True)
            return
        SUBSCRIBERS_BOT_ENABLED = True
        save_subscribers_bot_status()
        await query.answer("▶️ تم تشغيل البوت للمشتركين.")
        await query.message.reply_text("▶️ تم تشغيل البوت عند المشتركين من جديد.")
        return

    if query.data == "admin_broadcast":
        if not is_developer(update):
            await query.answer("⛔ للمطور فقط.", show_alert=True)
            return
        BROADCAST_MODE[update.effective_user.id] = True
        await query.answer()
        await query.message.reply_text(
            "📢 تم تفعيل إرسال رسالة للمشتركين.\n\n"
            "أرسل الآن الرسالة التي تريد إرسالها لجميع المشتركين.\n"
            "يمكنك إرسال نص أو صورة أو ملف.\n\n"
            "❌ للإلغاء أرسل /cancel_broadcast"
        )
        return

    if query.data.startswith("download_mod:"):
        if await subscriber_gate(update, context):
            return

        await query.answer("⏬ جاري تنزيل المود...")
        parts = query.data.split(":")
        if len(parts) != 4:
            await query.message.reply_text("❌ بيانات التحميل غير صحيحة.")
            return

        try:
            category_key = parts[1]
            sub_index = int(parts[2])
            item_index = int(parts[3])
            sub_names = list(MAIN_CATEGORIES[category_key]["subcategories"].keys())
            sub_name = sub_names[sub_index]
            item = MAIN_CATEGORIES[category_key]["subcategories"][sub_name][item_index]
        except (KeyError, IndexError, ValueError, TypeError):
            await query.message.reply_text("❌ لم يتم العثور على المود.")
            return

        await download_and_send_mod(update, context, item)
        return

    if query.data == "search_again":
        if await subscriber_gate(update, context):
            return
        await query.answer()
        context.user_data["search_mode"] = True
        await query.message.reply_text(
            "🔎 <b>البحث في جميع الأقسام</b>\n\n"
            "أرسل اسم العنصر الذي تريد البحث عنه.\n"
            "سيبحث البوت في جميع الأقسام والفئات.\n\n"
            "❌ للإلغاء أرسل /cancel_search",
            parse_mode="HTML"
        )
        return

    if query.data.startswith("modview_"):
        parts = query.data.split("_")
        if len(parts) != 4:
            await query.answer("❌ بيانات المود غير صحيحة.", show_alert=True)
            return
        category_key = parts[1]
        sub_index = int(parts[2])
        item_index = int(parts[3])
        await show_mod_details(update, context, category_key, sub_index, item_index)
        return

    data = query.data
    
    if data in ("admin_stop_post", "admin_start_post"):
        if not is_developer(update):
            await query.answer("❌ هذه الخاصية للمطور فقط.", show_alert=True)
            return
        AUTO_POST_ENABLED = data == "admin_start_post"
        save_auto_post_enabled(AUTO_POST_ENABLED)
        await query.answer("تم تحديث الحالة")
        role = "👑 المطور" if is_developer(update) else "🛡️ مشرف"
        status = "🟢 النشر التلقائي يعمل" if AUTO_POST_ENABLED else "🔴 النشر التلقائي متوقف"
        keyboard = [
            [InlineKeyboardButton("👥 عدد المشتركين", callback_data="admin_users")],
            [InlineKeyboardButton("📢 إرسال رسالة للمشتركين", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📢 إدارة الاشتراك", callback_data="admin_subscriptions")],
            [InlineKeyboardButton("➕ إضافة عنصر", callback_data="admin_add")],
            [InlineKeyboardButton("➖ حذف عنصر", callback_data="admin_delete")],
            [InlineKeyboardButton("⏸️ إيقاف النشر التلقائي" if AUTO_POST_ENABLED else "▶️ تشغيل النشر التلقائي", callback_data="admin_stop_post" if AUTO_POST_ENABLED else "admin_start_post")],
        ]
        if is_developer(update):
            keyboard.append([InlineKeyboardButton("👥 إدارة المشرفين", callback_data="admin_mods")])
        await query.edit_message_text(f"🛠️ <b>لوحة التحكم</b>\n\nصلاحيتك: {role}\n{status}\n\nاختر العملية:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        return

    if data == "admin_users":
        if not is_staff(update):
            await query.answer("❌ غير مصرح لك.", show_alert=True)
            return
        await query.answer()
        await query.edit_message_text(
            f"📊 <b>إحصائيات البوت</b>\n\n"
            f"👥 <b>عدد المشتركين:</b> {len(USERS)}\n\n"
            f"🟢 يتم احتساب كل مستخدم بدأ استخدام البوت مرة واحدة.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع للوحة التحكم", callback_data="admin_panel")]
            ]),
            parse_mode="HTML"
        )
        return

    if data == "admin_panel":
        if not is_staff(update):
            await query.answer("❌ غير مصرح لك.", show_alert=True)
            return
        await query.answer()
        role = "👑 المطور" if is_developer(update) else "🛡️ مشرف"
        status_text = "▶️ تشغيل النشر التلقائي" if not AUTO_POST_ENABLED else "⏸️ إيقاف النشر التلقائي"
        status_callback = "admin_start_post" if not AUTO_POST_ENABLED else "admin_stop_post"
        keyboard = [
            [InlineKeyboardButton("👥 عدد المشتركين", callback_data="admin_users")],
            [InlineKeyboardButton("➕ إضافة عنصر", callback_data="admin_add")],
            [InlineKeyboardButton("➖ حذف عنصر", callback_data="admin_delete")],
            [InlineKeyboardButton(status_text, callback_data=status_callback)],
        ]
        if is_developer(update):
            keyboard.append([InlineKeyboardButton("👥 إدارة المشرفين", callback_data="admin_mods")])
        await query.edit_message_text(
            f"🛠️ <b>لوحة التحكم</b>\n\nصلاحيتك: {role}\n\nاختر العملية:",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML"
        )
        return

    if data == "admin_subscriptions":
        await admin_subscriptions(update, context)
        return

    if data == "admin_subscription_add":
        if not is_staff(update):
            await query.answer("❌ غير مصرح لك.", show_alert=True)
            return
        await query.answer()
        context.user_data["admin_action"] = "subscriptions"
        await query.edit_message_text(
            "➕ <b>إضافة اشتراك إجباري</b>\n\n"
            "أرسل <b>رابط الاشتراك</b> فقط:\n"
            "<code>https://t.me/mychannel</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_subscriptions")]])
        )
        return

    if data == "admin_subscription_delete":
        if not is_staff(update):
            await query.answer("❌ غير مصرح لك.", show_alert=True)
            return
        await query.answer()
        context.user_data["admin_action"] = "subscriptions"
        await query.edit_message_text(
            "➖ <b>حذف اشتراك إجباري</b>\n\n"
            "أرسل رقم القناة المراد حذفها، مثل: <code>del 1</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_subscriptions")]])
        )
        return

    if data == "admin_add":
        await admin_categories(update, context, "add")
        return

    if data == "admin_delete":
        await admin_categories(update, context, "delete")
        return

    if data == "admin_mods":
        await admin_mods(update, context)
        return

    if data == "admin_cancel":
        await admin_cancel(update, context)
        return

    if data.startswith("admincat_"):
        parts = data.split("_", 2)
        await admin_subcategories(update, context, parts[1], parts[2])
        return

    if data.startswith("adminsub_"):
        parts = data.split("_")
        await admin_select_sub(update, context, parts[1], parts[2], int(parts[3]))
        return

    if data == "main_menu":
        await main_menu(update, context)
        return
    
    if data.startswith("main_"):
        category_key = data.split("_")[1]
        await show_subcategories(update, context, category_key)
        return
    
    if data.startswith("sub_"):
        parts = data.split("_")
        category_key = parts[1]
        sub_name = parts[2]
        page = int(parts[3])
        await show_items(update, context, category_key, sub_name, page)
        return
    
    if data.startswith("items_"):
        parts = data.split("_")
        category_key = parts[1]
        sub_name = parts[2]
        page = int(parts[3])
        await show_items(update, context, category_key, sub_name, page)
        return


# ====================== حالة البوت للمشتركين ======================
SUBSCRIBERS_BOT_ENABLED_FILE = "subscribers_bot_enabled.json"
SUBSCRIBERS_BOT_ENABLED = True

def load_subscribers_bot_status():
    global SUBSCRIBERS_BOT_ENABLED
    try:
        import json
        if os.path.exists(SUBSCRIBERS_BOT_ENABLED_FILE):
            with open(SUBSCRIBERS_BOT_ENABLED_FILE, "r", encoding="utf-8") as f:
                SUBSCRIBERS_BOT_ENABLED = bool(json.load(f).get("enabled", True))
    except Exception:
        SUBSCRIBERS_BOT_ENABLED = True

def save_subscribers_bot_status():
    import json
    with open(SUBSCRIBERS_BOT_ENABLED_FILE, "w", encoding="utf-8") as f:
        json.dump({"enabled": SUBSCRIBERS_BOT_ENABLED}, f, ensure_ascii=False)

def subscribers_bot_is_enabled():
    return SUBSCRIBERS_BOT_ENABLED

async def stop_for_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SUBSCRIBERS_BOT_ENABLED
    if not is_developer(update):
        await update.message.reply_text("❌ هذا الأمر خاص بالمطور.")
        return
    SUBSCRIBERS_BOT_ENABLED = False
    save_subscribers_bot_status()
    await update.message.reply_text("⏸️ تم إيقاف البوت عند المشتركين.\nالمطور والمشرفون ما زال بإمكانهم استخدام لوحة التحكم.")

async def start_for_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SUBSCRIBERS_BOT_ENABLED
    if not is_developer(update):
        await update.message.reply_text("❌ هذا الأمر خاص بالمطور.")
        return
    SUBSCRIBERS_BOT_ENABLED = True
    save_subscribers_bot_status()
    await update.message.reply_text("▶️ تم تشغيل البوت عند المشتركين.")

async def subscriber_gate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يمنع المشتركين من استخدام البوت عندما يكون متوقفًا."""
    if subscribers_bot_is_enabled():
        return False

    user = update.effective_user
    if user and (user.id == DEVELOPER_ID or user.id in MODS_IDS):
        return False

    message = update.effective_message
    if message:
        await message.reply_text("⏸️ البوت متوقف مؤقتًا عند المشتركين. حاول لاحقًا.")
    return True

# إنشاء وصف تلقائي لكل مود لا يملك وصفًا.
def enrich_mods_with_descriptions():
    for sub_name, items in MODS.items():
        for item in items:
            if not item.get("description"):
                item["description"] = (
                    f"🛠️ {item.get('name', 'مود')}\n"
                    "✨ مود لماينكرافت يضيف محتوى وتجربة جديدة.\n"
                    f"📂 التصنيف: {sub_name}"
                )

enrich_mods_with_descriptions()

# ====================== تشغيل البوت ======================
def main():
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        raise ValueError("لم يتم تعيين متغير TOKEN في البيئة !!")
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("cancel_search", cancel_search))
    application.add_handler(CommandHandler("stop_subscribers", stop_for_subscribers))
    application.add_handler(CommandHandler("start_subscribers", start_for_subscribers))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("cancel_broadcast", cancel_broadcast))
    application.add_handler(CommandHandler("panel", panel))
    application.add_handler(CommandHandler("post_now", post_now))
    application.add_handler(CommandHandler("stop_bot", stop_bot))
    application.add_handler(CommandHandler("start_bot", start_bot))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # نشر مودين يوميًا الساعة 8:00 مساءً بتوقيت اليمن
    application.job_queue.run_daily(
        auto_post_two_mods,
        time=time(AUTO_POST_HOUR, AUTO_POST_MINUTE, tzinfo=ZoneInfo("Asia/Aden")),
        name="daily_two_mods"
    )
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_message))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
    
    logging.info("✅ البوت يعمل الآن مع نظام الفئات الفرعية (الشادرات مقسمة حسب الاسم)!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
