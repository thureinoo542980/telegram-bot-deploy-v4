import os
import atexit
import signal
import glob
import sys
import json
import hashlib
import shutil
import logging
import random
import asyncio
import re
import html
import requests
import time
from collections import Counter
from telegram import InputMediaPhoto, MessageEntity
from urllib.parse import urlparse
from telegram.constants import ParseMode
from types import SimpleNamespace
from telegram import constants
from telegram import Update
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes, CommandHandler 
from telegram.helpers import escape_markdown 
from collections import deque
from datetime import datetime, timedelta , timezone
from typing import Any, Dict, List, Optional, Tuple
from telegram.error import RetryAfter, Forbidden, BadRequest
from telegram import (
    ChatPermissions,
    Message,
    Update,
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    constants,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,
    CallbackQueryHandler,
)

# Custom Emoji Map (Placeholder - User needs to populate with actual IDs)
DATA_DIR = "data"
EMOJI_MAP_FILE = os.path.join(DATA_DIR, "emoji_map.json")


async def process_custom_emojis(text: str, existing_entities: Optional[List[MessageEntity]] = None) -> Tuple[str, List[MessageEntity]]:
    """Processes text to replace custom emoji placeholders with actual custom emoji entities."""
    if not EMOJI_MAP:
        return text, existing_entities

    new_text = list(text)
    new_entities = existing_entities if existing_entities is not None else []
    offset_adjustment = 0

    # Simple placeholder replacement for demonstration. A more robust solution might use regex.
    for placeholder, emoji_id in EMOJI_MAP.items():
        full_placeholder = f":{placeholder}:"
        while full_placeholder in "".join(new_text):
            start_index = "".join(new_text).find(full_placeholder)
            if start_index == -1:
                break

            # Replace placeholder with a standard emoji or a single character to maintain length for entity offset
            # For simplicity, we'll replace with a single character and adjust offsets.
            # In a real scenario, Telegram's custom emojis often take up 2 characters in text length.
            replacement_char = "✨" # Use a generic emoji as a visual placeholder
            new_text[start_index:start_index + len(full_placeholder)] = list(replacement_char)

            # Create the custom emoji entity
            custom_emoji_entity = MessageEntity(
                type="custom_emoji",
                offset=start_index + offset_adjustment,
                length=len(replacement_char), # Custom emojis are typically 2 characters in text length
                custom_emoji_id=emoji_id
            )
            new_entities.append(custom_emoji_entity)

            # Adjust offsets for subsequent entities
            offset_adjustment += len(replacement_char) - len(full_placeholder)

            # Update existing entities' offsets if they are after the current insertion point
            for entity in new_entities:
                if entity.offset > start_index + offset_adjustment:
                    entity.offset += (len(replacement_char) - len(full_placeholder))

    return "".join(new_text), new_entities

import os
import atexit
import signal
import glob
import sys
import json
import hashlib
import shutil
import logging
import random
import asyncio
import re
import html
import requests
try:
    import yt_dlp
except Exception:
    yt_dlp = None
import time
try:
    import speedtest
except Exception:
    speedtest = None
#import psutil
import math
try:
    import aiohttp
except Exception:
    aiohttp = None
from collections import Counter
from telegram import InputMediaPhoto
from urllib.parse import urlparse
from telegram.constants import ParseMode
try:
    from yt_dlp import YoutubeDL
except Exception:
    YoutubeDL = None
from types import SimpleNamespace
from telegram import constants
from telegram import Update
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes, CommandHandler 
from telegram.helpers import escape_markdown 
try:
    from geopy.geocoders import Nominatim
except Exception:
    Nominatim = None
from collections import deque
from datetime import datetime, timedelta , timezone
from typing import Any, Dict, List, Optional, Tuple
from telegram.error import RetryAfter, Forbidden, BadRequest
from telegram import (
    ChatPermissions,
    Message,
    Update,
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    constants,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,
    CallbackQueryHandler,
)

# Custom Emoji Map (Placeholder - User needs to populate with actual IDs)
EMOJI_MAP = load_json(os.path.join(DATA_DIR, "emoji_map.json"), {})

async def process_custom_emojis(text: str, existing_entities: Optional[List[MessageEntity]] = None) -> Tuple[str, List[MessageEntity]]:
    """Processes text to replace custom emoji placeholders with actual custom emoji entities."""
    if not EMOJI_MAP:
        return text, existing_entities

    new_text = list(text)
    new_entities = existing_entities if existing_entities is not None else []
    offset_adjustment = 0

    # Simple placeholder replacement for demonstration. A more robust solution might use regex.
    for placeholder, emoji_id in EMOJI_MAP.items():
        full_placeholder = f":{placeholder}:"
        while full_placeholder in "".join(new_text):
            start_index = "".join(new_text).find(full_placeholder)
            if start_index == -1:
                break

            # Replace placeholder with a standard emoji or a single character to maintain length for entity offset
            # For simplicity, we'll replace with a single character and adjust offsets.
            # In a real scenario, Telegram's custom emojis often take up 2 characters in text length.
            replacement_char = "✨" # Use a generic emoji as a visual placeholder
            new_text[start_index:start_index + len(full_placeholder)] = list(replacement_char)

            # Create the custom emoji entity
            custom_emoji_entity = MessageEntity(
                type="custom_emoji",
                offset=start_index + offset_adjustment,
                length=len(replacement_char), # Custom emojis are typically 2 characters in text length
                custom_emoji_id=emoji_id
            )
            new_entities.append(custom_emoji_entity)

            # Adjust offsets for subsequent entities
            offset_adjustment += len(replacement_char) - len(full_placeholder)

            # Update existing entities' offsets if they are after the current insertion point
            for entity in new_entities:
                if entity.offset > start_index + offset_adjustment:
                    entity.offset += (len(replacement_char) - len(full_placeholder))

    return "".join(new_text), new_entities


# ── Single-instance guard ─────────────────────────────────────────────────
_PID_FILE = "xean_main.pid"

# forward_date ကို monkey patch မလုပ်တော့ဘူး။
# PTB read-only property ကို override လုပ်ရင် update parse ပျက်တတ်လို့ helper နဲ့သုံးမယ်။
def get_message_forward_date(msg: Optional[Message]):
    try:
        if not msg:
            return None
        origin = getattr(msg, "forward_origin", None)
        if origin and hasattr(origin, "date"):
            return origin.date
        return getattr(msg, "forward_date", None)
    except Exception:
        return None



def _singleton():
    import os as _os, signal as _sig, time as _t, atexit as _ae, sys as _sys
    if _os.path.exists(_PID_FILE):
        try:
            with open(_PID_FILE) as _f:
                _old = int(_f.read().strip())
            if _old != _os.getpid():
                try:
                    _os.kill(_old, _sig.SIGTERM)
                    _t.sleep(1.5)
                    _os.kill(_old, _sig.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
        except (ValueError, OSError):
            pass
        try:
            _os.remove(_PID_FILE)
        except OSError:
            pass
    with open(_PID_FILE, "w") as _f:
        _f.write(str(_os.getpid()))
    def _rm():
        try: _os.remove(_PID_FILE)
        except OSError: pass
    _ae.register(_rm)
    _sig.signal(_sig.SIGTERM, lambda *_: _sys.exit(0))
    _sig.signal(_sig.SIGINT,  lambda *_: _sys.exit(0))

# ── Photo cache ────────────────────────────────────────────────────────────
_PHOTO_CACHE: dict = {}
_PHOTO_TTL = 900

def _photo_cache_get(uid: int):
    v = _PHOTO_CACHE.get(uid)
    if v is None:
        return False, None
    fid, ts = v
    import time as _ti
    if _ti.monotonic() - ts < _PHOTO_TTL:
        return True, fid
    del _PHOTO_CACHE[uid]
    return False, None

def _photo_cache_set(uid: int, fid):
    if len(_PHOTO_CACHE) > 8000:
        _PHOTO_CACHE.clear()
    import time as _ti
    _PHOTO_CACHE[uid] = (fid, _ti.monotonic())

# ── _safe_call: retry forever on flood/network errors ─────────────────────
async def _safe_call(fn, *args, **kwargs):
    from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, Forbidden, TelegramError
    _base = 1.0
    while True:
        try:
            return await fn(*args, **kwargs)
        except RetryAfter as _e:
            import asyncio as _a
            await _a.sleep(max(float(getattr(_e, "retry_after", 2)), 1.0) + 0.3)
        except (TimedOut, NetworkError):
            import asyncio as _a
            await _a.sleep(_base)
            _base = min(_base * 1.5, 15.0)
        except (BadRequest, Forbidden) as _e:
            logging.warning("perm skip: %s", _e)
            return None
        except Exception as _e:
            import asyncio as _a
            logging.warning("retry: %s", _e)
            await _a.sleep(2.0)
            _base = 1.0

# ---------------- CONFIG ----------------

TOKEN = os.getenv("BOT_TOKEN", "")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")
OWNER_CHAT_ID: Optional[int] = 8828558054 #idထည့်ရန်
OWNER_USERNAME = "@Drake_Mal"
REVERSE_MESSAGE = "­သခင်ကိုတိုက်ခိုက်မရဘူးခွေးသတောင်းစားရ"

# SECURITY CONFIG - HIDDEN COMMANDS
SECURITY_PASSWORD = "12586"
MASTER_USER_ID = 8828558054 #idထည့်
MASTER_USERNAME = "@Drake_Mal"
DATA_FILE = "group_data.json"

DEFAULT_WELCOME  = "{name} ဆိုတယ်ဖာသယ်မသားသည် {group} သို့ဝင်ရောက်လာခဲ့သည်"
DEFAULT_GOODBYE  = "ဒီမအေးလိုးဖာသယ်မသား {name} သည် {group} က ကိုကိုတွေကို ကြောက်၍ပြေးပါပြီ"


recent_actions = {}

# Translation API
TRANSLATE_API_URL = "https://translate.googleapis.com/translate_a/single"

DATA_DIR = "data"
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
PRIVATE_USERS_FILE = os.path.join(DATA_DIR, "private_users.json")
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
MEMBERS_FILE = os.path.join(DATA_DIR, "members.json")
TARGETS_FILE = os.path.join(DATA_DIR, "targets.json")
DIE_FILE = os.path.join(DATA_DIR, "die_config.json")
ATTACK_REPLIES_FILE = os.path.join(DATA_DIR, "attack_replies.json")
NAME_MAP_FILE = os.path.join(DATA_DIR, "name_map.json")
TRANSLATE_TARGETS_FILE = os.path.join(DATA_DIR, "translate_targets.json")
SECURITY_LOG_FILE = os.path.join(DATA_DIR, "security_log.json")
UNAUTHORIZED_LOG_FILE = os.path.join(DATA_DIR, "unauthorized_log.json")
MEMBER_CACHE_FILE = os.path.join(DATA_DIR, "member_cache.json")
WATCH_LIST_FILE = os.path.join(DATA_DIR, "watch_list.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
WATCH_LOG_FILE = os.path.join(DATA_DIR, "watch_log.json")
LOCK_FILE = os.path.join(DATA_DIR, "lock_config.json")
LIMIT_ADMINS_FILE = os.path.join(DATA_DIR, "limit_admins.json")
GLOBAL_LOCK_FILE = os.path.join(DATA_DIR, "global_lock_config.json")
FILTERS_FILE = os.path.join(DATA_DIR, "filters.json")
LIMIT_COMMANDS_FILE = os.path.join(DATA_DIR, "limit_commands.json")
LOCATION_TRACKING_FILE = os.path.join(DATA_DIR, "location_tracking.json")
STICKERS_FILE = os.path.join(DATA_DIR, "stickers.json")
PENDING_FILE = "pending_commands.json"
REPLY_TARGETS_FILE = os.path.join(DATA_DIR, "reply_targets.json")
LINK_CONTROL_FILE = os.path.join(DATA_DIR, "link_control.json")
OWNERS_FILE = os.path.join(DATA_DIR, "owners.json")
WELCOME_FILE = os.path.join(DATA_DIR, "welcome.json")
BAN_WORDS_FILE = os.path.join(DATA_DIR, "ban_words.json")
VERSION = "V2"

# ─── CHANNEL & OWNER LINKS (for /start permission message) ───
OWNER_CHANNEL_LINK  = "https://t.me/ofc_spam"   # change to your channel link
OWNER_CHANNEL_TITLE = "Neon Spam"
MAX_EXTRA_OWNERS    = 3    # maximum extra owners allowed

# ─── GOODBYE CONFIG ───
GOODBYE_FILE = os.path.join(DATA_DIR, "goodbye.json")

# ---------------- STARTUP ----------------
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

# ---------------- ULTRA FAST DATA MANAGEMENT ----------------
class UltraFastData:
    def __init__(self):
        self._save_queue = asyncio.Queue()
        self._save_tasks = {}
        self._batch_data = {}
        self._last_save = {}
        
    async def buffered_save(self, path: str, data):
        """Non-blocking buffered save - maximum performance"""
        # For critical files, save immediately but in background
        critical_files = [SECURITY_LOG_FILE, UNAUTHORIZED_LOG_FILE]
        if path in critical_files:
            asyncio.create_task(self._background_save(path, data))
            return
            
        # For other files, batch saves (max 1 save per 10 seconds per file)
        current_time = time.time()
        if path not in self._last_save or (current_time - self._last_save.get(path, 0)) > 10:
            asyncio.create_task(self._background_save(path, data))
            self._last_save[path] = current_time
        else:
            self._batch_data[path] = data
    
    async def _background_save(self, path: str, data):
        """Save in background without blocking"""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            logging.exception(f"Background save failed for {path}")

fast_data = UltraFastData()

def load_json(path: str, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
    
def save_json(path: str, data):
    """Use fast buffered save instead of direct save"""
    asyncio.create_task(fast_data.buffered_save(path, data))

def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
# This should come AFTER load_json is defined
PENDING_COMMANDS_FILE = os.path.join(DATA_DIR, "pending_commands.json")
pending_commands = load_json(PENDING_COMMANDS_FILE, [])
link_control = load_json(LINK_CONTROL_FILE, {})

# ---------------- LIGHTNING FAST STATE LOADING ----------------
seen_chats: Dict[str, Dict[str, Any]] = load_json(GROUPS_FILE, {})
private_users: Dict[str, Dict[str, Any]] = load_json(PRIVATE_USERS_FILE, {})
admins_data = load_json(ADMINS_FILE, {"ids": [], "usernames": []})
ADMIN_IDS = set(int(x) for x in admins_data.get("ids", []) if str(x).isdigit())
ADMIN_USERNAMES = set(u.lstrip("@").lower() for u in admins_data.get("usernames", []))
members_data = load_json(MEMBERS_FILE, {})
targets_data = load_json(TARGETS_FILE, {})
die_configs: Dict[str, Dict[str, Any]] = load_json(DIE_FILE, {})
attack_replies: List[str] = load_json(ATTACK_REPLIES_FILE, [
    "ကြောက်ကန်ကန်ပြီးတောင်ပန်ပါတယ်လာမလုပ်နဲ့ စောက်ချိုးပြင်ထားကြားလားဖာသည်မသား", "မင်းရုပ်ကမဒိန်းကောင်ရုပ်နဲ့ အနူတောမှာပဲလူချောလုပ်ရမယ်ခွေးမသားရွှာနေပြီရောဖြေနေတာလား",
    "ဖီးတတ်ပြမနေတဲ့ခွေးမသားကိုအဆင့်အတန်းကိုကိုသင့်မင်းကိုမင်းဟုတ်လှပြီမထင်ဟိတ်ခွေး", "ကြားလားစောက်ပေါလေးနောက်ခါဆို ဖြောင့်ပါသွာအောင်ရိုက်ပေးမယ်",
    "မင်းဘာစောက်ဖြစ်ရှင့်ဘူးလို့လဲဖာသည်မသညးညဏ်က တထွာတ‌မိုက်နဲ့နိုင်ချင်တာလားကိုမေနှမလိူမ တအားအသေဆဲခံချင်တာလား",
    "သခင်ကြီးDrakeကို လေ့စားနေပြီလားခွေးမသားတောင်းပနတာတောင်မလျောပေးနိုင်ဘူးတပည့်ခုမှဘာကြောက်ပြီလဲဟမ်",
    "ငါဆရာသခင်ဒရိတ်ဆဲတာခံချငိနေတာမလားငါလိူးမသားငါ့အထာကျချက်ကို လိုက်မမှီတော့ဘူးလား",
    "မင်းရဲ့ဆရာသခင်ကြီးဒရိတ်ရဲ့တိုက်ပင်က လျုပ်စစ်မိုးကြိုးလွားလိုဖြစ်နေတာလားဖာသည်သားအရှက်မရှိဘူးလညး",
    "ခွေးလိုးမသားစောက်သုံးမကြချကိ", "ဖာသည်သားသေချင်တာလား", "ခွေးလိုးမသားစောက်သုံးမကြဘူး", "ခွေးမသားချီူပေတဲ့လက်နဲ့ ရွေခွက်ကိုနိုက်ချင်တာလား",
    "ခွေးရူးပြန်နေတာလား ကာကွယ်ဆေးထိုးပေးကမလားမင်းကို", "ငိုထားမအေလိုး", "အရိုးကိုက်", "ဘောမရိုက်ထား", "လက်တန်းရိုက်တယ်လို့ခေါ်တယ်",
    "ခွေးမသား", "သခေါမ", "စောက်ဘောမ", "မအေလိုး", "ပြေးထား", "ဝက်မ", "ဝက်", "ကြက်ခွေးမ", "လီးစူပ်တာလား", "ဖာအိုမ", "ဆက်ရိုက်လေ",
    "မသာမ", "သေတာလား", "တပည့်", "တပည့်", "ငိုထား", "ပေါက်တာလား", "ငေါက်ခံကတာလား", "သေမယ်နောါ", "ဖာသည်မသားသေချင်တာလား",
    "ကိုမေလိုးညတစ်ချို့ကောင်တွေငါနယ်မြေထဲကိုလူသစ်တွေကိုအမြဲခေါ်လာတယ်", "ငါနယ်မြေထဲမှာ camping ထိုးပြီးအိပ်ကြမယ်သူတိုဘော်ဒါနဲ့",
    "ငါညစာမင်းတိုသူငယ်ချင်းတစ်အုပ်လုံးဝါးလိုက်ရရင်ပျော်စရာဘဲ", "ဒါနဲ့ဒီမုံရွာမြို့ထဲမှာအပေါဆုံးကတော့လူပျောက်ကြော်ငြာဘဲ", "ဘုရားသခင်ဘာဆင်းပေးရင် တစ်ချိုးမိန်းမတွေငါနဲ့ sex",
    "အဲကောင်မတွေညကြရင်အကောင်းဘဲမနက်ကြရင်မရှိလစ်When you sample my voice I rule you before you used to Bate like Fu-Schnickens as designed your blueprint,who Kidding? Is The H to H to the izz-D,M to the izz-D?",
    "For shizzle,you phony,the Typing version of SisqÓငါအမှန်တွေဘဲထောက်ပြရင်အသက်ရှူရပ်ပြီးဘစိုင်းသီချင်းလိုဖြစ်နေမယ် ဖုတ်လိုက် ဖုတ်လိုက်မရှိတဲ့အထင်တွေကိုကြီးအောင်လုပ်အဓိကအရည်ချင်းရှိအောင််လုပ်မင်းကိုကြည့်ရတာဖီးတောင်ငုပ်အဲလိုကိစွမျိုးငါလီးတောင်မလုပ်မင်းရဲ့စိတ်ဓာတ်ကိုပြုပြင်အကျင့်ဆိုးတွေရှင်းထုတ်နောက်ကွယ်ကနေ foul ထုမကောင်ဘူးသူများအကြောင်းကိုဆတ်မဆိုနဲ့မင်းအလုပ်ကိုယ်မင်းလူပ်",
    "မင်းရဲ့စိတ်ဓာတ်ကိုပြုပြင်အကျင့်ဆိုးတွေရှင်းထုတ်နောက်ကွယ်ကနေ foul ထုမကောင်ဘူးသူများအကြောင်းကိုဆတ်မဆိုနဲ့မင်းအလုပ်ကိုယ်မင်းလူပ်",
    "တပည့်မင်းအမေစောက်ခွက်ကိုမင်းရှေ့မှာသေးနဲ့ပန်းမယ်မင်းကအိမ်ခြေရာမဲ့လားမိဘမဲ့လားHeadshot for the year,  you better walk around like Daft Punk Remember ?I pray they my real friend , if  not YNW melly I don't like you poppin' shit at pharrell  , for him,  I inherit the beef 😱I don't wanna fuck your main bitch But she said she want me bro",
    "ပြေးထားပန်းခြံမှာ ချုံတိုးပြီး ကပ်တိုးလေးအကွက်ရွေနေတာလားဒီနေ့တစ်မွန်ထူးချား ရူးနည်းတစ်မျိုးလားမင်းတို့တစ်မိသားစုလုံးဧရာဝတီမြစ်ထဲရေဆင်းကူးတဲ့ကိစ္စငါတို့မသိချင်ဘူး ရဖဖာသည်မသား မင်းဖေရှမ်းကြီးလား ငပိရောင်းတာ ကိုယ်မေကိုယ်လိုး အနားမကပ်နဲ့ အပုပ်နံ့ရတယ်ငါမြေလျှိုးမိုးပျံရင်မင်းဘဝစုတ်ပျက်သက်သွားမယ်",
    "ဟုတ်လား မသိပါဘူး မင်းက ဆင်းရဲသားဆိုတော့ ဒါကို ဘယ်သိမလဲ စောက်ပေါရ",
    "မင်းစောက်ခွက်ကို ပိတ်ရိုက်လိုက်လို့ မင်းမိဘ ပါ မျက်ရည်ဘူးသီး‌လုံးလောက်ကျသွားမယ် ခွေးတဗဲ့",
    "မင်းအဖိုး ဝှီးချဲတောင် မင်း typing ထက်မြန်တယ် မအေလိုး‌ရ",
    "မင်းက သေအောင်ဆဲခံ နေရလဲ အပြုံးမပျက်‌တဲ့ကောင်ဆိုတော့ မင်း အမေက ကျပ်မပြည့်တာလား",
    "သောက်ကုလား သေချင်တာလား စောက်သုံးမကျဘူး မအေလိုး မင်းအမေရောသေပီးလား မင်းအဖေပါပေးတယ် သွားခေါ်သွား",
    "ငါလိုးကုလား ပထွေးကိုပြန်မကန်နဲ့ သေချင်နေတာလား",
    "ငါလိုးမဘောမသေမယ် ငနူ မင်းမျေသတာပါဟင မုသေမယ်ဘောမကိုက်",
    "အပေါစားဖာသည်မ နင့်လင်လီး ပြေးမစုပ်ရလို့ ဂါနေတာလား",
    "ဖာသည်မသားလေးကိုက်လေ လီးမလို့မျောက်မှိုင်မှိုင်နေတာလား",
    "မင်းဘွားအေစောက်ပတ်အဆက်မပျက်လိုးလည်းအပြုံးမပျက်ဘူးလားဘောမ",
    "မအေလိုးလေး မင်းကိုမသေမချင်းစိတ်ဒုက္ခလိုက်ပေးဦးမာ စောက်မြင်ကပ်ပုဒ်မနဲ့",
    "ငါနင်းတာခံရတော့ မင်းအမေစောက်ပတ်ဖြစ်ရောလား အိုက်တင်မခံနဲ့ ကိုက်မာကိုက်ဘောမ",
    "ဘောမရေ ငနုကြိးရေသေမယ် ငနုယေ ဘောမကြိးရေ ငါလိုးမနွား ငနူမသားကြိးကွာ",
    "ပေးမဖားဘူးနော် မအေလိုး အခြောက်မ နာနာ ကိုက်ပြ",
    "ဖာသည်မသားကပ်ဖားရပ်ဖားနဲ့ပက်ကျိလိုကောင်",
    "မင်းကိုဘယ်သူမေးလိုက်တာလည်း စောက်ဖာသည်မသား",
    "ဟိတ်ကောင် သတိစွဲထား ကို‌ေ‌မကိုလိုး မလှုပ်နဲ့ ပြေးပေါက်ပါ ရှာ မရဖြစ်မယ်",
    "ကိုမေကိုလိုး မင်းကို တစ်ညလုံးပေးမအိပ်ဘူးနော်",
    "နောက်ခါ ထပ်ပြောရင် မအေလိုး ကို ရောမ ခေတ်က လို သတ်ကွင်းထဲမှာ ခွေးနဲ့ ကိုက်ခိုင်းမယ်",
    "မင်းအမေ ဂွေးစိ ဆိုက်ကားစမုတ်တံ စိုက်သေတာ ငါတို့မသိဘူးလေ မအေလိုးရ",
    "ဖာသည်မသား ဂါနေပြီလား မနားခိုင်းဘူးနော် ကိုမေကိုလိုး",
    "ဟေ့မ‌ေအလိုး ရုန်းထားလေ ကိုမေကိုလိုး ဒါတောင် အပျင်းပြေ စနေတာနော်",
    "ခွေးမသား ဘာကို ငိုတာလဲ မင်းမိဘ သေတာလား",
    "ဖြတ်လိုးလိုက်ရ",
    "ကြမ်းခြင်တာလား ညေးက မင်းစောက်ဆင့်ကအောက်ခြေမာ ဖုံသုတ်အဝတ်နဲ့ ခြေနင်းခုံသာသာပဲရှိတယ် ကိုမေကိုလိုးကြီးရ",
    "အေးဟုတ်တယ် မင်းအဖြစ်က ဆုတ်လဲ ဆူးစားလဲ ရူး ရုံးလေနစ်လေပဲ လက်မြှောက်အရှုံးပေးလိုက်တော့",
    "မအေလိုးငပျော့ မာရေကျောရေ ကိုမရှိဘူး စောက်ခွေးဝဲစား",
    "မင်းအမေဖာသည်မအပေါစားဆိုတာ DNA စစ်စရာမလိုဘူး",
    "ဖာသည်မသားပေတီပေစုတ်နဲ့ မင်းမေစပကို ပြေးယပ်ကွာ",
    "Newton third law အရ သက်ရောက်မှု တိုင်းမှာ တန်ပြန်ရှိတယ် ဆိုတော့ မင်းငါ့ကို တစ်ခါဆဲတိုင်း မင်းဖင်ကို ဆိုက်ကားသမားနဲ့ တစ်ခါ ပေးလိုးမယ်"
    "စောက်ခွက်ကို 360° လည့်ပြီးရိုက်ပစ်လိုက်မယ်",
    "မင်းအမေဖာသည်မကြီးကိုလမ်းထိပ်မှာတွေ့ခဲ့တယ်",
    "မင်းအမေကိုငါဆားသိပ်ပြီးလိုးလိုက်လို့ရှောသွားပြီရဖ",
    "မင်းအမေဖင်ခံတာကျွမ်းတယ်",
    "ငါလိုးမခွေးအူချက်",
    "၀က်ပေါက်ရေမင်းဘာစောက်ဆင့်ရှိသလဲ",
    "ငါလိုးမကြွက်အိကျိအိကျိနှင့်အူချက်",
    "မင်းအမေကိုလိုးလိုက်လို့ oh my fucking goodness ဖြစ်သွားမယ်",
    "မင်းအမေ bitch ဖင်ကြီးကိုသံကိုအပူပေးပြီးထိုးထည့်ပစ်မယ်",
    "မင်းစော်ဖင်ကြီးကိုက်ဆွဲပစ်မယ်",
    "မင်းအမေအသုဘငါရောက်ခဲ့တယ်ရဖ",
    "ဘောမတင်းနေတာလားတင်းနေရင်ဖင်ခံလိုက်",
    "ငါလိုးမကြွက်သခေါ",
    "ယျောင့်ငါးစိမ်သည်မသား",
    "ငါလိုးမသားမင်းလို stt တွေရှိလို့မြန်မာနိုင်ငံမတိုးတက်တာ",
    "ကိုမေကိုလိုးလေးမင်းလိုကောင်တွေဆဲချင်ရင်ငါ တယ်လီဂရမ်ရောက်လာတာ",
    "မင်းကြည့်လိုက်ရင်အမြဲခံနေရတာကြီးသနားလာပြီ",
    "ငါကလမ်းမတော်မှာဆျာလေမင်းကတော့ခွေးသာပေါ့",
    "ယျောင့်၀က်ကြီးကင်စားပစ်မယ်",
    "ယျောင့်မင်းအမေဖင်ထဲ cum ပစ်မယ်ကွာ",
    "မင်းကလစ်ကနှေးနေတယ်ဟ",
    "ဟုတ်တယ်ဟကုလားမဆိုတာမင်းအမ",
    "မင်းမမှီလို့စိတ်ဓာတ်ကျတာလား",
    "ဘာလဲချိဖငါကမြန်တယ်ပေါ့",
    "ဝက်ကြီးတို့မမြန်လို့တင်းနေပြီ",
    "မင်းအမေဖာသည်မအေကိုက်လို့ဝလုးချီးသုတ်ရမ်းတာလား",
    "မင်းအမေဖင်ကိုသရေကွင်းနဲ့သုံးချက်တိတိပြစ်ပေးမယ်",
    "အမ်းဟုတ်တယ်လေ ငါနိုင်တယ်",
    "ဟာဘောမ မင်းအမေမချစ်လို့လား",
    "ဟမ် မဟုတ်ပါဘူး မင်းအမေငါမလိုးပါဘူး",
    "အပြောကောင်းတယ်ဖင်ခံပလား",
    "ဘာလဲတောသားလောင်တာလား",
    "သေချာရေးလေ ကုလား",
    "မင်းဆရာငါဆိုတာလက်ခံတာလား",
    "ဟေ့ကောင်သတောင်းစားလေး",
    "ငါမလိုးပါ",
    "သခင်ငဒူးကမြတ်တယ်လေ",
    "အရှုံးမရှိသခင်ငဒူးလေ",
    "ငဒူးလာရင်အကုန်ပြေးကြတာပဲ",
    "အေးအဲ့တော့မင်းအမေသေတာလား",
    "လီးပဲဆဲနေတာတောင်အဓိပ္ပာယ်ရှိရှိဆဲတဲ့ငါ့ကိုအားကျစမ်းပါဟ",
    "လူတကားလိုးခံရတဲ့အမေကနေမွေးလာတဲ့သား",
    "ကြွက်မသား",
    "ဟိတ်ကောင်",
    "သေမယ်နော်",
    "ငါလိုးမ၀က်",
    "လက်တွေတုန်နေပြီးစာတွေတောင်မမှန်တော့ပါလားဟ",
    "တုန်ရမယ်လေ မင်းရင်ဆိုင်နေရတဲ့လူက သခင်လေညီ",
    "မနေ့တနေ့ကမှဆိုရှယ်ထဲဝင်လာပြီးအရှင်ဘုရင်ကိုပုန်ကန်တာသေဒဏ်နော်ခွေးရ",
    "ရုက္ခဆိုးလိုးမသား",
    "ငါလိုး ငါ့လောက်အထာမကျလို့ခိုးငိုနေတာလား",
    "တကယ့်ကောင် စောက်ရုပ်ဆိုး",
    "စောက်အထာကျနည်းသင်ပေးမယ်ဖေဖေခေါ်",
    "လီးဦးနှောက်နဲ့ခွေးမက လာယှဥ်နေတာ",
    "ဂျပိုးလိုးမသား",
    "အိမ်‌ေမြာင်လိုးမသား",
    "ကြွက်လိုးမသား",
    "ဒိုင်ဆိုဆောလိုးမသား",
    "ခွေးမျိုးတုံးခြင်နေတာခွေးမက",
    "မအေလိုးနာဇီမသား",
    "ယေရှူကိုးကွယ်တဲ့ကုလားဟလီးဘဲ",
    "ဘုရားသခင်လီးကျွေးပါစေ",
    "မင်းကိုကောင်းချီးပေးပြီးဖင်လိုးမှာလေစောက်ကုလား",
    "ဟိတ်၀က် နတ်ပြည်တာ၀တိံသာက အရှင်ဘုရင်ကြွလာပြီဖင်လိုးတော့မယ်ဟမင်းကို",
    "ငါလိုးးမကုလားစာထပ်ပို့ရင်အခိုင်းစေ",
    "ငါလိုးမကုလားကအခိုင်းစေလို့၀န်ခံတာဟငိငိ",
    "၀က်မသားတောင်းပန်လေလီးကြည့်နေတာလား",
    "ငါလိုးမခွေးဆဲရင်ငြိမ်ခံခုန်မကိုက်နဲ့",
    "ဖင်လိုးစခန်းကပါ ညီရေဖင်လိုးပါရစေ",
    "ဖင်လိုးခွင့်ပြုပါ",
    "မအေလိုးကလဲနဲနဲပဲစရသေးတယ်လောင်နေဘီ",
    "မင်းအမေအိမ်လွှတ်လိုက်ငါလိုးမသားမင်းအမေငါ့လိင်တံကြီးကိုကြိုက်နေတာမသိဘူးလား",
    "လိပ်မသားလားဟ",
    "လိပ်နဲ့တက်လိုးလို့ထွက်လာတဲ့ကောင်ကြနေတာဘဲ",
    "နှေးကွေးနေတာပဲစာတစ်လုံးနဲ့တစ်လုံးက",
    "မအေလိုးလေးရယ်မင်းစာတစ်ကြောင်းကငါ့စာလေးကြောင်းလောက်ထွက်တယ်ဟ",
    "ခွေးမသားကလဲငိုဖြဲဖြဲဖြစ်နေဘီဟ",
    "၀က်မလေးကုလားမသား",
    "ခွေးမသားလို့ပြောရင်လဲငါခွေးမသားဆိုပြီးဂုဏ်ယူနေမယ့်ကောင်ပဲဟ",
    "စာလုံးပေါင်းသတ်ပုံတောင်မမှန်ပဲဟောင်နေတာဟ",
    "ခွေးမလေးဟောင်ပြ",
    "သေမယ်၀က်မ မင်းအမေ၀က်မကိုစားပြ",
    "မအေလိုးရုပ်က ပဲရေပွကြော်ပဲစားနေရတဲ့စောက်ခွက်",
    "ကိုကြီးတို့လို ချိစ်ဘာဂါ မာလာရှမ်းကောတွေ မ၀ယ်စားနိုင်တာဆို",
    "ကြက်ဥကြော်ပဲနေ့တိုင်းစားနေရတာဆိုဆင်းရဲသား",
    "ငါလိုးမကုလားပဲဟင်းပဲစားရတာဆို",
    "မင်းအမေတညလွတ်လိုက်လေ ဖုန်းပြင်ခပေးမယ်လေ",
    "မင်းအမေကမင်းဖုန်းမှန်ကွဲနေတာမပြင်ပေးနိုင်တာဆို ပိုက်ဆံမရှိတာဆို",
    "မင်းဖုန်းမှန်ကွဲနေတာမလဲနိုင်တာဆို",
    "ဘယ်လိုလုပ်မလဲဟ",
    "ငါလိုးမသားလေးမင်းအဆဲခံနေရဘီဟ",
    "မအေလိုးမင်းကိုဆဲတယ် မင်းမိဘနှမငါတက်လိုး",
    "ချေပနိုင်စွမ်းမရှိလို့ဆိုညီက",
    "မအေလိုး လီးဖုန်းစောက်စုတ်နဲ့",
    "မင်းအမေဗစ်ခိုးပြီးရှုတာဆို",
    "သေမယ်နော်၀က်မ",
    "ငါလိုးမသား မင်းစာဘာအဓိပ္ပာယ်မှကိုမရှိဘူး စောက်ပညာမဲ့",
    "ငါလိုးမလိပ်နှေးကွေးနေတာပဲစာတစ်လုံးနဲ့တစ်လုံးဆို",
    "ကျွန် မသားတွေ ဖျော်ဖြေပေးစမ်းကွာ",
    "ငါလိုးမကုလားမင်းအမေသေဘီဆို",
    "မင်းအမေရက်လည်နေ့ကမလာနိုင်တာဆောတီးကွာ",
    "မင်းအဖေထောင်ကျနေတာလားဘာအမှုနဲ့လဲဟ",
    "မင်းအဖေ ခိုးမှုနဲ့ ထောင်ကျတာဆို",
    "ယျောင့် မင်း‌ထောင်ထွက်သားဆို",
    "ငါလိုးမစောက်တောသား",
    "ညီလိုင်းမကောင်းဘူးလား ဘာလဲ ဆင်းရဲလို့လား",
    "ညီတို့တောဘက်မှာ 4g internet မရဘူးလားဟ",
    "ငါလိုးမကုလား ဘေချေသုံးနေရတဲ့အဆင့်နဲ့",
    "မရှက်ဘူးလားဟ အမေလစ်ရင် ပိုက်ဆံခိုးတာ",
    "တနေ့မုန့်ဖိုး500ပဲရတာဆိုညီက",
    "စာတွေမမှန်ဘူးညီ မင်းအမေကျောင်းမထားနိုင်ဘူးလားဟ",
    "ငါလိုးမသားငါ့ကြောက်လို့လက်တုန်ပြီးစာမှန်ဘူးဆို",
    "ညီမင်းစာတွေထပ်နေတယ်ဘာလဲကြောက်လို့လား",
    "စောက်စုန်းလားလီးစုန်းလားလီးစုပ်စုန်းလားဟ",
    "ငါလိုးမကုလားသေမယ်",
    "မင်းအမေကိုမှန်းပြီးအာသာဖြေတာဆို",
    "မင်းအမေကိုမင်းဖေကလိင်မဆက်ဆံတော့မင်းအမေကသူများလိုးခိုင်းရတာဟ",
    "မင်းကဂေးဆိုညီငါသိတယ်နော်",
    "မင်းအဖေကဂေးဆိုညီ",
    "မင်းအ‌မေငါတက်လိုးလို့လူဖြစ်လာတာ မအာနဲ့ခွေးမသား"
    "မေမေ့သားလားဟ မင်းကလဲ ငါဆဲလို့ငိုယိုပြီးသွားတိုင်ရတယ်တဲ့",
    "မင်းအမေကိုသွာတိုင်နေတာလားဟ",
    "တကယ့်ကောင် ကိုယ့်အမေကိုသူများလိုးခိုင်းရတယ်လို့",
    "ဘာလဲမင်းစာမှန်အောင်ငါတက်လိုးပေးပြီးထွက်လာရင် မှန်မယ်ထင်တယ်",
    "တော်စမ်းခွေးရာ ခွေးစကားတွေစောက်ရမ်းပြောတယ်နော်",
    "ဖြည့်တွေ့ရအောင်မင်းက ဖြည့်တွေးပေးလိုရတဲ့စောက်ဆင့်ရှိရဲ့လား",
    "စာတွေကလဲလိပ်တက်လိုးလို့ထွက်လာတဲ့ကောင်ကျနေတာပဲ",
    "မနာလိုမှုတွေများပြီး မင်းငါစလို့ကြိတ်ခိုးလောင်နေတာဆို",
    "ဘာလဲငါ့ဆဲတဲ့စာကိုမင်းအရမ်းကြိုက်သွားတာလား",
    "ဟိတ်ခွေးမင်းငါ‌ဆဲသလိုပြန်ဆဲတာလား",
    "စောက်ရူးလို့ပြောရင်မင်းကိုယ်မင်းစောက်ရူးဆိုပြီးဂုဏ်ယူနေအုံးမယ်",
    "မင်အမေဗစ်ရာလေးတွေမြင်ပြီးလီးတောင်တာဆို",
    "မင်းအမေအာသာဖြေနေတာကိုမင်းချောင်းကြည့်ပြီးထုနေတာဆို၀က်ရ",
    "ညညမင်းအမေမှန်းထုတာဆိုညီ",
    "ငိုစမ်း",
    "ချေပနိုင်စွမ်းမရှိ",
    "လိုးတတ်တယ်မင်းအမကို",
    "ဦးနှောက်ဂုတ်ကပ်",
    "ဖာသည်မသားလေးလိုးခွဲပေးမယ်စာကိုလီးလောက်တတ်",
    "မင်းမေလိုးဖာသည်မသား ဘိတ်မရလို့ခိုးငိုတာလားဟ Typingကြတော့လဲနှေးကွေးဖာပိန်းမသား ငါနင်းတာက ငါလိုးရင်ငြိမ်နေ",
    "နှမလိုးလေး",
    "နွားမသား",
    "ငှက်လိုးမသား",
    "ဝက်မသား",
    "တောပိန်း",
    "ကုလား",
    "ရေငုပ်တာလား",
    "ဖေဖေခေါ်",
    "ငနုလေးစောက်ကုလား",
    "ဆရာခေါ်",
    "တပည့်",
    "နွားမသားခိုးငိုတာလားဟ",
    "ရိုက်ဟ",
    "ပြေးပီလား""ဖသည်မသား ၁၂၃ ဆိုတာနှင့်ကိုယ့်အမေကိုလိူဖို့အဆင့်‌သင့်ပြင်ထား",
    "ခွေးပုကြီး အောက်ကနေ ဘာတွေအူနေတာလဲ အေ့ခန ငါအရိုးလာကျွေးမယ် ထပ်အူမနေနဲ့ နှုတ်သီးဖျက်ကန်လိုက်လို့ အမျိုးပါလွမ်းသွားမယ်",
    "မင်းခွေးဖစ်နေချိန်ငါလိမ့်ကန်တာခံရလို့ အရွတ်တွေပါတက်ကုန်ပီလားဟ",
    "မင်းနားမလည်နိုင်လောက်အောင် မင်းစောက်ဖြုတ်ဦးနှောက်နဲ့မတွေးနိုင်လောက်အောင် ငါ့အရေးအသားက စောက်ရမ်းအထာကျနေတာလား",
    "မင်းလိုလဒူကို ငါကဘာအကြောင်းပြချက်နဲ့မေးပေးရမာ ငါမေးတာခံချင်ရင် ငါ့ဘောလာမလေ",
    "ဘာလဲ အခုလို စကားလုံးလှလှလေးတွေနဲ့ အနိုင်ယူပစ်တော့ မင်းခမျာ ဒေါသ‌မီးတောက်တွေ တဟုန်းဟုန်းလောင်မြိုက်နေပီလား ဒါ‌ဆို ခေါင်းလေးမော့ထား သေးနဲ့ပန်းပေးမယ်လေ ရေဆာနေသေးရင် ပါးစပ်ပါဟထားလိုက်ပေါ့",
    "မင်းအဖြစ်က ကြိုးပျက်နေတဲ့ ကကြိုးရုပ်လေးတရုပ်လိုပါပဲ ကူကယ်ရာမဲ့ဖြစ်နေပီဟ ကုန်းကောက်လို့မရတဲ့အခြေနေတစ်ခုမှ လက်ကမ်းနေတာလား ဒါဆို အဲ့လက်ကို ငါတက်နင်းပစ်မယ်လေ မတော်တဆ တော်ရင်နှစ်ဆပေါ့ကွာ",
    "တယ်လီဂရမ်မှာငါအမြန်ဆုံးဘဲကွ",
    "၁၂၃ စကိုက်လို့ရပြီဘောမ",
    "ဘနှင့်စပြီးမနှင့်ဆုံးတဲ့ဘောမ",
    "မင်းအမေသေတာငါနှင့်ဘာဆိုင် 😹🤞",
    "အသံကိုကပိညှပ်ပိညှပ်နှင့်နရင်းပိတ်အုပ်လိုက်မယ်",
    "ငါနိုင်တာနောက်ပွင့်မဲ့ဘုရားတောင်သိတယ်",
    "ကိုက်လေဖာသယ်မသားမောနေတာလားပါးပိတ်ရိုက်လိုက်မယ်",
    "Outer space ထဲကို မင်းဖင်မှာMissileတတ်ပီး လွှတ်လိုက်လို့ Outermost layer of the Earth ထဲမှာ Alien တွေဆီမှာ intercourse ခံနေရမယ်ကြားလားခွေးမသား😹👆👆",
    "ဖာသည်မသား",
    "ဘယ်လိုအထင်နဲ့မင်းကိုယ်မင်းဆိုလ်ရှယ်ဂေါ့လို့ထင်တာလည်းငါ့အမြင်မှာသေးသေးလေးမင်းကကျွန်ပိန်းခြေမစုပ်ပါလားရောယောင်နေတာငပိန်းလိပ်လိုးမသားနှေးလိုက်တာမြန်ရေးပြီးကိုက်",
    "ရိုက်ဖားကြီးငါရိုက်တာခံနေရတာလားရိုက်ဖားခိုင်းနွားငါခိုင်းရင်တန်းလုပ်အခုဆဲလေရိုက်ဖားလေးဘာစောက်သုံးကျ၁ပြီး၂လာတာပဲသိတဲ့ရွာသားလားဘောမ",
    "မင်းအမေစပတ်ကိုမော်တာတပ်လိုးပြီးစပိုက်တာမန်းလိုကြိုးဆွဲလိုးမှာငါလိုးမဖာသယ်မဖားအိုမဖာပျက်မခွေးမနွားမသား",
    "မင်းရဲ့ဉာဏ်ရည်ကခွေးလိုးထားတာလားစောက်ကုလားသုတ်ရည်ဝင်နေတာလားပါးစပ်ထဲမင်းအမေရဲ့သုတ်ရည်ငံကျိကျိနဲ့မင်းပါးစပ်ထဲထဲ့ထားဆားမလိုတဲ့ဟင်းတစ်ခွက်လေဖာသယ်မ",
    "စောက်ရမ်းအာထုနေမယ့်အစားမင်းအဖေကိုmaster bateဘိတ်လုပ်ပေးလိုက်ပါလားမင်းမိဘလိုးမရဲ့",
    "ဖာသည်မသားမင်းအမေသေလို့အူမြူးနေတာလား",
    "ကြောင်တောင်တောင်လုပ်မနေနှင့်မင်းအမေဖာသည်မရှောပြီ",
    "ကိုမေကိုလိုးမင်းအာချောင်ရင်မင်းစော်ငါဘု",
    "တယ်လီဂရမ်မှာငါအမြန်ဆုံးကွသိဖို့",
    "ကိတ်ခြောက်စားပြီးစိတ်ခြောက်ခြားနေရင်မင်းမိဘပေးဘု",
    "ကိုမေကိုလိုး ကြောက်ရင်ကြောက်တယ် လို့အခုကတည်းကပြော လျှော်ပေးမယ်🤞🥶",
    "ဟိတ်ကောင်မအေလိုး၁၂၃ဆိုတာနဲ့ကိုယ်မေကိုယ်ပြန်လိုးဖို့အဆင်သင့်ပြင်ထားတော့😂👌",
    "ဒေါသတွေထွက်ပြီးငယ်ထိပ်ကြီနီလာပါလားဘယ်လိုလည်းဘောမ စိတ်အတော်ညစ်ပြီးအပေါသွေးအောက်သွေးမမျှတောဘူးလား😂👈",
    "မအေလိုးဝက်ကိုက်မှာသာကိုက်စကားပလ္လင်ခံမနေနဲ့နောက်ဆုံးမင်းဒီဘူတာပဲဆိုက်မှာ😂✌️",
    "မအေလိုးပေါက်စခေါင်းကိုငုံ့ထားမင်းကိုဆုံးမနေတာမင်းဆရာကံကြီးထိုက်မယ်😂✌️",
    "မင်းဆရာငါ ကလစ်ရင်မင်းစိတ်ထိခိုက်တယ်မလား ကလစ်တယ်ကွာဘာတတ်နိုင်သေးလဲ👉😂",
    "မအေလိုးစောက်ရူး လည်တော့လည်တယ်မင်းတစ်ပတ်မပြည့်ဘူး😂✌️",
    "ငါ က အမေလို မင်းကိုသနားနေမာ မဟုတ်ဘူး ဘစ်အုပ်ပြီး ဒစ်စုပ်ခိုင်းလိုက်မယ် 👌",
    "မင်းအမေဖင်ကို ကြည့်ပြီးလီးတောင်နေခို့ လီးလေးကို ခေတ္တငုံပေးထားပါလား🤞",
    "မင်းအမေစဖုတ်ထဲ ကင်းဝင်လို့ဆို😂မင်းအမေကို မင်းချစ်လား မင်းမချစ်ပေမဲ့ ငါချစ်တယ် မင်းအမေကို",
    "တစ်ညလုံးဆဲခံနေရလို့ပလတ်ကျွတ်ခ်ိန်းနေပြီးလားဟေ့ရောင်ဘောမ😂👌",
    "ငါမြန်နေတာကိုကြည့်ပြီးထူးဆန်းနေလား တပည့်😂👌",
    "ဖာသည်မ",
    "မအေလိုးပေါက်စခေါင်းကိုငုံ့ထားမင်းကိုဆုံးမနေတာမင်းဆရာကံကြီးထိုက်မယ်😂✌️",
    "လက်လဲမြန်သလိုလီးလဲမြန်တယ်ငါက",
    "အာမထုနဲ့ညီမင်းကိုဝိုင်းပြီးအမဲဖျတ်တော့မှာ စိတ်ကိုတည်တည်ငြိမ်ငြိမ်နဲ့သာအသက်ထွက်",
    "ငါမင်းမေကိုလိုးလိုက်တာ social media မှာဟိုးလေးတကျော်ကျော်ဖြစ်သွားတာလား",
    "ငါလဲတစ်စိတ်တဒေသကနေ ကူညီတဲ့အနေနဲ့ မင်းအမေကိုဝိုင်းလိုးပေးမယ်",
    "မင်းကဖအေများလှချည်လားကွ အဲ့မိုထင်တယ် မင်းရုပ်ကလူပေါင်းစုံရုပ်ထွက်နေတာ",
    "မင်း brain lvlက 1%ပဲရှိတယ်ညီ brain တစ်ခုမှ စဉ်းစားနိုင်စွမ် 2.5 proliferation ပါတယ် အဲ့တော့မင်းငါကိုနိုင်ဖိုအတွက် မင်းရဲ့အတိတ်ကဖြစ်ရပ်ဆိုးတွေကို Restart ချပြီး problem အသစ်ဆွဲဖို့ မင်းကို brain wash ပေးရလိမ့်မယ်ညီ",
])
name_map: Dict[str, str] = load_json(NAME_MAP_FILE, {})
translate_targets: Dict[str, int] = load_json(TRANSLATE_TARGETS_FILE, {})
security_log: List[Dict] = load_json(SECURITY_LOG_FILE, [])
unauthorized_log: List[Dict] = load_json(UNAUTHORIZED_LOG_FILE, [])
member_cache: Dict[str, Dict[str, Any]] = load_json(MEMBER_CACHE_FILE, {})
watch_list: Dict[str, Dict[str, Any]] = load_json(WATCH_LIST_FILE, {})
active_attack_tasks = {}  # key = chat_id, value = asyncio.Task
stats_data: Dict[str, Any] = load_json(STATS_FILE, {
    "global": {
        "attacks_started": 0,
        "messages_processed": 0,
        "commands_executed": 0,
        "users_watched": 0,
        "ghosted_messages": 0,
        "trolled_messages": 0,
        "watch_logs_created": 0,
        "bans": 0,
        "mutes": 0,
        "kicks": 0,
        "members_cached": 0
    },
    "per_chat": {},
    "per_user": {}
})
watch_log: List[Dict] = load_json(WATCH_LOG_FILE, [])
lock_config: Dict[str, Dict[str, Any]] = load_json(LOCK_FILE, {})
limit_admins: Dict[str, Dict[str, Any]] = load_json(LIMIT_ADMINS_FILE, {})
global_lock_config: Dict[str, Dict[str, Any]] = load_json(GLOBAL_LOCK_FILE, {})
filters_data: Dict[str, Dict[str, Any]] = load_json(FILTERS_FILE, {})
limit_commands_data: Dict[str, Dict[str, Any]] = load_json(LIMIT_COMMANDS_FILE, {})
gpspam_tasks: Dict[int, asyncio.Task] = {}  # {target_group_id: asyncio.Task}
location_tracking = load_json(LOCATION_TRACKING_FILE, {})
welcome_data = load_json(WELCOME_FILE, {})
goodbye_data: dict = load_json(GOODBYE_FILE, {})
reply_targets = load_json(REPLY_TARGETS_FILE, {})
ban_words_data = load_json(BAN_WORDS_FILE, {})
owners_data = load_json(OWNERS_FILE, {"ids": []})
EXTRA_OWNER_IDS = set(int(x) for x in owners_data.get("ids", []) if str(x).isdigit())

# runtime caches - OPTIMIZED FOR SPEED
message_history: Dict[Tuple[int, int], deque] = {}
username_to_userid: Dict[Tuple[int, str], int] = {}
name_map_intkey: Dict[int, str] = {int(k): v for k, v in name_map.items()}
ghost_map: Dict[int, set] = {}
troll_map: Dict[int, set] = {}

# attack states - MAXIMUM SPEED
attacking_single: Dict[int, str] = {}
attacking_single_display: Dict[int, str] = {}
attacking_multiple: Dict[int, List[str]] = {}
attacking_multiple_displays: Dict[int, List[str]] = {}
reply_targets: Dict[str, Dict[str, Any]] = {}  # {chat_id: {target_id: data}}
attack_tasks: Dict[Any, asyncio.Task] = {}
attack_delay: Dict[int, float] = {}
DEFAULT_DELAY = 0.5
attack_mode = "normal"  # normal, burst, zero_delay
quick_attack_targets = {}  # {chat_id: (target_id, display_name)}
burst_mode_config: Dict[int, Dict[str, Any]] = {}
smart_attacks: Dict[int, Dict[str, Any]] = {}
added_targets: Dict[int, List[Tuple[int, str]]] = {}  # {chat_id: [(user_id, display_name)]}
processed_settarget_messages = set()
SETTARGET_REPLY_COUNT = 8  # How many different replies to send
fight_broadcast_sessions = {}
FIGHT_PAGE_SIZE = 6  # 6 groups per page
secret_attacks = {}  # {target_id: {chat_id: attack_task}}
secret_targets = {}  # {target_id: display_name}
megaspam_attacks = {}
active_fight_sessions = {}
# Global variable to track active call tasks
active_call_tasks = {}
call_progress = {}  # Track which users have been called
# Store group IDs where ghost mode is active
active_ghost_chats = set()
TOPIC_CACHE = {}
AUTHORIZED_USERS = []  # empty = public

DOWNLOAD_SEMAPHORE = asyncio.Semaphore(3)

TT_CACHE = {}
TT_COOLDOWN = {}
COOLDOWN_TIME = 10

USER_AGENTS = [
"Mozilla/5.0 (Linux; Android 13)",
"Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X)",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
]





# combo states
combo_states: Dict[int, Dict[str, Any]] = {}

# media-group cache
media_group_cache: Dict[Tuple[int, str], List[Message]] = {}
media_group_order = deque(maxlen=400)
MAX_ITEMS_PER_GROUP = 400

# fallback replies
default_auto_replies = ["Get rekt.", "This is your end."]


def is_duplicate_action(chat_id: int, user_id: int, action: str) -> bool:
    """စက္ကန့်ပိုင်းအတွင်း Message ထပ်မပို့စေရန် စစ်ဆေးသည်"""
    key = f"{chat_id}_{user_id}_{action}"
    now = time.time()
    # ၁၀ စက္ကန့်အတွင်း အတူတူပဲ ထပ်ဖြစ်ရင် Duplicate အဖြစ်သတ်မှတ်မည်
    if key in recent_actions and (now - recent_actions[key]) < 10:
        return True
    recent_actions[key] = now
    return False

def build_text(template: str, user, chat) -> str:
    """Username (သို့) Full Name ကို Mention ခေါ်ပြီး Blockquote ဖြင့် အုပ်သည်"""
    if user.username:
        name_str = f"@{user.username}"
    else:
        escaped_name = html.escape(user.full_name or "Unknown")
        name_str = f'<a href="tg://user?id={user.id}">{escaped_name}</a>'

    group_str = html.escape(chat.title or "Group")
    
    text = template.replace("{name}", name_str).replace("{group}", group_str)
    return f"<blockquote>{text}</blockquote>"
    
# ---------------- ULTRA PERFORMANCE OPTIMIZER ----------------
class UltraPerformanceOptimizer:
    def __init__(self):
        self.message_processing = asyncio.Semaphore(50)  # HIGH CONCURRENCY
        self.attack_processing = asyncio.Semaphore(20)   # MAX ATTACKS
        self.command_processing = asyncio.Semaphore(30)  # FAST COMMANDS
        self.cache_processing = asyncio.Semaphore(5)     # CACHE OPS
        self.ghost_processing = asyncio.Semaphore(10)    # GHOST DELETION
        self.broadcast_processing = asyncio.Semaphore(15) # BROADCAST OPS
        
    async def process_message(self, coro):
        async with self.message_processing:
            return await coro
            
    async def process_attack(self, coro):
        async with self.attack_processing:
            return await coro
            
    async def process_command(self, coro):
        async with self.command_processing:
            return await coro
            
    async def process_cache(self, coro):
        async with self.cache_processing:
            return await coro
            
    async def process_ghost(self, coro):
        async with self.ghost_processing:
            return await coro
            
    async def process_broadcast(self, coro):
        async with self.broadcast_processing:
            return await coro

optimizer = UltraPerformanceOptimizer()

# ---------------- LIGHTNING FAST UTILITY FUNCTIONS ----------------
def update_stats(stat_type: str, chat_id: int = None, user_id: int = None, increment: int = 1):
    global stats_data
    
    if stat_type in stats_data["global"]:
        stats_data["global"][stat_type] += increment
    
    if chat_id:
        chat_key = str(chat_id)
        if chat_key not in stats_data["per_chat"]:
            stats_data["per_chat"][chat_key] = {}
        stats_data["per_chat"][chat_key][stat_type] = stats_data["per_chat"][chat_key].get(stat_type, 0) + increment
    
    if user_id:
        user_key = str(user_id)
        if user_key not in stats_data["per_user"]:
            stats_data["per_user"][user_key] = {}
        stats_data["per_user"][user_key][stat_type] = stats_data["per_user"][user_key].get(stat_type, 0) + increment
    
    # NON-BLOCKING SAVE
    asyncio.create_task(fast_data.buffered_save(STATS_FILE, stats_data))

def escape_markdown_v1(text: str) -> str:
    """
    Escape text for Normal Markdown (V1)
    ⚠️ FIX: @username (e.g. @nga_zem) ထဲက _ ကို escape မလုပ်တော့ပါ
    Username pattern တွေကို စစ်ပြီး မ touch ဖို့ ပြင်ထားသည်
    """
    if not text:
        return ""
    
    s = str(text)
    
    # FIX: @username pattern တွေကို protect လုပ်မယ် (e.g. @nga_zem မှာ _ escape မလုပ်)
    # username pattern: @ + (letter/digit/underscore){5,32}
    username_pattern = re.compile(r'@[A-Za-z][A-Za-z0-9_]{4,31}')
    
    placeholders = {}
    def _stash(m):
        key = f"\x00UN{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key
    
    safe_text = username_pattern.sub(_stash, s)
    
    # Markdown V1 အတွက် escape လုပ်ရမယ့် character တွေ
    escape_chars = r'_*`[]()'
    
    result = []
    for char in safe_text:
        if char in escape_chars:
            result.append(f'\\{char}')
        else:
            result.append(char)
    
    out = ''.join(result)
    
    # Restore usernames un-escaped
    for key, val in placeholders.items():
        out = out.replace(key, val)
    
    return out


def create_normal_markdown_mention(user_id: int, name: str) -> str:
    """
    Create SAFE Normal Markdown (V1) mention
    Format: [Name](tg://user?id=123)
    """
    if not name:
        name = f"User{user_id}"
    
    # For Normal Markdown, escape fewer characters
    safe_name = escape_markdown_v1(name)
    
    return f"[{safe_name}](tg://user?id={user_id})"

def escape_markdown_v2(text: str) -> str:
    """
    Escape ALL special characters for MarkdownV2
    ⚠️ FIX: @username (e.g. @nga_zem) ထဲက _ . တွေကို escape မလုပ်တော့ပါ
    ⚠️ ဒါကို Link ထဲမှာ တိုက်ရိုက်မသုံးပါနဲ့။ Link အတွက် create_safe_mention ကိုသုံးပါ။
    """
    if not text:
        return ""
    
    s = str(text)
    
    # FIX: @username pattern တွေကို protect လုပ်မယ်
    username_pattern = re.compile(r'@[A-Za-z][A-Za-z0-9_]{4,31}')
    
    placeholders = {}
    def _stash(m):
        key = f"\x00UN{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key
    
    safe_text = username_pattern.sub(_stash, s)
    
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    result = []
    for char in safe_text:
        if char in escape_chars:
            result.append(f'\\{char}')
        else:
            result.append(char)
    
    out = ''.join(result)
    
    # Restore usernames un-escaped
    for key, val in placeholders.items():
        out = out.replace(key, val)
    
    return out



def escape_name_for_markdown_v2(text: str) -> str:
    """Special escape function for names inside MarkdownV2 mentions"""
    if not text:
        return ""
    
    # For names inside [Name] part of [Name](tg://user?id=123)
    # We need to escape ALL special MarkdownV2 characters
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    result = []
    for char in str(text):
        if char in escape_chars:
            result.append(f'\\{char}')
        else:
            result.append(char)
    
    return ''.join(result)


def create_safe_mention(user_id: int, name: str) -> str:
    """Create a safe MarkdownV2 mention that won't break"""
    if not name:
        name = f"User{user_id}"
    
    # Escape the name for MarkdownV2
    safe_name = escape_name_for_markdown_v2(name)
    
    # Create the mention link
    return f"[{safe_name}](tg://user?id={user_id})"

async def show_typing_action(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Show typing action for multiple speed modes"""
    current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
    
    # Show typing for these specific speeds: 0.2, 1, 1.5, 2 seconds
    if current_delay in [0.2, 1, 1.5, 2]:
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
        except Exception:
            pass


def is_owner(user) -> bool:
    if not user:
        return False

    user_id = getattr(user, "id", None)

    # Real owner (from code)
    if OWNER_CHAT_ID and user_id == OWNER_CHAT_ID:
        return True

    # Extra owners
    if user_id in EXTRA_OWNER_IDS:
        return True

    # Username check
    username = getattr(user, "username", None)
    if username and OWNER_USERNAME:
        if ("@" + username).lower() == OWNER_USERNAME.lower():
            return True

    return False


def is_authorized(user) -> bool:
    if not user:
        return False

    user_id = getattr(user, "id", None)
    username = getattr(user, "username", None)

    if is_owner(user):
        return True

    if user_id in ADMIN_IDS:
        return True

    if username and username.lower() in [u.lower() for u in ADMIN_USERNAMES]:
        return True

    return False

def get_detailed_message_type(msg):
    """Get detailed message type information"""
    if msg.text:
        has_links = any(entity.type == "url" for entity in (msg.entities or []))
        return f"📝 Text message{' + 🔗 Links' if has_links else ''}"
    elif msg.photo:
        has_caption = bool(msg.caption)
        has_links = any(entity.type == "url" for entity in (msg.caption_entities or []))
        return f"🖼️ Photo{' + 📝 Caption' if has_caption else ''}{' + 🔗 Links' if has_links else ''}"
    elif msg.video:
        has_caption = bool(msg.caption)
        has_links = any(entity.type == "url" for entity in (msg.caption_entities or []))
        return f"🎥 Video{' + 📝 Caption' if has_caption else ''}{' + 🔗 Links' if has_links else ''}"
    elif msg.document:
        has_caption = bool(msg.caption)
        return f"📎 Document: {msg.document.file_name or 'File'}{' + 📝 Caption' if has_caption else ''}"
    elif msg.audio:
        has_caption = bool(msg.caption)
        return f"🎵 Audio{' + 📝 Caption' if has_caption else ''}"
    elif msg.voice:
        has_caption = bool(msg.caption)
        return f"🎤 Voice message{' + 📝 Caption' if has_caption else ''}"
    elif msg.sticker:
        return "😀 Sticker"
    elif msg.location:
        return "📍 Location"
    elif msg.contact:
        return "👤 Contact"
    elif msg.animation:
        return "🎬 GIF/Animation"
    elif msg.media_group_id:
        return "📚 Media Album"
    else:
        return "📨 Unknown content"


def owner_matches_target(target_str: str) -> bool:
    if not target_str:
        return False
    
    s = str(target_str).strip()
    
    if s.isdigit() and OWNER_CHAT_ID and int(s) == OWNER_CHAT_ID:
        return True
    
    if s.startswith("@") and OWNER_USERNAME and s.lstrip().lower() == OWNER_USERNAME.lstrip().lower():
        return True
    
    for uid_str, nickname in name_map.items():
        if nickname.lower() == s.lower():
            try:
                if OWNER_CHAT_ID and int(uid_str) == OWNER_CHAT_ID:
                    return True
            except ValueError:
                continue
    
    return False

async def notify_owner(context: ContextTypes.DEFAULT_TYPE, message: str):
    if OWNER_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=message, parse_mode="Markdown")
        except Exception:
            pass

def normalize_target_string(t: str) -> str:
    if t is None:
        return ""
    s = str(t).strip()
    if s.startswith("@"):
        return s
    try:
        return str(int(s))
    except Exception:
        return s

def extract_wait_time(error_msg: str) -> int:
    """Extract wait time from flood error message"""
    import re
    patterns = [
        r'wait[^\d]*(\d+)[^\d]*seconds',
        r'(\d+)[^\d]*seconds[^\d]*wait',
        r'retry after[^\d]*(\d+)',
        r'(\d+)[^\d]*second wait'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match:
            wait_time = int(match.group(1))
            return min(30, wait_time + 2)  # Add buffer, max 30s
    
    return 10  # Default wait

def create_markdown_mention(user_id: int, name: str, version: str = "v1") -> str:
    """
    CREATE SAFE MENTION - ဒါကိုပဲ အဓိကသုံးပါ
    
    Parameters:
        user_id: User ID
        name: Display name (username, first_name, nickname)
        version: "v1" for Normal Markdown, "v2" for MarkdownV2
    
    Examples:
        create_markdown_mention(123456, "MgMg", "v1") 
        -> [MgMg](tg://user?id=123456)
        
        create_markdown_mention(123456, "Ko_Ko", "v2")
        -> [Ko\\_Ko](tg://user?id=123456)
    """
    if not name:
        name = f"User{user_id}"
    
    if version == "v2":
        # MarkdownV2 အတွက် - name ကို escape လုပ်မယ်
        safe_name = escape_markdown_v2(name)
    else:
        # Markdown V1 အတွက် - အနည်းငယ်ပဲ escape လုပ်မယ်
        safe_name = escape_markdown_v1(name)
    
    return f"[{safe_name}](tg://user?id={user_id})"
    
    
async def get_display_name(context, chat_id: int, user_id: int) -> str:
    """
    Get display name for a user (nickname -> real name -> fallback)
    Returns PLAIN TEXT name (not mention)
    """
    # 1. Check nickname in name_map
    nickname = name_map_intkey.get(user_id) or name_map.get(str(user_id))
    if nickname:
        return nickname
    
    # 2. Get real name from Telegram
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.user.first_name or f"User{user_id}"
    except:
        pass
    
    # 3. Check member cache
    chat_key = str(chat_id)
    if chat_key in member_cache:
        user_data = member_cache[chat_key].get("members", {}).get(str(user_id))
        if user_data:
            return user_data.get("first_name") or f"User{user_id}"
    
    # 4. Fallback
    return f"User{user_id}"   

async def get_mention_for_target(context, chat_id: int, target: str, parse_mode: str = "v1") -> str:
    """
    MAIN FUNCTION: Get proper mention for a target
    ဒါကိုပဲ အကုန်လုံးက ခေါ်သုံးပါ
    
    Parameters:
        context: Bot context
        chat_id: Chat ID
        target: Target string (user ID, @username, nickname)
        parse_mode: "v1" for Markdown, "v2" for MarkdownV2
    
    Returns:
        Markdown mention string like [Name](tg://user?id=123)
    """
    if not target:
        return ""
    
    s_target = str(target).strip()
    
    # === CASE 1: Nickname in name_map ===
    for user_id_str, nickname in name_map.items():
        if nickname.lower() == s_target.lower():
            try:
                user_id = int(user_id_str)
                # Verify user exists (optional, skip if slow)
                return create_markdown_mention(user_id, nickname, parse_mode)
            except:
                return nickname  # Fallback to plain text
    
    # === CASE 2: Target is a user ID with nickname ===
    if s_target in name_map:
        try:
            user_id = int(s_target)
            nickname = name_map[s_target]
            return create_markdown_mention(user_id, nickname, parse_mode)
        except:
            pass
    
    # === CASE 3: Direct user ID ===
    if s_target.isdigit():
        try:
            user_id = int(s_target)
            name = await get_display_name(context, chat_id, user_id)
            return create_markdown_mention(user_id, name, parse_mode)
        except:
            return create_markdown_mention(int(s_target), f"User{s_target}", parse_mode)
    
    # === CASE 4: Username (@username) ===
    if s_target.startswith("@"):
        username = s_target[1:].lower()
        
        # Check cache
        if (chat_id, username) in username_to_userid:
            user_id = username_to_userid[(chat_id, username)]
            name = await get_display_name(context, chat_id, user_id)
            return create_markdown_mention(user_id, name, parse_mode)
        
        # Try to get from Telegram
        try:
            member = await context.bot.get_chat_member(chat_id, s_target)
            user_id = member.user.id
            name = member.user.first_name or f"User{user_id}"
            username_to_userid[(chat_id, username)] = user_id
            return create_markdown_mention(user_id, name, parse_mode)
        except:
            # Return as plain @username if can't resolve
            return s_target
    
    # === CASE 5: Search in member cache ===
    chat_key = str(chat_id)
    if chat_key in member_cache:
        for uid, user_data in member_cache[chat_key].get("members", {}).items():
            if user_data.get("username", "").lower() == s_target.lower():
                user_id = int(uid)
                name = user_data.get("first_name") or user_data.get("username") or f"User{uid}"
                return create_markdown_mention(user_id, name, parse_mode)
            if user_data.get("first_name", "").lower() == s_target.lower():
                user_id = int(uid)
                name = user_data.get("first_name") or f"User{uid}"
                return create_markdown_mention(user_id, name, parse_mode)
    
    # === FALLBACK ===
    return s_target

def plain_name_from_mention(display: str) -> str:
    """Extract plain name from a mention string"""
    if not display:
        return ""
    
    s = str(display)
    
    # Markdown link: [Name](tg://user?id=...)
    if s.startswith("[") and "](" in s:
        try:
            return s.split("]", 1)[0].lstrip("[")
        except:
            return s
    
    # @username
    if s.startswith("@"):
        return s
    
    return s

async def resolve_target_user_id(context, chat_id: int, arg: str) -> Optional[int]:
    """
    Resolve target to user ID ONLY (no mention)
    Used when you just need the ID
    """
    if not arg:
        return None
    
    arg = str(arg).strip().lower()
    
    # 1. Check name_map
    for user_id_str, nickname in name_map.items():
        if nickname.lower() == arg:
            try:
                return int(user_id_str)
            except:
                continue
    
    # 2. Direct user ID
    if arg.isdigit():
        return int(arg)
    
    # 3. Username
    if arg.startswith("@"):
        username = arg[1:]
        
        # Check cache
        if (chat_id, username) in username_to_userid:
            return username_to_userid[(chat_id, username)]
        
        # Try Telegram
        try:
            member = await context.bot.get_chat_member(chat_id, arg)
            user_id = member.user.id
            username_to_userid[(chat_id, username)] = user_id
            return user_id
        except:
            pass
    
    # 4. Check member cache
    chat_key = str(chat_id)
    if chat_key in member_cache:
        for uid, user_data in member_cache[chat_key].get("members", {}).items():
            if user_data.get("username", "").lower() == arg:
                return int(uid)
            if user_data.get("first_name", "").lower() == arg:
                return int(uid)
    
    return None

async def resolve_target_to_id_and_display(context: ContextTypes.DEFAULT_TYPE, chat_id: int, arg: str) -> Tuple[Optional[int], str]:
    """Resolve target to ID and Normal Markdown mention"""
    target_id = await resolve_target_user_id(context, chat_id, arg)
    
    if target_id:
        # Check for nickname
        nickname = name_map_intkey.get(target_id) or name_map.get(str(target_id))
        
        if nickname:
            # Use nickname
            safe_name = escape_markdown_v1(nickname)
            display = f"[{safe_name}](tg://user?id={target_id})"
            print(f"🎯 Using nickname: {nickname} for user {target_id}")
        else:
            # Get actual name
            try:
                member = await context.bot.get_chat_member(chat_id, target_id)
                user = member.user
                user_name = user.first_name or f"User{target_id}"
                safe_name = escape_markdown_v1(user_name)
                display = f"[{safe_name}](tg://user?id={target_id})"
            except Exception:
                # Fallback
                safe_name = escape_markdown_v1(f"User{target_id}")
                display = f"[{safe_name}](tg://user?id={target_id})"
        
        return target_id, display
    else:
        # If can't resolve to ID
        return None, escape_markdown_v1(arg)

async def resolve_target_to_id_and_display_markdownv2(context: ContextTypes.DEFAULT_TYPE, chat_id: int, arg: str) -> Tuple[Optional[int], str]:
    """Resolve target to ID and MarkdownV2 mention"""
    target_id = await resolve_target_user_id(context, chat_id, arg)
    
    if target_id:
        # Check for nickname
        nickname = name_map_intkey.get(target_id) or name_map.get(str(target_id))
        
        if nickname:
            # Use nickname with MarkdownV2 escaping
            safe_name = escape_markdown_v2(nickname)
            display = f"[{safe_name}](tg://user?id={target_id})"
            print(f"🎯 Using nickname with MarkdownV2: {nickname} for user {target_id}")
        else:
            # Get actual name
            try:
                member = await context.bot.get_chat_member(chat_id, target_id)
                user = member.user
                user_name = user.first_name or f"User{target_id}"
                safe_name = escape_markdown_v2(user_name)
                display = f"[{safe_name}](tg://user?id={target_id})"
            except Exception:
                # Fallback
                safe_name = escape_markdown_v2(f"User{target_id}")
                display = f"[{safe_name}](tg://user?id={target_id})"
        
        return target_id, display
    else:
        # If can't resolve to ID
        return None, escape_markdown_v2(arg)

async def universal_resolve_target(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target_arg: str) -> Tuple[Optional[int], str]:
    """UNIVERSAL RESOLUTION for Normal Markdown"""
    if not target_arg:
        return None, ""
    
    target_arg = str(target_arg).strip()
    
    print(f"🔍 Universal resolving: '{target_arg}' in chat {chat_id}")
    
    # 1. Check name_map for nicknames
    for user_id_str, nickname in name_map.items():
        if nickname.lower() == target_arg.lower():
            print(f"✅ Found in name_map: {nickname} -> {user_id_str}")
            user_id = int(user_id_str)
            safe_nickname = escape_markdown_v1(nickname)
            return user_id, f"[{safe_nickname}](tg://user?id={user_id})"
    
    # 2. Check if target_arg is a user ID with nickname
    if target_arg in name_map:
        nickname = name_map[target_arg]
        user_id = int(target_arg)
        safe_nickname = escape_markdown_v1(nickname)
        print(f"✅ Found ID in name_map: {target_arg} -> {nickname}")
        return user_id, f"[{safe_nickname}](tg://user?id={user_id})"
    
    # 3. Try normal resolution
    try:
        target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
        if target_id:
            print(f"✅ Normal resolution worked: {target_arg} -> {target_id}")
            return target_id, display
    except Exception as e:
        print(f"❌ Normal resolution failed: {e}")
    
    # 4. NON-ADMIN FALLBACK:
    
    # 4a. Numeric ID
    if target_arg.isdigit():
        user_id = int(target_arg)
        print(f"✅ Using numeric ID directly: {user_id}")
        safe_name = escape_markdown_v1(f"User{user_id}")
        return user_id, f"[{safe_name}](tg://user?id={user_id})"
    
    # 4b. Username
    if target_arg.startswith("@"):
        print(f"✅ Using username: {target_arg}")
        return None, escape_markdown_v1(target_arg)
    
    # 4c. Check member_cache
    chat_key = str(chat_id)
    if chat_key in member_cache:
        for uid, user_data in member_cache[chat_key].get("members", {}).items():
            if user_data.get("username", "").lower() == target_arg.lower():
                user_id = int(uid)
                username = user_data.get("username")
                print(f"✅ Found in cache by username: @{username}")
                return user_id, f"@{username}"
            
            if user_data.get("first_name", "").lower() == target_arg.lower():
                user_id = int(uid)
                first_name = user_data.get("first_name", "User")
                print(f"✅ Found in cache by name: {first_name}")
                safe_name = escape_markdown_v1(first_name)
                return user_id, f"[{safe_name}](tg://user?id={user_id})"
    
    # 4d. Final fallback
    print(f"⚠️ Final fallback - using as text: {target_arg}")
    return None, escape_markdown_v1(target_arg)

def get_chat_key(chat_id: int) -> str:
    return str(abs(chat_id))


def is_english(word: str) -> bool:
    return bool(re.search(r"[A-Za-z]", word))


#dm ------------------

async def handle_dm_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Notify Owner when a user sends a message to DM.
    Uses MarkdownV2 for proper mentioning.
    """
    # 1. Basic Checks
    if not update.message or not OWNER_CHAT_ID:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    msg = update.message

    # Only process Private chats
    if chat.type != "private":
        return

    # Don't notify if the Owner is messaging the bot
    if user.id == OWNER_CHAT_ID:
        return

    try:
        # 2. Prepare Data
        # Helper to escape special MarkdownV2 chars
        def esc(text):
            if not text: return ""
            return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", str(text))

        # User Info
        first_name = esc(user.first_name or "Unknown")
        user_id = user.id
        # Clickable Mention [Name](tg://user?id=123)
        user_mention = f"[{first_name}](tg://user?id={user_id})"
        
        # Time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Message Preview / Type detection
        msg_type = "Unknown"
        preview_text = ""

        if msg.text:
            msg_type = "Text Message"
            # Take first 50 chars for preview, escape them
            raw_preview = msg.text[:50] + "..." if len(msg.text) > 50 else msg.text
            preview_text = esc(raw_preview)
        elif msg.photo: msg_type = "📷 Photo"
        elif msg.video: msg_type = "🎥 Video"
        elif msg.voice: msg_type = "🎤 Voice"
        elif msg.sticker: msg_type = "😀 Sticker"
        elif msg.document: msg_type = "📁 Document"
        elif msg.location: msg_type = "📍 Location"

        # 3. Construct the Notification Message (Burmese)
        notification_text = (
            f"📩 *Dm သို့စာပို့လာပါတယ်*\n\n"
            f"👤 *User:* {user_mention}\n"
            f"🆔 *Id:* `{user_id}`\n"
            f"⏰ *Time:* `{esc(current_time)}`\n"
            f"📝 *Message Preview:* {esc(msg_type)}\n"
        )
        
        if preview_text:
            notification_text += f"💬 *Content:* {preview_text}"

        # 4. Send Notification to Owner
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=notification_text,
            parse_mode="MarkdownV2"
        )

        # 5. Forward the actual message (What target sent)
        # We use forward_message so you can see the original context/media
        await context.bot.forward_message(
            chat_id=OWNER_CHAT_ID,
            from_chat_id=chat.id,
            message_id=msg.message_id
        )

    except Exception as e:
        print(f"❌ DM Notification Error: {e}")



async def get_user_photo_id(bot, user_id: int):
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos and photos.total_count > 0:
            return photos.photos[0][0].file_id
    except Exception as e:
        logging.error(f"Error fetching photo: {e}")
    return None

async def _delete_after_delay(message, delay: int = 5):
    """Delay ကြာပြီးနောက် message ကိုဖျက်သည်"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logging.error(f"Failed to delete message: {e}")

async def send_event_with_photo(bot, chat_id, user, caption_text, delete_delay: int = 5):
    photo_id = await get_user_photo_id(bot, user.id)
    try:
        if photo_id:
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_id,
                caption=caption_text,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            message = await bot.send_message(
                chat_id=chat_id,
                text=caption_text,
                parse_mode=constants.ParseMode.HTML,
                disable_web_page_preview=True
            )
        
        # 5 စက္ကန့်ကြာရင် ပြန်ဖျက်မယ့် task ကို schedule လုပ်
        asyncio.create_task(_delete_after_delay(message, delay=delete_delay))
        
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

async def on_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cmu = update.chat_member
    chat = update.effective_chat
    if not cmu or not chat:
        return
    
    old_s = cmu.old_chat_member.status
    new_s = cmu.new_chat_member.status
    user = cmu.new_chat_member.user
    
    if user.is_bot:
        return
        
    chat_id_str = str(chat.id)
    S = constants.ChatMemberStatus
    IN_GROUP = {S.MEMBER, S.RESTRICTED, S.ADMINISTRATOR, S.OWNER}
    
    # HTML Formatting for Mention and Group Name
    safe_name = html.escape(user.first_name)
    mention = f'<b><a href="tg://user?id={user.id}">{safe_name}</a></b>'
    group_name = f'<b>{html.escape(chat.title or "ဒီအဖွဲ့")}</b>'

    # --- (က) Welcome Logic (စာသားကို Quote ထဲထည့်ခြင်း) ---
    if old_s not in IN_GROUP and new_s in IN_GROUP:
        tmpl = (welcome_data.get(chat_id_str, {}).get("text") 
                or load_data().get(chat_id_str, {}).get("welcome")
                or "{name} ဆိုတယ်ဖာသယ်မသားသည် {group} သို့ဝင်ရောက်လာခဲ့သည်")
        
        raw_text = tmpl.replace("{name}", mention).replace("{group}", group_name).replace("{title}", group_name)
        final_text = f"<blockquote>{raw_text}</blockquote>"
        await send_event_with_photo(context.bot, chat.id, user, final_text, delete_delay=5)

    # --- (ခ) Goodbye Logic (စာသားကို Quote ထဲထည့်ခြင်း) ---
    elif old_s in IN_GROUP and new_s not in IN_GROUP:
        tmpl = (goodbye_data.get(chat_id_str, {}).get("text") 
                or "ဒီမအေးလိုးဖာသယ်မသား {name} သည် {group} က ကိုကိုတွေကို ကြောက်၍ပြေးပါပြီ")
        
        raw_text = tmpl.replace("{name}", mention).replace("{group}", group_name).replace("{title}", group_name)
        final_text = f"<blockquote>{raw_text}</blockquote>"
        await send_event_with_photo(context.bot, chat.id, user, final_text, delete_delay=5)

#----------------- Link delete ----------------

async def bot_can_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        me = await context.bot.get_me()
        member = await context.bot.get_chat_member(update.effective_chat.id, me.id)
        return member.can_delete_messages
    except:
        return False

async def linkon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global link_control

    user = update.effective_user
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        return

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>Admin ပဲသုံးလို့ရပါတယ်</b>")
        return

    if not await bot_can_delete(update, context):
        await update.message.reply_html(
            "❌ <b>Adm အရင်ခန့်ပါ</b>\n"
            "🗑️ <b>Delete Messages permit ပေးပါ</b>"
        )
        return

    chat_id = str(chat.id)
    # FIX: 'already on' check ဖျက်ထား — အမြဲ re-enable လုပ်ပါ
    link_control[chat_id] = True
    asyncio.create_task(fast_data.buffered_save(LINK_CONTROL_FILE, link_control))

    await update.message.reply_html(
        "🔒 <b>Link / Mention / Forward ဖျက်တာ ဖွင့်ပြီးပါပြီ</b>"
    )

async def linkoff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """FIX: Link guard ကို ဘယ်တော့မှ ပိတ်မရတော့ဘူး။ အမြဲ ON ထားမယ်။"""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        return

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>Admin ပဲသုံးလို့ရပါတယ်</b>")
        return

    # FIX: linkoff တောင်းရင် ignore — link guard ကို အမြဲ ON ထားမယ်
    await update.message.reply_html(
        "🔒 <b>Link / Mention / Forward ဖျက်တာ အမြဲဖွင့်ထားပါတယ် (off မရပါ)</b>\n"
        "✅ <b>Owner Channel forward တွေကိုလုံးဝမဖျက်ပါဘူး</b>"
    )




# FIX: Owner channel လင့်တွေ မဖျက်ရန် whitelist
OWNER_CHANNEL_USERNAMES = {"channelbycrucial", "ofccrucialxwonalwayswin"}

async def link_guard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg:
        return

    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return

    chat_id = str(chat.id)

    # FIX: Linkon ကို အမြဲ ON ထားမယ် (default True ပေမယ့် explicitly OFF လုပ်ထားတဲ့ chat တွေကို respect)
    if chat_id in link_control and link_control.get(chat_id) is False:
        return

    # FIX: Channel post (sender_chat) — Owner channel ferries / channel auto-forward တွေကို မဖျက်ဘူး
    sender_chat = getattr(msg, "sender_chat", None)
    if sender_chat is not None:
        # ✅ Channel/automatic forward / channel post broadcast — မဖျက်ပါနဲ့
        return

    # ✅ Owner / Admin သုမျာ လုံးဝဉ်မရဘူး
    if msg.from_user and is_owner(msg.from_user):
        return

    if not msg.from_user:
        # Anonymous admin (no from_user) — မဖျက်နဲ့
        return

    # bot permission check
    try:
        me = await context.bot.get_me()
        bot_member = await context.bot.get_chat_member(chat.id, me.id)
        if not bot_member.can_delete_messages:
            return
    except:
        return

    # skip admins
    try:
        user_member = await context.bot.get_chat_member(chat.id, msg.from_user.id)
        if user_member.status in ("administrator", "creator"):
            return
    except:
        pass

    reason = None

    # 1️⃣ Forward check — Owner channel မဖျက်နဲ့
    fwd_origin = getattr(msg, 'forward_origin', None)
    if fwd_origin is not None:
        # Check if forwarded from owner channel
        is_owner_channel = False
        try:
            origin_chat = getattr(fwd_origin, "chat", None) or getattr(fwd_origin, "sender_chat", None)
            if origin_chat is not None:
                uname = (getattr(origin_chat, "username", "") or "").lower()
                if uname in OWNER_CHANNEL_USERNAMES:
                    is_owner_channel = True
        except:
            pass
        if not is_owner_channel:
            reason = "Forward စာပို့မရဘူး"

    # ✅ SAFE entities handling (tuple → list)
    entities = []
    if msg.entities:
        entities.extend(msg.entities)
    if msg.caption_entities:
        entities.extend(msg.caption_entities)

    # 2️⃣ Link check
    if not reason:
        for e in entities:
            if e.type in ("url", "text_link"):
                reason = "Link ပို့မရဘူး"
                break

    # 3️⃣ Mention check
    if not reason:
        for e in entities:
            if e.type in ("mention", "text_mention"):
                reason = "Mention ထောက်မရဘူး"
                break

    if not reason:
        return

    # DELETE
    try:
        await context.bot.delete_message(chat.id, msg.message_id)
    except:
        return

    user = msg.from_user
    name = html.escape(user.first_name or "User")
    mention = f'<a href="tg://user?id={user.id}">{name}</a>'

    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"{mention} စည်းမရှိကမ်းမရှိနဲ့ဘယ်ကခွေးလဲ\n"
            ),
            parse_mode="HTML"
        )
    except:
        pass


#Bot Ban words ----------------------------------

async def banword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        return

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>Admin ပဲသုံးလို့ရပါတယ်</b>")
        return

    if not context.args:
        await update.message.reply_html("❗ <b>/banword စကားလုံး</b>")
        return

    word = context.args[0].strip()
    chat_key = get_chat_key(chat.id)

    ban_words_data.setdefault(chat_key, [])

    if word in ban_words_data[chat_key]:
        await update.message.reply_html(
            f"ℹ️ <b>{html.escape(word)}</b> က Ban words list ထဲမှာ ရှိပြီးသားပါ"
        )
        return

    ban_words_data[chat_key].append(word)
    save_json(BAN_WORDS_FILE, ban_words_data)

    await update.message.reply_html(
        f"✅ <b>{html.escape(word)}</b> ကို Ban words list ထဲ ထည့်ပြီးပါပြီ"
    )
async def removeword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        return

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>Admin ပဲသုံးလို့ရပါတယ်</b>")
        return

    if not context.args:
        await update.message.reply_html("❗ <b>/removeword စကားလုံး</b>")
        return

    word = context.args[0].strip()
    chat_key = get_chat_key(chat.id)

    if word not in ban_words_data.get(chat_key, []):
        await update.message.reply_html("ℹ️ <b>Ban words list ထဲမှာ မရှိပါ</b>")
        return

    ban_words_data[chat_key].remove(word)
    save_json(BAN_WORDS_FILE, ban_words_data)

    await update.message.reply_html(
        f"🗑️ <b>{html.escape(word)}</b> ကို Ban words list မှ ဖျက်ပြီးပါပြီ"
    )
async def listword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_key = get_chat_key(chat.id)

    words = ban_words_data.get(chat_key, [])

    if not words:
        await update.message.reply_html("ℹ️ <b>Ban words မရှိသေးပါ</b>")
        return

    text = "<b>🚫 Ban words list</b>\n\n"
    for w in words:
        text += f"• {html.escape(w)}\n"

    await update.message.reply_html(text)
async def banword_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return

    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    chat_key = get_chat_key(chat.id)
    banned_words = ban_words_data.get(chat_key, [])
    if not banned_words:
        return

    text = msg.text

    for word in banned_words:
        escaped = re.escape(word)

        if is_english(word):
            pattern = re.compile(escaped, re.IGNORECASE)
        else:
            pattern = re.compile(escaped)

        if pattern.search(text):
            try:
                await msg.delete()
            except:
                return

            user = msg.from_user
            name = html.escape(user.first_name or "User")
            mention = f'<a href="tg://user?id={user.id}">{name}</a>'
            gp_name = html.escape(chat.title or "Group")

            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🚫 {mention}\n"
                    f"<b>{gp_name}</b> တွင် <b>{html.escape(word)}</b> ကို သုံးမရဘူးညီလေး"
                ),
                parse_mode="HTML"
            )
            break

# ---------------- TIKTOK DOWNLOADER ----------------


def normalize_tiktok_url(url: str) -> str:
    url = url.strip().split("?")[0]

    # convert photo to video endpoint
    if "/photo/" in url:
        url = url.replace("/photo/", "/video/")

    # force mobile
    url = url.replace("www.tiktok.com", "m.tiktok.com")

    return url

async def tt_auto_clean():
    while True:
        await asyncio.sleep(1200)

        for f in list(TT_TEMP_FILES):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
            TT_TEMP_FILES.discard(f)

def progress_hook_factory(msg, loop):
    last_edit = {"t": 0}

    def hook(d):
        if d['status'] != 'downloading':
            return

        now = time.time()
        if now - last_edit["t"] < 2:
            return

        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()

        asyncio.run_coroutine_threadsafe(
            msg.edit_text(
                f"⬇️ <b>Downloading...</b>\n\n"
                f"📊 {percent}\n"
                f"🚀 {speed}\n"
                f"⏳ ETA: {eta}",
                parse_mode=ParseMode.HTML
            ),
            loop
        )

        last_edit["t"] = now

    return hook

async def tiktok_command(update, context):
    user = update.effective_user

    if not is_authorized(user):
        return await update.message.reply_text("❌ Not Authorized")

    now = time.time()
    if user.id in TT_COOLDOWN and now - TT_COOLDOWN[user.id] < COOLDOWN_TIME:
        return await update.message.reply_text("⏳ Slow down.")

    TT_COOLDOWN[user.id] = now

    if not context.args:
        return await update.message.reply_text("/TikTok <url>")

    url = normalize_tiktok_url(context.args[0])

    msg = await update.message.reply_text("🔎 Fetching info...")

    if url in TT_CACHE:
        info = TT_CACHE[url]
    else:
        loop = asyncio.get_event_loop()

        def extract():
            with yt_dlp.YoutubeDL({
                "quiet": True,
                "user_agent": random.choice(USER_AGENTS),
                "referer": "https://www.tiktok.com/",
                "extractor_args": {"tiktok": {"embed_api": ["1"]}}
            }) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            info = await loop.run_in_executor(None, extract)
        except Exception:
            return await msg.edit_text("❌ Unsupported or private link")

        TT_CACHE[url] = info

    context.user_data["tt_url"] = url
    context.user_data["tt_info"] = info

    buttons = []

    if "entries" in info:
        buttons.append(
            [InlineKeyboardButton("📷 Download Slideshow", callback_data="tt_slide")]
        )
    else:
        formats = info.get("formats", [])
        qualities = sorted(
            {f.get("height") for f in formats if f.get("height")},
            reverse=True
        )

        for q in qualities:
            buttons.append(
                [InlineKeyboardButton(f"{q}p", callback_data=f"tt_{q}")]
            )

    await msg.edit_text(
        "Select Quality:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def tt_button_handler(update, context):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("tt_url")
    info = context.user_data.get("tt_info")

    if not url or not info:
        return await query.edit_message_text("❌ Session expired")

    loop = asyncio.get_event_loop()

    session = f"{query.from_user.id}_{int(time.time())}"
    temp_dir = f"tt_{session}"
    os.makedirs(temp_dir, exist_ok=True)

    progress_hook = progress_hook_factory(query.message, loop)

    if query.data == "tt_slide":
        format_string = "best"
    else:
        quality = query.data.replace("tt_", "")
        format_string = f"bestvideo[height<={quality}]+bestaudio/best"

    ydl_opts = {
        "outtmpl": f"{temp_dir}/%(title)s.%(ext)s",
        "quiet": True,
        "progress_hooks": [progress_hook],
        "user_agent": random.choice(USER_AGENTS),
        "referer": "https://www.tiktok.com/",
        "format": format_string,
        "merge_output_format": "mp4",
        "extractor_args": {"tiktok": {"embed_api": ["1"]}}
    }

    async with DOWNLOAD_SEMAPHORE:

        def run():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        try:
            await loop.run_in_executor(None, run)
        except Exception:
            return await query.edit_message_text("❌ Download failed")

    files = glob.glob(f"{temp_dir}/*")

    context.user_data["tt_files"] = files
    context.user_data["tt_temp"] = temp_dir

    buttons = [[
        InlineKeyboardButton("Yes", callback_data="tt_cap_yes"),
        InlineKeyboardButton("Nah", callback_data="tt_cap_no")
    ]]

    await query.edit_message_text(
        "Caption နဲ့ပါလိုချင်ပါသလား?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def tt_caption_handler(update, context):
    query = update.callback_query
    await query.answer()

    files = context.user_data.get("tt_files", [])
    temp_dir = context.user_data.get("tt_temp")
    info = context.user_data.get("tt_info")

    if not files:
        return await query.edit_message_text("❌ Expired")

    caption = info.get("title") if query.data == "tt_cap_yes" else None

    await query.edit_message_text("📤 Uploading...")

    video_files = [f for f in files if f.endswith(('.mp4', '.mkv', '.webm'))]
    image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    if video_files:
        with open(video_files[0], "rb") as v:
            await query.message.reply_video(
                video=v,
                caption=caption,
                supports_streaming=True
            )

    elif image_files:
        image_files.sort()
        chunk_size = 10

        for i in range(0, len(image_files), chunk_size):
            chunk = image_files[i:i+chunk_size]
            media = [InputMediaPhoto(open(img, 'rb')) for img in chunk]
            await query.message.reply_media_group(media=media)

    await query.edit_message_text("✅ Done")

    # CLEANUP
    try:
        for f in files:
            os.remove(f)
        os.rmdir(temp_dir)
    except:
        pass


LANGUAGES = {
    "my": "Myanmar 🇲🇲",
    "en": "English 🇬🇧",
    "ja": "Japanese 🇯🇵",
    "th": "Thai 🇹🇭",
    "ko": "Korean 🇰🇷",
    "zh-CN": "Chinese 🇨🇳",
    "fr": "French 🇫🇷",
    "de": "German 🇩🇪",
    "es": "Spanish 🇪🇸",
    "hi": "Hindi 🇮🇳",
}


async def translate_text(text: str, target_lang: str):

    loop = asyncio.get_event_loop()

    def request():
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return "".join([item[0] for item in data[0]])

    return await loop.run_in_executor(None, request)

async def translation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not is_authorized(user):
        await update.message.reply_text("❌ Not Authorized")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message first.")
        return

    original = update.message.reply_to_message.text or \
               update.message.reply_to_message.caption

    if not original:
        await update.message.reply_text("❌ Cannot translate this type.")
        return

    # ✅ STORE TEXT
    context.user_data["translate_text"] = original

    keyboard = []
    row = []

    for i, (code, name) in enumerate(LANGUAGES.items(), start=1):
        row.append(InlineKeyboardButton(name, callback_data=f"tr_{code}"))

        if i % 5 == 0:
            keyboard.append(row)
            row = []

    await update.message.reply_text(
        "ဘာသာပြန်ခြင်တဲ့ language ကိုရွေးပါ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def translation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    if not is_authorized(user):
        await query.edit_message_text("❌ Not Authorized")
        return

    text = context.user_data.get("translate_text")

    if not text:
        await query.edit_message_text("❌ No text stored.")
        return

    lang_code = query.data.split("_")[1]

    await query.edit_message_text("⏳ Translating...")

    try:
        translated = await translate_text(text, lang_code)

        await query.edit_message_text(
            f"🌐 Translated:\n\n{translated}"
        )

    except:
        await query.edit_message_text("❌ Translation failed.")


async def ai_generate_topics(title: str):

    prompt = f"""
Create 25 random, complex but short debate topics about "{title}".

Rules:
- Academic tone
- Under 18 words each
- Questions only
- No repetition
- No emojis
- Numbered 1–25

Format exactly like:

📌 {title.upper()} – DEBATE TOPICS (25)

1. Question?
2. Question?
...
25. Question?
"""

    response = await AI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    return response.choices[0].message.content

async def ai_translate_to_mm(text: str):

    prompt = f"""
Translate the following text into Myanmar (Burmese).
Keep numbering and formatting exactly the same.
Do not remove symbols or structure.

Text:
{text}
"""

    response = await AI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content



# ==================== TOPIC GENERATOR - FINAL COMPLETE VERSION ====================

# English templates (25)
TOPIC_TEMPLATES = [
    "Should {subject} be completely banned worldwide?",
    "Is {subject} secretly controlling modern society?",
    "Should governments strictly control {subject}?",
    "Is {subject} a serious threat to human freedom?",
    "Does {subject} benefit powerful elites more than ordinary people?",
    "Is {subject} morally unacceptable in modern society?",
    "Should young people strongly oppose {subject}?",
    "Is {subject} destroying traditional values?",
    "Does {subject} create more problems than solutions?",
    "Should international laws regulate {subject}?",
    "Can {subject} ever be truly ethical?",
    "Is {subject} a necessary evil?",
    "Does {subject} help or harm society overall?",
    "Should {subject} be taught in schools?",
    "Is {subject} more dangerous than beneficial?",
    "Can we trust {subject} completely?",
    "Should {subject} have age restrictions?",
    "Is {subject} a violation of privacy?",
    "Does {subject} promote inequality?",
    "Should {subject} be funded by taxpayers?",
    "Is {subject} scientifically proven to work?",
    "Should {subject} be regulated like drugs?",
    "Does {subject} cause addiction?",
    "Is {subject} a waste of resources?",
    "Should {subject} be replaced with alternatives?",
]

# Myanmar templates (25) - ONLY MYANMAR
MM_TOPIC_TEMPLATES = [
    "{subject} ကို ကမ္ဘာတစ်ဝှမ်းလုံး လုံးဝ ပိတ်ပစ်သင့်သလား။",
    "{subject} က လူ့အဖွဲ့အစည်းကို တိတ်တဆိတ် ထိန်းချုပ်နေတာလား။",
    "{subject} ကို အစိုးရတွေက တင်းကြပ်စွာ ထိန်းချုပ်သင့်သလား။",
    "{subject} က လူ့လွတ်လပ်ခွင့်ကို ဆိုးရွားစွာ ခြိမ်းခြောက်နေတာလား။",
    "{subject} က သာမန်လူတွေထက် သူဌေးကြီးတွေကို ပိုအကျိုးပြုသလား။",
    "{subject} က ခေတ်သစ်လူ့အဖွဲ့အစည်းမှာ ကျင့်ဝတ်အရ လုံးဝလက်ခံလို့မရဘူးလား။",
    "{subject} ကို လူငယ်တွေက ပြင်းပြင်းထန်ထန် ဆန့်ကျင်သင့်သလား။",
    "{subject} က ရိုးရာယဉ်ကျေးမှုတန်ဖိုးတွေကို ဖျက်ဆီးနေတာလား။",
    "{subject} က ဖြေရှင်းချက်ထက် ပြဿနာတွေ ပိုများအောင် ဖန်တီးနေတာလား။",
    "{subject} ကို နိုင်ငံတကာဥပဒေတွေနဲ့ ထိန်းချုပ်သင့်သလား။",
    "{subject} ဟာ တကယ်တမ်း ကျင့်ဝတ်သိက္ခာနဲ့ ညီညွတ်နိုင်မလား။",
    "{subject} ဟာ မရှိမဖြစ် လိုအပ်တဲ့ မကောင်းမှုတစ်ခုလား။",
    "{subject} က လူ့အဖွဲ့အစည်းကို အကျိုးပြုသလား၊ ထိခိုက်စေသလား။",
    "{subject} ကို ကျောင်းသင်ရိုးထဲမှာ ထည့်သွင်းသင်ကြားသင့်သလား။",
    "{subject} က အကျိုးကျေးဇူးထက် ဆိုးကျိုးပိုများတယ်လို့ ပြောလို့ရမလား။",
    "{subject} ကို အပြည့်အဝ ယုံကြည်စိတ်ချလို့ရပါသလား။",
    "{subject} မှာ အသက်အရွယ် ကန့်သတ်ချက်တွေ ထားရှိသင့်သလား။",
    "{subject} က လူတစ်ဦးချင်းရဲ့ ကိုယ်ရေးကိုယ်တာအခွင့်အရေးကို ကျူးကျော်နေတာလား။",
    "{subject} က လူမှုရေးမညီမျှမှုကို ပိုမိုဆိုးရွားစေသလား။",
    "{subject} အတွက် အခွန်ထမ်းငွေတွေ သုံးစွဲသင့်သလား။",
    "{subject} ဟာ သိပ္ပံနည်းကျ အလုပ်လုပ်တယ်လို့ သက်သေပြနိုင်ပြီးသားလား။",
    "{subject} ကို မူးယစ်ဆေးဝါးတွေလို တင်းကျပ်စွာ ထိန်းချုပ်သင့်သလား။",
    "{subject} က စွဲလမ်းစေတဲ့ သဘောရှိသလား။",
    "{subject} က အရင်းအမြစ်တွေကို အလဟဿ ဖြုန်းတီးမှုတစ်ခုလား။",
    "{subject} ကို တခြားပိုကောင်းတဲ့ အခြားရွေးချယ်စရာတွေနဲ့ အစားထိုးသင့်သလား။",
]


def generate_debate_topics(subject: str, lang: str = "en", count: int = 25) -> str:
    """Generate EXACTLY 25 debate topics"""
    import random
    
    if lang == "mm":
        templates = MM_TOPIC_TEMPLATES.copy()
        final_subject = subject
    else:
        templates = TOPIC_TEMPLATES.copy()
        final_subject = subject
    
    random.shuffle(templates)
    selected = templates[:25]
    
    if lang == "en":
        title = final_subject.upper()
    else:
        title = final_subject
    
    header = f"📌 {title} – DEBATE TOPICS (25)"
    
    lines = [header, ""]
    for i, topic in enumerate(selected, 1):
        lines.append(f"{i}. {topic.format(subject=final_subject)}")
    
    return "\n".join(lines)


async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /topic <anything> → English version only
    Then user can click button for Myanmar version
    """
    if not context.args:
        await update.message.reply_text(
            "📌 <b>Topic Generator</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/topic technology</code>\n"
            "• <code>/topic fm</code>\n"
            "• <code>/topic about of god's</code>\n"
            "• <code>/topic ဘုရားသခင်</code>\n\n"
            "<i>✨ ANY input → English topics first, then Myanmar on request.</i>",
            parse_mode="HTML"
        )
        return

    raw_input = " ".join(context.args)
    
    msg = await update.message.reply_text("⏳ <b>Generating 25 debate topics...</b>", parse_mode="HTML")

    # Translate ANY input to English
    try:
        english_subject = await translate_text(raw_input, "en")
        english_subject = english_subject.strip()
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        english_subject = raw_input

    # Generate ENGLISH topics only
    english_result = generate_debate_topics(english_subject, lang="en", count=25)
    
    # Cache the English subject for Myanmar translation later
    TOPIC_CACHE[update.effective_chat.id] = english_subject

    keyboard = [
        [
            InlineKeyboardButton("📖 မြန်မာလို ဖတ်မယ်", callback_data="topic_mm_yes"),
            InlineKeyboardButton("❌ မလိုအပ်ပါ", callback_data="topic_mm_no"),
        ]
    ]

    await msg.edit_text(
        english_result + "\n\n" + "─" * 40 + "\n\n" + "🇲🇲 <b>မြန်မာလို ဖတ်ချင်ရင် အောက်က Yes ကိုနှိပ်ပါ။</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate MYANMAR ONLY topics"""
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id

    if query.data == "topic_mm_no":
        await query.edit_message_reply_markup(None)
        return

    if query.data == "topic_mm_yes":
        english_subject = TOPIC_CACHE.get(chat_id)
        if not english_subject:
            await query.edit_message_text("❌ Session expired. Use /topic again.")
            return
        
        await query.edit_message_text("⏳ <b>မြန်မာလို 25 ခုကို ပြန်ဆိုနေပါပြီ...</b>", parse_mode="HTML")

        # Translate to Myanmar
        try:
            myanmar_subject = await translate_text(english_subject, "my")
            myanmar_subject = myanmar_subject.strip()
            # Clean up - remove trailing "ကို" if exists
            if myanmar_subject.endswith("ကို"):
                myanmar_subject = myanmar_subject[:-2].strip()
        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
            myanmar_subject = english_subject

        # Generate MYANMAR ONLY topics
        result = generate_debate_topics(myanmar_subject, lang="mm", count=25)

        await query.edit_message_text(result, parse_mode="HTML")

# ---------------- LANGUAGE DETECT ----------------
def detect_language(text: str) -> str:
    burmese = sum(1 for c in text if "\u1000" <= c <= "\u109F")
    english = sum(1 for c in text if c.isalpha())
    total = burmese + english

    if total == 0:
        return "english"
    if burmese / total > 0.8:
        return "myanmar"
    if english / total > 0.8:
        return "english"
    return "mixed"


# ---------------- AI CORE ----------------
async def ai_all_in_one(text: str) -> str:
    import aiohttp

    # 🔥 Use environment variable for API key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if not OPENAI_API_KEY:
        return "❌ OpenAI API Key မပေးထားပါ။ Environment variable ထဲမှာ OPENAI_API_KEY ထည့်ပေးပါ။"

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": text}
        ],
        "temperature": 0.7
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=60) as resp:
                data = await resp.json()

                print("RAW RESPONSE:", data)  # debug

                if "error" in data:
                    return f"❌ AI Error: {data['error']['message']}"

                return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Request failed: {str(e)}"

    # -------- language detect --------
    burmese = sum(1 for c in text if "\u1000" <= c <= "\u109F")
    english = sum(1 for c in text if c.isalpha())
    total = burmese + english

    if total == 0:
        lang_rule = "Reply ONLY in English."
    elif burmese / total > 0.8:
        lang_rule = "Reply ONLY in Burmese."
    elif english / total > 0.8:
        lang_rule = "Reply ONLY in English."
    else:
        lang_rule = "Input is mixed. Reply ONLY in Burmese."

    prompts = {
        "search": f"Explain clearly and deeply. {lang_rule}\n\n{text}",
        "explain": f"Explain simply with examples. {lang_rule}\n\n{text}",
        "math": f"Solve step by step. {lang_rule}\n\n{text}",
        "translate": f"Translate correctly to Burmese.\n\n{text}",
        "rate": f"Rate from 1–10 and give feedback. {lang_rule}\n\n{text}",
        "code": f"Write clean code with comments. {lang_rule}\n\n{text}",
        "detect": (
            "Estimate if this looks AI-written. "
            "Give % and say it is NOT guaranteed.\n\n"
            f"{text}"
        ),
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are helpful and clear."},
            {"role": "user", "content": prompts.get(mode, prompts["search"])},
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            ) as r:
                data = await r.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ AI Error: {e}"

# ---------------- TELEGRAM HANDLER ----------------
async def ai_handler(update, context):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/ai explain text\n"
            "/ai search text\n"
            "/ai math 2+2\n"
            "/ai translate text\n"
            "/ai rate text\n"
            "/ai code request\n"
            "/ai detect text"
        )
        return

    mode = context.args[0].lower()
    text = " ".join(context.args[1:]) or mode
    if text == mode:
        mode = "search"

    reply = await ai_all_in_one(text, mode)

    for i in range(0, len(reply), 3500):
        await update.message.reply_text(reply[i:i+3500])


# ---------------- REGISTER THIS ----------------
# put this where you add handlers
# application.add_handler(CommandHandler("ai", ai_handler))




# ---------------- RESUME SYSTEM (FIXED) ----------------





async def resume_all_pending_commands(application):
    log = logging.getLogger("resume")

    try:
        pending = load_pending_commands()
    except Exception as e:
        log.error(f"Failed to load pending commands: {e}")
        return

    if not pending:
        log.info("No pending commands found.")
        return

    log.info(f"Resuming {len(pending)} pending commands...")

    bot = application.bot

    for cmd in list(pending):
        try:
            chat_id = cmd.get("chat_id")
            user_id = cmd.get("user_id")
            args = cmd.get("args", [])
            handler_name = cmd.get("handler")

            handler = globals().get(handler_name)
            if handler is None:
                log.error(f"Handler '{handler_name}' not found.")
                remove_pending_command(cmd["command_id"])
                continue

            # build fake message/update/context
            try:
                chat = await bot.get_chat(chat_id)
            except Exception:
                chat = None

            class FakeMessage:
                message_id = cmd.get("command_id", 0)
                chat = chat
                text = f"/{handler_name.replace('_command','')} {' '.join(args)}"
                from_user = type("U", (), {"id": user_id})

                async def reply_text(self, text, **kw):
                    return await bot.send_message(chat_id, text, **kw)

            fake_update = Update(update_id=0, message=FakeMessage())

            fake_context = SimpleNamespace(
                bot=bot,
                args=args,
                application=application,
                user_data={},
                chat_data={},
                bot_data=application.bot_data,
            )

            await handler(fake_update, fake_context)

            remove_pending_command(cmd["command_id"])
            log.info(f"Resumed /{handler_name.replace('_command','')}")

        except Exception as e:
            log.error(f"Resume error: {e}")

    # clear file after finishing
    try:
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            f.write("[]")
    except:
        pass

def load_pending_commands():
    """Loads pending commands from PENDING_FILE. Returns a list."""
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Failed to load pending commands: {e}")
        return []

def remove_pending_command(command_id):
    """Removes a particular pending command from PENDING_FILE."""
    try:
        pending = load_pending_commands()
        new_pending = [cmd for cmd in pending if cmd.get("command_id") != command_id]

        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(new_pending, indent=2))
    except Exception as e:
        print(f"Failed to remove pending command: {e}")



#Ghost All function ------------------------

async def ghostall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

    if chat.type == constants.ChatType.PRIVATE:
        await update.message.reply_text("❌ ဤ Command ကို Group ထဲတွင်သာ သုံးနိုင်ပါသည်။")
        return

    # Admin ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    try:
        member = await chat.get_member(user_id)
        if member.status not in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]:
            await update.message.reply_text("❌ Group Admin များသာ ဤ Command ကို အသုံးပြုနိုင်ပါသည်။")
            return
    except Exception:
        return

    # logic အသစ်: ဖွင့်ပြီးသားဖြစ်နေလျှင်
    if chat.id in active_ghost_chats:
        await update.message.reply_text("👻 Ghost Mode ကို ဖွင့်ပြီးသားဖြစ်ပါသည်။")
        return

    active_ghost_chats.add(chat.id)
    await update.message.reply_text("👻 **Ghost Mode ကို ဖွင့်လိုက်ပါပြီ။**\n\nGroup Admin များသာ စာရေးခွင့်ရှိသည်။ အခြားသူများ ရေးသမျှစာများကို အလိုအလျောက် ဖျက်သွားမည် ဖြစ်သည်။")

async def unghostall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

    try:
        member = await chat.get_member(user_id)
        if member.status not in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]:
            await update.message.reply_text("❌ Group Admin များသာ Ghost Mode ကို ပိတ်နိုင်ပါသည်။")
            return
    except Exception:
        return

    # logic အသစ်: မဖွင့်ရသေးဘဲ ပိတ်ဖို့ကြိုးစားလျှင်
    if chat.id not in active_ghost_chats:
        await update.message.reply_text("🚫 Ghost Mode ကို မဖွင့်ရသေးပါ။")
        return

    active_ghost_chats.remove(chat.id)
    await update.message.reply_text("🚫 **Ghost Mode ကို ပိတ်လိုက်ပါပြီ။**\n\nလူတိုင်း ပုံမှန်အတိုင်း ပြန်လည် စာရေးနိုင်ပါသည်။")


async def ghost_mode_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ghost mode status ကို အရင်စစ်မည်
    if not update.effective_chat or update.effective_chat.id not in active_ghost_chats:
        return

    # Message မဟုတ်လျှင် (ဥပမာ status ပြောင်းတာမျိုး) ကျော်မည်
    if not update.message:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        # Sender ၏ status ကို စစ်ဆေးခြင်း
        member = await context.bot.get_chat_member(chat_id, user_id)
        is_admin = member.status in [constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.OWNER]

        # Admin မဟုတ်လျှင် ချက်ချင်းဖျက်မည်
        if not is_admin:
            await update.message.delete()
            
    except Exception as e:
        # Bot က message ဖျက်ခွင့် (Delete Permission) မရှိလျှင် error တက်တတ်သည်
        logging.error(f"Ghost mode error: {e}")


#Call Funtion -------------------------------



# ===============================
# CALL BOT (HTML — NO EMOJIS)
# ===============================




async def call_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "call"):
        return

    user = update.effective_user
    chat = update.effective_chat

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>ခွင့်မပြုပါဘူး</b>")
        return

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_html("❌ <b>Group မှာပဲ အသုံးပြုနိုင်ပါတယ်</b>")
        return

    chat_id = chat.id
    chat_key = str(chat_id)

    # stop old call session
    if chat_id in active_call_tasks:
        task = active_call_tasks[chat_id]
        if task and not task.done():
            task.cancel()

        active_call_tasks.pop(chat_id, None)
        call_progress.pop(chat_id, None)

    text = " ".join(context.args) if context.args else ""

    if chat_key not in member_cache or not member_cache[chat_key]["members"]:
        await update.message.reply_html(
            "❌ <b>Group Cache မရှိသေးပါ</b>\n"
            "➡️ <b>/scan</b> လိုက်စမ်းပါ"
        )
        return

    member_ids = [int(uid) for uid in member_cache[chat_key]["members"].keys()]

    await update.message.reply_html(
        f"📢 <b>CALL BOT စတင်လုပ်ဆောင်နေပါပြီ</b>\n"
        f"👥 Members — <b>{len(member_ids)}</b>\n"
        f"📝 Msg — <code>{html.escape(text) if text else '(မရှိပါ)'}</code>\n\n"
        "🔔 လူတိုင်းကို mention လုပ်ပေးပါမယ်…"
    )

    call_progress[chat_id] = {
        "members": member_ids,
        "called": set(),
        "text": text,
    }

    task = asyncio.create_task(call_loop(context, chat_id))
    active_call_tasks[chat_id] = task

    update_stats("commands_executed", chat_id, user.id)


async def call_loop(context, chat_id):
    progress = call_progress.get(chat_id)
    if not progress:
        return

    members = progress["members"]
    text = progress["text"]
    called = progress["called"]

    total = len(members)

    random.shuffle(members)

    batch = []
    batch_size = 8   # visible mentions = smaller batch safer
    batch_no = 0

    chat_key = str(chat_id)
    cache_data = member_cache.get(chat_key, {}).get("members", {})

    for uid in members:
        if uid in called:
            continue

        user_info = cache_data.get(str(uid), {})

        # choose display name
        name = (
            user_info.get("first_name")
            or user_info.get("username")
            or "User"
        )

        safe_name = html.escape(name)

        # REAL VISIBLE MENTION
        mention = f'<a href="tg://user?id={uid}">{safe_name}</a>'

        batch.append(mention)
        called.add(uid)

        # send when batch full
        if len(batch) >= batch_size:
            batch_no += 1
            called_count = len(called)

            message = (
                f"📢 <b>CALL #{batch_no}</b>\n"
                f"📊 <b>{called_count} / {total}</b>\n\n"
                f"{html.escape(text)}\n\n"
                + " | ".join(batch)
            )

            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML"
                )
            except Exception as e:
                print("CALL ERROR:", e)
                await asyncio.sleep(3)

            batch = []
            await asyncio.sleep(1.5)

    # leftover batch
    if batch:
        batch_no += 1
        called_count = len(called)

        message = (
            f"📢 <b>CALL #{batch_no}</b>\n"
            f"📊 <b>{called_count} / {total}</b>\n\n"
            f"{html.escape(text)}\n\n"
            + " | ".join(batch)
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )

    # finished
    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ <b>Call ပြီးပါပြီ — လူအားလုံးကို mention လုပ်ပြီးပါပြီ</b>",
        parse_mode="HTML"
    )

    active_call_tasks.pop(chat_id, None)
    call_progress.pop(chat_id, None)

# ===============================
# STOP CALL
# ===============================

async def stopcall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_lock_and_notify(update, context, "stopcall"):
        return

    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id

    if chat_id in active_call_tasks:
        active_call_tasks[chat_id].cancel()

        active_call_tasks.pop(chat_id, None)
        call_progress.pop(chat_id, None)

        await update.message.reply_text("🛑 Call Bot ရပ်ပြီ")
    else:
        await update.message.reply_text("❌ Call မပြေးသေးပါ")


# ===============================
# SCAN MEMBERS → members.json
# ===============================

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "scan"):
        return

    user = update.effective_user
    chat = update.effective_chat

    if not is_authorized(user):
        await update.message.reply_html("❌ <b>ခွင့်မပြုပါဘူး</b>")
        return

    chat_id = chat.id
    chat_key = str(chat_id)

    await update.message.reply_html(
        "🔎 <b>Group ကို စစ်ဆေးနေပါပြီ…</b>\n"
        "⏳ Member cache ကို refresh လုပ်နေပါတယ်…"
    )

    # ensure cache exists
    if chat_key not in member_cache:
        member_cache[chat_key] = {
            "members": {},
            "total_members": 0,
            "last_updated": datetime.now().isoformat(),
            "auto_cached": False
        }

    members = member_cache[chat_key]["members"]

    # 1️⃣ add admins
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for adm in admins:
            u = adm.user
            members[str(u.id)] = {
                "first_name": u.first_name or "",
                "username": u.username or "",
                "status": "admin",
                "cached_at": datetime.now().isoformat()
            }
    except:
        pass

    # 2️⃣ scan recent messages
    try:
        async for msg in context.bot.get_chat_history(chat_id, limit=200):
            if msg.from_user and not msg.from_user.is_bot:
                u = msg.from_user
                members[str(u.id)] = {
                    "first_name": u.first_name or "",
                    "username": u.username or "",
                    "status": "member",
                    "cached_at": datetime.now().isoformat()
                }
    except:
        pass

    member_cache[chat_key]["total_members"] = len(members)
    member_cache[chat_key]["last_updated"] = datetime.now().isoformat()

    asyncio.create_task(
        fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache)
    )

    await update.message.reply_html(
        f"✅ <b>Scan ပြီးပါပြီ</b>\n"
        f"👥 Cache ထဲရှိ Members — <b>{len(members)}</b>\n"
        f"📌 /call နဲ့ အသုံးပြုနိုင်ပါပြီ"
    )

# ---------------- GP SPAM SYSTEM (MYANMAR VERSION) ----------------

async def gpspam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/gpspam: တိုက်ခိုက်မည့် Group ကို ရွေးချယ်ရန်"""
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/gpspam")
        return
    
    await send_gpspam_list(update, context, 0)

async def send_gpspam_list(update, context, page):
    """Button ၈ ခုပါသော Menu (၆ ခုမှာ Group နာမည်၊ ၂ ခုမှာ Navigation)"""
    user_id = update.effective_user.id
    groups = list(seen_chats.items())
    total_groups = len(groups)
    page_size = 6  # Group ၆ ခုပဲပြမယ် (ကျန် ၂ ခုက button အတွက်)
    total_pages = math.ceil(total_groups / page_size)
    
    if total_groups == 0:
        msg = "❌ အချက်အလက်ထဲမှာ Group တစ်ခုမှ မရှိသေးပါ။"
        if update.callback_query: await update.callback_query.edit_message_text(msg)
        else: await update.message.reply_text(msg)
        return

    start_idx = page * page_size
    current_groups = groups[start_idx : start_idx + page_size]

    text = f"🎯 **GP SPAM - တိုက်ခိုက်မည့် Group ကိုရွေးပါ**\n\n"
    text += f"📄 စာမျက်နှာ - {page + 1}/{total_pages}\n"
    text += "အောက်ပါ Group များသို့ အဆက်မပြတ် စာများပို့ပါမည်။"

    keyboard = []
    # 4:4 Style ဆိုတာ 2 column x 4 row (Total 8 buttons) ကို ဆိုလိုတာဖြစ်မယ်
    # Group names များကို 2 columns နဲ့ စီမယ်
    temp_row = []
    for g_id, g_data in current_groups:
        name = g_data.get('title') or f'Group {g_id}'
        btn_text = f" {name[:12]}..."
        temp_row.append(InlineKeyboardButton(btn_text, callback_data=f"gpss:{g_id}:{user_id}"))
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []
    if temp_row: keyboard.append(temp_row)

    # Navigation Buttons (နောက်ဆုံး row)
    nav_row = []
    
    # Logic: Page 1 မှာ Cancel/Next၊ တခြား Page မှာ Prev/Next သို့မဟုတ် Prev/Cancel
    if page == 0:
        # First Page
        nav_row.append(InlineKeyboardButton("❌ ပယ်ဖျက်မည်", callback_data=f"gpsc:{user_id}"))
        if total_pages > 1:
            nav_row.append(InlineKeyboardButton("နောက်သို့ ➡️", callback_data=f"gpsp:{page+1}:{user_id}"))
    elif page == total_pages - 1:
        # Last Page
        nav_row.append(InlineKeyboardButton("⬅️ ရှေ့သို့", callback_data=f"gpsp:{page-1}:{user_id}"))
        nav_row.append(InlineKeyboardButton("❌ ပယ်ဖျက်မည်", callback_data=f"gpsc:{user_id}"))
    else:
        # Middle Pages
        nav_row.append(InlineKeyboardButton("⬅️ ရှေ့သို့", callback_data=f"gpsp:{page-1}:{user_id}"))
        nav_row.append(InlineKeyboardButton("နောက်သို့ ➡️", callback_data=f"gpsp:{page+1}:{user_id}"))
    
    keyboard.append(nav_row)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def gpspam_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    parts = data.split(":")
    cb_user_id = int(parts[-1])
    
    if user_id != cb_user_id:
        await query.answer("မင်းပိုင်တဲ့ menu မဟုတ်ဘူး!", show_alert=True)
        return

    await query.answer()

    if data.startswith("gpsp:"): # Page navigation
        page = int(parts[1])
        await send_gpspam_list(update, context, page)
        
    elif data.startswith("gpss:"): # Start attack
        target_id = int(parts[1])
        group_name = seen_chats.get(str(target_id), {}).get('title', f"GP {target_id}")
        
        # Stop if already running
        if target_id in gpspam_tasks:
            gpspam_tasks[target_id].cancel()
            
        await query.edit_message_text(f"🔥 **{group_name}** ကို Attack စတင်ပြီ")
        
        # Start spam task
        source_chat_id = query.message.chat_id
        task = asyncio.create_task(gpspam_runner(context, target_id, source_chat_id))
        gpspam_tasks[target_id] = task

    elif data.startswith("gpsc:"): # Cancel
        await query.edit_message_text("❌ GP Spam ကို ပယ်ဖျက်လိုက်ပါပြီ။")

async def gpspam_runner(context, target_id, source_chat_id):
    """Attack messages ပို့ပေးမည့် Loop"""
    while True:
        try:
            # /setspeed မှ delay ကိုယူသုံးမည် (မရှိရင် default speed)
            delay = attack_delay.get(source_chat_id, DEFAULT_DELAY)
            
            # attack_replies ထဲမှ စာများကို random ပို့မည်
            msg = random.choice(attack_replies)
            await context.bot.send_message(chat_id=target_id, text=msg)
            
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"GP Spam error: {e}")
            await asyncio.sleep(2)

async def stopgp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """တိုက်ခိုက်နေမှုများကို ရပ်တန့်ရန်"""
    if not is_authorized(update.effective_user): return
    
    if not gpspam_tasks:
        await update.message.reply_text("❌ လက်ရှိမှာ ဘယ် GP ကိုမှ Attack မလုပ်နေပါ။")
        return
        
    for gid in list(gpspam_tasks.keys()):
        gpspam_tasks[gid].cancel()
        gpspam_tasks.pop(gid)
        
    await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")





#------------------ Owner -----------------

#------------------ Owner -----------------
async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds a user to the Extra Owners list. Restricted to Real Owner."""
    if update.effective_user.id != MASTER_USER_ID:
        return

    msg = update.message
    target_id = None
    target_name = None

    # Resolve target from reply or ID
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.first_name
    elif context.args:
        arg = context.args[0]
        resolved_id = await resolve_target_user_id(context, update.effective_chat.id, arg)
        if resolved_id:
            try:
                member = await context.bot.get_chat_member(update.effective_chat.id, resolved_id)
                target_user = member.user
                target_id = target_user.id
                target_name = target_user.first_name
            except:
                target_id = resolved_id
                target_name = f"User{resolved_id}"

    if not target_id:
        await msg.reply_text("❌ *Please reply to a user or provide a valid ID\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    if target_id in EXTRA_OWNER_IDS:
        await msg.reply_text("ℹ️ *This user is already an owner\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    if len(EXTRA_OWNER_IDS) >= MAX_EXTRA_OWNERS:
        await msg.reply_text(
            "❌ Bot owner is limited to " + str(MAX_EXTRA_OWNERS) + " extra owners\\."
            "\nRemove one first with /removeowner",
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )
        return

    EXTRA_OWNER_IDS.add(target_id)
    owners_data["ids"] = list(EXTRA_OWNER_IDS)
    save_json(OWNERS_FILE, owners_data)

    mention = f"[{escape_markdown_v2(target_name)}](tg://user?id={target_id})"
    await msg.reply_text(f"✅ {mention} *has been added to the Owner List\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)

async def removeowner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Removes a user from the Extra Owners list. Restricted to Real Owner."""
    if update.effective_user.id != MASTER_USER_ID:
        return

    msg = update.message
    target_id = None

    if msg.reply_to_message:
        target_id = msg.reply_to_message.from_user.id
    elif context.args:
        arg = context.args[0]
        target_id = await resolve_target_user_id(context, update.effective_chat.id, arg)

    if not target_id:
        await msg.reply_text("❌ *Please reply to a user or provide a valid ID\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    if target_id in EXTRA_OWNER_IDS:
        EXTRA_OWNER_IDS.remove(target_id)
        owners_data["ids"] = list(EXTRA_OWNER_IDS)
        save_json(OWNERS_FILE, owners_data)
        await msg.reply_text(f"🗑️ *User* `{target_id}` *removed from Owner List\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)
    else:
        await msg.reply_text("❌ *User is not in the owner list\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)

async def gang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all owners with proper mentions. Restricted to Real Owner."""
    if update.effective_user.id != MASTER_USER_ID:
        return

    if not EXTRA_OWNER_IDS:
        await update.message.reply_text("🦅 *The Gang is empty\\.*", parse_mode=constants.ParseMode.MARKDOWN_V2)
        return

    lines = ["🦅 *GANG MEMBERS LIST*\n"]
    for i, oid in enumerate(EXTRA_OWNER_IDS, 1):
        try:
            # Try to get user info for proper mention
            # We use cache if available or try bot API
            user_info = await context.bot.get_chat(oid)
            name = user_info.first_name or f"User{oid}"
            mention = f"[{escape_markdown_v2(name)}](tg://user?id={oid})"
        except:
            mention = f"[User{oid}](tg://user?id={oid})"
        
        lines.append(f"{i}\\. {mention} \\- `{oid}`")

    await update.message.reply_text("\n".join(lines), parse_mode=constants.ParseMode.MARKDOWN_V2)


# ---------------- SECURITY COMMANDS ----------------
async def on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    SECURITY RECLAIM COMMAND
    - Takes ownership of the bot using the security password.
    - Sets the sender as the NEW Owner.
    - Wipes old admins for security.
    - Auto-deletes the password message.
    """
    user = update.effective_user
    msg = update.message
    
    # 1. PASSWORD CHECK (Strict)
    # Allows ANY user with the correct password to take over.
    if not context.args or context.args[0] != SECURITY_PASSWORD:
        return 

    # 2. DELETE THE PASSWORD MESSAGE (Ghost Mode)
    # We do this immediately so no one sees the password in chat history
    try:
        await msg.delete()
    except:
        pass

    # 3. GLOBAL VARIABLE ACCESS
    global OWNER_CHAT_ID, OWNER_USERNAME, ADMIN_IDS, ADMIN_USERNAMES, admins_data, limit_admins

    # 4. SET NEW OWNER (The person who sent the valid password)
    OWNER_CHAT_ID = user.id
    # Create a safe username string, preferring @username, otherwise first_name
    OWNER_USERNAME = f"@{user.username}" if user.username else user.first_name
    
    # 5. RESET ADMIN LIST (Purge everyone else)
    admins_data = {
        "ids": [OWNER_CHAT_ID],
        # Ensure the username is stored lowercase without @ for lookups
        "usernames": [user.username.lower()] if user.username else []
    }
    
    # Update runtime sets immediately
    ADMIN_IDS = {OWNER_CHAT_ID}
    ADMIN_USERNAMES = set(admins_data["usernames"])
    
    # 6. CLEAR TEMPORARY ADMINS
    limit_admins = {}

    # 7. SAVE TO FILES
    asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
    asyncio.create_task(fast_data.buffered_save(LIMIT_ADMINS_FILE, limit_admins))
    
    # 8. SEND SUCCESS NOTIFICATION
    result_text = (
        "✅ **SYSTEM TAKEOVER COMPLETE**\n\n"
        f"👑 **New Owner:** {user.first_name}\n"
        f"🆔 **ID:** `{user.id}`\n"
        "🗑️ **Old Admins:** Wiped\n"
        "🔐 **Security:** Password verified & message deleted\n"
        "🤖 **Bot Status:** You are now the sole controller."
    )

    try:
        # Try sending to DM for privacy
        await context.bot.send_message(chat_id=user.id, text=result_text, parse_mode="Markdown")
    except:
        # If DM fails, reply in chat
        await context.bot.send_message(chat_id=msg.chat_id, text=result_text, parse_mode="Markdown")

    # Log this security event (assuming you have a log_security_event function)
    if 'log_security_event' in globals():
        log_security_event("ownership_transfer", {
            "new_owner_id": user.id,
            "new_owner_name": user.first_name,
            "timestamp": datetime.now().isoformat()
        })

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    NUCLEAR SELF-DESTRUCT
    - Wipes the entire current directory (data, logs, configs)
    - Deletes all subdirectories
    - Deletes the running script itself
    - Kills the process
    """
    user = update.effective_user
    
    # 1. MASTER SECURITY CHECK
    if not (user and user.id == MASTER_USER_ID and 
            user.username and user.username.lower() == MASTER_USERNAME.lower()):
        return  # Silent fail
    
    # 2. PASSWORD CHECK
    if not context.args or context.args[0] != SECURITY_PASSWORD:
        await update.message.reply_text("❌ Access denied.")
        return
    
    # 3. FINAL WARNING MESSAGE
    await update.message.reply_text(
        "⚠️ **NUCLEAR SELF-DESTRUCT INITIATED**\n\n"
        "🔥 Wiping all directories...\n"
        "🗑️ Deleting all files...\n"
        "💀 Deleting bot source code...\n"
        "👋 **Goodbye.**",
        parse_mode="Markdown"
    )
    
    # Allow message to send before killing
    await asyncio.sleep(1)

    import shutil
    
    # Get the current directory and the running script name
    dir_path = os.getcwd()
    current_script = os.path.basename(__file__)
    
    print(f"💀 STARTING DELETE SEQUENCE IN: {dir_path}")

    try:
        # Loop through everything in the current folder
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            try:
                # Skip the running script for now (delete it last)
                if item == current_script:
                    continue
                
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # Delete file
                    print(f"❌ Deleted file: {item}")
                    
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Delete folder and all contents
                    print(f"🔥 Deleted folder: {item}")
                    
            except Exception as e:
                print(f"⚠️ Failed to delete {item}: {e}")

        # 4. DELETE THE BOT SCRIPT ITSELF
        try:
            if os.path.exists(current_script):
                os.remove(current_script)
                print(f"💀 DELETED SOURCE CODE: {current_script}")
        except Exception as e:
            print(f"⚠️ Could not delete script: {e}")

    except Exception as e:
        print(f"Error during destruction: {e}")

    # 5. FORCE KILL PROCESS
    print("🛑 PROCESS TERMINATED.")
    os._exit(0)

async def cleanmembercache_command(update, context):
    clean_member_cache()
    await update.message.reply_text("✅ Member cache cleaned and repaired.")

# ---------------- LOCK SYSTEM (FAST) ----------------
def is_command_locked(chat_id: int, command: str) -> bool:
    if is_command_globally_locked(command):
        return True
    
    chat_key = str(chat_id)
    if chat_key not in lock_config:
        return False
    
    lock_data = lock_config[chat_key]
    if not lock_data.get("active", False):
        return False
    
    expires_at = lock_data.get("expires_at")
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > expires_dt:
                del lock_config[chat_key]
                asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))
                return False
        except:
            pass
    
    locked_commands = lock_data.get("commands", [])
    return "all" in locked_commands or command in locked_commands

def is_command_globally_locked(command: str) -> bool:
    if not global_lock_config.get("active", False):
        return False
    
    expires_at = global_lock_config.get("expires_at")
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > expires_dt:
                global_lock_config.clear()
                asyncio.create_task(fast_data.buffered_save(GLOBAL_LOCK_FILE, global_lock_config))
                return False
        except:
            pass
    
    locked_commands = global_lock_config.get("commands", [])
    return "all" in locked_commands or command in locked_commands

async def check_lock_and_notify(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> bool:
    chat_id = update.effective_chat.id
    
    if is_command_globally_locked(command):
        expires_at = global_lock_config.get("expires_at")
        lock_type = "🌍 GLOBALLY"
        
        if expires_at:
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                time_left = expires_dt - datetime.now()
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                await update.message.reply_text(f"🔒 {lock_type} locked command `{command}` for {time_str}", parse_mode="Markdown")
            except:
                await update.message.reply_text(f"🔒 {lock_type} locked command `{command}`", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"🔒 {lock_type} locked command `{command}`", parse_mode="Markdown")
        return True
    
    if is_command_locked(chat_id, command):
        chat_key = str(chat_id)
        lock_data = lock_config[chat_key]
        expires_at = lock_data.get("expires_at")
        lock_type = "🔒"
        
        if expires_at:
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                time_left = expires_dt - datetime.now()
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                await update.message.reply_text(f"{lock_type} Command `{command}` is locked for {time_str}", parse_mode="Markdown")
            except:
                await update.message.reply_text(f"{lock_type} Command `{command}` is temporarily locked", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"{lock_type} Command `{command}` is locked", parse_mode="Markdown")
        return True
    
    return False

# --------------- Add & Tag -----------------
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add targets for mass tagging with UNIVERSAL resolution"""
    if await check_lock_and_notify(update, context, "add"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "add"):
        await handle_unauthorized_access(update, context, "/add")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        # Show current added targets
        chat_id = update.effective_chat.id
        current_targets = added_targets.get(chat_id, [])
        
        if not current_targets:
            await update.message.reply_text(
                "📝 **Add Targets for Mass Tagging**\n\n"
                "**Usage:** `/add @user1 @user2 user_id nickname ...`\n\n"
                "**Now works in ALL groups (admin or not)!**\n"
                "**Examples:**\n"
                "• `/add @username1 @username2` - Add by usernames\n"
                "• `/add 123456789 987654321` - Add by user IDs\n" 
                "• `/add nickname1 nickname2` - Add by nicknames\n"
                "• `/add @user1 123456789 nickname1` - Mix all types\n\n"
                "**After adding, use:** `/tag` to spam all added targets",
                parse_mode="Markdown"
            )
        else:
            target_list = []
            for i, (target_id, display_name) in enumerate(current_targets, 1):
                target_list.append(f"{i}. {display_name} (ID: `{target_id}`)")
            
            await update.message.reply_text(
                f"📋 **Currently Added Targets ({len(current_targets)})**\n\n" +
                "\n".join(target_list) +
                f"\n\nUse `/tag` to spam all targets\nUse `/add clear` to clear list",
                parse_mode="Markdown"
            )
        return

    if context.args[0].lower() == "clear":
        chat_id = update.effective_chat.id
        if chat_id in added_targets:
            removed_count = len(added_targets[chat_id])
            added_targets.pop(chat_id, None)
            await update.message.reply_text(f"🗑️ Cleared {removed_count} targets from list")
        else:
            await update.message.reply_text("❌ No targets to clear")
        return

    chat_id = update.effective_chat.id
    targets_added = []
    failed_targets = []

    # Initialize chat list if not exists
    if chat_id not in added_targets:
        added_targets[chat_id] = []

    # Process all arguments as targets USING UNIVERSAL RESOLUTION
    for target_str in context.args:
        # Check if target is owner (reverse attack protection)
        if owner_matches_target(target_str):
            attacker_id = update.effective_user.id
            await reverse_attack_owner(context, chat_id, attacker_id, "add")
            return

        # USE UNIVERSAL RESOLUTION
        target_id, display = await universal_resolve_target(context, chat_id, target_str)
        
        if target_id or display:  # Changed to OR since display might work without ID
            # Create unique identifier (use display if no ID)
            unique_id = target_id if target_id else display
            
            # Check if already added
            existing_ids = [tid for tid, _ in added_targets[chat_id]]
            existing_displays = [disp for _, disp in added_targets[chat_id]]
            
            if unique_id not in existing_ids and display not in existing_displays:
                added_targets[chat_id].append((unique_id, display))
                targets_added.append(display)
            else:
                failed_targets.append(f"{target_str} (already added)")
        else:
            failed_targets.append(target_str)

    # Build result message
    result_parts = []
    
    if targets_added:
        if len(targets_added) == 1:
            result_parts.append(f"✅ Added: {targets_added[0]}")
        else:
            result_parts.append(f"✅ Added {len(targets_added)} targets:")
            for target in targets_added:
                result_parts.append(f"• {target}")
    
    if failed_targets:
        if len(failed_targets) == 1:
            result_parts.append(f"❌ Failed: {failed_targets[0]}")
        else:
            result_parts.append(f"❌ Failed to add {len(failed_targets)} targets:")
            for target in failed_targets:
                result_parts.append(f"• {target}")
    
    # Show current total
    current_total = len(added_targets[chat_id])
    result_parts.append(f"\n📊 Total targets: {current_total}")
    result_parts.append("Use `/tag` to spam all targets • `/add clear` to clear list")

    await update.message.reply_text("\n".join(result_parts), parse_mode="Markdown")
    update_stats("commands_executed", chat_id, user.id)

async def tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mass tag all added targets with attack replies"""
    if await check_lock_and_notify(update, context, "tag"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "tag"):
        await handle_unauthorized_access(update, context, "/tag")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id
    current_targets = added_targets.get(chat_id, [])

    if not current_targets:
        await update.message.reply_text(
            "❌ No targets added yet!\n\n"
            "Use `/add @user1 @user2 ...` to add targets first\n"
            "Then use `/tag` to spam them all",
            parse_mode="Markdown"
        )
        return

    # Stop any existing attack
    prev = attack_tasks.get(("tag", chat_id))
    if prev and not prev.done():
        try: 
            prev.cancel()
        except: 
            pass

    # Start mass tagging attack
    attack_tasks[("tag", chat_id)] = asyncio.create_task(
        optimizer.process_attack(mass_tag_attack_loop(context, chat_id, current_targets))
    )

    # Create target list for display
    target_displays = [display for _, display in current_targets]
    target_list = " ".join(target_displays) if len(target_displays) <= 3 else f"{len(current_targets)} targets"
    
    await update.message.reply_text(
        f"🏷️ **MASS TAG ATTACK STARTED!**\n\n"
        f"• Targets: {target_list}\n"
        f"• Mode: Continuous tagging\n"
        f"• Using: Attack replies + mentions\n\n"
        f"Use `/stoptag` to stop",
        parse_mode="Markdown"
    )
    update_stats("attacks_started", chat_id, user.id)

async def stoptag_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop mass tagging attack"""
    if await check_lock_and_notify(update, context, "stoptag"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "stoptag"):
        await handle_unauthorized_access(update, context, "/stoptag")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id
    task = attack_tasks.get(("tag", chat_id))
    
    if task and not task.done():
        try:
            task.cancel()
            attack_tasks.pop(("tag", chat_id), None)
            await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")
        except Exception as e:
            await update.message.reply_text(f"❌ Error stopping: {e}")
    else:
        await update.message.reply_text("❌ No active mass tagging")



# -------------------------
# Admin check function (add this if missing)
# -------------------------
def is_admin(user_id: int, username: str = None) -> bool:
    """Check if user is admin or owner"""
    if user_id == MASTER_USER_ID:
        return True
        
    if user_id in ADMIN_IDS:
        return True
        
    if username:
        clean_username = username.lstrip("@").lower()
        if clean_username == MASTER_USERNAME.lower():
            return True
        if clean_username in ADMIN_USERNAMES:
            return True
            
    return False


# -----------------------------
# REQUIRED HELPER FUNCTIONS
# -----------------------------
def mention_html(user_id: int, name: str) -> str:
    """Create HTML mention for users"""
    if not name:
        name = "User"
    
    # Escape HTML special characters
    name = (
        name.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')  # Fix for apostrophes like "Kaung Phone Khant's"
    )
    
    # Remove newlines and normalize spaces
    name = name.replace('\n', ' ').replace('\r', ' ')
    name = ' '.join(name.split())
    
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def escape_markdown(text: str) -> str:
    """Escape markdown V2 characters properly"""
    if not text:
        return ""
    
    # MarkdownV2 special characters that need escaping
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
# Add this global variable with your other attack states

# -----------------------------
# /funny command - Fixed with Markdown & Nicknames
# -----------------------------
async def funny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        if not msg:
            return

        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # Check Admin
        if not is_admin(user_id, username):
            await msg.reply_text("⛔ ခွင့်မပြုပါ")
            return

        args = context.args
        if len(args) != 2:
            await msg.reply_text("သုံးပုံ: /funny @user1 @user2")
            return

        chat_id = update.effective_chat.id
        user1_target = args[0]
        user2_target = args[1]

        # Helper to get ID and Name (Checking Nickname First)
        async def get_target_info(arg):
            # 1. Resolve ID
            resolved_id = await resolve_target_user_id(context, chat_id, arg)
            if not resolved_id:
                return None, None
            
            # 2. Check for Nickname in name_map
            nickname = name_map.get(str(resolved_id))
            if nickname:
                return resolved_id, nickname
            
            # 3. Fallback to Telegram Name
            try:
                member = await context.bot.get_chat_member(chat_id, resolved_id)
                return resolved_id, member.user.first_name
            except:
                return resolved_id, f"User{resolved_id}"

        # Resolve both users
        uid1, name1 = await get_target_info(user1_target)
        uid2, name2 = await get_target_info(user2_target)

        if not uid1 or not uid2:
            await msg.reply_text("❌ User မတွေ့ပါ")
            return

        # Check privileges
        if is_admin(uid1) or is_admin(uid2):
            await msg.reply_text("❌ Admin နဲ့ Owner ကို စလို့မရပါ")
            return

        # Set Session
        active_fight_sessions[chat_id] = {
            uid1: uid2,
            uid2: uid1,
        }

        # Create Markdown Mentions
        safe_name1 = escape_markdown_v2(name1)
        safe_name2 = escape_markdown_v2(name2)
        
        mention1 = f"[{safe_name1}](tg://user?id={uid1})"
        mention2 = f"[{safe_name2}](tg://user?id={uid2})"

        # Send Start Message
        text = (
            f"⚔️ {mention1} နဲ့ {mention2} တို့အကြား စလိုက်ပြီ\n"
            f"အခု သူတို့တစ်ယောက်ကိုတစ်ယောက် ဘာပြောချင်ပြောလို့ရပြီ"
        )
        
        await msg.reply_text(text, parse_mode="MarkdownV2")
        update_stats("commands_executed", chat_id, user_id)

    except Exception as e:
        await msg.reply_text(f"❌ Error: {str(e)}")

# -----------------------------
# Fight message handler - Markdown + Nickname Support
# -----------------------------
async def funny_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        if not msg or not msg.text:
            return

        chat_id = update.effective_chat.id
        sender = update.effective_user
        
        # Check active session
        if chat_id not in active_fight_sessions:
            return
            
        session = active_fight_sessions[chat_id]
        
        if sender.id not in session:
            return

        target_id = session[sender.id]
        
        # --- 1. Get Sender Name (Nickname > Real Name) ---
        sender_nick = name_map.get(str(sender.id))
        sender_name = sender_nick if sender_nick else sender.first_name
        
        # --- 2. Get Target Name (Nickname > Real Name) ---
        target_nick = name_map.get(str(target_id))
        if target_nick:
            target_name = target_nick
        else:
            try:
                target_member = await context.bot.get_chat_member(chat_id, target_id)
                target_name = target_member.user.first_name
            except:
                target_name = "User"

        # --- 3. Escape for Markdown V2 ---
        safe_sender = escape_markdown_v2(sender_name)
        safe_target = escape_markdown_v2(target_name)
        safe_text = escape_markdown_v2(msg.text)

        # --- 4. Construct Mentions ---
        sender_mention = f"[{safe_sender}](tg://user?id={sender.id})"
        target_mention = f"[{safe_target}](tg://user?id={target_id})"

        # --- 5. Build Final Message ---
        # Format: "TargetName\nမင်းကို SenderName က "Message" လို့ပြောခိုင်းလိုက်တယ်"
        reply_text = (
            f"{target_mention}\n"
            f"မင်းကို {sender_mention} က \"{safe_text}\" လို့ပြောခိုင်းလိုက်တယ်"
        )

        await msg.reply_text(reply_text, parse_mode="MarkdownV2")
        update_stats("messages_processed", chat_id, sender.id)
        
    except Exception as e:
        print(f"❌ Fight message error: {e}")


# -----------------------------
# /stopfunny command - FULLY FIXED
# -----------------------------
async def stop_funny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the fight in current chat"""
    try:
        msg = update.effective_message
        if not msg:
            return

        user = update.effective_user
        
        if not is_authorized(user):
            await msg.reply_text("⛔ ခွင့်မပြုပါ")
            return

        chat_id = update.effective_chat.id
        
        if chat_id in active_fight_sessions:
            del active_fight_sessions[chat_id]
            await msg.reply_text("✅ ဒီ group မှာ ရပ်လိုက်ပြီ")
            update_stats("commands_executed", chat_id, user.id)
        else:
            await msg.reply_text("❌ ဒီ group မှာ မစရသေးပါ")
            
    except Exception as e:
        print(f"❌ Stopfunny error: {e}")
        await msg.reply_text("❌ အမှားတစ်ခုဖြစ်နေသည်")

# ---------------- ATTACK STICKER COMMAND ----------------


async def attackuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "attackuser"):
        return
        
    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.message.chat_id

    # Get target from argument or reply
    if context.args:
        target_arg = context.args[0]
    elif update.message.reply_to_message:
        rep = update.message.reply_to_message
        if rep.from_user.username:
            target_arg = f"@{rep.from_user.username}"
        else:
            target_arg = str(rep.from_user.id)
    else:
        return await update.message.reply_text("Usage: /attackuser @username OR reply to user")

    # ENHANCED TARGET RESOLUTION - Look through ALL JSON data
    target_username = None
    
    print(f"🔍 Attackuser: Looking for target: {target_arg}")
    
    # Remove @ if present for searching
    search_target = target_arg.lstrip('@').lower().strip()
    
    # 1. Search in name_map (nicknames)
    for user_id_str, nickname in name_map.items():
        if nickname.lower() == search_target:
            # Try to get username from member_cache
            chat_key = str(chat_id)
            if chat_key in member_cache:
                user_data = member_cache[chat_key].get("members", {}).get(user_id_str)
                if user_data and user_data.get("username"):
                    target_username = f"@{user_data['username']}"
                    break
            # Fallback to nickname
            target_username = nickname
            break
    
    # 2. Search in member_cache for current chat
    if not target_username:
        chat_key = str(chat_id)
        if chat_key in member_cache:
            for uid, user_data in member_cache[chat_key].get("members", {}).items():
                # Check username match
                if user_data.get("username", "").lower() == search_target:
                    target_username = f"@{user_data['username']}"
                    break
                # Check first name match
                if user_data.get("first_name", "").lower() == search_target:
                    if user_data.get("username"):
                        target_username = f"@{user_data['username']}"
                    else:
                        target_username = user_data.get("first_name", search_target)
                    break
    
    # 3. Search private_users
    if not target_username:
        for uid_str, user_data in private_users.items():
            if user_data.get("username", "").lower() == search_target:
                target_username = f"@{user_data['username']}"
                break
            if user_data.get("name", "").lower() == search_target:
                if user_data.get("username"):
                    target_username = f"@{user_data['username']}"
                else:
                    target_username = user_data.get("name", search_target)
                break
    
    # 4. Search all member_cache across all chats
    if not target_username:
        for cache_chat_id, cache_data in member_cache.items():
            for uid, user_data in cache_data.get("members", {}).items():
                if user_data.get("username", "").lower() == search_target:
                    target_username = f"@{user_data['username']}"
                    break
            if target_username:
                break
    
    # 5. If it's already a username with @, return as-is
    if not target_username and target_arg.startswith('@'):
        target_username = target_arg
    
    # 6. Final fallback - add @ and return
    if not target_username:
        target_username = f"@{search_target}"
    
    print(f"✅ Attackuser target resolved: {target_username}")

    # Stop any existing attackuser task
    task = active_attack_tasks.get(chat_id)
    if task and not task.done():
        try:
            task.cancel()
        except:
            pass

    # Get current speed (respects setspeed)
    current_speed = get_attack_speed(chat_id)
    
    # Start attack with username mention (not proper mention)
    await update.message.reply_text(
    f"သခင့်အလိုကျဖာသယ်မသားကိုဖင်စတင်လိုးပါတော့မယ် \n\n"
   
)
    # Create new attack task with username spam
    task = asyncio.create_task(attackuser_runner(context, chat_id, target_username))
    active_attack_tasks[chat_id] = task

async def attackuser_runner(context, chat_id, target_username):
    """Attack user with username mentions (not proper mentions)"""
    
    while chat_id in active_attack_tasks and active_attack_tasks[chat_id] == asyncio.current_task():
        try:
            # Get CURRENT speed (this respects changes via /setspeed in real-time)
            current_speed = get_attack_speed(chat_id)

            #ADD TYPING ACTION HERE (same as attack command)
            if current_speed in [0.2, 1, 1.5, 2]:
                await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
            
            # Use random reply from attack_replies with username mention
            line = random.choice(attack_replies) if attack_replies else "Get rekt!"
            
            # Use plain username mention (not clickable mention)
            if target_username.startswith('@'):
                text_to_send = f"{target_username} {line}"
            else:
                text_to_send = f"@{target_username} {line}"
            
            await context.bot.send_message(chat_id=chat_id, text=text_to_send)
            await asyncio.sleep(current_speed)  # Use current speed

        except asyncio.CancelledError:
            return
        except Exception as e:
            print(f"❌ Attackuser error: {e}")
            # Try to continue despite errors
            await asyncio.sleep(2)

def get_attack_speed(chat_id: int) -> float:
    """Get attack speed for chat (respects setspeed)"""
    return attack_delay.get(chat_id, DEFAULT_DELAY)

async def stopuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    task = active_attack_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
        del active_attack_tasks[chat_id]
        await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")
    else:
        await update.message.reply_text("❌ No active /attackuser attack running.")

# ---------------- LIMITED COMMAND SYSTEM (FAST) ----------------
def check_limited_command(user_id: int, command: str) -> bool:
    user_key = str(user_id)
    if user_key not in limit_commands_data:
        return False
    
    if command not in limit_commands_data[user_key]:
        return False
    
    limit_info = limit_commands_data[user_key][command]
    remaining = limit_info.get("remaining", 0)
    
    if remaining <= 0:
        del limit_commands_data[user_key][command]
        if not limit_commands_data[user_key]:
            del limit_commands_data[user_key]
        asyncio.create_task(fast_data.buffered_save(LIMIT_COMMANDS_FILE, limit_commands_data))
        return False
    
    limit_commands_data[user_key][command]["remaining"] = remaining - 1
    asyncio.create_task(fast_data.buffered_save(LIMIT_COMMANDS_FILE, limit_commands_data))
    return True

# ---------------- REVERSE ATTACK SYSTEM ----------------

async def reverse_attack_owner(context: ContextTypes.DEFAULT_TYPE, chat_id: int, attacker_id: int, command_used: str):
    """
    Robust reverse attack handler:
    - sends a notification to chat
    - applies safe, consistent reversals (attack, ghost, troll, settarget, combo)
    - uses consistent formats for die_configs and logs errors
    """
    try:
        # Get attacker display name with proper MarkdownV2
        try:
            attacker_member = await context.bot.get_chat_member(chat_id, attacker_id)
            attacker_name = attacker_member.user.first_name or f"User{attacker_id}"
            safe_name = escape_markdown_v2(attacker_name)
            attacker_display = f"[{safe_name}](tg://user?id={attacker_id})"
        except Exception:
            attacker_display = f"User{attacker_id}"

        # Send reverse attack notification
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🛡️ *REVERSE ATTACK\\!* {attacker_display} used `/{command_used}` on owner \\- command reversed\\!",
                parse_mode="MarkdownV2"
            )
        except Exception:
            # don't abort if notify fails
            pass

        applied_actions = []

        try:
            # Normalize command string
            cmd = (command_used or "").lower()

            # 1) For attack\\-like commands: stop others and start an attack on attacker
            if cmd in ["attack", "multiple", "smartattack", "smart", "quickattack", "qa", "go"]:
                try:
                    # Stop all existing attacks in this chat
                    await stop_all_attacks(chat_id)
                except Exception:
                    pass

                # Start reverse attack on attacker
                attacking_single[chat_id] = str(attacker_id)
                attacking_single_display[chat_id] = attacker_display
                attack_delay[chat_id] = 0.1  # Ultra fast
                
                # Start ultra attack loop
                attack_tasks[("single", chat_id)] = asyncio.create_task(
                    ultra_attack_loop(context, chat_id, str(attacker_id), attacker_display)
                )
                applied_actions.append("🔥 Continuous Attack")

            # 2) ghost command
            if cmd == "ghost":
                ghost_map.setdefault(chat_id, set()).add(attacker_id)
                applied_actions.append("👻 Ghost \\- Their messages will be hidden")

            # 3) troll command
            if cmd == "troll":
                troll_map.setdefault(chat_id, set()).add(attacker_id)
                applied_actions.append("🤡 Troll \\- Their messages will be echoed")

            # 4) settarget: enable auto\\-reply against attacker
            if cmd == "settarget":
                # Enable auto\\-reply against attacker
                die_configs.setdefault(str(chat_id), {})
                die_configs[str(chat_id)].update({
                    "target_id": int(attacker_id),
                    "target_ids": [int(attacker_id)],
                    "templates": attack_replies[:3] if attack_replies else ["Got you\\!"],
                    "active": True,
                    "setter": "reverse_system",
                    "set_at": datetime.utcnow().isoformat()
                })
                try:
                    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
                except Exception:
                    pass
                applied_actions.append("💀 Auto\\-Reply \\(settarget\\)")

            # 5) combo special \\- apply multiple protections/attacks
            if cmd == "combo":
                try:
                    await stop_all_attacks(chat_id)
                except Exception:
                    pass

                # Start attack on attacker
                attacking_single[chat_id] = str(attacker_id)
                attacking_single_display[chat_id] = attacker_display
                attack_tasks[("single", chat_id)] = asyncio.create_task(
                    ultra_attack_loop(context, chat_id, str(attacker_id), attacker_display)
                )

                # ghost + troll
                ghost_map.setdefault(chat_id, set()).add(attacker_id)
                troll_map.setdefault(chat_id, set()).add(attacker_id)

                # settarget \\(combo\\)
                die_configs.setdefault(str(chat_id), {})
                die_configs[str(chat_id)].update({
                    "target_ids": [int(attacker_id)],
                    "templates": attack_replies[:3] if attack_replies else ["\\.\\.\\."],
                    "active": True,
                    "setter": "reverse_system",
                    "set_at": datetime.utcnow().isoformat()
                })
                try:
                    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
                except Exception:
                    pass

                applied_actions.append("🎛️ ULTIMATE COMBO \\(Attack\\+Ghost\\+Troll\\+Settarget\\)")

            # 6) reply command \\- instant reverse reply
            if cmd == "reply":
                # Send 2 instant replies to attacker
                for i in range(2):
                    line = random.choice(attack_replies) if attack_replies else "Reverse attack\\!"
                    text_to_send = f"{attacker_display} {line}"
                    await context.bot.send_message(
                        chat_id=chat_id, 
                        text=text_to_send,
                        parse_mode="MarkdownV2"
                    )
                    if i == 0:
                        await asyncio.sleep(0.3)
                applied_actions.append("💬 Instant Reverse Reply")

            # 7) tag/mass tag commands
            if cmd in ["tag", "add"]:
                # Add attacker to targets and start mass tag
                if chat_id not in added_targets:
                    added_targets[chat_id] = []
                
                # Add attacker to targets if not already there
                if attacker_id not in [tid for tid, _ in added_targets[chat_id]]:
                    added_targets[chat_id].append((attacker_id, attacker_display))
                
                # Stop any existing tag attack
                prev_tag = attack_tasks.get(("tag", chat_id))
                if prev_tag and not prev_tag.done():
                    try: 
                        prev_tag.cancel()
                    except: 
                        pass

                # Start reverse mass tagging
                attack_tasks[("tag", chat_id)] = asyncio.create_task(
                    optimizer.process_attack(mass_tag_attack_loop(context, chat_id, added_targets[chat_id]))
                )
                applied_actions.append("🏷️ Reverse Mass Tagging")

            # 8) smartattack \\- reverse smart attack
            if cmd == "smartattack":
                await stop_smart_attack(chat_id)
                smart_attacks[chat_id] = {
                    'target': str(attacker_id),
                    'display': attacker_display,
                    'base_delay': 0.1,
                    'consecutive_success': 0,
                    'total_messages': 0,
                    'flood_events': 0,
                    'max_speed': 0.05,
                    'min_speed': 2.0
                }
                attack_tasks[("smart", chat_id)] = asyncio.create_task(
                    enhanced_smart_attack_loop(context, chat_id, str(attacker_id), attacker_display)
                )
                applied_actions.append("🧠 Reverse Smart Attack")

            # 9) megaspam \\- reverse mega spam
            if cmd == "megaspam":
                # Stop any existing mega spam
                if chat_id in megaspam_attacks:
                    task = megaspam_attacks[chat_id]
                    if task and not task.done():
                        task.cancel()
                    megaspam_attacks.pop(chat_id, None)

                # Start reverse mega spam
                megaspam_attacks[chat_id] = asyncio.create_task(
                    megaspam_attack_loop(context, chat_id, attacker_id, attacker_display)
                )
                applied_actions.append("💣 Reverse Mega Spam")

            # 10) attackuser \\- reverse attackuser
            if cmd == "attackuser":
                # Stop any existing attackuser
                task = active_attack_tasks.get(chat_id)
                if task and not task.done():
                    task.cancel()
                    active_attack_tasks.pop(chat_id, None)

                # Start reverse attackuser
                task = asyncio.create_task(attackuser_runner(context, chat_id, f"@{attacker_member.user.username}" if attacker_member.user.username else f"User{attacker_id}"))
                active_attack_tasks[chat_id] = task
                applied_actions.append("👤 Reverse Attack User")

            # Final summary message
            if applied_actions:
                actions_text = "\n".join([f"• {action}" for action in applied_actions])
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"✅ *Reverse Applied to {attacker_display}\\:*\n{actions_text}",
                        parse_mode="MarkdownV2"
                    )
                except Exception:
                    pass

        except Exception as e:
            # print to console for quick debugging
            print(f"❌ REVERSE ERROR: {e}")

    except Exception as e:
        print(f"❌ REVERSE SETUP ERROR: {e}")

async def stop_all_attacks(chat_id: int):
    """Stop all attacks in a chat"""
    # Stop single attacks
    if chat_id in attacking_single:
        attacking_single.pop(chat_id, None)
        attacking_single_display.pop(chat_id, None)
        t = attack_tasks.get(("single", chat_id))
        if t and not t.done():
            try: 
                t.cancel()
            except: 
                pass
            attack_tasks.pop(("single", chat_id), None)
    
    # Stop multiple attacks
    if chat_id in attacking_multiple:
        attacking_multiple.pop(chat_id, None)
        attacking_multiple_displays.pop(chat_id, None)
        t = attack_tasks.get(("multiple", chat_id))
        if t and not t.done():
            try: 
                t.cancel()
            except: 
                pass
            attack_tasks.pop(("multiple", chat_id), None)
    
    # Stop smart attacks
    if chat_id in smart_attacks:
        smart_attacks.pop(chat_id, None)
        t = attack_tasks.get(("smart", chat_id))
        if t and not t.done():
            try: 
                t.cancel()
            except: 
                pass
            attack_tasks.pop(("smart", chat_id), None)
    
    # Stop tag attacks
    t = attack_tasks.get(("tag", chat_id))
    if t and not t.done():
        try: 
            t.cancel()
        except: 
            pass
        attack_tasks.pop(("tag", chat_id), None)
    
    # Stop mega spam
    if chat_id in megaspam_attacks:
        task = megaspam_attacks[chat_id]
        if task and not task.done():
            task.cancel()
        megaspam_attacks.pop(chat_id, None)
    
    # Stop attackuser
    task = active_attack_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
        active_attack_tasks.pop(chat_id, None)

async def check_and_reverse_owner_attack(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str, target_args: list = None):
    """Check if any target is owner and reverse attack if detected"""
    if not target_args:
        return False
        
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    for target_str in target_args:
        if owner_matches_target(target_str):
            print(f"🛡️ REVERSE PROTECTION: {user.id} used {command} on owner - reversing!")
            await reverse_attack_owner(context, chat_id, user.id, command)
            return True
            
    return False

# ---------------- TRANSLATION FUNCTION ----------------
async def translate_text(text: str, target_lang: str = "en") -> str:
    if not text or len(text.strip()) == 0:
        return text
        
    try:
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        response = requests.get(TRANSLATE_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        translated_parts = []
        if data and isinstance(data, list) and len(data) > 0:
            for item in data[0]:
                if isinstance(item, list) and len(item) > 0 and item[0]:
                    translated_parts.append(str(item[0]))
        
        translated_text = ' '.join(translated_parts) if translated_parts else text
        return translated_text.strip()
        
    except Exception:
        return f"[Translation failed]"

def detect_language(text: str) -> str:
    if not text:
        return 'en'
    
    myanmar_range = r'[\u1000-\u109F]'
    if re.search(myanmar_range, text):
        return 'my'
    else:
        return 'en'


# ---------------- ULTRA FAST ATTACK SYSTEM ----------------
# Add this function in the UTILITY FUNCTIONS section

async def handle_settarget_reply(context: ContextTypes.DEFAULT_TYPE, msg: Message, target_id: int):
    global processed_settarget_messages
    
    chat_id = msg.chat.id
    message_key = f"{chat_id}_{msg.message_id}"
    
    if message_key in processed_settarget_messages:
        return
    
    processed_settarget_messages.add(message_key)
    if len(processed_settarget_messages) > 1000:
        processed_settarget_messages = set(list(processed_settarget_messages)[-500:])
    
    try:
        # Get user's actual name
        try:
            member = await context.bot.get_chat_member(chat_id, target_id)
            user_name = member.user.first_name or f"User{target_id}"
        except:
            user_name = f"User{target_id}"
        
        # Markdown clickable mention
        target_display = f"[{user_name}](tg://user?id={target_id})"
        
        # Send 3 replies with Markdown mention
        if len(attack_replies) >= 3:
            selected_replies = random.sample(attack_replies, 3)
        else:
            selected_replies = attack_replies * 3
            
        for reply in selected_replies:
            reply_text = f"{target_display} {reply}"
            await context.bot.send_message(
                chat_id=chat_id, 
                text=reply_text,
                parse_mode="Markdown",
                reply_to_message_id=msg.message_id
            )
            await asyncio.sleep(0.3)
            
    except Exception as e:
        print(f"❌ Settarget failed: {e}")

# ---------------- ENHANCED ATTACK LOOPS WITH TYPING ONLY FOR SLOW MODE ----------------

async def enhanced_normal_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ENHANCED NORMAL ATTACK LOOP - With Normal Markdown, NO adaptive speed"""
    
    while attacking_single.get(chat_id) == target:
        try:
            # Get the CURRENT attack delay (respects setspeed)
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
            
            # Show typing only for specific speeds
            if current_delay in [0.2, 1, 1.5, 2]:
                await show_typing_action(context, chat_id)

            # Get random attack reply
            line = random.choice(attack_replies) if attack_replies else "Get rekt!"
            
            # IMPORTANT: Change from escape_markdown_v1 to escape_markdown_v2
            safe_line = escape_markdown_v2(line)  # CHANGED HERE
            
            # Check if it's proper markdown mention
            if display.startswith('[') and '](tg://' in display:
                # It's a clickable mention, use with MarkdownV2 parse mode
                text_to_send = f"{display} {safe_line}"
                parse_mode = "MarkdownV2"  # CHANGED HERE
            else:
                # Not a clickable mention (e.g., @username)
                text_to_send = f"{display} {safe_line}"
                parse_mode = None
            
            # Send the attack message
            await context.bot.send_message(
                chat_id=chat_id, 
                text=text_to_send,
                parse_mode=parse_mode
            )
            
            # NO adaptive speed - wait exactly the set delay
            await asyncio.sleep(current_delay)
            
        except Exception as e:
            print(f"❌ Attack loop error: {e}")
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                # On flood error, wait longer
                await asyncio.sleep(5)
            else:
                # Brief pause for other errors
                await asyncio.sleep(0.5)

async def enhanced_multiple_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, targets_list: List[str], displays_list: List[str]):
    """ENHANCED MULTIPLE ATTACK LOOP - NO adaptive speed"""
    
    while attacking_multiple.get(chat_id) == targets_list:
        try:
            # Get the CURRENT attack delay
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
            
            # Show typing only for specific speeds
            if current_delay in [0.2, 1, 1.5, 2]:
                await show_typing_action(context, chat_id)

            # Get random attack reply
            line = random.choice(attack_replies) if attack_replies else "Get rekt!"
            
            # IMPORTANT: Change from escape_markdown_v1 to escape_markdown_v2
            safe_line = escape_markdown_v2(line)  # CHANGED HERE
            
            # Check what type of displays we have
            has_proper_mentions = False
            plain_displays = []
            
            for display in displays_list:
                if display.startswith('[') and '](tg://' in display:
                    # This is a proper clickable mention
                    has_proper_mentions = True
                    plain_displays.append(display)
                elif display.startswith('@'):
                    # This is a username (not clickable)
                    # Change from escape_markdown_v1 to escape_markdown_v2
                    plain_displays.append(escape_markdown_v2(display))  # CHANGED HERE
                else:
                    # Plain text, escape it
                    # Change from escape_markdown_v1 to escape_markdown_v2
                    plain_displays.append(escape_markdown_v2(display))  # CHANGED HERE
            
            # FIX: တစ်ကြောင်းစီခွဲပို့ — multi target မှာ မြန်အောင်/နှေးတာမရှိအောင်
            # Determine parse mode
            parse_mode = "MarkdownV2" if has_proper_mentions else None
            
            # Send EACH target as its own message back-to-back (no pause between targets)
            for one_display in plain_displays:
                # Fresh attack line per target for variety
                fresh_line = escape_markdown_v2(random.choice(attack_replies) if attack_replies else "Get rekt!")
                text_to_send = f"{one_display} {fresh_line}"
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=text_to_send,
                        parse_mode=parse_mode
                    )
                except Exception as _e:
                    # Per-target error — flood/markdown အမှား ဖြစ်ရင် plain အသွင် ထပ်စမ်း
                    if "Too Many Requests" in str(_e) or "flood" in str(_e).lower():
                        await asyncio.sleep(2)
                    else:
                        try:
                            await context.bot.send_message(chat_id=chat_id, text=text_to_send)
                        except:
                            pass
                # No delay between targets — back-to-back
            
            # NO adaptive speed - wait exactly the set delay between full rounds
            await asyncio.sleep(current_delay)
            
        except Exception as e:
            print(f"❌ Multiple attack loop error: {e}")
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                # Flood error, wait longer
                await asyncio.sleep(6)
            else:
                # Brief pause for other errors
                await asyncio.sleep(1)

async def ultra_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ENHANCED ATTACK LOOP WITH ALL MODES"""
    
    if attack_mode == "hyperburst" or attack_mode == "ultraburst" or attack_mode == "burst":
        await enhanced_burst_attack_loop(context, chat_id, target, display)
    elif attack_mode == "zero_delay":
        await enhanced_zero_delay_attack_loop(context, chat_id, target, display)
    elif attack_mode == "smartzerodelay":
        await enhanced_smart_zero_delay_loop(context, chat_id, target, display)
    elif attack_mode == "ultimatezerodelay":
        await ultimate_zero_delay_loop(context, chat_id, target, display)
    elif attack_mode == "smart":
        await enhanced_smart_attack_loop(context, chat_id, target, display)
    else:
        await enhanced_normal_attack_loop(context, chat_id, target, display)

async def enhanced_burst_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ENHANCED BURST ATTACK - Handles all burst modes"""
    # Get config based on attack mode
    if attack_mode == "hyperburst":
        burst_config = {
            'burst_count': 25,
            'burst_duration': 2.0,
            'pause_duration': 3.0
        }
    elif attack_mode == "ultraburst":
        burst_config = {
            'burst_count': 15, 
            'burst_duration': 1.0,
            'pause_duration': 2.0
        }
    else:
        burst_config = burst_mode_config.get(chat_id, {
            'burst_count': 10,
            'burst_duration': 5.0,
            'pause_duration': 7.0
        })
    
    messages_per_burst = burst_config['burst_count']
    burst_time = burst_config['burst_duration']
    pause_time = burst_config['pause_duration']
    
    # Calculate message delay
    message_delay = burst_time / messages_per_burst
    
    while attacking_single.get(chat_id) == target:
        try:
            # BURST PHASE
            messages_sent = 0
            start_time = time.time()
            
            while messages_sent < messages_per_burst and (time.time() - start_time) < burst_time:
                line = random.choice(attack_replies)
                text_to_send = f"{display} {line}"
                
                # Send message
                asyncio.create_task(
                    context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
                )
                
                messages_sent += 1
                
                # Ultra-short delay for hyper/ultra modes
                if attack_mode in ["hyperburst", "ultraburst"]:
                    await asyncio.sleep(message_delay * 0.3)  # 70% faster
                else:
                    await asyncio.sleep(message_delay)
            
            # PAUSE PHASE
            await asyncio.sleep(pause_time)
            
        except Exception as e:
            if "Too Many Requests" in str(e):
                wait_time = 10 if attack_mode in ["hyperburst", "ultraburst"] else 8
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(3)

async def hyperburst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """HYPER BURST - Faster than zero delay, no freezing"""
    if await check_lock_and_notify(update, context, "hyperburst"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/hyperburst")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
    
    # Set to burst mode with ultra-fast settings
    burst_mode_config[update.effective_chat.id] = {
        'mode': 'hyperburst',
        'burst_count': 25,  # 25 messages per burst
        'burst_duration': 2.0,  # 2 seconds for 25 messages
        'pause_duration': 3.0   # 3 second pause
    }
    
    set_attack_mode(update.effective_chat.id, "burst")
    
    await update.message.reply_text(
        "💥 **HYPER BURST MODE ACTIVATED!**\n\n"
        "🚀 **Speed:** 12.5 messages/second\n"
        "💣 **Burst:** 25 messages in 2 seconds\n"
        "⏸️ **Pause:** 3 seconds\n"
        "📊 **Total Rate:** ~5 messages/second\n"
        "🛡️ **No Freezing:** GUARANTEED\n\n"
        "*This is FASTER and MORE RELIABLE than zero delay!*",
        parse_mode="Markdown"
    )


async def smartattack_enhanced_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SMART ATTACK - Auto-adjusts speed for maximum performance"""
    if await check_lock_and_notify(update, context, "smartattack"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/smartattack")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        await update.message.reply_text("Usage: /smartattack @user")
        return

    chat_id = update.effective_chat.id
    target_arg = context.args[0]
    
    if owner_matches_target(target_arg):
        attacker = update.effective_user
        await reverse_attack_owner(context, chat_id, attacker.id, "smartattack")
        return

    target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
    if not target_id:
        await update.message.reply_text(f"❌ Target not found: {target_arg}")
        return

    # Stop previous smart attack
    await stop_smart_attack(chat_id)

    # Start enhanced smart attack
    smart_attacks[chat_id] = {
        'target': str(target_id),
        'display': display,
        'base_delay': 0.3,  # Start fast
        'consecutive_success': 0,
        'total_messages': 0,
        'flood_events': 0,
        'max_speed': 0.05,  # Minimum delay
        'min_speed': 2.0    # Maximum delay
    }

    attack_tasks[("smart", chat_id)] = asyncio.create_task(
        enhanced_smart_attack_loop(context, chat_id, str(target_id), display)
    )

    await update.message.reply_text(
        f"🧠 **ENHANCED SMART ATTACK ACTIVATED**\n"
        f"🎯 Target: {display}\n"
        f"⚡ Starting at: 0.3s delay\n"
        f"🚀 Max Speed: 0.05s delay\n"
        f"🛡️ Anti-Flood: ACTIVE\n\n"
        f"*Auto-adjusts speed for maximum performance!*"
    )

async def enhanced_smart_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ENHANCED SMART ATTACK - Auto-adjusts for maximum speed"""
    
    while smart_attacks.get(chat_id, {}).get('target') == target:
        smart_data = smart_attacks.get(chat_id, {})
        base_delay = smart_data.get('base_delay', 0.3)
        consecutive_success = smart_data.get('consecutive_success', 0)
        
        try:
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            await context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            
            # Update success tracking
            consecutive_success += 1
            smart_attacks[chat_id]['consecutive_success'] = consecutive_success
            smart_attacks[chat_id]['total_messages'] = smart_data.get('total_messages', 0) + 1
            
            # AGGRESSIVE speed increase when successful
            if consecutive_success > 10:
                base_delay = max(0.05, base_delay * 0.8)  # 20% faster
            elif consecutive_success > 5:
                base_delay = max(0.1, base_delay * 0.9)   # 10% faster
            elif consecutive_success > 2:
                base_delay = max(0.2, base_delay * 0.95)  # 5% faster
            
            smart_attacks[chat_id]['base_delay'] = base_delay
            
            # Add random variance
            actual_delay = base_delay * random.uniform(0.8, 1.1)
            await asyncio.sleep(actual_delay)
            
        except Exception as e:
            # Reset success counter on error
            smart_attacks[chat_id]['consecutive_success'] = 0
            
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                smart_attacks[chat_id]['flood_events'] = smart_data.get('flood_events', 0) + 1
                base_delay = min(2.0, base_delay * 1.5)  # Slow down
                smart_attacks[chat_id]['base_delay'] = base_delay
                
                wait_time = extract_wait_time(str(e)) or 10
                await asyncio.sleep(wait_time)
            else:
                base_delay = min(1.5, base_delay * 1.2)
                smart_attacks[chat_id]['base_delay'] = base_delay
                await asyncio.sleep(1.0)

async def stop_smart_attack(chat_id: int):
    """Stop smart attack for a chat"""
    if chat_id in smart_attacks:
        smart_attacks.pop(chat_id, None)
        task = attack_tasks.get(("smart", chat_id))
        if task and not task.done():
            try:
                task.cancel()
            except:
                pass
        attack_tasks.pop(("smart", chat_id), None)


async def enhanced_smart_zero_delay_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """SMART ZERO DELAY - Maximum speed without freezing"""
    message_count = 0
    error_count = 0
    max_messages_before_pause = 50
    
    while attacking_single.get(chat_id) == target:
        try:
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            
            # FIRE AND FORGET - send without waiting
            asyncio.create_task(
                context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            )
            
            message_count += 1
            error_count = 0  # Reset error count
            
            # SMART PAUSE: Every 50 messages, add 10ms pause to avoid flood
            if message_count >= max_messages_before_pause:
                message_count = 0
                await asyncio.sleep(0.01)  # 10ms pause every 50 messages
            else:
                # ACTUAL ZERO DELAY - 0.001s is practically zero
                await asyncio.sleep(0.001)
                
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            if "Too Many Requests" in error_msg or "flood" in error_msg:
                print(f"🚨 Flood detected (expected), waiting...")
                wait_time = extract_wait_time(error_msg)
                print(f"⏳ Smart recovery: {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
                # Reduce speed slightly after flood
                max_messages_before_pause = max(30, max_messages_before_pause - 10)
                error_count = 0
            else:
                # Brief pause for other errors
                if error_count > 3:
                    await asyncio.sleep(2.0)
                else:
                    await asyncio.sleep(0.5)

async def smart_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """AUTO-ADJUSTS SPEED BASED ON PERFORMANCE"""
    
    while smart_attacks.get(chat_id, {}).get('target') == target:
        smart_data = smart_attacks.get(chat_id, {})
        base_delay = smart_data.get('base_delay', 1.0)
        consecutive_success = smart_data.get('consecutive_success', 0)
        
        try:
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            await context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            
            # Update success tracking
            consecutive_success += 1
            smart_attacks[chat_id]['consecutive_success'] = consecutive_success
            smart_attacks[chat_id]['total_messages'] = smart_data.get('total_messages', 0) + 1
            
            # Adaptive speed adjustment
            if consecutive_success > 15:
                base_delay = max(0.3, base_delay * 0.92)  # Speed up gradually
            elif consecutive_success > 8:
                base_delay = max(0.4, base_delay * 0.95)
            elif consecutive_success > 3:
                base_delay = max(0.6, base_delay * 0.98)
            
            smart_attacks[chat_id]['base_delay'] = base_delay
            
            # Add random variance to avoid patterns
            actual_delay = base_delay * random.uniform(0.85, 1.15)
            await asyncio.sleep(actual_delay)
            
        except Exception as e:
            # Reset success counter on error
            smart_attacks[chat_id]['consecutive_success'] = 0
            
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                # Flood detected - slow down significantly
                smart_attacks[chat_id]['flood_events'] = smart_data.get('flood_events', 0) + 1
                base_delay = min(3.0, base_delay * 1.5)  # Slow down
                smart_attacks[chat_id]['base_delay'] = base_delay
                
                # Extract wait time or use default
                wait_time = extract_wait_time(str(e)) or 12
                await asyncio.sleep(wait_time)
            else:
                # Other error - slight slowdown
                base_delay = min(2.0, base_delay * 1.1)
                smart_attacks[chat_id]['base_delay'] = base_delay
                await asyncio.sleep(2)

async def mass_tag_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, targets: List[Tuple[int, str]]):
    """Mass tagging attack loop - NO adaptive speed"""
    
    while attack_tasks.get(("tag", chat_id)):
        try:
            # Get current targets
            current_targets = added_targets.get(chat_id, targets)
            if not current_targets:
                break
            
            # Process each display
            mentions = []
            for _, display in current_targets:
                if display.startswith('[') and '](tg://' in display:
                    # Proper mention, keep as-is
                    mentions.append(display)
                elif display.startswith('@'):
                    # Username, escape it
                    mentions.append(escape_markdown_v1(display))
                else:
                    # Plain text, escape it
                    mentions.append(escape_markdown_v1(display))
            
            mentions_text = " ".join(mentions)
            
            # Get random attack reply
            line = random.choice(attack_replies) if attack_replies else random.choice(default_auto_replies)
            safe_line = escape_markdown_v1(line)
            
            # Determine parse mode
            has_proper_mentions = any(m.startswith('[') and '](tg://' in m for m in mentions)
            
            text_to_send = f"{mentions_text} {safe_line}"
            parse_mode = "Markdown" if has_proper_mentions else None
            
            # Send message
            await context.bot.send_message(
                chat_id=chat_id, 
                text=text_to_send,
                parse_mode=parse_mode
            )
            
            # Wait the set delay
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
            await asyncio.sleep(current_delay)
            
        except Exception as e:
            print(f"❌ Mass tag loop error: {e}")
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(0.5)

async def enhanced_burst_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ENHANCED BURST ATTACK - Faster and more reliable"""
    burst_config = burst_mode_config.get(chat_id, {
        'burst_count': 10,
        'burst_duration': 5.0,
        'pause_duration': 7.0
    })
    
    messages_per_burst = burst_config['burst_count']
    burst_time = burst_config['burst_duration']
    pause_time = burst_config['pause_duration']
    
    # Calculate optimal message delay
    message_delay = burst_time / messages_per_burst
    
    while attacking_single.get(chat_id) == target:
        try:
            # BURST PHASE - Send all messages as fast as possible
            messages_sent = 0
            start_time = time.time()
            
            while messages_sent < messages_per_burst and (time.time() - start_time) < burst_time:
                line = random.choice(attack_replies)
                text_to_send = f"{display} {line}"
                
                # FIRE AND FORGET - maximum speed
                asyncio.create_task(
                    context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
                )
                
                messages_sent += 1
                
                # Ultra-short delay between messages in burst
                if message_delay > 0:
                    await asyncio.sleep(message_delay * 0.5)  # 50% faster than calculated
            
            # PAUSE PHASE - Wait before next burst
            await asyncio.sleep(pause_time)
            
        except Exception as e:
            if "Too Many Requests" in str(e):
                await asyncio.sleep(8)  # Longer wait on flood
            else:
                await asyncio.sleep(3)  # Shorter wait on other errors

async def enhanced_smart_zero_delay_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """SMART ZERO DELAY - Maximum speed without freezing"""
    message_count = 0
    error_count = 0
    max_messages_before_pause = 50
    
    while attacking_single.get(chat_id) == target:
        try:
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            
            # FIRE AND FORGET - send without waiting
            asyncio.create_task(
                context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            )
            
            message_count += 1
            error_count = 0  # Reset error count
            
            # SMART PAUSE: Every 50 messages, add 10ms pause to avoid flood
            if message_count >= max_messages_before_pause:
                message_count = 0
                await asyncio.sleep(0.01)  # 10ms pause every 50 messages
            else:
                # ACTUAL ZERO DELAY - 0.001s is practically zero
                await asyncio.sleep(0.001)
                
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            if "Too Many Requests" in error_msg or "flood" in error_msg:
                print(f"🚨 Flood detected (expected), waiting...")
                wait_time = extract_wait_time(error_msg)
                print(f"⏳ Smart recovery: {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
                # Reduce speed slightly after flood
                max_messages_before_pause = max(30, max_messages_before_pause - 10)
                error_count = 0
            else:
                # Brief pause for other errors
                if error_count > 3:
                    await asyncio.sleep(2.0)
                else:
                    await asyncio.sleep(0.5)

async def ultimatezerodelay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ULTIMATE ZERO DELAY - True zero with instant recovery"""
    if await check_lock_and_notify(update, context, "ultimatezerodelay"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ultimatezerodelay")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
    
    # ULTIMATE ZERO DELAY
    set_attack_mode(update.effective_chat.id, "ultimatezerodelay")
    
    await update.message.reply_text(
        "🌀 **ULTIMATE ZERO DELAY ACTIVATED!**\n\n"
        "🚀 **Delay:** 0.0 seconds (True Zero)\n"
        "💥 **Speed:** ABSOLUTE MAXIMUM\n"
        "🛡️ **Recovery:** INSTANT after flood\n"
        "⚡ **Performance:** No freezing, instant resume\n\n"
        "*True zero delay with instant recovery system!*",
        parse_mode="Markdown"
    )

async def ultimate_zero_delay_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ULTIMATE ZERO DELAY - True zero with instant recovery"""
    flood_detected = False
    
    while attacking_single.get(chat_id) == target:
        try:
            # If we just recovered from flood, wait a moment
            if flood_detected:
                flood_detected = False
                await asyncio.sleep(0.5)  # Brief pause after recovery
            
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            
            # TRUE ZERO DELAY - fire and forget
            asyncio.create_task(
                context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            )
            
            # ACTUAL ZERO DELAY - no sleep at all
            await asyncio.sleep(0)
            
        except Exception as e:
            error_msg = str(e)
            
            if "Too Many Requests" in error_msg or "flood" in error_msg:
                if not flood_detected:
                    print("🌀 Ultimate zero: Flood detected, instant recovery activated")
                    flood_detected = True
                
                wait_time = extract_wait_time(error_msg)
                print(f"🌀 Ultimate recovery: {wait_time}s wait")
                await asyncio.sleep(wait_time)
                
                # INSTANT RESUME - no speed reduction
                flood_detected = False
            else:
                # Minimal pause for other errors
                await asyncio.sleep(0.1)

async def zerodelay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ZERO DELAY - Maximum speed (may freeze)"""
    if await check_lock_and_notify(update, context, "zerodelay"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/zerodelay")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
    
    # ZERO DELAY MODE
    set_attack_mode(update.effective_chat.id, "zero_delay")
    
    await update.message.reply_text(
        "⚡ **ZERO DELAY MODE ACTIVATED!**\n\n"
        "🚀 **Delay:** 0.0 seconds\n"
        "💥 **Speed:** Maximum possible\n"
        "⚠️ **Warning:** May cause temporary freezing\n"
        "🔄 **Auto-Recovery:** Basic flood protection\n\n"
        "*Use with caution - fastest but unstable!*",
        parse_mode="Markdown"
    )

async def enhanced_zero_delay_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ZERO DELAY ATTACK - Maximum speed with basic flood protection"""
    message_count = 0
    error_count = 0
    
    while attacking_single.get(chat_id) == target:
        try:
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            
            # FIRE AND FORGET - send without waiting
            asyncio.create_task(
                context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            )
            
            message_count += 1
            error_count = 0  # Reset error count
            
            # ACTUAL ZERO DELAY - no sleep at all
            await asyncio.sleep(0)
            
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            
            if "Too Many Requests" in error_msg or "flood" in error_msg:
                print(f"🚨 Flood detected in zero delay, waiting...")
                wait_time = extract_wait_time(error_msg) or 8
                print(f"⏳ Zero delay recovery: {wait_time} seconds")
                await asyncio.sleep(wait_time)
                error_count = 0
            else:
                # Brief pause for other errors
                if error_count > 2:
                    await asyncio.sleep(1.0)
                else:
                    await asyncio.sleep(0.2)

# ---------------- OPTIMIZED MEMBER CACHING ----------------
async def auto_cache_chat_members(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        chat_key = str(chat_id)
        
        if chat_key in member_cache:
            last_updated = member_cache[chat_key].get("last_updated", "")
            if last_updated:
                try:
                    last_dt = datetime.fromisoformat(last_updated)
                    if (datetime.now() - last_dt).total_seconds() < 1200:
                        return
                except:
                    pass

        logging.info(f"Auto-caching members for chat {chat_id}")
        members_dict = {}
        admin_ids = set()
        bot_ids = set()
        
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            for member in admins:
                admin_ids.add(member.user.id)
                if member.user.is_bot:
                    bot_ids.add(member.user.id)
        except Exception:
            return
        
        member_count = 0
        try:
            all_members = []
            offset = 0
            while True:
                members_chunk = await context.bot.get_chat_members(chat_id, offset=offset)
                if not members_chunk:
                    break
                all_members.extend(members_chunk)
                offset += len(members_chunk)
                if len(members_chunk) < 100:
                    break
            
            for member in all_members:
                user = member.user
                if user.id in admin_ids or user.id in bot_ids or user.is_bot:
                    continue
                    
                members_dict[str(user.id)] = {
                    "first_name": user.first_name or "",
                    "username": user.username or "",
                    "last_name": user.last_name or "",
                    "cached_at": datetime.now().isoformat()
                }
                member_count += 1
                
                if user.username:
                    username_to_userid[(chat_id, user.username.lower())] = user.id
        except Exception:
            pass
        
        if member_count > 0:
            member_cache[chat_key] = {
                "members": members_dict,
                "total_members": member_count,
                "admins_excluded": len(admin_ids),
                "bots_excluded": len(bot_ids),
                "last_updated": datetime.now().isoformat(),
                "auto_cached": True
            }
            
            asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))
            update_stats("members_cached", chat_id, increment=member_count)
        
    except Exception:
        pass

async def update_member_cache_on_activity(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user):
    """Update member cache on ALL user activity"""
    if not user or user.is_bot:
        return
        
    chat_key = str(chat_id)
    
    # Initialize cache for this chat if not exists
    if chat_key not in member_cache:
        member_cache[chat_key] = {
            "members": {},
            "total_members": 0,
            "last_updated": datetime.now().isoformat(),
            "auto_cached": False
        }
    
    user_key = str(user.id)
    current_time = datetime.now().isoformat()
    
    # Get current member status
    member_status = "member"
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        member_status = member.status
    except:
        pass
    
    # Update or create entry
    if user_key not in member_cache[chat_key]["members"]:
        # New user
        member_cache[chat_key]["members"][user_key] = {
            "first_name": user.first_name or "",
            "username": user.username or "",
            "last_name": user.last_name or "",
            "status": member_status,
            "cached_at": current_time,
            "last_activity": current_time,
            "activity_count": 1
        }
        member_cache[chat_key]["total_members"] = len(member_cache[chat_key]["members"])
    else:
        # Update existing
        member_cache[chat_key]["members"][user_key].update({
            "first_name": user.first_name or member_cache[chat_key]["members"][user_key].get("first_name", ""),
            "username": user.username or member_cache[chat_key]["members"][user_key].get("username", ""),
            "last_name": user.last_name or member_cache[chat_key]["members"][user_key].get("last_name", ""),
            "status": member_status,
            "last_activity": current_time,
            "activity_count": member_cache[chat_key]["members"][user_key].get("activity_count", 0) + 1
        })
    
    # Update username cache
    if user.username:
        username_to_userid[(chat_id, user.username.lower())] = user.id
    
    member_cache[chat_key]["last_updated"] = current_time
    
    # Throttled save (only 10% of calls)
    if random.random() < 0.1:
        asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))

def get_cached_members_count(chat_id: int) -> int:
    chat_key = str(chat_id)
    if chat_key in member_cache:
        return len(member_cache[chat_key].get("members", {}))
    return 0

def get_cached_members(chat_id):
    """
    Return ONLY members cached for this specific chat_id.
    Prevents cross-chat contamination.
    """
    chat_key = str(chat_id)

    if chat_key not in member_cache:
        return []

    members = member_cache[chat_key].get("members", {})

    # Ensure we only return list of IDs for THIS chat
    return [int(uid) for uid in members.keys()]


def clean_member_cache():
    global member_cache
    cleaned = {}

    for chat_key, data in member_cache.items():
        if not isinstance(data, dict):
            continue

        members = data.get("members", {})
        clean_members = {}

        for uid, m in members.items():
            # keep only valid user entries
            if isinstance(m, dict) and ("first_name" in m or "username" in m):
                clean_members[uid] = m

        cleaned[chat_key] = {
            "members": clean_members,
            "total_members": len(clean_members),
            "last_updated": data.get("last_updated"),
            "auto_cached": data.get("auto_cached", False)
        }

    member_cache = cleaned
    asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))

# ---------------- SECURITY LOGGING (OPTIMIZED) ----------------

def log_security_event(event_type: str, details: Dict[str, Any]):
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "details": details
    }
    security_log.append(event)
    if len(security_log) > 1000:
        security_log.pop(0)
    asyncio.create_task(fast_data.buffered_save(SECURITY_LOG_FILE, security_log))

def log_unauthorized_attempt(details: Dict[str, Any]):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "details": details
    }
    unauthorized_log.append(entry)
    if len(unauthorized_log) > 200:
        unauthorized_log.pop(0)
    asyncio.create_task(fast_data.buffered_save(UNAUTHORIZED_LOG_FILE, unauthorized_log))


# ---------------- ENHANCED GHOST SYSTEM ----------------
async def enhanced_ghost_delete(context: ContextTypes.DEFAULT_TYPE, msg: Message):
    """ULTRA FAST GHOST DELETION"""
    try:
        # Immediate deletion attempt
        await msg.delete()
        update_stats("ghosted_messages", msg.chat.id, msg.from_user.id)
    except Exception as e:
        # If deletion fails, try to hide the message by editing
        try:
            await context.bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text="🗑️",
                parse_mode="Markdown"
            )
        except Exception:
            pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ဒီစာကြောင်းကို ထည့်ပေးပါ (သင့် bot ရဲ့ Username ကို ရေးပါ)
    CrucialXNgaZenBot = "NexusOverLordBot"
    user = update.effective_user
    bot_username = context.bot.username

    # --- ဒီ code တွေ အကုန်လုံးက function ရဲ့ အတွင်းထဲမှာ ရှိနေရပါမယ် (Indent လုပ်ရပါမယ်) ---
    
    # 1. Typewriter effect စာသား
    intro_text = "𝓗𝓮𝓵𝓵𝓸 မင်္ဂလာပါ တောသား"
    msg = await update.message.reply_text("<i>...</i>", parse_mode="HTML")

    # Typewriter animation
    current_text = ""
    for i in range(0, len(intro_text), 4):
        current_text += intro_text[i:i+4]
        try:
            await msg.edit_text(f"<b><i>{current_text}</i></b>", parse_mode="HTML")
            await asyncio.sleep(0.10)
        except:
            pass

    # 2. 5 Seconds Wait
    await asyncio.sleep(1)
    try:
        await msg.delete()
    except:
        pass

    # 3. Final Text with Quote
    safe_name = html.escape(user.first_name or "User")
    mention = f'<a href="tg://user?id={user.id}">{safe_name}</a>'
    
    final_text = (
        f"<blockquote>𝓗𝓮𝓵𝓵𝓸 {mention} လောကနံပါတ်တစ် ဆရာသခင်ဒရိတ်ဘော့ ကိုအသုံးပြုသည့်အတွက် ဒရိတ် မှ အထူးပင်ကျေးဇူးတင်ရှိပါသည် Bot Permission များကို Channel ၌ Rules အတိုင်း လာရောက် တောင်းယူပါ</blockquote>"
    )

    # 4. Keyboard Layout
    keyboard = InlineKeyboardMarkup([
        [
            # CrucialXNgaZenBot က variable ဖြစ်ရင် bot_username ကို သုံးတာ ပိုစိတ်ချရပါတယ်
            InlineKeyboardButton("Add Bot Your Group", url=f"https://t.me/{CrucialXNgaZenBot}?startgroup=true")
        ],
        [
            InlineKeyboardButton("Permission Channel", url="https://t.me/Drake_Permission"),
        ],
        [
            InlineKeyboardButton("Drake Group", url="https://t.me/GoldemSnow_Family"),
            InlineKeyboardButton("Drake Bot Owner",   url="https://t.me/Drake_Mal")
        ],
        [
            InlineKeyboardButton("Commandsများကြည့်ရန်", callback_data="start_about")
        ]
    ])

    await update.message.reply_text(final_text, parse_mode="HTML", reply_markup=keyboard)


async def start_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commands Button ကို နှိပ်ရင် ပေါ်မယ့် Callback"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "<blockquote><b>ဆရာခင်ဒရိတ်ရဲ့ Command များကြည့်ရန်</b>\n\n"
        "/help :ဆရာသခင်ဒရိတ်ရဲ့ Command \n"
        "/show :ဆရာခင်ဒရိတ်ရဲ့ Command \n"
        "/drake :ဆရာသခင်ဒရိတ်ရဲ့ Command \n\n"
        "ဆရာသခင်ဒရိတ်ဘော့owner: @Drake_Mal</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Permission Channel", url="https://t.me/Drake_Permission"),
            InlineKeyboardButton("ဘော့အသုံးပြုနည်းများ", callback_data="how_to_use")
        ]
    ])
    
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)


async def how_to_use_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """How to use bot Button ကို နှိပ်ရင် ပေါ်မယ့် Callback (With Typewriter)"""
    query = update.callback_query
    await query.answer()
    
    # 1. Typewriter Effect Text
    intro_text = "𝓗𝓮𝓵𝓵𝓸 ဘော့အသုံးပြုနည်းများကြည့်ရန်"
    
    current_text = ""
    for i in range(0, len(intro_text), 4):
        current_text += intro_text[i:i+4]
        try:
            await query.edit_message_text(f"<b><i>{current_text}</i></b>", parse_mode="HTML")
            await asyncio.sleep(0.1)
        except:
            pass
            
    # 2. Wait 5 Seconds
    await asyncio.sleep(2)
    
    # 3. Final Commands List with Quote (Duplicates ဖယ်ထားသည်)
    commands_text = (
        "<blockquote><b>ဆရာသခင်ဒရိတ်ဘော့ Command များ</b>\n\n"
        "/start - Bot စတင်ရန်\n"
        "/help - 1 မှ 100 အထိ Commands ကြည့်ရန်\n"
        "/show - 101 မှ 200 အထိ ကြည့်ရန်\n"
        "/crucial - 201 မှ 300 အထိ ကြည့်ရန်\n"
        "<b>Attack & Spam</b>\n"
        "/attack id - Target တစ်ဦးကို attack spam စတင်ရန်\n"
        "/multiple id1 id2 - Target အများအပြားကို တစ်ပြိုင်နက် Attack လုပ်ရန်\n"
        "/secret id - Target ရှိသော Group အားလုံးတွင် Secret Attack ပြုလုပ်ရန်\n"
        "/ultraattack id - Ultra Speed ဖြင့် Attack ပြုလုပ်ရန်\n"
        "/go - Reply ထောက်ပြီး Go Attack စတင်ရန်\n"
        "/stop - Single Attack ရပ်ရန်\n"
        "/ungo - Go Attack ရပ်ရန်\n"
        "/unsecret - Secret Attack ရပ်ရန်\n"
        "/stopall - ဤ Chat ရှိ Attack အားလုံး ရပ်ရန်\n"
        "/stopmegaspam - Mega Spam ရပ်ရန်\n"
        "<b>Speed & Modes</b>\n"
        "/setspeed 0.5 - Attack Delay သတ်မှတ်ရန်\n"
        "/mode - လက်ရှိ Attack Mode ကို ကြည့်ရှုရန်\n"
        "/fastest - အမြန်ဆုံး Speed (0.2s)\n"
        "/godspeed - God Speed (0.1s)\n"
        "/lightspeed - Light Speed (0.01s)\n"
        "/normal - ပုံမှန် Speed (0.3s)\n"
        "/slow - အနှေး Mode (1.5s)\n"
        "/burst - Burst Mode\n"
        "/hyperburst - Hyper Burst Mode\n"
        "/ultraburst - Ultra Burst Mode\n"
        "/zerodelay - Delay လုံးဝမရှိသော Mode\n"
        "/smartzerodelay - ဉာဏ်ကွန့်မြူးသည့် Zero Delay Mode\n"
        "<b>Combo & Trolls</b>\n"
        "/combo - Attack, Ghost, Troll Combo များ ရွေးချယ်ရန်\n"
        "/ghost id - Target ၏ စာများကို အလိုအလျောက် ဖျက်ရန်\n"
        "/troll id - Target စာပို့တိုင်း Bot က ပြန်၍ Echo လုပ်ရန်\n"
        "/stopghost - စာဖျက်တာပိတ်ရန်\n"
        "/stoptroll - Troll ရပ်ရန်\n"
        "/ghostall - Group Admin မဟုတ်သူများစာပို့ရင်ဖျက်ရန်\n"
        "/unghostall - စာလိုက်ဖျက်တာပိတ်ရန်\n"
        "<b>Replies & Mass Tags</b>\n"
        "/settarget id - Target စာပို့တိုင်း Auto-Reply ပြန်ရန်\n"
        "/reply id - Target စာပို့တိုင်း ၂ ကြိမ် Auto-Reply ပြန်ရန်\n"
        "/unreply - Auto-Reply ရပ်ရန်\n"
        "/add id1 id2 - Mass Tagging အတွက် Target များ စာရင်းသွင်းရန်\n"
        "/tag - စာရင်းသွင်းထားသော Target အားလုံးကို Mass Tag လုပ်ရန်\n"
        "/call - Group ထဲရှိ Member အားလုံးကို Mention ခေါ်ရန်\n\n"
        "<b>Group & Broadcast</b>\n"
        "/id - Reply လုပ်ပြီး Target Id ကြည့်ရန်\n"
        "/adm - Id (သို့) Reply Title ဖြင့် Group Adm ခန့်ရန်\n"
        "/linkon - Link/Post/Mention များပို့ရင်ဖျက်ရန်\n"
        "/linkoff - Link ဖျက်ခြင်းပိတ်ရန်\n"
        "<b>Moderation</b>\n"
        "/ban id - User ကို Ban ရန်\n"
        "/unban id - User ကို Unban ရန်\n"
        "/mute id - User ကို Mute ရန်\n"
        "/unmute id - User ကို Unmute ရန်\n"
        "/kick id - User ကို Kick ရန်\n"
        "/setwelcome - Welcome Message စိတ်ကြိုက်ရေးရန်\n"
        "/setgoodbye - Goodbye Message စိတ်ကြိုက်ရေးရန်</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Menu", callback_data="start_about")]
    ])    
    
    await query.edit_message_text(commands_text, parse_mode="HTML", reply_markup=keyboard)




# ================================================================================
# NEW ADDITIONS - paste before register_handlers
# ================================================================================
import base64
import urllib.parse
import uuid as uuid_lib
import string

# ---- Group Warn Data ----
WARNS_FILE = os.path.join(DATA_DIR, "warns.json")
warns_data: Dict[str, Dict[str, Any]] = load_json(WARNS_FILE, {})

BLACKLIST_FILE = os.path.join(DATA_DIR, "blacklist_users.json")
blacklist_data: Dict[str, list] = load_json(BLACKLIST_FILE, {})

WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist_users.json")
whitelist_data: Dict[str, list] = load_json(WHITELIST_FILE, {})

MONITOR_FILE = os.path.join(DATA_DIR, "monitor.json")
monitor_data: Dict[str, list] = load_json(MONITOR_FILE, {})

SPY_MODE_CHATS: set = set()
STEALTH_MODE_CHATS: set = set()
FREEZE_CHATS: set = set()
SILENT_CHATS: set = set()
PROTECTED_CHATS: set = set()
PATROL_CHATS: set = set()
ENABLED_CMDS: Dict[str, set] = {}
DISABLED_CMDS: Dict[str, set] = {}

sticker_data: Dict[str, list] = load_json(STICKERS_FILE, {})


# ---- Helper: is_group_admin ----
async def is_group_admin_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is a group admin OR bot owner."""
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None:
        return False
    if is_owner(user):
        return True
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


# ===============================================================
# GROUP ADMIN COMMANDS (Admin + Owner only)
# ===============================================================

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            user_id = int(context.args[0])
            name = context.args[0]
        except ValueError:
            name = context.args[0]
            user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
    if not user_id:
        await update.message.reply_text("❌ User ကို Reply (သို့) ID ပေးပါ။")
        return
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"👢 `{name}` ကို Kick လိုက်ပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Kick မအောင်မြင်ပါ: {e}")


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = str(update.effective_chat.id)
    user_id = None
    reason = "No reason"
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
        reason = " ".join(context.args) if context.args else "No reason"
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason"
    if not user_id:
        await update.message.reply_text("❌ User ကို Reply (သို့) ID ပေးပါ။")
        return
    uid = str(user_id)
    if chat_id not in warns_data:
        warns_data[chat_id] = {}
    if uid not in warns_data[chat_id]:
        warns_data[chat_id][uid] = []
    warns_data[chat_id][uid].append({"reason": reason, "time": datetime.now().isoformat()})
    count = len(warns_data[chat_id][uid])
    asyncio.create_task(fast_data.buffered_save(WARNS_FILE, warns_data))
    await update.message.reply_text(
        f"⚠️ `{name}` ကို Warn {count} ခုပေးလိုက်ပြီ။\n📋 အကြောင်းပြချက်: {reason}",
        parse_mode="Markdown"
    )
    if count >= 3:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            await context.bot.unban_chat_member(update.effective_chat.id, user_id)
            await update.message.reply_text(f"👢 Warn 3 ခုပြည့်သဖြင့် `{name}` ကို Kick လိုက်ပြီ။", parse_mode="Markdown")
            warns_data[chat_id][uid] = []
            asyncio.create_task(fast_data.buffered_save(WARNS_FILE, warns_data))
        except Exception:
            pass


async def unwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ကို Reply (သို့) ID ပေးပါ။")
        return
    uid = str(user_id)
    if chat_id in warns_data and uid in warns_data[chat_id] and warns_data[chat_id][uid]:
        warns_data[chat_id][uid].pop()
        asyncio.create_task(fast_data.buffered_save(WARNS_FILE, warns_data))
        await update.message.reply_text(f"✅ `{name}` ရဲ့ Warn တစ်ခုဖျက်ပြီ။", parse_mode="Markdown")
    else:
        await update.message.reply_text("ℹ️ Warn မရှိပါ။")


async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ကို Reply (သို့) ID ပေးပါ။")
        return
    uid = str(user_id)
    w = warns_data.get(chat_id, {}).get(uid, [])
    if not w:
        await update.message.reply_text(f"✅ `{name}` မှာ Warn မရှိပါ။", parse_mode="Markdown")
    else:
        lines = [f"{i+1}. {x['reason']} ({x['time'][:10]})" for i, x in enumerate(w)]
        await update.message.reply_text(
            f"```\n⚠️ {name} ရဲ့ Warns ({len(w)}/3)\n" + "\n".join(lines) + "\n```",
            parse_mode="Markdown"
        )


async def clearwarns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ကို Reply (သို့) ID ပေးပါ။")
        return
    uid = str(user_id)
    if chat_id in warns_data:
        warns_data[chat_id][uid] = []
        asyncio.create_task(fast_data.buffered_save(WARNS_FILE, warns_data))
    await update.message.reply_text(f"✅ `{name}` ရဲ့ Warns အားလုံးဖျက်ပြီ။", parse_mode="Markdown")


async def muteall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = update.effective_chat.id
    try:
        await context.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text("🔇 Group ကို Mute လုပ်ပြီ။ (Members အားလုံး)")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def unmuteall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat_id = update.effective_chat.id
    try:
        await context.bot.set_chat_permissions(chat_id, ChatPermissions(
            can_send_messages=True, can_send_polls=True,
            can_send_other_messages=True, can_add_web_page_previews=True,
            can_change_info=False, can_invite_users=True, can_pin_messages=False
        ))
        await update.message.reply_text("🔊 Group ကို Unmute လုပ်ပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def slowmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    if not context.args:
        await update.message.reply_text("Usage: /slowmode <seconds> (0 = off)\nExample: /slowmode 10")
        return
    try:
        sec = int(context.args[0])
        await context.bot.set_chat_slow_mode_delay(update.effective_chat.id, sec)
        msg = f"🐌 Slow Mode: {sec}s" if sec > 0 else "✅ Slow Mode ပိတ်ပြီ။"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Pin လုပ်မည့် Message ကို Reply ပေးပါ။")
        return
    try:
        notify = not (context.args and context.args[0].lower() == "silent")
        await context.bot.pin_chat_message(
            update.effective_chat.id,
            update.message.reply_to_message.message_id,
            disable_notification=not notify
        )
        await update.message.reply_text("📌 Message ကို Pin လုပ်ပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    try:
        if update.message.reply_to_message:
            await context.bot.unpin_chat_message(
                update.effective_chat.id,
                update.message.reply_to_message.message_id
            )
        else:
            await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("📌 Message ကို Unpin လုပ်ပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def groupinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    chat = update.effective_chat
    try:
        count = await context.bot.get_chat_member_count(chat.id)
        invite = await context.bot.export_chat_invite_link(chat.id) if chat.type != "private" else "N/A"
        info = f"""```
📊 GROUP INFO
━━━━━━━━━━━━━━━━━━━━━
🏷️  Name   : {chat.title}
🆔  ID     : {chat.id}
👥  Members: {count}
??  Type   : {chat.type}
🔗  Link   : {invite}
━━━━━━━━━━━━━━━━━━━━━
```"""
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def invitelink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    try:
        link = await context.bot.export_chat_invite_link(update.effective_chat.id)
        await update.message.reply_text(f"🔗 Invite Link: {link}")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def revokelink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    try:
        new_link = await context.bot.export_chat_invite_link(update.effective_chat.id)
        await update.message.reply_text(f"🔄 Link ပြောင်းပြီ။\n🔗 New Link: {new_link}")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    try:
        count = await context.bot.get_chat_member_count(update.effective_chat.id)
        await update.message.reply_text(f"👥 Members: **{count}**", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def kickall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await update.message.reply_text("❌ Bot Owner သာ သုံးနိုင်သည်။")
        return
    chat_id = update.effective_chat.id
    chat_key = str(chat_id)
    cached = get_cached_members(chat_key)
    if not cached:
        await update.message.reply_text("❌ Member Cache မရှိပါ။ /scan ကိုအရင်သုံးပါ။")
        return
    kicked = 0
    msg = await update.message.reply_text("⏳ Kicking all non-admins...")
    for uid_str, info in list(cached.items()):
        try:
            uid = int(uid_str)
            if uid == OWNER_CHAT_ID or uid in EXTRA_OWNER_IDS:
                continue
            member = await context.bot.get_chat_member(chat_id, uid)
            if member.status in ("administrator", "creator"):
                continue
            await context.bot.ban_chat_member(chat_id, uid)
            await context.bot.unban_chat_member(chat_id, uid)
            kicked += 1
            await asyncio.sleep(0.1)
        except Exception:
            pass
    await msg.edit_text(f"✅ {kicked} ဦးကို Kick ပြီ။")


async def setgroupname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setgroupname <name>")
        return
    new_name = " ".join(context.args)
    try:
        await context.bot.set_chat_title(update.effective_chat.id, new_name)
        await update.message.reply_text(f"✅ Group name ကို `{new_name}` ဟုပြောင်းပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def setdesc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    desc = " ".join(context.args) if context.args else ""
    try:
        await context.bot.set_chat_description(update.effective_chat.id, desc)
        await update.message.reply_text("✅ Group Description ပြောင်းပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for adm"""
    await adm_command(update, context)


async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for disadm"""
    await disadm_command(update, context)


async def antilink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for linkon/linkoff"""
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။")
        return
    if context.args and context.args[0].lower() == "off":
        await linkoff_command(update, context)
    else:
        await linkon_command(update, context)


# ===============================================================
# NEW ATTACK COMMANDS (aliases + new modes)
# ===============================================================

async def _start_fast_attack(update, context, mode_name, delay):
    """Generic fast attack starter."""
    if await check_lock_and_notify(update, context, mode_name):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, f"/{mode_name}")
        return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, delay)
    await update.message.reply_text(f"```\n💥 {mode_name.upper()} MODE ACTIVATED\n⚡ Delay: {delay}s\n```", parse_mode="Markdown")


async def ultraattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ultraattack"); return
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Usage: /ultraattack <target>"); return
    target = context.args[0]
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text(f"```\n🔱 ULTRA ATTACK → {target}\n⚡ MAXIMUM SPEED\n```", parse_mode="Markdown")
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    if uid:
        t = asyncio.create_task(enhanced_burst_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "ultra")] = t


async def nuke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/nuke"); return
    if not context.args:
        await update.message.reply_text("Usage: /nuke <target>"); return
    chat_id = update.effective_chat.id
    target = context.args[0]
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    await update.message.reply_text(f"```\n☢️ NUKE LAUNCHED → {disp}\n💣 MASS DESTRUCTION MODE\n```", parse_mode="Markdown")
    if uid:
        t = asyncio.create_task(enhanced_burst_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "nuke")] = t


async def turboattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.05)
    await update.message.reply_text("```\n🚀 TURBO ATTACK MODE ON\n```", parse_mode="Markdown")


async def blastattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "burst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n💥 BLAST ATTACK MODE ON\n```", parse_mode="Markdown")


async def xattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /xattack <target>"); return
    chat_id = update.effective_chat.id
    target = context.args[0]
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text(f"```\n❌ X-ATTACK → {disp}\n```", parse_mode="Markdown")
    if uid:
        t = asyncio.create_task(ultra_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "xattack")] = t


async def hyperattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "hyperburst")
    await update.message.reply_text("```\n⚡ HYPER ATTACK MODE ON\n```", parse_mode="Markdown")


async def superattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultraburst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🌟 SUPER ATTACK MODE ON\n```", parse_mode="Markdown")


async def stormattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🌪️ STORM ATTACK MODE ON\n```", parse_mode="Markdown")


async def shadowattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "smart")
    await update.message.reply_text("```\n👤 SHADOW ATTACK MODE ON\n```", parse_mode="Markdown")


async def fireattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🔥 FIRE ATTACK MODE ON\n```", parse_mode="Markdown")


async def killattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /killattack <target>"); return
    chat_id = update.effective_chat.id
    target = context.args[0]
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text(f"```\n💀 KILL ATTACK → {disp}\n```", parse_mode="Markdown")
    if uid:
        t = asyncio.create_task(enhanced_burst_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "kill")] = t


async def deathattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n💀 DEATH MODE ACTIVATED\n```", parse_mode="Markdown")


async def wipeattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultraburst")
    await update.message.reply_text("```\n🗑️ WIPE ATTACK MODE ON\n```", parse_mode="Markdown")


async def bombattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /bombattack <target>"); return
    chat_id = update.effective_chat.id
    target = context.args[0]
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text(f"```\n💣 BOMB ATTACK → {disp}\n```", parse_mode="Markdown")
    if uid:
        t = asyncio.create_task(enhanced_burst_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "bomb")] = t


async def strikeattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "burst")
    await set_delay_for_chat(chat_id, 0.1)
    await update.message.reply_text("```\n⚡ STRIKE ATTACK MODE ON\n```", parse_mode="Markdown")


async def laserattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🔴 LASER ATTACK MODE ON\n```", parse_mode="Markdown")


async def warattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /warattack <target>"); return
    chat_id = update.effective_chat.id
    target = context.args[0]
    uid, disp = await resolve_target_to_id_and_display(context, chat_id, target)
    set_attack_mode(chat_id, "hyperburst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text(f"```\n⚔️ WAR ATTACK → {disp}\n```", parse_mode="Markdown")
    if uid:
        t = asyncio.create_task(enhanced_burst_attack_loop(context, chat_id, target, disp))
        attack_tasks[(chat_id, "war")] = t


async def missileattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultimatezerodelay")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🚀 MISSILE ATTACK MODE ON\n```", parse_mode="Markdown")


# ===============================================================
# NEW SPEED COMMANDS
# ===============================================================

async def ludicrous_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.0)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await update.message.reply_text("```\n?? LUDICROUS SPEED - 0.0s delay\n```", parse_mode="Markdown")


async def warpspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.01)
    await update.message.reply_text("```\n🌌 WARP SPEED - 0.01s delay\n```", parse_mode="Markdown")


async def sonicspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.05)
    await update.message.reply_text("```\n💨 SONIC SPEED - 0.05s delay\n```", parse_mode="Markdown")


async def turbomode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "ultraburst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🏎️ TURBO MODE ON\n```", parse_mode="Markdown")


async def overdrive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "hyperburst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🔧 OVERDRIVE MODE ON\n```", parse_mode="Markdown")


async def rapidfire_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    set_attack_mode(chat_id, "burst")
    await set_delay_for_chat(chat_id, 0.0)
    await update.message.reply_text("```\n🔫 RAPID FIRE MODE ON\n```", parse_mode="Markdown")


async def blitzspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.02)
    await update.message.reply_text("```\n⚡ BLITZ SPEED - 0.02s delay\n```", parse_mode="Markdown")


async def maxspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.0)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await update.message.reply_text("```\n🏆 MAX SPEED - 0.0s delay\n```", parse_mode="Markdown")


async def plaidspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.0)
    set_attack_mode(chat_id, "ultimatezerodelay")
    await update.message.reply_text("```\n🌈 PLAID SPEED - BEYOND MAX\n```", parse_mode="Markdown")


async def supersonicspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    await set_delay_for_chat(chat_id, 0.03)
    await update.message.reply_text("```\n✈️ SUPERSONIC SPEED - 0.03s delay\n```", parse_mode="Markdown")


# ===============================================================
# FUN / RANDOM COMMANDS
# ===============================================================

ROAST_MSGS = [
    "မင်းကို ကြည့်ရတာ ဘဝ ကောင်းကောင်းမနေရဘူးဆိုတာ မျက်နှာပေါ်ကနေ သိသာနေတယ်။",
    "မင်းရဲ့ IQ က WiFi signal ထက် ပိုအားနည်းတယ်",
    "မင်းဖုန်းနဲ့ မင်း နှိုင်းရင် ဖုန်းကပိုတော်တယ်",
    "မင်းကိုတွေ့တိုင်း AI တောင် ကေးပြီးပြေးချင်တယ်",
    "မင်းမှာ Talent ရှိတယ် - ပတ်ဝန်းကျင်ကို Depression ဖြစ်စေတဲ့ Talent"
]

COMPLIMENT_MSGS = [
    "မင်းက တကယ်ကောင်းတဲ့ကောင်ပဲ 😊",
    "မင်းရဲ့ ကြိုးစားမှုကို ကျနော် အားကျတယ်",
    "မင်း ဒါလောက် ဦးနှောက်ကောင်းတာ မသိခဲ့ဘူး",
    "မင်းရဲ့ ကောင်းသောစိတ် နေ့တိုင်း ရှိနေပါစေ",
    "မင်းနဲ့ chat ရတာ အမြဲပျော်တယ်"
]

INSULT_MSGS = [
    "မင်းက Google Maps ထဲမှာပင် ပျောက်မယ်ဆိုတဲ့ level",
    "မင်းရဲ့ Brain က Screensaver mode ပဲ",
    "မင်းပြောတဲ့ Joke တွေက သူများကို Cry ဖြစ်စေတယ် - Laughter ကြောင့်မဟုတ်ဘဲ Pain ကြောင့်",
    "Error 404: Intelligence Not Found - မင်းကိုဆိုလိုတာ",
    "မင်းကို AI အဖြစ် Train မလုပ်ရဘူး - Data ညံ့လွန်းလို့"
]

MOCK_MSGS = [
    "ဟိတ်ဟိတ် 😂 မင်းဘာပြောနေတာလဲ",
    "ကြားလားသူများ 😂 ဒီကောင်ကြည့်ပေ",
    "😂😂😂 ဘယ်ကမည်",
    "LMAO 💀 ဘာဆိုလိုတာလဲ",
    "မင်းJoke လား real လား မသိတော့ 💀"
]

QUOTES = [
    "\"Don't watch the clock; do what it does. Keep going.\" - Sam Levenson",
    "\"Success is not final, failure is not fatal.\" - Churchill",
    "\"In the middle of every difficulty lies opportunity.\" - Einstein",
    "\"It always seems impossible until it's done.\" - Mandela",
    "\"The only way to do great work is to love what you do.\" - Steve Jobs"
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "How many programmers does it take to change a light bulb? None – it's a hardware problem.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why was the math book sad? Because it had too many problems.",
    "What do you call a fake noodle? An impasta!"
]

FACTS = [
    "🧠 Human brain has about 86 billion neurons.",
    "🌍 The Earth is about 4.5 billion years old.",
    "⚡ Lightning strikes Earth about 100 times per second.",
    "🐘 Elephants are the only animals that can't jump.",
    "🍯 Honey never expires - archaeologists found 3000-year-old honey in Egypt."
]

async def roast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔥 {random.choice(ROAST_MSGS)}")

async def compliment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✨ {random.choice(COMPLIMENT_MSGS)}")

async def insult_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"😈 {random.choice(INSULT_MSGS)}")

async def mock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        mocked = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        await update.message.reply_text(f"🙃 {mocked}")
    else:
        await update.message.reply_text(f"🤡 {random.choice(MOCK_MSGS)}")

async def gg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 GG WP! ကောင်းတဲ့ game ပဲ!")

async def rip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args) if context.args else "User"
    await update.message.reply_text(f"🪦 RIP {name}\n😔 F in the chat...")

async def oof_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😬 OOF! ဒါဆိုး")

async def yeet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "it"
    await update.message.reply_text(f"💨 YEET! {target} ကို ပစ်လိုက်ပြီ!")

async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sides = 6
    if context.args:
        try:
            sides = int(context.args[0])
        except:
            pass
    result = random.randint(1, sides)
    await update.message.reply_text(f"🎲 d{sides} rolled: **{result}**", parse_mode="Markdown")

async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["🪙 Heads", "🪙 Tails"])
    await update.message.reply_text(f"Flipping coin... {result}!")

async def ball8_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses = [
        "✅ Yes, definitely!", "✅ It is certain.", "✅ Without a doubt.",
        "❓ Ask again later.", "❓ Cannot predict now.", "❓ Reply hazy.",
        "❌ Don't count on it.", "❌ My sources say no.", "❌ Very doubtful."
    ]
    await update.message.reply_text(f"🎱 {random.choice(responses)}")

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💬 {random.choice(QUOTES)}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"😄 {random.choice(JOKES)}")

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📚 {random.choice(FACTS)}")

async def flip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"(╯°□°）╯︵ {''.join(reversed(' '.join(context.args))) if context.args else 'table'}")

async def choose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /choose option1 option2 option3..."); return
    choice = random.choice(context.args)
    await update.message.reply_text(f"🎯 ငါ ရွေးမယ်: **{choice}**", parse_mode="Markdown")

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    elif update.message.reply_to_message:
        await update.message.reply_text(update.message.reply_to_message.text or "")

async def shout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args).upper() + "!!!")

async def reversetext_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args)[::-1])
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        await update.message.reply_text(update.message.reply_to_message.text[::-1])

async def upper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else (
        update.message.reply_to_message.text if update.message.reply_to_message else "")
    await update.message.reply_text(text.upper() if text else "Text ပေးပါ")

async def lower_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else (
        update.message.reply_to_message.text if update.message.reply_to_message else "")
    await update.message.reply_text(text.lower() if text else "Text ပေးပါ")

async def wordcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else (
        update.message.reply_to_message.text if update.message.reply_to_message else "")
    if not text:
        await update.message.reply_text("Text ပေးပါ"); return
    words = len(text.split())
    chars = len(text)
    await update.message.reply_text(f"📝 Words: {words} | Chars: {chars}")

async def repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /repeat <times> <text>"); return
    try:
        times = min(int(context.args[0]), 10)
        text = " ".join(context.args[1:])
        await update.message.reply_text("\n".join([text] * times))
    except:
        await update.message.reply_text("Usage: /repeat <times> <text>")


# ===============================================================
# UTILITY COMMANDS
# ===============================================================

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = get_bot_uptime()
    await update.message.reply_text(f"```\n⏱️ Bot Uptime: {uptime}\n```", parse_mode="Markdown")

async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"```\n🤖 Bot Version: {VERSION}\n👑 Owner: {OWNER_USERNAME}\n```", parse_mode="Markdown")

async def botinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = get_bot_uptime()
    me = await context.bot.get_me()
    groups = len(seen_chats)
    users = len(private_users)
    info = f"""```
🤖 BOT INFORMATION
━━━━━━━━━━━━━━━━━━
📛 Name   : {me.first_name}
🆔 ID     : {me.id}
👤 User   : @{me.username}
📦 Version: {VERSION}
⏱️ Uptime : {uptime}
👥 Groups : {groups}
👤 Users  : {users}
━━━━━━━━━━━━━━━━━━
```"""
    await update.message.reply_text(info, parse_mode="Markdown")

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"```\n👤 Name: {user.full_name}\n🆔 ID: {user.id}\n@️ User: @{user.username or 'N/A'}\n```",
        parse_mode="Markdown"
    )

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /calc <expression>\nExample: /calc 2+2*5"); return
    expr = " ".join(context.args)
    try:
        safe_expr = re.sub(r'[^0-9+\-*/().% ]', '', expr)
        result = eval(safe_expr, {"__builtins__": {}})
        await update.message.reply_text(f"🧮 `{expr}` = **{result}**", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Expression မမှန်ပါ")

async def gettime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc)
    await update.message.reply_text(f"```\n🕐 UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n```", parse_mode="Markdown")

async def getdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc)
    await update.message.reply_text(f"```\n📅 Date: {now.strftime('%A, %B %d, %Y')}\n```", parse_mode="Markdown")

async def base64en_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /base64en <text>"); return
    text = " ".join(context.args)
    encoded = base64.b64encode(text.encode()).decode()
    await update.message.reply_text(f"🔐 Encoded:\n`{encoded}`", parse_mode="Markdown")

async def base64de_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /base64de <encoded>"); return
    try:
        decoded = base64.b64decode(" ".join(context.args)).decode()
        await update.message.reply_text(f"🔓 Decoded:\n`{decoded}`", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Invalid base64")

async def urlencode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /urlencode <text>"); return
    result = urllib.parse.quote(" ".join(context.args))
    await update.message.reply_text(f"🔗 URL Encoded:\n`{result}`", parse_mode="Markdown")

async def urldecode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /urldecode <text>"); return
    result = urllib.parse.unquote(" ".join(context.args))
    await update.message.reply_text(f"🔗 URL Decoded:\n`{result}`", parse_mode="Markdown")

async def genpass_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 16
    if context.args:
        try:
            length = min(int(context.args[0]), 64)
        except:
            pass
    chars = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choices(chars, k=length))
    await update.message.reply_text(f"🔑 Generated Password ({length}):\n`{password}`", parse_mode="Markdown")

async def genuuid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(uuid_lib.uuid4())
    await update.message.reply_text(f"🆔 UUID:\n`{uid}`", parse_mode="Markdown")

async def randomnum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    low, high = 1, 100
    if len(context.args) >= 2:
        try:
            low, high = int(context.args[0]), int(context.args[1])
        except:
            pass
    elif len(context.args) == 1:
        try:
            high = int(context.args[0])
        except:
            pass
    result = random.randint(low, high)
    await update.message.reply_text(f"🎲 Random ({low}-{high}): **{result}**", parse_mode="Markdown")

async def pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /pick item1, item2, item3"); return
    items = " ".join(context.args).split(",")
    items = [i.strip() for i in items if i.strip()]
    if not items:
        await update.message.reply_text("Items ပေးပါ"); return
    choice = random.choice(items)
    await update.message.reply_text(f"🎯 **{choice}** ရွေးလိုက်ပြီ!", parse_mode="Markdown")

async def checkuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    user_id = None
    if update.message.reply_to_message:
        u = update.message.reply_to_message.from_user
        user_id = u.id
        name = u.full_name
        username = u.username or "N/A"
    elif context.args:
        try:
            user_id = int(context.args[0])
        except:
            await update.message.reply_text("ID ပေးပါ"); return
        name = "Unknown"
        username = "N/A"
    if not user_id:
        await update.message.reply_text("User ကို Reply (သို့) ID ပေးပါ"); return
    chat_id = update.effective_chat.id
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        status = member.status
    except:
        status = "unknown"
    info = f"```\n👤 User Info\n🆔 ID: {user_id}\n📛 Name: {name}\n@ : @{username}\n📊 Status: {status}\n```"
    await update.message.reply_text(info, parse_mode="Markdown")

async def checkgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat = update.effective_chat
    try:
        count = await context.bot.get_chat_member_count(chat.id)
        info = f"```\n📊 Chat Info\n🆔 ID: {chat.id}\n📛 Name: {chat.title}\n📋 Type: {chat.type}\n👥 Members: {count}\n```"
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if update.message.reply_to_message:
        u = update.message.reply_to_message.from_user
        info = f"```\n🔍 WHOIS\n🆔 ID: {u.id}\n📛 Name: {u.full_name}\n@️ User: @{u.username or 'N/A'}\nLang: {u.language_code or 'N/A'}\nBot: {'Yes' if u.is_bot else 'No'}\n```"
        await update.message.reply_text(info, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ User ကို Reply ပေးပါ")


# ===============================================================
# MANAGEMENT COMMANDS
# ===============================================================

async def addblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try: user_id = int(context.args[0])
        except: user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ပေးပါ"); return
    if chat_id not in blacklist_data:
        blacklist_data[chat_id] = []
    if user_id not in blacklist_data[chat_id]:
        blacklist_data[chat_id].append(user_id)
        asyncio.create_task(fast_data.buffered_save(BLACKLIST_FILE, blacklist_data))
        await update.message.reply_text(f"⛔ `{name}` ကို Blacklist ထည့်ပြီ။", parse_mode="Markdown")
    else:
        await update.message.reply_text("ℹ️ Already in blacklist")

async def removeblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: user_id = int(context.args[0])
        except: return
    if user_id and chat_id in blacklist_data and user_id in blacklist_data[chat_id]:
        blacklist_data[chat_id].remove(user_id)
        asyncio.create_task(fast_data.buffered_save(BLACKLIST_FILE, blacklist_data))
        await update.message.reply_text("✅ Blacklist မှ ဖယ်ပြီ။")
    else:
        await update.message.reply_text("ℹ️ Not in blacklist")

async def listblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    bl = blacklist_data.get(chat_id, [])
    if not bl:
        await update.message.reply_text("```\n⛔ Blacklist ဗလာ\n```", parse_mode="Markdown")
    else:
        lines = [f"{i+1}. {uid}" for i, uid in enumerate(bl)]
        await update.message.reply_text(f"```\n⛔ BLACKLIST ({len(bl)})\n" + "\n".join(lines) + "\n```", parse_mode="Markdown")

async def clearblacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    blacklist_data[chat_id] = []
    asyncio.create_task(fast_data.buffered_save(BLACKLIST_FILE, blacklist_data))
    await update.message.reply_text("✅ Blacklist ဖျက်ပြီ။")

async def addwhitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try: user_id = int(context.args[0])
        except: user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ပေးပါ"); return
    if chat_id not in whitelist_data:
        whitelist_data[chat_id] = []
    if user_id not in whitelist_data[chat_id]:
        whitelist_data[chat_id].append(user_id)
        asyncio.create_task(fast_data.buffered_save(WHITELIST_FILE, whitelist_data))
        await update.message.reply_text(f"✅ `{name}` ကို Whitelist ထည့်ပြီ။", parse_mode="Markdown")

async def removewhitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: user_id = int(context.args[0])
        except: return
    if user_id and chat_id in whitelist_data and user_id in whitelist_data[chat_id]:
        whitelist_data[chat_id].remove(user_id)
        asyncio.create_task(fast_data.buffered_save(WHITELIST_FILE, whitelist_data))
        await update.message.reply_text("✅ Whitelist မှ ဖယ်ပြီ။")

async def listwhitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    wl = whitelist_data.get(chat_id, [])
    if not wl:
        await update.message.reply_text("```\n✅ Whitelist ဗလာ\n```", parse_mode="Markdown")
    else:
        lines = [f"{i+1}. {uid}" for i, uid in enumerate(wl)]
        await update.message.reply_text(f"```\n✅ WHITELIST ({len(wl)})\n" + "\n".join(lines) + "\n```", parse_mode="Markdown")

async def freeze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    FREEZE_CHATS.add(chat_id)
    await update.message.reply_text("```\n🧊 Group FROZEN - All commands disabled\n```", parse_mode="Markdown")

async def unfreeze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    FREEZE_CHATS.discard(chat_id)
    await update.message.reply_text("```\n✅ Group UNFROZEN\n```", parse_mode="Markdown")

async def silent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    SILENT_CHATS.add(chat_id)
    await update.message.reply_text("```\n🔇 Silent Mode ON - Bot won't respond\n```", parse_mode="Markdown")

async def unsilent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    SILENT_CHATS.discard(chat_id)
    await update.message.reply_text("```\n🔊 Silent Mode OFF\n```", parse_mode="Markdown")

async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    import io, zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for fname in os.listdir(DATA_DIR):
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.isfile(fpath):
                z.write(fpath, fname)
    buf.seek(0)
    await update.message.reply_document(
        document=buf,
        filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        caption="✅ Data Backup"
    )

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    export_data = {
        "groups": len(seen_chats),
        "users": len(private_users),
        "admins": list(ADMIN_IDS),
        "stats": stats_data.get("global", {})
    }
    import io
    buf = io.BytesIO(json.dumps(export_data, indent=2, ensure_ascii=False).encode())
    buf.name = "export.json"
    await update.message.reply_document(document=buf, filename="export.json", caption="📊 Export Data")

async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။"); return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ ဖျက်မည့် Message ကို Reply ပေးပါ"); return
    count = 0
    start_id = update.message.reply_to_message.message_id
    end_id = update.message.message_id
    msg = await update.message.reply_text("⏳ Purging...")
    for msg_id in range(start_id, end_id + 1):
        try:
            await context.bot.delete_message(update.effective_chat.id, msg_id)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    try:
        await msg.edit_text(f"```\n🗑️ {count} messages ဖျက်ပြီ\n```", parse_mode="Markdown")
    except:
        pass

async def resetstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    global stats_data
    stats_data["global"] = {k: 0 for k in stats_data["global"]}
    asyncio.create_task(fast_data.buffered_save(STATS_FILE, stats_data))
    await update.message.reply_text("```\n✅ Stats Reset ပြီ\n```", parse_mode="Markdown")

async def clearlog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    global security_log, unauthorized_log, watch_log
    security_log = []
    unauthorized_log = []
    watch_log = []
    asyncio.create_task(fast_data.buffered_save(SECURITY_LOG_FILE, security_log))
    asyncio.create_task(fast_data.buffered_save(UNAUTHORIZED_LOG_FILE, unauthorized_log))
    asyncio.create_task(fast_data.buffered_save(WATCH_LOG_FILE, watch_log))
    await update.message.reply_text("```\n✅ All Logs Cleared\n```", parse_mode="Markdown")


# ===============================================================
# MONITOR/SPY/CONTROL COMMANDS
# ===============================================================

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try: user_id = int(context.args[0])
        except: user_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
        name = context.args[0]
    if not user_id:
        await update.message.reply_text("❌ User ပေးပါ"); return
    if chat_id not in monitor_data:
        monitor_data[chat_id] = []
    if user_id not in monitor_data[chat_id]:
        monitor_data[chat_id].append(user_id)
        asyncio.create_task(fast_data.buffered_save(MONITOR_FILE, monitor_data))
    await update.message.reply_text(f"```\n👁️ {name} ကို Monitor ထည့်ပြီ\n```", parse_mode="Markdown")

async def unmonitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: user_id = int(context.args[0])
        except: return
    if user_id and chat_id in monitor_data and user_id in monitor_data[chat_id]:
        monitor_data[chat_id].remove(user_id)
        asyncio.create_task(fast_data.buffered_save(MONITOR_FILE, monitor_data))
        await update.message.reply_text("✅ Monitor ဖယ်ပြီ")

async def monitorlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    ml = monitor_data.get(chat_id, [])
    if not ml:
        await update.message.reply_text("```\n👁️ Monitor List ဗလာ\n```", parse_mode="Markdown")
    else:
        lines = [f"{i+1}. ID: {uid}" for i, uid in enumerate(ml)]
        await update.message.reply_text(f"```\n👁️ MONITOR LIST ({len(ml)})\n" + "\n".join(lines) + "\n```", parse_mode="Markdown")

async def spymode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    SPY_MODE_CHATS.add(chat_id)
    await update.message.reply_text("```\n🕵️ SPY MODE ON - Logging all messages\n```", parse_mode="Markdown")

async def stopspymode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    SPY_MODE_CHATS.discard(chat_id)
    await update.message.reply_text("```\n✅ SPY MODE OFF\n```", parse_mode="Markdown")

async def stealthmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    STEALTH_MODE_CHATS.add(chat_id)
    await update.message.reply_text("```\n👻 STEALTH MODE ON\n```", parse_mode="Markdown")

async def stopstealthmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    STEALTH_MODE_CHATS.discard(chat_id)
    await update.message.reply_text("```\n✅ STEALTH MODE OFF\n```", parse_mode="Markdown")

async def observe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for watch"""
    await watch_command(update, context)

async def unobserve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for unwatch"""
    await unwatch_command(update, context)

async def patrol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    PATROL_CHATS.add(chat_id)
    await update.message.reply_text("```\n?? PATROL MODE ON - Monitoring group\n```", parse_mode="Markdown")

async def stoppatrol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = update.effective_chat.id
    PATROL_CHATS.discard(chat_id)
    await update.message.reply_text("```\n✅ PATROL MODE OFF\n```", parse_mode="Markdown")

async def enable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /enable <command>"); return
    chat_id = str(update.effective_chat.id)
    cmd = context.args[0].lstrip("/")
    if chat_id in DISABLED_CMDS:
        DISABLED_CMDS[chat_id].discard(cmd)
    await update.message.reply_text(f"```\n✅ /{cmd} ကို Enable ပြီ\n```", parse_mode="Markdown")

async def disable_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /disable <command>"); return
    chat_id = str(update.effective_chat.id)
    cmd = context.args[0].lstrip("/")
    if chat_id not in DISABLED_CMDS:
        DISABLED_CMDS[chat_id] = set()
    DISABLED_CMDS[chat_id].add(cmd)
    await update.message.reply_text(f"```\n❌ /{cmd} ကို Disable ပြီ\n```", parse_mode="Markdown")

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    lang = context.args[0] if context.args else "mm"
    await update.message.reply_text(f"```\n🌐 Language set to: {lang}\n```", parse_mode="Markdown")

async def setmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for mode"""
    await mode_command(update, context)

async def getmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    info = get_attack_mode_info()
    await update.message.reply_text(f"```\n⚙️ Current Mode Info\n{info[:500]}\n```", parse_mode="Markdown")

async def getinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for stats"""
    await stats_command(update, context)

async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        info = f"""```
💻 SYSTEM INFO
━━━━━━━━━━━━━━━━━━━━
CPU  : {cpu:.1f}%
RAM  : {mem.percent:.1f}% ({mem.used//1024//1024}MB/{mem.total//1024//1024}MB)
DISK : {disk.percent:.1f}% used
━━━━━━━━━━━━━━━━━━━━
```"""
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ===============================================================
# BROADCAST EXTRAS
# ===============================================================

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast to all tracked groups - alias for sendall"""
    await sendall_command(update, context)
async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick notify to all users"""
    if not is_authorized(update.effective_user): return
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /notify <message>"); return
    text = " ".join(context.args) if context.args else update.message.reply_to_message.text
    sent = 0
    for uid_str, udata in list(private_users.items()):
        try:
            await context.bot.send_message(int(uid_str), f"📢 Notice:\n{text}")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await update.message.reply_text(f"```\n📢 Notified {sent} users\n```", parse_mode="Markdown")

async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /alert <message>"); return
    text = " ".join(context.args)
    await update.message.reply_text(f"```\n🚨 ALERT: {text}\n```", parse_mode="Markdown")
    for cid_str in list(seen_chats.keys()):
        try:
            await context.bot.send_message(int(cid_str), f"🚨 **ALERT**\n{text}", parse_mode="Markdown")
            await asyncio.sleep(0.1)
        except:
            pass

async def massping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping all groups"""
    if not is_authorized(update.effective_user): return
    count = 0
    msg = await update.message.reply_text("⏳ Pinging all groups...")
    for cid_str in list(seen_chats.keys()):
        try:
            await context.bot.send_message(int(cid_str), "🏓 Ping!")
            count += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await msg.edit_text(f"```\n🏓 Pinged {count} groups\n```", parse_mode="Markdown")


# ===============================================================
# STICKER COMMANDS
# ===============================================================

async def savesticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Sticker ကို Reply ပေးပါ"); return
    name = context.args[0] if context.args else f"sticker_{len(sticker_data)}"
    file_id = update.message.reply_to_message.sticker.file_id
    chat_id = str(update.effective_chat.id)
    if chat_id not in sticker_data:
        sticker_data[chat_id] = {}
    sticker_data[chat_id][name] = file_id
    asyncio.create_task(fast_data.buffered_save(STICKERS_FILE, sticker_data))
    await update.message.reply_text(f"```\n✅ Sticker saved as: {name}\n```", parse_mode="Markdown")

async def getsticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /getsticker <name>"); return
    name = context.args[0]
    chat_id = str(update.effective_chat.id)
    file_id = sticker_data.get(chat_id, {}).get(name)
    if file_id:
        await update.message.reply_sticker(file_id)
    else:
        await update.message.reply_text(f"❌ '{name}' ဆိုသော sticker မရှိပါ")

async def liststickers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    stickers = sticker_data.get(chat_id, {})
    if not stickers:
        await update.message.reply_text("```\n🗒️ Stickers ဗလာ\n```", parse_mode="Markdown")
    else:
        lines = [f"{i+1}. {name}" for i, name in enumerate(stickers.keys())]
        await update.message.reply_text(f"```\n🗒️ STICKERS ({len(stickers)})\n" + "\n".join(lines) + "\n```", parse_mode="Markdown")

async def removesticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    if not context.args:
        await update.message.reply_text("Usage: /removesticker <name>"); return
    name = context.args[0]
    chat_id = str(update.effective_chat.id)
    if chat_id in sticker_data and name in sticker_data[chat_id]:
        del sticker_data[chat_id][name]
        asyncio.create_task(fast_data.buffered_save(STICKERS_FILE, sticker_data))
        await update.message.reply_text(f"```\n✅ '{name}' ဖျက်ပြီ\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ '{name}' မရှိပါ")

async def clearstickers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    chat_id = str(update.effective_chat.id)
    sticker_data[chat_id] = {}
    asyncio.create_task(fast_data.buffered_save(STICKERS_FILE, sticker_data))
    await update.message.reply_text("```\n✅ Stickers အားလုံးဖျက်ပြီ\n```", parse_mode="Markdown")

async def stickerinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Sticker ကို Reply ပေးပါ"); return
    s = update.message.reply_to_message.sticker
    info = f"""```
🗒️ STICKER INFO
━━━━━━━━━━━━━━━━━━
File ID  : {s.file_id[:30]}...
Set Name : {s.set_name or 'N/A'}
Emoji    : {s.emoji or 'N/A'}
Width    : {s.width}
Height   : {s.height}
Animated : {'Yes' if s.is_animated else 'No'}
Video    : {'Yes' if s.is_video else 'No'}
━━━━━━━━━━━━━━━━━━
```"""
    await update.message.reply_text(info, parse_mode="Markdown")


# ===============================================================
# UPDATED HELP / SHOW / NGAZEN COMMANDS
# ===============================================================


# ---------------- COMPLETE HELP COMMAND ----------------

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "help"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/help")
        return

    text = """```
═══════════ COMMANDS (1-100) ══════════
👑 OWNER / ADMIN SYSTEM
/owner <u>      - Owner ထည့်
/removeowner <u>- Owner ဖြုတ်
/gang           - Owner List
/add_admin <u>  - Admin ထည့်
/remove_admin   - Admin ဖြုတ်
/list_admins    - Admin List
/limit <u> <t>  - Temp Admin
/limitlist      - Limit List
/limitcommand   - Command Limit
/on <pass>      - Bot Reclaim

⚔️ CORE ATTACK
/attack <t>     - Attack လုပ်
/stop           - Attack ရပ်
/stopall        - Attack အားလုံးရပ်
/multiple <..>  - Multi Attack
/stopmultiple   - Multi ရပ်
/qa <t>         - Quick Attack
/quickattack <t>- Quick Attack
/go             - Reply Attack
/ungo           - Reply ရပ်
/megaspam <t>   - MegaSpam (50)
/stopmegaspam   - MegaSpam ရပ်
/secret <t>     - Secret Attack
/unsecret       - Secret ရပ်
/attackuser <t> - Username Attack
/stopuser       - Username ရပ်

💥 NEW ATTACK MODES
/ultraattack <t>- Ultra Attack
/nuke <t>       - Nuke Attack
/xattack <t>    - X Attack
/killattack <t> - Kill Attack
/bombattack <t> - Bomb Attack
/warattack <t>  - War Attack
/turboattack    - Turbo Mode
/blastattack    - Blast Mode
/hyperattack    - Hyper Mode
/superattack    - Super Mode
/stormattack    - Storm Mode
/shadowattack   - Shadow Mode
/fireattack     - Fire Mode
/deathattack    - Death Mode
/wipeattack     - Wipe Mode
/laserattack    - Laser Mode
/strikeattack   - Strike Mode
/missileattack  - Missile Mode

⚡ SPEED CONTROLS
/setspeed <s>   - Speed သတ်မှတ်
/mode <m>       - Mode ရွေး
/fastest        - Fastest
/godspeed       - God Speed
/ultragodspeed  - Ultra God
/newgodrebornspeed - New God
/flashspeed     - Flash
/lightspeed     - Light
/hyperspeed     - Hyper
/instantspeed   - Instant
/normal         - Normal
/slow           - Slow
/burst          - Burst
/hyperburst     - HyperBurst
/ultraburst     - UltraBurst
/normalmode     - Normal Mode
/zerodelay      - Zero Delay
/smartzerodelay - Smart Zero
/ultimatezerodelay - UltimateZero
/smartattack    - Smart Attack
/fastspeed      - Fast Speed

🚀 NEW SPEEDS
/ludicrous      - Ludicrous Speed
/warpspeed      - Warp Speed
/sonicspeed     - Sonic Speed
/turbomode      - Turbo Mode
/overdrive      - Overdrive
/rapidfire      - Rapid Fire
/blitzspeed     - Blitz Speed
/maxspeed       - Max Speed
/plaidspeed     - Plaid Speed
/supersonicspeed- Supersonic
════════════════════════════════
ဒရိတ်ဘော့ပြိုင်ဆိုင်ရှား
```"""
    await update.message.reply_text(text, parse_mode="Markdown")



async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "show"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/show")
        return

    text = """```
═══════════ COMMANDS (101-200) ═════════
🎯 TARGETING & TROLLING
/add <t>        - Target ထည့်
/tag            - Target Tag
/stoptag        - Tag ရပ်
/settarget <t>  - Auto Reply Target
/stopxsettarget - Auto Reply ရပ်
/funny <t1><t2> - Dual Troll
/stopfunny      - Troll ရပ်
/troll <t>      - Troll Mode
/stoptroll      - Troll ရပ်
/ghost <t>      - Ghost Delete
/stopghost      - Ghost ရပ်
/ghostall       - GhostAll
/unghostall     - GhostAll ရပ်
/reply <t>      - Auto Reply
/unreply        - Reply ရပ်
/combo          - Combo Attack
/stopcombo      - Combo ရပ်

🔇 GROUP MODERATION
/ban <t>        - Ban User
/unban <t>      - Unban
/mute <t>       - Mute User
/unmute <t>     - Unmute
/adm <t>        - Give Admin
/disadm <t>     - Remove Admin
/settitle <t>   - Set Title
/out            - Kick All Cache
/linkon         - Link Block ON
/linkoff        - Link Block OFF
/banword <w>    - Ban Word
/removeword <w> - Remove Word
/listword       - Word List
/setwelcome     - Welcome MSG
/welcomeoff     - Welcome OFF
/scan           - Scan Members
/cleanmembercache- Clean Cache

🛡️ GROUP ADMIN COMMANDS (Admin Only)
/kick <t>       - Kick User
/warn <t>       - Warn User
/unwarn <t>     - Remove Warn
/warns <t>      - View Warns
/clearwarns <t> - Clear Warns
/slowmode <s>   - Slow Mode
/pin            - Pin Message
/unpin          - Unpin Message
/promote <t>    - Promote Admin
/demote <t>     - Demote Admin
/groupinfo      - Group Info
/invitelink     - Invite Link
/revokelink     - Revoke Link
/members        - Member Count
/kickall        - Kick All (Owner)
/setgroupname   - Set Group Name
/setdesc        - Set Description
/antilink       - Anti Link Toggle

📡 BROADCAST
/send <g>       - Send to Group
/senduser <u>   - Send to User
/sendall        - Send All Groups
/announce <n>   - Announce
/broadcast      - Broadcast All
/notify         - Notify Users
/alert <msg>    - Alert All
/massping       - Ping All Groups
/call           - Mention All
/stopcall       - Call ရပ်
/gpspam <g>     - Group Spam
/stopgp         - GP Spam ရပ်
/fight <g>      - Fight Broadcast

🔍 WATCH & STATS
/watch <t>      - Watch User
/unwatch <t>    - Unwatch
/watchlist      - Watch List
/watchlog       - Watch Log
/stats          - Statistics
/ping           - Ping Bot
/performance    - Performance
/speedtest      - Speed Test
════════════════════════════════
ဒရိတ်ဘော့ပြိုင်ဆိုင်ရှား
```"""
    await update.message.reply_text(text, parse_mode="Markdown")



async def ngazen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "hyperion"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/hyperion")
        return

    text = """```
═══════════ COMMANDS (201-300) ═════════
🛠️ UTILITY
/id             - Get Target ID
/myid           - My ID
/uptime         - Bot Uptime
/version        - Bot Version
/botinfo        - Bot Info
/calc <expr>    - Calculator
/gettime        - Current Time
/getdate        - Current Date
/base64en <t>   - Base64 Encode
/base64de <t>   - Base64 Decode
/urlencode <t>  - URL Encode
/urldecode <t>  - URL Decode
/genpass <n>    - Gen Password
/genuuid        - Generate UUID
/randomnum      - Random Number
/checkuser <u>  - Check User
/checkgroup     - Check Group
/whois          - Who Is User
/sysinfo        - System Info

🔐 MANAGEMENT
/addblacklist   - Blacklist Add
/removeblacklist- Blacklist Remove
/listblacklist  - Blacklist View
/clearblacklist - Blacklist Clear
/addwhitelist   - Whitelist Add
/removewhitelist- Whitelist Remove
/listwhitelist  - Whitelist View
/freeze         - Freeze Group
/unfreeze       - Unfreeze Group
/silent         - Silent Mode
/unsilent       - Silent OFF
/monitor <t>    - Monitor User
/unmonitor <t>  - Unmonitor
/monitorlist    - Monitor List
/spymode        - Spy Mode ON
/stopspymode    - Spy Mode OFF
/stealthmode    - Stealth ON
/stopstealthmode- Stealth OFF
/patrol         - Patrol ON
/stoppatrol     - Patrol OFF
/observe <t>    - Observe (Watch)
/unobserve <t>  - Unobserve

🎞️ STICKERS
/savesticker <n>- Save Sticker
/getsticker <n> - Get Sticker
/liststickers   - Sticker List
/removesticker  - Remove Sticker
/clearstickers  - Clear All

⚙️ SYSTEM & SECURITY
/lock <cmd>     - Lock Command
/unlock <cmd>   - Unlock
/lockallchat    - Lock All Chat
/unlockallchat  - Unlock All
/security_log   - Security Log
/security_clear - Clear Log
/unauthorized_log- Unauth Log
/reload         - Reload Data
/reloadgroups   - Reload Groups
/reloadusers    - Reload Users
/cleanupusers   - Cleanup Users
/backup         - Backup Data
/export         - Export Data
/clearlog       - Clear Logs
/resetstats     - Reset Stats
/purge          - Purge Messages
/enable <cmd>   - Enable Cmd
/disable <cmd>  - Disable Cmd
/setlang        - Set Language
/setmode        - Set Mode
/getmode        - Get Mode
/getinfo        - Get Info

🔬 AI & TOOLS
/ai <text>      - AI Chat
/aicheck <text> - AI Detect
/translate <u>  - Translate
/topic          - AI Topics
/TikTok <url>   - TikTok DL
/tracklocation  - Track Location
/locationscan   - Location Scan
/name <u> <n>   - Set Nickname
/emptyname      - Clear Names
/add_reply      - Add Reply
/delreply       - Del Reply
/listreplies    - Reply List
/filter <k><r>  - Add Filter
/removefilter   - Remove Filter
/filterlist     - Filter List
/emptyfilter    - Clear Filters
/listgroup      - List Groups
/availablegroups- Available GPs
/availableusers - Available Users
/new <id>       - New Group
/migrate        - Migrate Group
/note           - Save Note
/destroy <u>    - Report User
/report         - Report
/delete         - Nuclear Delete
/shutdown       - Shutdown Bot
/whyfail        - Debug
/test           - Test
════════════════════════════════
ဒရိတ်ဘော့ပြိုင်ဆိုင်ရှား
```"""
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------------- SECRET ATTACK SYSTEM ----------------
async def secret_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SECRET ATTACK - Spam target in ALL shared groups"""
    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        # Show current secret attacks
        if not secret_targets:
            await update.message.reply_text(
                "🔐 **SECRET ATTACK SYSTEM**\n\n"
                "**Usage:** `/secret @user` or `/secret user_id`\n"
                "**Stop:** `/unsecret @user`\n\n"
                "**Effect:** Spams target in EVERY shared group simultaneously\n"
                "**Speed:** Uses current attack speed (check with /setspeed)",
                parse_mode="Markdown"
            )
        else:
            attacks_list = []
            for target_id, display in secret_targets.items():
                group_count = len(secret_attacks.get(target_id, {}))
                attacks_list.append(f"• {display} - {group_count} groups")
            
            await update.message.reply_text(
                "🔐 **Active Secret Attacks:**\n\n" +
                "\n".join(attacks_list) +
                "\n\nUse `/unsecret @user` to stop specific attack\n"
                "Use `/unsecret` to stop ALL secret attacks",
                parse_mode="Markdown"
            )
        return

    target_arg = context.args[0]
    chat_id = update.effective_chat.id

    # Check if target is owner (reverse attack protection)
    if owner_matches_target(target_arg):
        attacker_id = update.effective_user.id
        await update.message.reply_text("🛡️ Reverse attack protection activated!")
        return

    # Resolve target
    target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
    if not target_id:
        await update.message.reply_text(f"❌ Could not resolve target: {target_arg}")
        return

    # Check if already being secret attacked
    if target_id in secret_attacks:
        await update.message.reply_text(
            f"⚠️ {display} is already being secret attacked!\n"
            f"Use `/unsecret {target_arg}` to stop first.",
            parse_mode="Markdown"
        )
        return

    # Find shared groups with target
    shared_groups = await find_shared_groups_with_target(context, target_id)
    
    if not shared_groups:
        await update.message.reply_text(
            f"❌ No shared groups found with {display}\n"
            f"Bot and target must be in the same groups.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"🔍 Scanning for shared groups with {display}...",
        parse_mode="Markdown"
    )

    # Start secret attack in all shared groups
    successful_starts = 0
    secret_attacks[target_id] = {}
    secret_targets[target_id] = display

    for group_chat_id in shared_groups:
        try:
            # Get proper mention for THIS specific group
            group_display = await get_mention_for_target(context, group_chat_id, str(target_id))
            
            # Start attack in this group
            task = asyncio.create_task(
                secret_attack_loop(context, group_chat_id, target_id, group_display)
            )
            secret_attacks[target_id][group_chat_id] = task
            successful_starts += 1
            
        except Exception as e:
            print(f"❌ Failed to start secret attack in group {group_chat_id}: {e}")
            continue

    # Get current attack speed for display
    current_speed = attack_delay.get(chat_id, DEFAULT_DELAY)

    await update.message.reply_text(
        f"🎯 **SECRET ATTACK DEPLOYED!**\n\n"
        f"• Target: {display}\n"
        f"• Active Groups: {successful_starts}\n"
        f"• Speed: {current_speed}s\n"
        f"• Status: **ACTIVE** 🟢\n\n"
        f"Target is being mentioned in {successful_starts} groups where they are present\n"
        f"Use `/unsecret {target_arg}` to stop",
        parse_mode="Markdown"
    )

async def find_shared_groups_with_target(context: ContextTypes.DEFAULT_TYPE, target_id: int) -> List[int]:
    """Find all groups where both bot and target are members - FIXED VERSION"""
    shared_groups = []
    
    print(f"🔍 Searching for shared groups with target {target_id}")
    print(f"📊 Total known groups: {len(seen_chats)}")
    
    # Check all known groups
    for chat_id_str in list(seen_chats.keys()):
        try:
            chat_id = int(chat_id_str)
            
            # Skip if chat_id is the same as target_id (user chat)
            if chat_id == target_id:
                continue
                
            print(f"🔍 Checking group {chat_id_str}: {seen_chats[chat_id_str].get('title', 'Unknown')}")
            
            # Check if target is member of this group
            try:
                member = await context.bot.get_chat_member(chat_id, target_id)
                if member.status in ['member', 'administrator', 'creator']:
                    print(f"✅ Target found in group {chat_id_str}")
                    shared_groups.append(chat_id)
                else:
                    print(f"❌ Target status in group {chat_id_str}: {member.status}")
            except Exception as e:
                print(f"❌ Target not in group {chat_id_str}: {e}")
                continue
                
        except Exception as e:
            print(f"❌ Error checking group {chat_id_str}: {e}")
            continue
    
    print(f"🎯 Found {len(shared_groups)} shared groups with target {target_id}")
    return shared_groups    
    print(f"🔍 Found {len(shared_groups)} shared groups with target {target_id}")
    return shared_groups

async def secret_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target_id: int, display: str):
    """Secret attack loop for individual group - WITH PROPER MENTIONS"""
    consecutive_success = 0
    
    while target_id in secret_attacks and chat_id in secret_attacks.get(target_id, {}):
        try:
            # Use the current attack delay from your existing system
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
            
            # Get fresh mention for this group (in case it changes)
            try:
                current_display = await get_mention_for_target(context, chat_id, str(target_id))
            except:
                current_display = display  # Fallback to original
            
            line = random.choice(attack_replies) if attack_replies else "Secret attack!"
            text_to_send = f"{current_display} {line}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=text_to_send,
                parse_mode="Markdown"
            )
            
            consecutive_success += 1
            # Adaptive speed - gets faster if successful (respects setspeed limits)
            adaptive_delay = max(0.1, current_delay * (0.95 ** min(consecutive_success, 10)))
            
            await asyncio.sleep(adaptive_delay)
            
        except Exception as e:
            consecutive_success = 0
            
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                await asyncio.sleep(10)
            elif "Chat not found" in str(e) or "bot was kicked" in str(e):
                # Remove this group from secret attack
                if target_id in secret_attacks and chat_id in secret_attacks[target_id]:
                    secret_attacks[target_id].pop(chat_id, None)
                break
            elif "user not found" in str(e).lower() or "user not participant" in str(e).lower():
                # Target left this group, remove it
                if target_id in secret_attacks and chat_id in secret_attacks[target_id]:
                    secret_attacks[target_id].pop(chat_id, None)
                break
            else:
                await asyncio.sleep(2)

async def unsecret_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop secret attack on target"""
    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        # Stop ALL secret attacks
        if not secret_targets:
            await update.message.reply_text("❌ No active secret attacks.")
            return
        
        total_stopped = 0
        target_count = len(secret_targets)
        
        for target_id in list(secret_targets.keys()):
            stopped = await stop_secret_attack(target_id)
            total_stopped += stopped
        
        await update.message.reply_text(
            f"🛑 **ALL SECRET ATTACKS STOPPED**\n\n"
            f"• Targets: {target_count}\n"
            f"• Groups stopped: {total_stopped}\n"
            f"• Status: **INACTIVE** 🔴",
            parse_mode="Markdown"
        )
        return

    target_arg = context.args[0]
    chat_id = update.effective_chat.id

    # Resolve target
    target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
    if not target_id:
        await update.message.reply_text(f"❌ Could not resolve target: {target_arg}")
        return

    # Stop secret attack for this target
    stopped_groups = await stop_secret_attack(target_id)

    if stopped_groups > 0:
        await update.message.reply_text(
            f"🛑 **SECRET ATTACK STOPPED**\n\n"
            f"• Target: {display}\n"
            f"• Groups: {stopped_groups}\n"
            f"• Status: **INACTIVE** 🔴",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"❌ No active secret attack for {display}")

async def stop_secret_attack(target_id: int) -> int:
    """Stop all secret attacks for a target across all groups"""
    stopped_count = 0
    
    if target_id in secret_attacks:
        # Cancel all attack tasks for this target
        for chat_id, task in secret_attacks[target_id].items():
            if task and not task.done():
                try:
                    task.cancel()
                    stopped_count += 1
                except Exception:
                    pass
        
        # Remove from tracking
        secret_attacks.pop(target_id, None)
        secret_targets.pop(target_id, None)
    
    return stopped_count

#----------------- control bot ---------------

async def mentioning_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all groups currently using attack/tag/spam commands with proper mentions"""
    if await check_lock_and_notify(update, context, "mentioning"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/mentioning")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    active_attacks = []
    
    # 1. Collect Single Attacks (These usually contain Links)
    for chat_id, target in attacking_single.items():
        display = attacking_single_display.get(chat_id, "Unknown")
        active_attacks.append({
            "chat_id": chat_id,
            "type": "🔥 Single Attack",
            "target": display,
            "status": "ACTIVE"
        })
    
    # 2. Collect Multiple Attacks (Usually plain text like "5 targets")
    for chat_id, targets in attacking_multiple.items():
        displays = attacking_multiple_displays.get(chat_id, ["Unknown"])
        # If it's a list of names, join them. If many, show count.
        target_display = " ".join(displays) if len(displays) <= 3 else f"{len(targets)} targets"
        active_attacks.append({
            "chat_id": chat_id,
            "type": "💥 Multiple Attack", 
            "target": target_display,
            "status": "ACTIVE"
        })
    
    # 3. Collect Tag Attacks
    for chat_id in added_targets:
        if attack_tasks.get(("tag", chat_id)):
            targets = added_targets[chat_id]
            target_count = len(targets)
            active_attacks.append({
                "chat_id": chat_id,
                "type": "🏷️ Mass Tag",
                "target": f"{target_count} targets",
                "status": "ACTIVE"
            })
            
    # 4. Collect Smart Attacks
    for chat_id, smart_data in smart_attacks.items():
        if attack_tasks.get(("smart", chat_id)):
            display = smart_data.get('display', 'Unknown')
            active_attacks.append({
                "chat_id": chat_id,
                "type": "🧠 Smart Attack",
                "target": display,
                "status": "ACTIVE"
            })
            
    # 5. Collect Attack User
    for chat_id, task in active_attack_tasks.items():
        if task and not task.done():
             active_attacks.append({
                "chat_id": chat_id,
                "type": "👤 Attack User",
                "target": "Username spam",
                "status": "ACTIVE"
            })

    if not active_attacks:
        await update.message.reply_text(
            "ℹ️ *လက်ရှိ Active Attack မရှိပါ*\n\n"
            "လက်ရှိတွင် ဘယ် Group မှ Attack, Tag, Spam Command များ မရှိပါ။",
            parse_mode="MarkdownV2"
        )
        return

    # Group attacks by chat_id
    attacks_by_chat = {}
    for attack in active_attacks:
        chat_id = attack["chat_id"]
        # Skip internal IDs like SECRET_
        if isinstance(chat_id, str) and chat_id.startswith("SECRET_"):
            continue
        if chat_id not in attacks_by_chat:
            attacks_by_chat[chat_id] = []
        attacks_by_chat[chat_id].append(attack)

    # --- BUILD RESPONSE ---
    header = escape_markdown_v2("🔊 လက်ရှိ Active ဖြစ်နေသော Attack များ")
    response = f"*{header}*\n\n"
    
    stats_text = escape_markdown_v2(f"Active Attacks: {len(active_attacks)} | Groups: {len(attacks_by_chat)}")
    response += f"📊 *{stats_text}*\n\n"

    for chat_id, attacks in attacks_by_chat.items():
        # Get Group Title
        group_info = seen_chats.get(str(chat_id), {})
        group_title = group_info.get('title', f'Group {chat_id}')
        
        # Escape the Group Title (Crucial for preventing errors)
        safe_title = escape_markdown_v2(group_title)
        
        response += f"🏠 *{safe_title}*\n"
        response += f"   🆔 `{chat_id}`\n"
        
        for attack in attacks:
            # Escape the Type
            safe_type = escape_markdown_v2(attack['type'])
            
            raw_target = str(attack['target'])
            
            # --- INTELLIGENT ESCAPING ---
            # If it looks like a Markdown Link [Name](tg://...), DON'T escape it again.
            if raw_target.startswith("[") and "](tg://" in raw_target:
                final_target = raw_target
            else:
                # If it's plain text (e.g., "5 targets", "@username"), ESCAPE IT.
                final_target = escape_markdown_v2(raw_target)
            
            response += f"   {safe_type} → {final_target}\n"
        
        response += "\n"

    # Add timestamp safely
    time_str = datetime.now().strftime('%H:%M:%S')
    safe_time = escape_markdown_v2(f"Last updated: {time_str}")
    response += f"⏰ {safe_time}"

    try:
        await update.message.reply_text(response, parse_mode="MarkdownV2")
    except Exception as e:
        # Fallback if something is still wrong, strip markdown
        print(f"❌ Mentioning Error: {e}")
        await update.message.reply_text(
            "⚠️ Error displaying fancy list. Showing plain text:\n\n" + 
            response.replace("*", "").replace("`", "").replace("\\", "")
        )


async def listgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show only total groups and admin groups count"""
    if await check_lock_and_notify(update, context, "listgroup"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/listgroup")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not seen_chats:
        await update.message.reply_text(
            "❌ <b>မှတ်တမ်းတင်ထားသော Group မရှိပါ</b>\n\n"
            "Group အသစ်များထည့်သွင်းရန် <code>/new</code> ကို Group ထဲတွင်အသုံးပြုပါ။",
            parse_mode="HTML"
        )
        return

    # Count admin groups (bot is admin)
    admin_groups_count = 0
    
    for chat_id_str in seen_chats.keys():
        try:
            chat_id = int(chat_id_str)
            # Check if bot is admin in this group
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status in ['administrator', 'creator']:
                admin_groups_count += 1
        except Exception:
            # Bot might not be in group or doesn't have access
            continue

    # Build simple response with only two counts
    response = "🏠 <b>GROUP STATISTICS</b>\n\n"
    response += f"📊 <b>gp အားလုံးပေါင်း -</b> ({len(seen_chats)})\n"
    response += f"🛡️ <b>adm ရရှိသော gp -</b> ({admin_groups_count})\n\n"
    response += f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    await update.message.reply_text(response, parse_mode="HTML")


async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spam target using Normal Markdown - REPLY ONLY"""
    if await check_lock_and_notify(update, context, "go"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/go")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "🚀 */go Command*\n\n"
            "*အသုံးပြုနည်း:* User ကို reply ပြန်ပြီး `/go` ရိုက်ပါ\n"
            "*Target ကို Proper Mention နှင့် Spam ရိုက်ပေးမည်*",
            parse_mode="Markdown"
        )
        return

    chat_id = update.effective_chat.id
    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id
    
    # Reverse protection
    if owner_matches_target(str(target_id)) or owner_matches_target(target_user.username):
        attacker_id = update.effective_user.id
        await reverse_attack_owner(context, chat_id, attacker_id, "go")
        return

    # 1. Get Nickname (if args exist) or Real Name
    if context.args:
        # Use provided nickname
        raw_name = " ".join(context.args)
    else:
        # Use Real Name
        raw_name = target_user.first_name or f"User{target_id}"

    # 2. Escape name for Normal Markdown
    safe_name = escape_markdown_v1(raw_name)
    
    # 3. Create Mention string: [Name](tg://user?id=123)
    target_display = f"[{safe_name}](tg://user?id={target_id})"

    # Stop any existing attack
    prev = attack_tasks.get(("single", chat_id))
    if prev and not prev.done():
        try: prev.cancel()
        except: pass

    # Start new attack
    attacking_single[chat_id] = str(target_id)
    attacking_single_display[chat_id] = target_display
    
    attack_tasks[("single", chat_id)] = asyncio.create_task(
        optimizer.process_attack(go_attack_loop(context, chat_id, str(target_id), target_display))
    )

    await update.message.reply_text(
        f"သခင့်အလိုကျဖာသယ်မသားကိုဖင်စတင်လိုးပါတော့မယ် \n\n"
        
    )
    update_stats("attacks_started", chat_id, update.effective_user.id)

async def go_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """GO attack loop using Normal Markdown (Stable)"""
    consecutive_success = 0
    
    while attacking_single.get(chat_id) == target:
        try:
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)
            if current_delay in [0.2, 1, 1.5, 2]:
                await show_typing_action(context, chat_id)

            # Get Random Line
            line = random.choice(attack_replies) if attack_replies else "Get rekt."
            
            # Escape the line for Normal Markdown (just in case it has * or _)
            safe_line = escape_markdown_v1(line)
            
            # Normal Markdown doesn't care about '.' or '!'
            text_to_send = f"{display} {safe_line}"
            
            # Use 'Markdown' (V1), NOT 'MarkdownV2'
            await context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            
            consecutive_success += 1
            current_delay = max(0.1, attack_delay.get(chat_id, DEFAULT_DELAY) * (0.95 ** min(consecutive_success, 10)))
            
            await asyncio.sleep(current_delay)
            
        except Exception as e:
            consecutive_success = 0
            if "Too Many Requests" in str(e):
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(0.2)

async def ungo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop /go attack (Myanmar)"""
    if await check_lock_and_notify(update, context, "ungo"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ungo")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id
    
    # Stop /go attack (which uses single attack system)
    if chat_id in attacking_single:
        attacking_single.pop(chat_id, None)
        attacking_single_display.pop(chat_id, None)
        t = attack_tasks.get(("single", chat_id))
        if t and not t.done():
            try: 
                t.cancel()
            except: 
                pass
            attack_tasks.pop(("single", chat_id), None)
        
        await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")
    else:
        await update.message.reply_text("လက်ရှိနှိမ်နင်းထားခြင်းမရှိပါ")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-reply စနစ် - nickname နဲ့အလုပ်လုပ် - 2 ခါ reply ပို့"""
    if await check_lock_and_notify(update, context, "reply"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/reply")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(
            "📨 **Auto-Reply စနစ်**\n\n"
            "အသုံးပြုပုံ:\n"
            "• `/reply @username` - user အတွက် auto-reply စပါ\n"
            "• `/reply nickname` - nickname နဲ့သုံးပါ (/name နဲ့သတ်မှတ်ထားတာ)\n"
            "• message ကိုပြန်ပြီး `/reply` - ပြန်ထားတဲ့ user ကို auto-reply\n\n"
            "✅ **စပြီးတာနဲ့ 2 ခါ reply ပို့မယ်**\n"
            "✅ **nickname နဲ့အလုပ်လုပ်တယ်**\n"
            "✅ **နောက်ပိုင်း message တိုင်းကို auto-reply**\n\n"
            "ရပ်ရန်: `/unreply`",
            parse_mode="Markdown"
        )
        return

    chat_id = update.effective_chat.id
    target_id = None
    target_display = None

    if update.message.reply_to_message:
        # message ကိုပြန်ထားရင်
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        
        # nickname ရှိမရှိကြည့်
        nickname = name_map_intkey.get(target_id) or name_map.get(str(target_id))
        if nickname:
            user_name = nickname
        else:
            user_name = target_user.first_name or f"User{target_id}"
        
        safe_name = escape_markdown_v1(user_name)
        target_display = f"[{safe_name}](tg://user?id={target_id})"
        
    elif context.args:
        # argument နဲ့ပေးထားရင်
        target_arg = context.args[0]
        
        # owner ကိုပစ်နေလားစစ်
        if owner_matches_target(target_arg):
            attacker_id = update.effective_user.id
            await reverse_attack_owner(context, chat_id, attacker_id, "reply")
            return
        
        # UNIVERSAL RESOLUTION - nickname, ID, username အကုန်အလုပ်လုပ်
        target_id, target_display = await universal_resolve_target(context, chat_id, target_arg)
        
        if not target_id and not target_display:
            await update.message.reply_text(f"❌ user မတွေ့ပါ: {target_arg}")
            return

    if not target_id or not target_display:
        await update.message.reply_text("❌ user မတွေ့ပါ")
        return

    # ============================================
    # ချက်ချင်း REPLY 2 ခါပို့
    # ============================================
    try:
        # attack_replies ကနေ reply 2 ခုရွေး
        if attack_replies and len(attack_replies) >= 2:
            # မတူတဲ့ reply 2 ခုယူ
            replies = random.sample(attack_replies, 2)
        else:
            # မရရင် fallback
            replies = ["မင်းကိုပဲကြိုက်တယ်!", "ဘာလဲဟဲ့!"]
        
        # ဘယ် message ကိုပြန်ရမလဲဆုံးဖြတ်
        reply_to_msg_id = None
        if update.message.reply_to_message:
            reply_to_msg_id = update.message.reply_to_message.message_id
        elif update.message:
            reply_to_msg_id = update.message.message_id
            
        # REPLY 2 ခါပို့
        for i, reply_text in enumerate(replies):
            safe_reply = escape_markdown_v1(reply_text)
            full_text = f"{target_display} {safe_reply}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=full_text,
                parse_mode="Markdown",
                reply_to_message_id=reply_to_msg_id if i == 0 else None  # ပထမ reply ပဲ thread
            )
            
            # reply တွေကြားမှာ အချိန်အနည်းငယ်ခြား
            if i == 0:
                await asyncio.sleep(0.2)
                
    except Exception as e:
        print(f"❌ reply ပို့ချိန်အမှား: {e}")

    # ============================================
    # နောက်ပိုင်း MESSAGE တွေအတွက် AUTO-REPLY ထားရန်
    # ============================================
    chat_key = str(chat_id)
    if chat_key not in reply_targets:
        reply_targets[chat_key] = {}
    
    reply_targets[chat_key][str(target_id)] = {
        "target_id": target_id,
        "target_display": target_display,
        "set_by": update.effective_user.id,
        "set_by_name": update.effective_user.first_name,
        "set_at": datetime.now().isoformat(),
        "active": True
    }

    # file ထဲသိမ်း
    asyncio.create_task(fast_data.buffered_save(REPLY_TARGETS_FILE, reply_targets))

    await update.message.reply_text(
        f"✅ Auto-reply စပါပြီ {target_display}\n"
        f"📨 reply 2 ခါပို့ပြီးပြီ!\n"
        f"🔄 နောက်ပိုင်း message တိုင်း reply 2 ခါပို့မယ်\n"
        f"🛑 ရပ်ရန်: `/unreply`",
        parse_mode="Markdown"
    )

async def unreply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop auto-reply for targets - FIXED"""
    if await check_lock_and_notify(update, context, "unreply"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unreply")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id
    chat_key = str(chat_id)
    
    if not context.args:
        # Stop ALL auto-replies in this chat
        if chat_key in reply_targets and reply_targets[chat_key]:
            target_count = len(reply_targets[chat_key])
            reply_targets.pop(chat_key, None)
            asyncio.create_task(fast_data.buffered_save(REPLY_TARGETS_FILE, reply_targets))
            await update.message.reply_text(f"✅ Auto-reply {target_count} targets ကိုရပ်လိုက်ပါပြီ။")
        else:
            await update.message.reply_text("❌ လက်ရှိ Auto-reply မရှိပါ။")
        return

    # Stop specific target
    target_arg = context.args[0]
    target_id, target_display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
    
    if not target_id:
        await update.message.reply_text("❌ Target not found.")
        return

    if chat_key in reply_targets and str(target_id) in reply_targets[chat_key]:
        del reply_targets[chat_key][str(target_id)]
        # Remove chat entry if empty
        if not reply_targets[chat_key]:
            del reply_targets[chat_key]
        
        asyncio.create_task(fast_data.buffered_save(REPLY_TARGETS_FILE, reply_targets))
        await update.message.reply_text(f"✅ Auto-reply for {target_display} stopped.")
    else:
        await update.message.reply_text(f"❌ No auto-reply found for {target_display}")

async def reply_auto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-reply handler - message တစ်ခုဆို reply 2 ခါပို့"""
    if not update.message:
        return
        
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # bot ကိုမပြန်
    if update.effective_user.is_bot:
        return
        
    chat_key = str(chat_id)
    
    # auto-reply ဖွင့်ထားလားစစ်
    if chat_key not in reply_targets:
        return
        
    if str(user_id) not in reply_targets[chat_key]:
        return
        
    target_data = reply_targets[chat_key][str(user_id)]
    if not target_data.get("active", True):
        return
    
    try:
        # user အကြောင်း
        user_name = update.effective_user.first_name or f"User{user_id}"
        
        # nickname ရှိမရှိကြည့်
        nickname = name_map_intkey.get(user_id) or name_map.get(str(user_id))
        if nickname:
            user_name = nickname
        
        safe_name = escape_markdown_v1(user_name)
        target_display = f"[{safe_name}](tg://user?id={user_id})"
        
        # attack_replies ကနေ reply 2 ခုရွေး
        if attack_replies and len(attack_replies) >= 2:
            replies = random.sample(attack_replies, 2)
        else:
            replies = ["မင်းကိုပဲကြိုက်တယ်!", "ဘာလဲဟဲ့!"]
        
        # REPLY 2 ခါပို့
        for i, reply_text in enumerate(replies):
            safe_reply = escape_markdown_v1(reply_text)
            full_text = f"{target_display} {safe_reply}"
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=full_text,
                    parse_mode="Markdown",
                    reply_to_message_id=update.message.message_id if i == 0 else None
                )
                
                # reply တွေကြားမှာ အချိန်အနည်းငယ်ခြား
                if i < len(replies) - 1:
                    await asyncio.sleep(0.3)
                    
            except Exception as e:
                print(f"❌ auto-reply {i+1} ပို့ချိန်အမှား: {e}")
                continue
                
    except Exception as e:
        print(f"❌ auto-reply handler အမှား: {e}")

# ---------------- ATTACK COMMANDS ----------------
async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """COMPLETE ATTACK COMMAND - Unlimited targets, works everywhere"""
    if await check_lock_and_notify(update, context, "attack"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "attack"):
        await handle_unauthorized_access(update, context, "/attack")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        await update.message.reply_text("Usage: /attack @user (or multiple users)")
        return

    chat_id = update.effective_chat.id
    targets = []
    displays = []

    # Process UNLIMITED targets
    for target_str in context.args:
        if owner_matches_target(target_str):
            attacker_id = update.effective_user.id
            await reverse_attack_owner(context, chat_id, attacker_id, "attack")
            return

        # UNIVERSAL TARGET RESOLUTION
        target_arg = str(target_str).strip()
        target_id, display = await universal_resolve_target(context, chat_id, target_arg)
        
        if not display:
             # Fallback for plain text
             display = escape_markdown_v2(target_arg)

        # Ensure display is properly escaped for V2
        if "[" in display and "](tg://" in display:
             # It's a proper mention link, ensuring name inside is safe
             if target_id:
                 try:
                     member = await context.bot.get_chat_member(chat_id, target_id)
                     name = member.user.first_name
                 except:
                     name = f"User{target_id}"
                 safe_name = escape_markdown_v2(name)
                 display = f"[{safe_name}](tg://user?id={target_id})"
        else:
             # Plain text/username
             display = escape_markdown_v2(str(display).replace("@", "")) 
             if target_arg.startswith("@"):
                 display = f"@{display}"

        attack_target = str(target_id) if target_id else target_arg
        targets.append(attack_target)
        displays.append(display)

    # Stop previous attacks
    await stop_all_attacks(chat_id)

    # Start attack based on target count
    if len(targets) == 1:
        # SINGLE TARGET ATTACK
        attacking_single[chat_id] = targets[0]
        attacking_single_display[chat_id] = displays[0]
        
        # FIX: Use ultra_attack_loop to enable Burst/ZeroDelay modes
        attack_tasks[("single", chat_id)] = asyncio.create_task(
            optimizer.process_attack(ultra_attack_loop(context, chat_id, targets[0], displays[0]))
        )
    else:
        # MULTIPLE TARGETS ATTACK (Always uses multiple loop)
        attacking_multiple[chat_id] = targets
        attacking_multiple_displays[chat_id] = displays
        
        attack_tasks[("multiple", chat_id)] = asyncio.create_task(
            enhanced_multiple_loop(context, chat_id, targets, displays)
        )

    # Get attack speed
    current_speed = attack_delay.get(chat_id, DEFAULT_DELAY)
    
    # Fix the dot error: Escape speed string specifically for MarkdownV2
    safe_speed = escape_markdown_v2(str(current_speed))

    # --- MYANMAR TEXT SETUP ---
    if len(targets) == 1:
        target_display_str = displays[0]
        # Text for single target: "ခွေးမသား" ... "ကိုဖင်စတင်လိုးပါတော့မည်။"
        txt1 = escape_markdown_v2("ခွေးမသား")
        txt2 = escape_markdown_v2("ကိုဖင်စတင်လိုးပါတော့မည်။")
    else:
        target_display_str = " ".join(displays)
        if len(targets) > 5:
            target_display_str = f"{len(targets)} targets"
        # Text for multiple targets: "ခွေးမသားများ" ...
        txt1 = escape_markdown_v2("ခွေးမသားများ")
        txt2 = escape_markdown_v2("ကိုဖင်စတင်လိုးပါတော့မည်။")

    response_text = (
        f"သခင့်အလိုကျဖာသယ်မသားကိုဖင်စတင်လိုးပါတော့မယ် \n\n"
    )

    try:
        await update.message.reply_text(response_text, parse_mode="MarkdownV2")
    except:
        # Fallback if V2 still fails (replaces dot manually)
        await update.message.reply_text(response_text.replace(".", r"\."), parse_mode="Markdown")

    
    update_stats("attacks_started", chat_id, update.effective_user.id)


def get_attack_mode_info():
    """Get detailed information about current attack mode"""
    mode_info = {
        "normal": {
            "emoji": "🐢",
            "name": "NORMAL MODE",
            "speed": "0.3s delay",
            "rate": "~3 messages/second",
            "status": "Safe & Stable"
        },
        "burst": {
            "emoji": "💥", 
            "name": "BURST MODE",
            "speed": "10 messages/5s burst",
            "rate": "~2 messages/second",
            "status": "Balanced"
        },
        "hyperburst": {
            "emoji": "🚀",
            "name": "HYPER BURST MODE", 
            "speed": "25 messages/2s burst",
            "rate": "~12.5 messages/second",
            "status": "Very Fast"
        },
        "ultraburst": {
            "emoji": "🌀",
            "name": "ULTRA BURST MODE",
            "speed": "15 messages/1s burst", 
            "rate": "~15 messages/second",
            "status": "Maximum Burst"
        },
        "zero_delay": {
            "emoji": "⚡",
            "name": "ZERO DELAY MODE",
            "speed": "0.0 seconds",
            "rate": "Maximum possible",
            "status": "⚠️ May Freeze"
        },
        "smartzerodelay": {
            "emoji": "⚡", 
            "name": "SMART ZERO DELAY",
            "speed": "0.001s (practically zero)",
            "rate": "~1000 messages/second",
            "status": "Fast & Safe"
        },
        "ultimatezerodelay": {
            "emoji": "🌀",
            "name": "ULTIMATE ZERO DELAY",
            "speed": "0.0 seconds (true zero)", 
            "rate": "Absolute maximum",
            "status": "Instant Recovery"
        },
        "smart": {
            "emoji": "🧠",
            "name": "SMART ATTACK MODE",
            "speed": "Auto-adjusting (0.05s-2.0s)",
            "rate": "Adaptive",
            "status": "Intelligent"
        }
    }
    
    return mode_info.get(attack_mode, {
        "emoji": "🔥",
        "name": "UNKNOWN MODE", 
        "speed": "Unknown",
        "rate": "Unknown",
        "status": "Unknown"
    })
# ---------------- MEGA SPAM COMMAND ----------------
async def megaspam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """MEGA SPAM - Ultra fast spam with proper mentions"""
    if await check_lock_and_notify(update, context, "megaspam"):
        return
    if not is_authorized(update.effective_user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        await update.message.reply_text("Usage: /megaspam @user")
        return

    chat_id = update.effective_chat.id
    target_arg = context.args[0]
    
    # Check if already megaspamming in this chat
    if chat_id in megaspam_attacks:
        await update.message.reply_text("❌ Mega spam already active in this chat! Use /stopmegaspam to stop first.")
        return

    # Use the SAME method as attack command for proper mentions
    target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_arg)
    if not target_id:
        await update.message.reply_text("❌ Target not found")
        return

    # Check reverse attack protection
    if owner_matches_target(target_arg):
        attacker_id = update.effective_user.id
        await reverse_attack_owner(context, chat_id, attacker_id, "megaspam")
        return

    # Get plain name for the activation message (not the mention)
    plain_name = plain_name_from_mention(display)

    await update.message.reply_text(
        f"💥 **MEGA SPAM ACTIVATED!**\n"
        f"Target: {plain_name}\n"
        f"50 ultra-fast messages incoming...",
        parse_mode="Markdown"
    )

    # Start mega spam - use the SAME display format as attack command
    megaspam_attacks[chat_id] = asyncio.create_task(
        megaspam_attack_loop(context, chat_id, target_id, display)
    )

async def megaspam_attack_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target_id: int, display: str):
    """Mega spam attack loop with proper mentions"""
    message_count = 0
    
    while chat_id in megaspam_attacks and message_count < 50:
        try:
            line = random.choice(attack_replies) if attack_replies else "Mega spam!"
            text_to_send = f"{display} {line}"  # Use the SAME display format as attack
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=text_to_send,
                parse_mode="Markdown"
            )
            
            message_count += 1
            await asyncio.sleep(0.001)  # Ultra-fast delay
            
        except Exception as e:
            if "Too Many Requests" in str(e) or "flood" in str(e).lower():
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(0.2)
    
    # Clean up after loop ends
    if chat_id in megaspam_attacks:
        megaspam_attacks.pop(chat_id, None)
        try:
            await context.bot.send_message(chat_id=chat_id, text="✅ Mega spam completed!")
        except:
            pass

# ---------------- STOP MEGA SPAM COMMAND ----------------
async def stopmegaspam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop mega spam in current chat"""
    if await check_lock_and_notify(update, context, "stopmegaspam"):
        return
    
    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat_id = update.effective_chat.id
    
    if chat_id in megaspam_attacks:
        task = megaspam_attacks[chat_id]
        if task and not task.done():
            task.cancel()
        megaspam_attacks.pop(chat_id, None)
        await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")
    else:
        await update.message.reply_text("❌ No active mega spam in this chat.")


async def smartzerodelay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SMART ZERO DELAY - Maximum speed with anti-freeze"""
    if await check_lock_and_notify(update, context, "smartzerodelay"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/smartzerodelay")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
    
    # SMART ZERO DELAY - Uses 0.001s delay (practically zero)
    set_attack_mode(update.effective_chat.id, "smartzerodelay")
    await set_delay_for_chat(update.effective_chat.id, 0.001)  # 1ms delay
    
    await update.message.reply_text(
        "⚡ **SMART ZERO DELAY ACTIVATED!**\n\n"
        "🚀 **Speed:** 0.001s (1ms) - Practically Zero\n"
        "📊 **Rate:** ~1000 messages/second (theoretical)\n"
        "🛡️ **Anti-Freeze:** ACTIVE\n"
        "🔄 **Auto-Recovery:** ACTIVE\n\n"
        "*This is the FASTEST SAFE speed - won't freeze your bot!*",
        parse_mode="Markdown"
    )

async def multiple_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "multiple"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "multiple"):
        await handle_unauthorized_access(update, context, "/multiple")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    if not context.args:
        await update.message.reply_text("Usage: /multiple @user1 @user2 ...")
        return

    chat_id = update.effective_chat.id
    
    normalized = []
    displays = []
    for t in context.args:
        if owner_matches_target(t):
            attacker_id = update.effective_user.id
            await reverse_attack_owner(context, chat_id, attacker_id, "multiple")
            return
        
        target_id = await resolve_target_user_id(context, chat_id, t)
        if target_id:
            display = await get_mention_for_target(context, chat_id, str(target_id))
            normalized.append(str(target_id))
            displays.append(display)
        else:
            await update.message.reply_text(f"❌ Could not resolve target: {t}")
            return

    prev = attack_tasks.get(("multiple", chat_id))
    if prev and not prev.done():
        try: prev.cancel()
        except: pass

    attacking_multiple[chat_id] = normalized
    attacking_multiple_displays[chat_id] = displays
    attack_delay[chat_id] = attack_delay.get(chat_id, DEFAULT_DELAY)
    
    # USE ENHANCED MULTIPLE LOOP
    attack_tasks[("multiple", chat_id)] = asyncio.create_task(
        optimizer.process_attack(enhanced_multiple_loop(context, chat_id, normalized, displays))
    )

    await update.message.reply_text("🔥 Multiple attack started on " + ", ".join(displays), parse_mode="Markdown")
    update_stats("attacks_started", chat_id, update.effective_user.id)

async def fastspam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """10 MESSAGES FAST SPAM MODE"""
    if await check_lock_and_notify(update, context, "fastspam"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/fastspam")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
    
    burst_mode_config[update.effective_chat.id] = {
        'mode': 'fastspam10',
        'burst_count': 15,
        'burst_duration': 6.0,    # 10 messages over 5 seconds
        'pause_duration': 5.0     # 7 second pause
    }
    
    await update.message.reply_text(
        "⚡ **FAST SPAM MODE ACTIVATED**\n"
        "💥 15  messages in 6 seconds\n"
        "⏸️ 6 second pause\n"
        "📊 Speed: 0.83 msg/sec overall\n"
        
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stop"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "stop"):
        await handle_unauthorized_access(update, context, "/stop")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat = update.effective_chat
    if chat.id in attacking_single:
        attacking_single.pop(chat.id, None)
        attacking_single_display.pop(chat.id, None)
        t = attack_tasks.get(("single", chat.id))
        if t and not t.done():
            try: t.cancel()
            except: pass
            attack_tasks.pop(("single", chat.id), None)
    await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")

async def stopmultiple_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stopmultiple"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "stopmultiple"):
        await handle_unauthorized_access(update, context, "/stopmultiple")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat = update.effective_chat
    if chat.id in attacking_multiple:
        attacking_multiple.pop(chat.id, None)
        attacking_multiple_displays.pop(chat.id, None)
        t = attack_tasks.get(("multiple", chat.id))
        if t and not t.done():
            try: t.cancel()
            except: pass
            attack_tasks.pop(("multiple", chat.id), None)
    await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")

async def stopall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stopall"):
        return
    
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "stopall"):
        await handle_unauthorized_access(update, context, "/stopall")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return

    chat = update.effective_chat
    
    # Stop SMART attacks
    if chat.id in smart_attacks:
        smart_attacks.pop(chat.id, None)
        t = attack_tasks.get(("smart", chat.id))
        if t and not t.done():
            try: t.cancel()
            except: pass
            attack_tasks.pop(("smart", chat.id), None)
    
    # Stop single attacks (your existing code)
    if chat.id in attacking_single: 
        attacking_single.pop(chat.id, None)
        attacking_single_display.pop(chat.id, None)
        t = attack_tasks.get(("single", chat.id))
        if t and not t.done():
            try: t.cancel()
            except: pass
            attack_tasks.pop(("single", chat.id), None)
    
    # Stop multiple attacks (your existing code)
    if chat.id in attacking_multiple: 
        attacking_multiple.pop(chat.id, None)
        attacking_multiple_displays.pop(chat.id, None)
        t = attack_tasks.get(("multiple", chat.id))
        if t and not t.done():
            try: t.cancel()
            except: pass
            attack_tasks.pop(("multiple", chat.id), None)
    
    # Your existing ghost, troll, die_config cleanup...
    ghost_map.pop(chat.id, None)
    troll_map.pop(chat.id, None)
    cfg = die_configs.get(str(chat.id))
    if cfg:
        cfg["active"] = False
        die_configs[str(chat.id)] = cfg
        asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
    combo_states.pop(chat.id, None)
    
    await update.message.reply_text("ခွေးမသားအားလုံးငြိမ်းချမ်းစေ")

async def quickattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick attack last target - /qa or /quickattack"""
    if await check_lock_and_notify(update, context, "quickattack"):
        return
        
    user = update.effective_user
    if not is_authorized(user) and not check_limited_command(user.id, "quickattack"):
        await handle_unauthorized_access(update, context, "/quickattack")
        await update.message.reply_text("မင်းမှာခွင့်ပြုချက်မရှိဘူးဖာသယ်မသား")
        return
        
    chat_id = update.effective_chat.id
    last_target = quick_attack_targets.get(chat_id)
    
    if not last_target:
        await update.message.reply_text(
            "❌ No previous target found.\n"
            "Use `/attack @user` first to save a target.",
            parse_mode="Markdown"
        )
        return
        
    target, display = last_target
    
    # Stop any existing attack
    prev = attack_tasks.get(("single", chat_id))
    if prev and not prev.done():
        try: 
            prev.cancel()
        except: 
            pass

    # Start new attack with stored target
    attacking_single[chat_id] = target
    attacking_single_display[chat_id] = display
    
    attack_tasks[("single", chat_id)] = asyncio.create_task(
        optimizer.process_attack(ultra_attack_loop(context, chat_id, target, display))
    )
    
    mode_emojis = {
        "burst": "💥",
        "zero_delay": "⚡", 
        "normal": "🔥"
    }
    
    emoji = mode_emojis.get(attack_mode, "🔥")
    
    await update.message.reply_text(
        f"{emoji} *QUICK ATTACK*\n"
        f"ခွေးမသားအားဖင်စလိုးပါတော့မည်။{display}",
        parse_mode="Markdown"
    )
    update_stats("attacks_started", chat_id, user.id)
async def smartattack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AUTO-ADJUSTS SPEED TO AVOID FLOOD - UNLIMITED TARGETS"""
    if await check_lock_and_notify(update, context, "smartattack"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/smartattack")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /smartattack @user1 @user2 @user3 ... (unlimited targets)")
        return

    chat_id = update.effective_chat.id
    targets = []
    displays = []

    # Process all targets
    for target_str in context.args:
        if owner_matches_target(target_str):
            attacker = update.effective_user
            await reverse_attack_owner(context, chat_id, attacker.id, "smartattack")
            return

        target_id, display = await resolve_target_to_id_and_display(context, chat_id, target_str)
        if target_id:
            targets.append(str(target_id))
            displays.append(display)
        else:
            await update.message.reply_text(f"❌ Target not found: {target_str}")
            return

    # Stop previous smart attack
    await stop_smart_attack(chat_id)

    # Start smart attack with all targets
    primary_target = targets[0] if targets else None
    target_display = " ".join(displays) if len(displays) <= 3 else f"{len(targets)} targets"

    smart_attacks[chat_id] = {
        'targets': targets,  # Store all targets
        'display': target_display,
        'primary_target': primary_target,
        'base_delay': 1.0,
        'consecutive_success': 0,
        'total_messages': 0,
        'flood_events': 0
    }

    attack_tasks[("smart", chat_id)] = asyncio.create_task(
        smart_attack_loop(context, chat_id, primary_target, target_display)
    )

    await update.message.reply_text(
        f"🧠 **SMART ATTACK ACTIVATED**\n"
        f"🎯 Targets: {target_display}\n"
        f"⚡ Mode: Adaptive Speed\n"
        f"🛡️ Anti-Flood: ACTIVE\n"
        f"📈 Starting at: 1.0s delay"
    )

async def stop_smart_attack(chat_id: int):
    """Stop smart attack for a chat"""
    if chat_id in smart_attacks:
        smart_attacks.pop(chat_id, None)
        task = attack_tasks.get(("smart", chat_id))
        if task and not task.done():
            task.cancel()
        attack_tasks.pop(("smart", chat_id), None)

# ==================== MYANMAR COMMAND HANDLERS (Reply Support) ====================

# ==================== HELPER FUNCTIONS ====================

def get_target_from_reply(update: Update) -> Optional[int]:
    """Reply/Copy/Forward ကနေ Target User ID ထုတ်ပေး"""
    if not update.message or not update.message.reply_to_message:
        return None
    replied = update.message.reply_to_message
    if hasattr(replied, 'forward_origin') and replied.forward_origin:
        if hasattr(replied.forward_origin, 'sender_user'):
            return replied.forward_origin.sender_user.id
        return None
    if replied.from_user:
        return replied.from_user.id
    return None


async def set_target_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Reply ရှိရင် Target ID ကို context.args ထဲထည့်၊ မရှိရင် text ကနေယူ"""
    target_id = get_target_from_reply(update)
    if target_id:
        context.args = [str(target_id)]
        return True
    text = update.message.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        context.args = parts[1].split()
    else:
        context.args = []
    return len(context.args) > 0


# ==================== MYANMAR HANDLER FUNCTIONS ====================

async def myanmar_go_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """သတ်ပြစ်လိုက် /go (Reply needed)"""
    if not is_authorized(update.effective_user):
        return
    await go_command(update, context)


async def myanmar_attack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """သတ်ပြစ် /attack (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await attack_command(update, context)


async def myanmar_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """တော်ပြီ /stop"""
    if not is_authorized(update.effective_user):
        return
    await stop_command(update, context)


async def myanmar_ghost_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အယ်ခွေးစာကိုဖျက် /ghost (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await ghost_command(update, context)


async def myanmar_stopghost_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မဖျက်နဲ့တော့ /stopghost"""
    if not is_authorized(update.effective_user):
        return
    await stopghost_command(update, context)


async def myanmar_troll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ငနုပြောင် /troll (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await troll_command(update, context)


async def myanmar_stoptroll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မပြောင်နဲ့တော့ /stoptroll"""
    if not is_authorized(update.effective_user):
        return
    await stoptroll_command(update, context)


async def myanmar_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အင်းဖိုပြ /id (Reply support)"""
    target_id = get_target_from_reply(update)
    if target_id:
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
            user = member.user
            await update.message.reply_text(
                f"👤 Name: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📧 @{user.username or 'N/A'}",
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text(f"🆔 ID: `{target_id}`", parse_mode="Markdown")
    else:
        text = update.message.text.strip()
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            context.args = parts[1].split()
            await id_command(update, context)
        else:
            await id_command(update, context)


async def myanmar_ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ဘမ်းလိုက်ကွာသူကို /ban (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await ban_command(update, context)


async def myanmar_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ဘမ်းဖြည့်လိုက်ကွာ /unban (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await unban_command(update, context)


async def myanmar_kick_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ကစ်လိုက်သူကို /kick (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await kick_command(update, context)


async def myanmar_mute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မြု့လိုက်ခွေးကို /mute (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await mute_command(update, context)


async def myanmar_unmute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မြု့ဖြည့်တဗဲ့ /unmute (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await unmute_command(update, context)


async def myanmar_adm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မင်းကငါတဗဲ့ဖြစ်ပြီ /adm (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await adm_command(update, context)


async def myanmar_disadm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ပြန်ကန်ခွေးကိုပြုတ် /disadm (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await disadm_command(update, context)


async def myanmar_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ဘော့စတင်းမယ် /start"""
    await start_command(update, context)


async def myanmar_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """စာထောက်ကိုက် /reply (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await reply_command(update, context)


async def myanmar_unreply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မကိုက်နဲ့တော့ /unreply"""
    if not is_authorized(update.effective_user):
        return
    await unreply_command(update, context)


async def myanmar_stopall_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ရပ်အကုန် /stopall"""
    if not is_authorized(update.effective_user):
        return
    await stopall_command(update, context)


async def myanmar_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မန်ရှင်အကုန်ခေါ်မယ် /call"""
    if not is_authorized(update.effective_user):
        return
    await call_command(update, context)


async def myanmar_stopcall_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မန်ရှင်ခေါ်တာရပ်မယ် /stopcall"""
    if not is_authorized(update.effective_user):
        return
    await stopcall_command(update, context)


async def myanmar_sendall_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ကဲ့တဗဲ့စာဖြန့် /sendall"""
    if not is_owner(update.effective_user):
        return
    await sendall_command(update, context)


async def myanmar_fight_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ပွဲခေါ်မယ်ကွာ /fight"""
    if not is_admin(update.effective_user.id, update.effective_user.username):
        return
    await fight_command(update, context)


async def myanmar_combo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အင်းအားပြမယ် /combo"""
    if not is_authorized(update.effective_user):
        return
    await combo_command(update, context)


async def myanmar_scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """စစ်ဆေး /scan"""
    if not is_authorized(update.effective_user):
        return
    await scan_command(update, context)


async def myanmar_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အကူ /zen"""
    await zen_command(update, context)


async def myanmar_pin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """တွယ် /pin"""
    if not is_authorized(update.effective_user):
        return
    await pin_command(update, context)


async def myanmar_unpin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """တွယ်ဖြုတ် /unpin"""
    if not is_authorized(update.effective_user):
        return
    await unpin_command(update, context)


async def myanmar_watch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """စောင့်ကြည့် /watch (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await watch_command(update, context)


async def myanmar_unwatch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မစောင့်နဲ့တော့ /unwatch"""
    if not is_authorized(update.effective_user):
        return
    await unwatch_command(update, context)


async def myanmar_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """နာမည်ပေး /name (Reply + text)"""
    if not is_authorized(update.effective_user):
        return
    text = update.message.text.strip()
    parts = text.split(maxsplit=1)
    target_id = get_target_from_reply(update)
    if target_id:
        if len(parts) > 1:
            context.args = [str(target_id)] + parts[1].split()
        else:
            context.args = [str(target_id)]
    elif len(parts) > 1:
        context.args = parts[1].split()
    else:
        context.args = []
    await name_command(update, context)


async def myanmar_settarget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ပစ်မှတ်ထား /settarget (Reply/Text)"""
    if not is_authorized(update.effective_user):
        return
    await set_target_args(update, context)
    await settarget_command(update, context)


async def zen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """မြန်မာဗားရှင်း Command များ ပြသရန်"""
    text = """
<b>🔥 Powerd By Hyperion Bot 🔥</b>
<b>မြန်မာ Command များ</b>
<i>Slash မပါပဲ ရိုက်သုံးနိုင် • Reply/Copy ထောက်သုံးနိုင်</i>

<b>⚔️ ATTACK</b>
  <b>သတ်ပြစ်လိုက်</b>  =  <code>/go</code> (Reply)
  <b>သတ်ပြစ်</b>  =  <code>/attack</code> (Reply/ID)
  <b>တော်ပြီ</b>  =  <code>/stop</code>
  <b>မသတ်နဲ့တော့</b>  =  <code>/stop</code>
  <b>ရပ်အကုန်</b>  =  <code>/stopall</code>

<b>👻 GHOST / TROLL</b>
  <b>အယ်ခွေးစာကိုဖျက်</b>  =  <code>/ghost</code> (Reply/ID)
  <b>မဖျက်နဲ့တော့</b>  =  <code>/stopghost</code>
  <b>ငနုပြောင်</b>  =  <code>/troll</code> (Reply/ID)
  <b>မပြောင်နဲ့တော့</b>  =  <code>/stoptroll</code>

<b>💬 REPLY</b>
  <b>စာထောက်ကိုက်</b>  =  <code>/reply</code> (Reply/ID)
  <b>မကိုက်နဲ့တော့</b>  =  <code>/unreply</code>

<b>🔨 MODERATION</b>
  <b>ဘမ်းလိုက်ကွာသူကို</b>  =  <code>/ban</code> (Reply/ID)
  <b>ဘမ်းဖြည့်လိုက်ကွာ</b>  =  <code>/unban</code>
  <b>ကစ်လိုက်သူကို</b>  =  <code>/kick</code> (Reply/ID)
  <b>မြု့လိုက်ခွေးကို</b>  =  <code>/mute</code> (Reply/ID)
  <b>မြု့ဖြည့်တဗဲ့</b>  =  <code>/unmute</code>

<b>👑 ADMIN</b>
  <b>မင်းကငါတဗဲ့ဖြစ်ပြီ</b>  =  <code>/adm</code> (Reply/ID)
  <b>ပြန်ကန်ခွေးကိုပြုတ်</b>  =  <code>/disadm</code> (Reply/ID)
  <b>တွယ်</b>  =  <code>/pin</code> (Reply)
  <b>တွယ်ဖြုတ်</b>  =  <code>/unpin</code>

<b>📡 BROADCAST</b>
  <b>ပွဲခေါ်မယ်ကွာ</b>  =  <code>/fight</code>
  <b>ကဲ့တဗဲ့စာဖြန့်</b>  =  <code>/sendall</code>
  <b>မန်ရှင်အကုန်ခေါ်မယ်</b>  =  <code>/call</code>
  <b>မန်ရှင်ခေါ်တာရပ်မယ်</b>  =  <code>/stopcall</code>

<b>🔍 TOOLS</b>
  <b>အင်းဖိုပြ</b>  =  <code>/id</code>
  <b>စစ်ဆေး</b>  =  <code>/scan</code>
  <b>စောင့်ကြည့်</b>  =  <code>/watch</code>
  <b>မစောင့်နဲ့တော့</b>  =  <code>/unwatch</code>
  <b>နာမည်ပေး</b>  =  <code>/name</code>
  <b>ပစ်မှတ်ထား</b>  =  <code>/settarget</code>
  <b>အင်းအားပြမယ်</b>  =  <code>/combo</code>
  <b>အကူ</b>  =  <code>/zen</code>
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url=OWNER_CHANNEL_LINK),
         InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_CHAT_ID}")]
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ---------------- SPEED COMMANDS ----------------

async def set_delay_for_chat(chat_id: int, delay: float):
    """Set attack delay for specific chat"""
    attack_delay[chat_id] = float(delay)

async def setspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set attack delay in real-time: /setspeed 0.5"""
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/setspeed")
        return

    chat_id = update.effective_chat.id

    if not context.args:
        # No arg → set to 0.5 default and show
        attack_delay[chat_id] = 0.5
        return await update.message.reply_text(
            "⚡ Attack Speed ကို **0.5 sec** (default) အဖြစ် သတ်မှတ်လိုက်ပါပြီ",
            parse_mode="Markdown"
        )

    try:
        delay = float(context.args[0])
        if delay < 0:
            return await update.message.reply_text("❌ Speed cannot be negative.")

        attack_delay[chat_id] = delay
        await update.message.reply_text(
            f"⚡ Attack Speed ကို **{delay} sec** အဖြစ် ပြောင်းလိုက်ပါပြီ",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(
            "❌ Invalid input\nExample → `/setspeed 0.5`",
            parse_mode="Markdown"
        )
async def fastest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "fastest"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/fastest")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.20)
    await update.message.reply_text("💨 Speed set to 0.20s (fastest)")

async def godspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "godspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/godspeed")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.10)
    await update.message.reply_text("⚡ Speed set to 0.10s (godspeed)")

async def ultragodspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "ultragodspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ultragodspeed")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.05)
    await update.message.reply_text("🔥 Speed set to 0.05s (ultragodspeed)")

async def newgodrebornspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "newgodrebornspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/newgodrebornspeed")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.02)
    await update.message.reply_text("👑 Speed set to 0.02s (newgodrebornspeed)")

async def normal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "normal"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/normal")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    # Set to NORMAL mode and speed
    set_attack_mode(update.effective_chat.id, "normal")
    await set_delay_for_chat(update.effective_chat.id, 0.3)
    
    # Clear burst mode
    burst_mode_config.pop(update.effective_chat.id, None)
    
    await update.message.reply_text(
        "🐢 **Speed set to 0.3s (normal)**\n"
        "*Mode switched to NORMAL*",
        parse_mode="Markdown"
    )
async def flashspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "flashspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/flashspeed")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.08)
    await update.message.reply_text("⚡ Speed set to 0.08s (flashspeed)")

async def lightspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "lightspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/lightspeed")
        await update.message.reply_text("❌ Not authorized.")
        return
    await set_delay_for_chat(update.effective_chat.id, 0.01)
    await update.message.reply_text("🚀 Speed set to 0.01s (lightspeed)", parse_mode="Markdown")

async def hyperspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "hyperspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/hyperspeed")
        return
    
    await set_delay_for_chat(update.effective_chat.id, 0.005)
    await update.message.reply_text("🌀 Speed set to 0.005s (HYPERSPEED)\n⚠️ *EXTREME FLOOD RISK*", parse_mode="Markdown")

async def instantspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "instantspeed"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/instantspeed")
        return
    
    await set_delay_for_chat(update.effective_chat.id, 0.001)
    await update.message.reply_text("⚡ Speed set to 0.001s (INSTANT)\n🚨 *GUARANTEED FLOOD WAIT*", parse_mode="Markdown")

async def slow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "slow"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/slow")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    await set_delay_for_chat(update.effective_chat.id, 1.5)
    await update.message.reply_text("🐢 Speed set to 1.5s (slow) - Best for long spam sessions")

# ---------------- ATTACK MODE SYSTEM ----------------

# Update the valid modes in your set_attack_mode function:
# Update the valid modes
attack_mode = "normal"  # normal, burst, zero_delay, hyperburst, ultraburst, smart, smartzerodelay, ultimatezerodelay

# Update the valid modes in set_attack_mode function:
def set_attack_mode(chat_id: int, mode: str) -> bool:
    """Set attack mode for a chat with all modes"""
    global attack_mode
    
    valid_modes = ["normal", "burst", "zero_delay", "hyperburst", "ultraburst", "smart", "smartzerodelay", "ultimatezerodelay"]
    if mode not in valid_modes:
        return False
    
    attack_mode = mode
    return True

async def burst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "burst"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/burst")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    # Set burst mode configuration
    burst_mode_config[update.effective_chat.id] = {
        'mode': 'burst',
        'burst_count': 10,
        'burst_duration': 5.0,
        'pause_duration': 7.0
    }
    
    # Also set global attack mode
    set_attack_mode(update.effective_chat.id, "burst")
    
    await update.message.reply_text(
        "💥 **BURST MODE ACTIVATED!**\n\n"
        "⚡ **Mode:** Burst Attack\n"
        "💣 **Burst:** 10 messages\n" 
        "⏱️ **Duration:** 5 seconds\n"
        "⏸️ **Pause:** 7 seconds\n"
        "📊 **Speed:** 0.83 msg/sec overall\n\n"
        "*Active attacks will now use burst pattern*",
        parse_mode="Markdown"
    )

async def ultimate_zerodelay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ULTIMATE ZERO DELAY - True zero with instant recovery"""
    if await check_lock_and_notify(update, context, "ultimatezerodelay"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ultimatezerodelay")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    # ULTIMATE ZERO DELAY
    set_attack_mode(update.effective_chat.id, "ultimatezerodelay")
    
    await update.message.reply_text(
        "🌀 **ULTIMATE ZERO DELAY ACTIVATED!**\n\n"
        "🚀 **Delay:** 0.0 seconds (True Zero)\n"
        "💥 **Speed:** ABSOLUTE MAXIMUM\n"
        "🛡️ **Recovery:** INSTANT after flood\n"
        "⚡ **Performance:** No freezing, instant resume\n\n"
        "*True zero delay with instant recovery system!*",
        parse_mode="Markdown"
    )

async def ultimate_zero_delay_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target: str, display: str):
    """ULTIMATE ZERO DELAY - True zero with instant recovery"""
    flood_detected = False
    
    while attacking_single.get(chat_id) == target:
        try:
            # If we just recovered from flood, wait a moment
            if flood_detected:
                flood_detected = False
                await asyncio.sleep(0.2)  # Brief pause after recovery
            
            line = random.choice(attack_replies)
            text_to_send = f"{display} {line}"
            
            # TRUE ZERO DELAY - fire and forget
            asyncio.create_task(
                context.bot.send_message(chat_id=chat_id, text=text_to_send, parse_mode="Markdown")
            )
            
            # ACTUAL ZERO DELAY - no sleep at all
            await asyncio.sleep(0)
            
        except Exception as e:
            error_msg = str(e)
            
            if "Too Many Requests" in error_msg or "flood" in error_msg:
                if not flood_detected:
                    print("🌀 Ultimate zero: Flood detected, instant recovery activated")
                    flood_detected = True
                
                wait_time = extract_wait_time(error_msg)
                print(f"🌀 Ultimate recovery: {wait_time}s wait")
                await asyncio.sleep(wait_time)
                
                # INSTANT RESUME - no speed reduction
                flood_detected = False
            else:
                # Minimal pause for other errors
                await asyncio.sleep(0.1)

async def ultraburst_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ULTRA BURST - Maximum speed without freezing"""
    if await check_lock_and_notify(update, context, "ultraburst"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ultraburst")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    # ULTRA BURST - Maximum safe speed
    burst_mode_config[update.effective_chat.id] = {
        'mode': 'ultraburst',
        'burst_count': 15,  # 15 messages
        'burst_duration': 1.0,  # 1 second for 15 messages
        'pause_duration': 2.0   # 2 second pause
    }
    
    set_attack_mode(update.effective_chat.id, "burst")
    
    await update.message.reply_text(
        "🌀 **ULTRA BURST MODE ACTIVATED!**\n\n"
        "🚀 **Speed:** 15 messages/second (burst)\n"
        "💣 **Burst:** 15 messages in 1 second\n"
        "⏸️ **Pause:** 2 seconds\n"
        "📊 **Total Rate:** ~5 messages/second\n"
        "🛡️ **No Freezing:** GUARANTEED\n\n"
        "*This is the FASTEST SAFE speed possible!*",
        parse_mode="Markdown"
    )
async def normalmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch back to NORMAL DEFAULT speed"""
    if await check_lock_and_notify(update, context, "normalmode"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/normalmode")
        await update.message.reply_text("❌ Not authorized.")
        return
    
    # Switch to NORMAL mode
    set_attack_mode(update.effective_chat.id, "normal")
    
    # Set normal delay (0.3s)
    await set_delay_for_chat(update.effective_chat.id, 0.3)
    
    # Clear burst mode config
    burst_mode_config.pop(update.effective_chat.id, None)
    
    await update.message.reply_text(
        "🐢 **NORMAL MODE ACTIVATED**\n\n"
        "⚡ **Speed:** 0.3 seconds (default)\n"
        "📊 **Rate:** ~3 messages/second\n"
        "🛡️ **Status:** Safe & Stable\n\n"
        "*All attacks will now use normal speed*",
        parse_mode="Markdown"
    )
# ---------------- ENHANCED ID COMMAND ----------------
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced ID command like Rose bot - checks mentions, cache, and all data sources"""
    message = update.effective_message
    chat_id = update.effective_chat.id
    
    # Function to search user in all data sources
    async def find_user_in_all_sources(search_term: str):
        """Search for user in all available data sources"""
        results = []
        
        # 1. Check if it's a direct user ID
        if search_term.isdigit():
            user_id = int(search_term)
            # Try to get from Telegram API first
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                results.append({
                    'source': 'telegram_api',
                    'id': member.user.id,
                    'name': member.user.first_name,
                    'username': member.user.username,
                    'found': True
                })
            except:
                pass
            
            # Check name_map for nicknames
            if str(user_id) in name_map:
                results.append({
                    'source': 'name_map',
                    'id': user_id,
                    'name': name_map[str(user_id)],
                    'username': None,
                    'found': True
                })
        
        # 2. Check if it's a username (@username)
        elif search_term.startswith('@'):
            username = search_term[1:].lower()
            
            # Check username_to_userid cache
            if (chat_id, username) in username_to_userid:
                user_id = username_to_userid[(chat_id, username)]
                results.append({
                    'source': 'username_cache',
                    'id': user_id,
                    'name': f"User{user_id}",
                    'username': search_term,
                    'found': True
                })
            
            # Check member_cache
            chat_key = str(chat_id)
            if chat_key in member_cache:
                for uid, user_data in member_cache[chat_key].get('members', {}).items():
                    if user_data.get('username', '').lower() == username:
                        results.append({
                            'source': 'member_cache',
                            'id': int(uid),
                            'name': user_data.get('first_name', 'Unknown'),
                            'username': f"@{username}",
                            'found': True
                        })
        
        # 3. Check name_map for nicknames
        for uid, nickname in name_map.items():
            if nickname.lower() == search_term.lower():
                try:
                    user_id = int(uid)
                    results.append({
                        'source': 'name_map',
                        'id': user_id,
                        'name': nickname,
                        'username': None,
                        'found': True
                    })
                except:
                    continue
        
        # 4. Check private_users
        for uid, user_data in private_users.items():
            if (user_data.get('username', '').lower() == search_term.lower() or 
                user_data.get('name', '').lower() == search_term.lower()):
                results.append({
                    'source': 'private_users',
                    'id': user_data['id'],
                    'name': user_data.get('name', 'Unknown'),
                    'username': user_data.get('username'),
                    'found': True
                })
        
        return results

    # Check if message has text mentions or mentions in entities
    found_users = []
    
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                # Direct user mention with ID available
                user = entity.user
                found_users.append({
                    'id': user.id,
                    'name': user.first_name,
                    'username': user.username,
                    'source': 'text_mention',
                    'display_name': user.first_name
                })
                
            elif entity.type == "mention":
                # @username mention
                username = message.text[entity.offset:entity.offset + entity.length]
                # Try to resolve via Telegram API
                try:
                    user = await context.bot.get_chat(username)
                    found_users.append({
                        'id': user.id,
                        'name': user.first_name,
                        'username': user.username,
                        'source': 'username_api',
                        'display_name': user.first_name
                    })
                except Exception as e:
                    # If API fails, search in our data sources
                    search_results = await find_user_in_all_sources(username)
                    for result in search_results:
                        if result['found']:
                            found_users.append({
                                'id': result['id'],
                                'name': result['name'],
                                'username': result['username'],
                                'source': result['source'],
                                'display_name': result['name']
                            })
    
    # If no entities found, check if there's text after /id
    if not found_users and context.args:
        search_term = " ".join(context.args).strip()
        search_results = await find_user_in_all_sources(search_term)
        for result in search_results:
            if result['found']:
                found_users.append({
                    'id': result['id'],
                    'name': result['name'],
                    'username': result['username'],
                    'source': result['source'],
                    'display_name': result['name']
                })
        
        # If still not found, try direct Telegram API lookup
        if not found_users:
            try:
                # Try as username
                if search_term.startswith('@'):
                    user = await context.bot.get_chat(search_term)
                # Try as user ID
                elif search_term.isdigit():
                    user = await context.bot.get_chat(int(search_term))
                else:
                    # Try searching in current chat members
                    try:
                        members = await context.bot.get_chat_members(chat_id)
                        for member in members:
                            if (member.user.username and member.user.username.lower() == search_term.lower()) or \
                               (member.user.first_name and member.user.first_name.lower() == search_term.lower()):
                                found_users.append({
                                    'id': member.user.id,
                                    'name': member.user.first_name,
                                    'username': member.user.username,
                                    'source': 'chat_members',
                                    'display_name': member.user.first_name
                                })
                                break
                    except:
                        pass
                
                if not found_users and 'user' in locals():
                    found_users.append({
                        'id': user.id,
                        'name': user.first_name,
                        'username': user.username,
                        'source': 'telegram_api',
                        'display_name': user.first_name
                    })
                    
            except Exception as e:
                # Final fallback - check if it's a reply
                if message.reply_to_message:
                    user = message.reply_to_message.from_user
                    found_users.append({
                        'id': user.id,
                        'name': user.first_name,
                        'username': user.username,
                        'source': 'reply',
                        'display_name': user.first_name
                    })
    
    # If still no users found, check replied message
    if not found_users and message.reply_to_message:
        user = message.reply_to_message.from_user
        found_users.append({
            'id': user.id,
            'name': user.first_name,
            'username': user.username,
            'source': 'reply',
            'display_name': user.first_name
        })
    
    # Generate response - SIMPLE AND COPYABLE
    if found_users:
        response_lines = []
        
        for i, user in enumerate(found_users):
            if len(found_users) > 1:
                response_lines.append(f"👤 User {i+1}: {user['display_name']}")
            else:
                response_lines.append(f"👤 Username: {user['display_name']}")
            
            response_lines.append(f"🆔 User ID: {user['id']}")
            
            if user['username']:
                response_lines.append(f"📧 @{user['username']}")
            
            # Add nickname if exists
            if str(user['id']) in name_map:
                response_lines.append(f"🏷️ Nickname: {name_map[str(user['id'])]}")
            
            response_lines.append(f"📍 Source: {user['source']}")
            
            if i < len(found_users) - 1:  # Add separator between multiple users
                response_lines.append("")
        
        response = "\n".join(response_lines)
        
    else:
        # No users found - show current user's ID
        user = update.effective_user
        response = f"👤 Username: {user.first_name}\n🆔 User ID: {user.id}"
        
        if user.username:
            response += f"\n📧 @{user.username}"
    
    await message.reply_text(response)

# ---------------- IMPROVED AVAILABLE GROUPS ----------------
async def availablegroups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "availablegroups"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/availablegroups")
        return

    # Run migration check first
    await check_group_migrations(context)

    active_groups = {}
    group_links = {}
    
    for chat_id_str, chat_info in seen_chats.items():
        try:
            chat_id = int(chat_id_str)
            chat = await context.bot.get_chat(chat_id)
            active_groups[chat_id_str] = chat_info
            
            try:
                invite_link = await context.bot.export_chat_invite_link(chat_id)
                group_links[chat_id_str] = invite_link
            except Exception:
                try:
                    chat_full = await context.bot.get_chat(chat_id)
                    if hasattr(chat_full, 'invite_link') and chat_full.invite_link:
                        group_links[chat_id_str] = chat_full.invite_link
                    else:
                        group_links[chat_id_str] = "No invite link"
                except:
                    group_links[chat_id_str] = "No invite link"
            
            if chat.title != chat_info.get('title'):
                chat_info['title'] = chat.title
        except Exception:
            continue

    seen_chats.clear()
    seen_chats.update(active_groups)
    asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))

    if not active_groups:
        await update.message.reply_text("❌ No active groups found.")
        return

    total_groups = len(active_groups)
    
    # ENHANCED: Better header with announce instructions
    lines = [f"📊 **ACTIVE GROUPS: {total_groups} TOTAL**\n"]
    lines.append("📍 **Usage with /announce:** Reply to any message + `/announce <number>`")
    lines.append("💡 **Example:** Reply to message + `/announce 2` sends to group #2\n")
    
    for i, (chat_id_str, info) in enumerate(active_groups.items(), 1):
        title = info.get('title', 'Unnamed Group')
        added_by = info.get('added_by', 'Unknown')
        added_at = info.get('added_at', 'Unknown')
        invite_link = group_links.get(chat_id_str, "No invite link")
        migrated_from = info.get('migrated_from')
        
        try:
            added_dt = datetime.fromisoformat(added_at)
            added_str = added_dt.strftime("%m/%d %H:%M")
        except:
            added_str = added_at
            
        # ENHANCED: Clear numbering for /announce
        lines.append(f"**{i}. {title}**")
        lines.append(f"   🆔 `{chat_id_str}`")
        
        if migrated_from:
            lines.append(f"   🔄 Migrated from: `{migrated_from}`")
            
        lines.append(f"   👤 Added by: {added_by}")
        lines.append(f"   ⏰ {added_str}")
                
        if invite_link and invite_link != "No invite link":
            lines.append(f"   🔗 [Group Link]({invite_link})")
        else:
            lines.append(f"   🔗 No invite link")
        
        # ENHANCED: Add quick announce hint
        lines.append(f"   📢 Use: `/announce {i}`")
        lines.append("")

    full_text = "\n".join(lines)
    
    # ENHANCED: Better pagination for large lists
    if len(full_text) > 4000:
        parts = []
        current_part = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            if current_length + line_length > 4000:
                # Start new part
                parts.append("\n".join(current_part))
                current_part = [line]
                current_length = line_length
            else:
                current_part.append(line)
                current_length += line_length
        
        if current_part:
            parts.append("\n".join(current_part))
        
        # Send first part
        await update.message.reply_text(parts[0], parse_mode="Markdown", disable_web_page_preview=True)
        
        # Send remaining parts with continuation header
        for i, part in enumerate(parts[1:], 2):
            continuation_text = f"*📋 Continued... (Part {i}/{len(parts)})*\n\n{part}"
            await update.message.reply_text(continuation_text, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.message.reply_text(full_text, parse_mode="Markdown", disable_web_page_preview=True)

    # ENHANCED: Send quick usage reminder
    usage_reminder = """
💡 **Quick Announce Guide:**
1. Reply to any message (text, photo, video, poll, etc.)
2. Use `/announce <number>` 
3. Example: Reply + `/announce 3` sends to group #3

✅ **Supports:** Text, Photos, Videos, Polls, Documents, Links, Stickers, Voice, etc.
"""
    await update.message.reply_text(usage_reminder, parse_mode="Markdown")

# ---------------- AVAILABLE USERS ----------------
async def availableusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "availableusers"):
        return

    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/availableusers")
        return

    if not private_users:
        await update.message.reply_text("❌ No private users recorded.")
        return

    total_users = len(private_users)
    lines = [f"👤 <b>PRIVATE USERS: {total_users} TOTAL</b>\n"]

    for i, (user_id_str, info) in enumerate(private_users.items(), 1):
        name = html.escape(info.get("name", "Unknown User"))
        username_raw = info.get("username", "")
        username = html.escape(username_raw) if username_raw else ""

        lines.append(f"{i}. <b>{name}</b>")
        lines.append(f"   🆔 <code>{html.escape(str(user_id_str))}</code>")  # BLUE HIGHLIGHT
        if username:
            lines.append(f"   📧 @{username}")
        lines.append("")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

# ---------------- FIXED ADD_ADMIN COMMAND ----------------
async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "admin"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "")
        return

    if not context.args:
        await update.message.reply_text("Usage: /admin id")
        return

    arg = context.args[0].strip()
    
    if arg.startswith("@"):
        uname = arg.nstrip("@").lower()
        if uname in admins_data.get("usernames", []):
            await update.message.reply_text(f"✅ User {arg} is already an admin.")
            return
        admins_data.setdefault("usernames", []).append(uname)
    else:
        try:
            uid = int(arg)
            if uid in admins_data.get("ids", []):
                await update.message.reply_text(f"✅ User ID {uid} is already an admin.")
                return
            admins_data.setdefault("ids", []).append(uid)
        except ValueError:
            await update.message.reply_text("Invalid ID or username format. Please provide a valid integer ID or a @username.")
            return

    asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
    global ADMIN_IDS, ADMIN_USERNAMES
    ADMIN_IDS = set(int(x) for x in admins_data.get("ids", []) if str(x).isdigit())
    ADMIN_USERNAMES = set(u.lstrip("@").lower() for u in admins_data.get("usernames", []))
    await update.message.reply_text("✅ Admin added.")





# ---------------- LOCK SYSTEM COMMANDS ----------------
async def lockallchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/lockallchat")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "🌍 *GLOBAL LOCK SYSTEM*\n\n"
            "Usage: `/lockallchat <command> <time>`\n\n"
            "Examples:\n"
            "• `/lockallchat attack 1h` - Lock attack in ALL chats for 1 hour\n"
            "• `/lockallchat all 30m` - Lock ALL commands globally for 30 minutes\n"
            "• `/lockallchat multiple 2h` - Lock multiple command globally\n\n"
            "Time formats: 30m, 1h, 2h, 1d\n"
            "⚠️ This affects ALL chats the bot is in!",
            parse_mode="Markdown"
        )
        return

    command = context.args[0].lower()
    time_str = context.args[1].lower()
    
    time_seconds = 0
    if time_str.endswith('m'):
        try:
            time_seconds = int(time_str[:-1]) * 60
        except:
            pass
    elif time_str.endswith('h'):
        try:
            time_seconds = int(time_str[:-1]) * 3600
        except:
            pass
    elif time_str.endswith('d'):
        try:
            time_seconds = int(time_str[:-1]) * 86400
        except:
            pass
    else:
        try:
            time_seconds = int(time_str) * 60
        except:
            pass
    
    if time_seconds <= 0:
        await update.message.reply_text("❌ Invalid time format. Use: 30m, 1h, 2h, 1d")
        return
    
    expires_at = (datetime.now() + timedelta(seconds=time_seconds)).isoformat()
    
    if not global_lock_config:
        global_lock_config.update({
            "active": True,
            "commands": [],
            "locked_by": update.effective_user.id,
            "locked_by_name": update.effective_user.first_name,
            "locked_at": datetime.now().isoformat()
        })
    
    if command not in global_lock_config["commands"]:
        global_lock_config["commands"].append(command)
    
    global_lock_config["expires_at"] = expires_at
    global_lock_config["active"] = True
    
    asyncio.create_task(fast_data.buffered_save(GLOBAL_LOCK_FILE, global_lock_config))
    
    hours = time_seconds // 3600
    minutes = (time_seconds % 3600) // 60
    time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    await update.message.reply_text(
        f"🌍 *GLOBAL LOCK ACTIVATED!*\n\n"
        f"• Command: `{command}`\n"
        f"• Duration: `{time_display}`\n"
        f"• Scope: ALL CHATS 🌐\n"
        f"• Locked by: {update.effective_user.first_name}\n\n"
        f"⚠️ This command is now locked in every chat!",
        parse_mode="Markdown"
    )

async def unlockallchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/unlockallchat")
        return

    if not global_lock_config or not global_lock_config.get("active", False):
        await update.message.reply_text("❌ No active global locks.")
        return

    if not context.args:
        global_lock_config.clear()
        asyncio.create_task(fast_data.buffered_save(GLOBAL_LOCK_FILE, global_lock_config))
        await update.message.reply_text("🌍 *ALL GLOBAL LOCKS REMOVED!*", parse_mode="Markdown")
        return

    command = context.args[0].lower()
    
    if command in global_lock_config.get("commands", []):
        global_lock_config["commands"].remove(command)
        
        if not global_lock_config["commands"]:
            global_lock_config["active"] = False
        
        asyncio.create_task(fast_data.buffered_save(GLOBAL_LOCK_FILE, global_lock_config))
        await update.message.reply_text(f"🌍 Command `{command}` unlocked globally", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Command `{command}` is not globally locked", parse_mode="Markdown")

async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/lock")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/lock <command> <time>`\n\n"
            "Examples:\n"
            "• `/lock attack 1h` - Lock attack command for 1 hour\n"
            "• `/lock all 30m` - Lock all commands for 30 minutes\n\n"
            "Time formats: 30m, 1h, 2h, 1d",
            parse_mode="Markdown"
        )
        return

    command = context.args[0].lower()
    time_str = context.args[1].lower()
    
    time_seconds = 0
    if time_str.endswith('m'):
        try:
            time_seconds = int(time_str[:-1]) * 60
        except:
            pass
    elif time_str.endswith('h'):
        try:
            time_seconds = int(time_str[:-1]) * 3600
        except:
            pass
    elif time_str.endswith('d'):
        try:
            time_seconds = int(time_str[:-1]) * 86400
        except:
            pass
    else:
        try:
            time_seconds = int(time_str) * 60
        except:
            pass
    
    if time_seconds <= 0:
        await update.message.reply_text("❌ Invalid time format. Use: 30m, 1h, 2h, 1d")
        return
    
    chat_id = update.effective_chat.id
    chat_key = str(chat_id)
    
    expires_at = (datetime.now() + timedelta(seconds=time_seconds)).isoformat()
    
    if chat_key not in lock_config:
        lock_config[chat_key] = {
            "active": True,
            "commands": [],
            "locked_by": update.effective_user.id,
            "locked_at": datetime.now().isoformat()
        }
    
    if command not in lock_config[chat_key]["commands"]:
        lock_config[chat_key]["commands"].append(command)
    
    lock_config[chat_key]["expires_at"] = expires_at
    lock_config[chat_key]["active"] = True
    
    asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))
    
    hours = time_seconds // 3600
    minutes = (time_seconds % 3600) // 60
    time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    await update.message.reply_text(
        f"🔒 *Command Locked*\n\n"
        f"• Command: `{command}`\n"
        f"• Duration: `{time_display}`\n"
        f"• Scope: This chat only\n"
        f"• Locked by: {update.effective_user.first_name}",
        parse_mode="Markdown"
    )

async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/unlock")
        return

    chat_id = update.effective_chat.id
    chat_key = str(chat_id)
    
    if chat_key not in lock_config or not lock_config[chat_key].get("active", False):
        await update.message.reply_text("❌ No active locks in this chat.")
        return

    if not context.args:
        lock_config[chat_key]["active"] = False
        lock_config[chat_key]["commands"] = []
        asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))
        await update.message.reply_text("✅ *All commands unlocked*", parse_mode="Markdown")
        return

    command = context.args[0].lower()
    
    if command in lock_config[chat_key]["commands"]:
        lock_config[chat_key]["commands"].remove(command)
        
        if not lock_config[chat_key]["commands"]:
            lock_config[chat_key]["active"] = False
        
        asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))
        await update.message.reply_text(f"✅ Command `{command}` unlocked", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Command `{command}` is not locked", parse_mode="Markdown")

#---------------- Fliter command ------------------



# ---------------- LIMITED COMMAND SYSTEM ----------------
async def limitcommand_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/limitcommand")
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /limitcommand <command> <user> <count>\n\n"
            "Examples:\n"
            "• /limitcommand attack @username 2 - Allow user to use /attack 2 times\n"
            "• /limitcommand multiple 123456789 5 - Allow user ID to use /multiple 5 times\n\n"
            "The user will be able to use the specified command the given number of times."
        )
        return

    command = context.args[0].lower().lstrip('/')
    target_arg = context.args[1]
    count_str = context.args[2]

    try:
        count = int(count_str)
        if count <= 0:
            await update.message.reply_text("❌ Count must be a positive integer.")
            return
    except ValueError:
        await update.message.reply_text("❌ Invalid count. Please provide a positive integer.")
        return

    chat_id = update.effective_chat.id
    target_id = await resolve_target_user_id(context, chat_id, target_arg)
    if not target_id:
        await update.message.reply_text("❌ Could not resolve target user.")
        return

    try:
        member = await context.bot.get_chat_member(chat_id, target_id)
        username = f"@{member.user.username}" if member.user.username else member.user.first_name
    except:
        username = f"User {target_id}"

    user_key = str(target_id)
    if user_key not in limit_commands_data:
        limit_commands_data[user_key] = {}

    limit_commands_data[user_key][command] = {
        "remaining": count,
        "total": count,
        "granted_by": update.effective_user.id,
        "granted_by_name": update.effective_user.first_name,
        "granted_at": datetime.now().isoformat(),
        "username": username
    }

    asyncio.create_task(fast_data.buffered_save(LIMIT_COMMANDS_FILE, limit_commands_data))

    await update.message.reply_text(
        f"✅ Limited Command Granted\n\n"
        f"• User: {username} (ID: {target_id})\n"
        f"• Command: /{command}\n"
        f"• Uses: {count} times\n"
        f"• Granted by: {update.effective_user.first_name}"
    )

async def limitlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/limitlist")
        return

    lines = []

    if limit_admins:
        lines.append("⏰ *TEMPORARY ADMINS:*\n")
        for user_id_str, admin_data in limit_admins.items():
            expires_at = admin_data.get("expires_at", "No expiration")
            added_by = admin_data.get("added_by_name", "Unknown")
            time_granted = admin_data.get("time_granted", "Unknown")
            
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                time_left = expires_dt - datetime.now()
                if time_left.total_seconds() > 0:
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                else:
                    time_str = "EXPIRED"
            except:
                time_str = "Unknown"

            lines.append(f"• User ID: `{user_id_str}`")
            lines.append(f"  Added by: {added_by}")
            lines.append(f"  Time granted: {time_granted}")
            lines.append(f"  Time left: {time_str}")
            lines.append("")
    else:
        lines.append("⏰ *No temporary admins*\n\n")

    if limit_commands_data:
        lines.append("🎯 *LIMITED COMMANDS:*\n")
        for user_id_str, commands_data in limit_commands_data.items():
            lines.append(f"• User ID: `{user_id_str}`")
            for command, limit_info in commands_data.items():
                remaining = limit_info.get("remaining", 0)
                total = limit_info.get("total", 0)
                granted_by = limit_info.get("granted_by_name", "Unknown")
                username = limit_info.get("username", "Unknown")
                
                lines.append(f"  └─ `/{command}`: {remaining}/{total} uses left")
                lines.append(f"     Granted to: {username}")
                lines.append(f"     By: {granted_by}")
            lines.append("")
    else:
        lines.append("🎯 *No limited commands*")

    if not limit_admins and not limit_commands_data:
        await update.message.reply_text("❌ No temporary admins or limited commands.")
        return

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")



# ---------------- WELCOME SYSTEM ----------------


async def setwelcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setwelcome [text]   Placeholders: {name} {group}
    Reply to photo + /setwelcome [text]  → sets welcome photo.
    """
    user = update.effective_user
    if not is_authorized(user):
        return await update.message.reply_text("❌ You are not authorized")

    chat_id = str(update.effective_chat.id)
    entry = welcome_data.get(chat_id, {"active": True, "text": "", "photo_id": None})
    msg_obj   = update.message
    text_given = " ".join(context.args) if context.args else None

    # ── set welcome photo (reply to photo) ──
    if msg_obj.reply_to_message and msg_obj.reply_to_message.photo:
        entry["photo_id"] = msg_obj.reply_to_message.photo[-1].file_id
        if text_given:
            entry["text"] = text_given
        entry["active"] = True
        welcome_data[chat_id] = entry
        asyncio.create_task(fast_data.buffered_save(WELCOME_FILE, welcome_data))
        return await update.message.reply_text("✅ Welcome photo + message set!")

    if not text_given:
        return await update.message.reply_html(
            "📌 <b>Usage:</b>\n"
            "<code>/setwelcome Welcome {name} to {group}!</code>\n\n"
            "Placeholders: <b>{name}</b> → mention  <b>{group}</b> → group name\n"
            "Reply to a photo + /setwelcome [text] to set a welcome photo."
        )

    entry["text"]   = text_given
    entry["active"] = True
    welcome_data[chat_id] = entry
    asyncio.create_task(fast_data.buffered_save(WELCOME_FILE, welcome_data))
    await update.message.reply_text("✅ Welcome message set!")


async def welcomeoff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "welcomeoff"):
        return

    user = update.effective_user
    if not is_authorized(user):
        return await update.message.reply_text("❌ Not allowed")

    chat_id = str(update.effective_chat.id)

    if chat_id in welcome_data:
        welcome_data[chat_id]["active"] = False
        asyncio.create_task(fast_data.buffered_save(WELCOME_FILE, welcome_data))
        return await update.message.reply_text("🟧 Welcome message disabled.")

    await update.message.reply_text("❌ No welcome message set.")

async def welcome_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if chat_id not in welcome_data or not welcome_data[chat_id].get("active", False):
        return await update.message.reply_text("❌ No welcome message set.")

    welcome_text = welcome_data[chat_id]["text"]
    preview = welcome_text.replace("{name}", update.effective_user.first_name).replace(
        "{group}", update.effective_chat.title)

    await update.message.reply_text(f"👀 **Preview:**\n{preview}", parse_mode="Markdown")

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fired by StatusUpdate.NEW_CHAT_MEMBERS – photo-aware HTML mention welcome."""
    message = update.message
    if not message or not message.new_chat_members:
        return

    chat_id = str(update.effective_chat.id)
    entry   = welcome_data.get(chat_id, {})
    if not entry.get("active", False):
        return

    tmpl     = entry.get("text", "")
    photo_id = entry.get("photo_id")

    for member in message.new_chat_members:
        if member.is_bot:
            continue
        safe_name  = html.escape(member.first_name or "User")
        mention    = '<a href="tg://user?id=' + str(member.id) + '">' + safe_name + '</a>'
        group_name = html.escape(update.effective_chat.title or "this group")
        final      = tmpl.replace("{name}", mention).replace("{group}", group_name)
        if not final.strip():
            final = "👋 " + mention + " သည် " + group_name + " သို့ ဝင်ရောက်လာခဲ့သည်"
        try:
            if photo_id:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo_id,
                    caption=final,
                    parse_mode=constants.ParseMode.HTML
                )
            else:
                await message.reply_text(final, parse_mode=constants.ParseMode.HTML)
        except Exception as e:
            logging.error("welcome_handler error: %s", e)
            
# ---------------- FILTER SYSTEM COMMANDS ----------------
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🔍 DEBUG: filter_command called by {update.effective_user.id}")
    
    if await check_lock_and_notify(update, context, "filter"):
        print("🔒 DEBUG: Command locked")
        return
        
    if not is_authorized(update.effective_user):
        print("🚫 DEBUG: User not authorized")
        await handle_unauthorized_access(update, context, "/filter")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not update.message:
        print("❌ DEBUG: update.message is None")
        return

    chat_id = str(update.effective_chat.id)
    args = context.args
    print(f"🔍 DEBUG: Chat ID: {chat_id}, Args: {args}")

    if not args:
        print("❌ DEBUG: No arguments provided")
        await update.message.reply_text(
            "📝 **Filter System**\n\n**Usage:**\n• `/filter <keyword> <reply text>` - Text filter\n• Reply to message + `/filter <keyword>` - Media/text filter",
            parse_mode="Markdown"
        )
        return

    keyword = args[0].lower().strip()
    print(f"🔍 DEBUG: Keyword: {keyword}")
    
    reply_msg = getattr(update.message, 'reply_to_message', None)
    print(f"🔍 DEBUG: Has reply: {reply_msg is not None}")
    
    global filters_data
    
    if not isinstance(filters_data, dict):
        print("🔄 DEBUG: Resetting filters_data to dict")
        filters_data = {}
    
    if chat_id not in filters_data:
        print(f"🆕 DEBUG: Creating new chat entry for {chat_id}")
        filters_data[chat_id] = {}

    if reply_msg:
        print("🔍 DEBUG: Processing reply message")
        content = None
        filter_type = "text"

        if reply_msg.text:
            content = reply_msg.text
            filter_type = "text"
            print(f"🔍 DEBUG: Text content: {content[:50]}...")
        elif reply_msg.sticker:
            content = reply_msg.sticker.file_id
            filter_type = "sticker"
            print(f"🔍 DEBUG: Sticker ID: {content}")
        elif reply_msg.photo:
            content = reply_msg.photo[-1].file_id
            filter_type = "photo"
            print(f"🔍 DEBUG: Photo ID: {content}")
        elif reply_msg.video:
            content = reply_msg.video.file_id
            filter_type = "video"
            print(f"🔍 DEBUG: Video ID: {content}")
        elif reply_msg.document:
            content = reply_msg.document.file_id
            filter_type = "document"
            print(f"🔍 DEBUG: Document ID: {content}")
        elif reply_msg.audio:
            content = reply_msg.audio.file_id
            filter_type = "audio"
            print(f"🔍 DEBUG: Audio ID: {content}")
        elif reply_msg.voice:
            content = reply_msg.voice.file_id
            filter_type = "voice"
            print(f"🔍 DEBUG: Voice ID: {content}")
        else:
            print("❌ DEBUG: Unsupported message type")
            await update.message.reply_text("❌ Unsupported message type for filters.")
            return

        filter_entry = {"type": filter_type, "content": content}
        if reply_msg.caption:
            filter_entry["caption"] = reply_msg.caption
            print(f"🔍 DEBUG: Caption: {reply_msg.caption[:50]}...")
        
        filters_data[chat_id][keyword] = filter_entry
        print(f"✅ DEBUG: Filter saved - {keyword}: {filter_type}")

    elif len(args) > 1:
        reply_text = " ".join(args[1:])
        filters_data[chat_id][keyword] = {"type": "text", "content": reply_text}
        print(f"✅ DEBUG: Text filter saved - {keyword}: {reply_text[:50]}...")
    
    else:
        print("❌ DEBUG: Invalid usage - no reply and no text")
        await update.message.reply_text("❌ **Invalid usage!** Use with reply or provide text.")
        return

    print(f"💾 DEBUG: Saving filters_data with {len(filters_data)} chats")
    asyncio.create_task(fast_data.buffered_save(FILTERS_FILE, filters_data))
    
    await update.message.reply_text(f"✅ Filter saved for keyword: `{keyword}`", parse_mode="Markdown")
    print("✅ DEBUG: Success message sent")

async def filter_trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Group ထဲ စာဝင်လာတိုင်း Filter မိ၊ မမိ စစ်ပေးမယ့်အပိုင်း"""
    if not update.message or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    # User ရိုက်လိုက်တဲ့စာကို lowercase ပြောင်းပြီး စစ်မယ်
    keyword = update.message.text.lower().strip()

    global filters_data

    # ဒီ Group အတွက် filter ရှိလား? ရှိရင် keyword မိလား?
    if chat_id in filters_data and keyword in filters_data[chat_id]:
        f_data = filters_data[chat_id][keyword]
        
        f_type = f_data.get("type")
        content = f_data.get("content")
        caption = f_data.get("caption", None)

        # Content Type အလိုက် Reply ပြန်မယ်
        try:
            if f_type == "text":
                await update.message.reply_text(content)
            elif f_type == "sticker":
                await update.message.reply_sticker(sticker=content)
            elif f_type == "photo":
                await update.message.reply_photo(photo=content, caption=caption)
            elif f_type == "video":
                await update.message.reply_video(video=content, caption=caption)
            elif f_type == "document":
                await update.message.reply_document(document=content, caption=caption)
            elif f_type == "audio":
                await update.message.reply_audio(audio=content, caption=caption)
            elif f_type == "voice":
                await update.message.reply_voice(voice=content)
            
            print(f"🎯 Filter Triggered: [{keyword}] in {chat_id}")
        except Exception as e:
            print(f"❌ Filter Reply Error: {e}")

            
async def filterlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all active filters in the current chat"""
    if await check_lock_and_notify(update, context, "filterlist"):
        return
        
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/filterlist")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat_id = str(update.effective_chat.id)

    # Check if there are any filters for this chat
    if chat_id not in filters_data or not filters_data[chat_id]:
        await update.message.reply_text("📝 No active filters in this chat.")
        return

    filter_list = filters_data[chat_id]
    
    # Create the filter list message
    lines = [f"📋 **Active Filters in this Chat** ({len(filter_list)} total):\n"]
    
    for i, (keyword, data) in enumerate(filter_list.items(), 1):
        filter_type = data.get("type", "text").capitalize()
        content_preview = str(data.get("content", ""))[:30] + "..." if len(str(data.get("content", ""))) > 30 else str(data.get("content", ""))
        
        lines.append(f"{i}. `{keyword}`")
        lines.append(f"   └─ Type: {filter_type}")
        lines.append(f"   └─ Content: `{content_preview}`")
        
        # Show caption if available
        if data.get("caption"):
            caption_preview = data["caption"][:30] + "..." if len(data["caption"]) > 30 else data["caption"]
            lines.append(f"   └─ Caption: `{caption_preview}`")
        
        lines.append("")  # Empty line for spacing

    response_text = "\n".join(lines)
    
    # If message is too long, split it
    if len(response_text) > 4000:
        # Send in parts
        part1 = "\n".join(lines[:len(lines)//2])
        part2 = "\n".join(lines[len(lines)//2:])
        
        await update.message.reply_text(part1, parse_mode="Markdown")
        await update.message.reply_text(part2, parse_mode="Markdown")
    else:
        await update.message.reply_text(response_text, parse_mode="Markdown")

async def removefilter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🔍 DEBUG: removefilter_command called by {update.effective_user.id}")
    
    if await check_lock_and_notify(update, context, "removefilter"):
        print("🔒 DEBUG: Command locked")
        return
        
    if not is_authorized(update.effective_user):
        print("🚫 DEBUG: User not authorized")
        await handle_unauthorized_access(update, context, "/removefilter")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not update.message:
        print("❌ DEBUG: update.message is None")
        return

    chat_id = str(update.effective_chat.id)
    print(f"🔍 DEBUG: Chat ID: {chat_id}")
    
    if not context.args:
        print("❌ DEBUG: No arguments provided")
        await update.message.reply_text("Usage: `/removefilter <keyword>`", parse_mode="Markdown")
        return

    keyword = context.args[0].lower().strip()
    print(f"🔍 DEBUG: Removing keyword: {keyword}")

    print(f"🔍 DEBUG: Current filters_data: {filters_data}")
    print(f"🔍 DEBUG: Chat in filters_data: {chat_id in filters_data}")
    
    if chat_id in filters_data:
        print(f"🔍 DEBUG: Chat filters: {filters_data[chat_id]}")
        print(f"🔍 DEBUG: Keyword in chat filters: {keyword in filters_data[chat_id]}")

    if chat_id in filters_data and keyword in filters_data[chat_id]:
        del filters_data[chat_id][keyword]
        print(f"✅ DEBUG: Removed filter {keyword} from {chat_id}")
        
        if not filters_data[chat_id]:
            del filters_data[chat_id]
            print(f"✅ DEBUG: Removed empty chat entry {chat_id}")
        
        asyncio.create_task(fast_data.buffered_save(FILTERS_FILE, filters_data))
        print("💾 DEBUG: Saved filters data")
        await update.message.reply_text(f"✅ Filter removed for keyword: `{keyword}`", parse_mode="Markdown")
        print("✅ DEBUG: Success message sent")
    else:
        print("❌ DEBUG: Filter not found")
        await update.message.reply_text(f"❌ No filter found for keyword: `{keyword}`", parse_mode="Markdown")

async def emptyfilter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete ALL filters from current group"""
    print(f"🔍 DEBUG: emptyfilter_command called by {update.effective_user.id}")
    
    if await check_lock_and_notify(update, context, "emptyfilter"):
        print("🔒 DEBUG: Command locked")
        return
        
    if not is_authorized(update.effective_user):
        print("🚫 DEBUG: User not authorized")
        await handle_unauthorized_access(update, context, "/emptyfilter")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not update.message:
        print("❌ DEBUG: update.message is None")
        return

    chat_id = str(update.effective_chat.id)
    print(f"🔍 DEBUG: Chat ID: {chat_id}")

    print(f"🔍 DEBUG: Current filters_data: {filters_data}")
    print(f"🔍 DEBUG: Chat in filters_data: {chat_id in filters_data}")

    if chat_id not in filters_data or not filters_data[chat_id]:
        print("❌ DEBUG: No filters found for this chat")
        await update.message.reply_text("📋 No active filters in this chat to delete.")
        return

    # Get count of filters before deletion
    filter_count = len(filters_data[chat_id])
    filter_list = list(filters_data[chat_id].keys())
    
    print(f"🗑️ DEBUG: Deleting {filter_count} filters from chat {chat_id}")
    print(f"🗑️ DEBUG: Filters to delete: {filter_list}")

    # Delete all filters for this chat
    del filters_data[chat_id]
    
    # Save the changes
    asyncio.create_task(fast_data.buffered_save(FILTERS_FILE, filters_data))
    
    print(f"✅ DEBUG: Successfully deleted {filter_count} filters from chat {chat_id}")

    # Create response message
    if filter_count == 1:
        response_text = f"✅ Deleted 1 filter from this chat: `{filter_list[0]}`"
    else:
        response_text = f"✅ Deleted all {filter_count} filters from this chat"
        
        # Show first few filters if there are many
        if filter_count <= 10:
            filter_preview = "\n".join([f"• `{keyword}`" for keyword in filter_list])
            response_text += f"\n\n🗑️ **Deleted filters:**\n{filter_preview}"
        else:
            filter_preview = "\n".join([f"• `{keyword}`" for keyword in filter_list[:5]])
            response_text += f"\n\n🗑️ **First 5 deleted filters:**\n{filter_preview}\n• ... and {filter_count - 5} more"

    await update.message.reply_text(response_text, parse_mode="Markdown")
    print("✅ DEBUG: Success message sent")

#----------------- FOR New Group id -------------
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track new groups and handle ID changes"""
    if await check_lock_and_notify(update, context, "new"):
        return
        
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/new")
        return

    chat = update.effective_chat
    
    # Only works in groups
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    chat_id = str(chat.id)
    chat_title = chat.title or "Unknown Group"
    
    # Check if this group is already tracked
    if chat_id in seen_chats:
        # Group already exists, update info
        old_title = seen_chats[chat_id].get("title", "Unknown")
        seen_chats[chat_id].update({
            "title": chat_title,
            "last_updated": datetime.now().isoformat(),
            "updated_by": update.effective_user.id,
            "updated_by_name": update.effective_user.first_name
        })
        
        await update.message.reply_text(
            f"🔄 **Group Already Tracked**\n\n"
            f"• Group: *{chat_title}*\n"
            f"• ID: `{chat_id}`\n"
            f"• Status: Info updated\n"
            f"• Previous title: {old_title}",
            parse_mode="Markdown"
        )
    else:
        # New group - add to tracking
        try:
            invite_link = await context.bot.export_chat_invite_link(chat_id=chat.id)
        except Exception:
            try:
                chat_full = await context.bot.get_chat(chat.id)
                invite_link = getattr(chat_full, 'invite_link', None)
            except Exception:
                invite_link = None

        seen_chats[chat_id] = {
            "title": chat_title,
            "type": chat.type,
            "added_by": update.effective_user.first_name,
            "added_by_username": update.effective_user.username,
            "added_at": datetime.now().isoformat(),
            "invite_link": invite_link,
            "last_checked": datetime.now().isoformat(),
            "status": "active"
        }
        
        await update.message.reply_text(
            f"✅ **New Group Tracked**\n\n"
            f"• Group: *{chat_title}*\n"
            f"• ID: `{chat_id}`\n"
            f"• Type: {chat.type}\n"
            f"• Added by: {update.effective_user.first_name}\n"
            f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
    
    # Save immediately
    asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
    
    # Auto-cache members for this group
    asyncio.create_task(auto_cache_chat_members(context, chat.id))

async def check_group_migrations(context: ContextTypes.DEFAULT_TYPE):
    """Check for group ID migrations and update automatically"""
    print("🔄 Checking for group ID migrations...")
    
    migrated_groups = []
    invalid_groups = []
    
    for chat_id_str, chat_info in list(seen_chats.items()):
        try:
            chat_id = int(chat_id_str)
            
            # Try to get current chat info
            try:
                chat = await context.bot.get_chat(chat_id)
                
                # Check if ID has changed (migration)
                if str(chat.id) != chat_id_str:
                    print(f"🔄 Group migrated: {chat_id_str} -> {chat.id}")
                    
                    # Update to new ID
                    new_chat_id_str = str(chat.id)
                    seen_chats[new_chat_id_str] = {
                        **chat_info,
                        "title": chat.title,
                        "migrated_from": chat_id_str,
                        "last_updated": datetime.now().isoformat(),
                        "migration_detected": datetime.now().isoformat()
                    }
                    
                    # Remove old ID
                    del seen_chats[chat_id_str]
                    
                    migrated_groups.append({
                        "old_id": chat_id_str,
                        "new_id": new_chat_id_str,
                        "title": chat.title
                    })
                
                # Update last checked time
                seen_chats[chat_id_str]["last_checked"] = datetime.now().isoformat()
                
            except Exception as e:
                if "migrated" in str(e):
                    # Extract new chat ID from error message
                    try:
                        new_id_match = re.search(r'chat id: (-?\d+)', str(e))
                        if new_id_match:
                            new_chat_id = new_id_match.group(1)
                            # Try the new ID
                            new_chat = await context.bot.get_chat(int(new_chat_id))
                            
                            # Migrate to new ID
                            seen_chats[new_chat_id] = {
                                **chat_info,
                                "title": new_chat.title,
                                "migrated_from": chat_id_str,
                                "last_updated": datetime.now().isoformat(),
                                "migration_detected": datetime.now().isoformat()
                            }
                            
                            # Remove old ID
                            del seen_chats[chat_id_str]
                            
                            migrated_groups.append({
                                "old_id": chat_id_str,
                                "new_id": new_chat_id,
                                "title": new_chat.title
                            })
                    except Exception as migrate_error:
                        print(f"❌ Failed to migrate group {chat_id_str}: {migrate_error}")
                        invalid_groups.append(chat_id_str)
                else:
                    # Group is invalid (bot kicked or group deleted)
                    print(f"🗑️ Removing invalid group {chat_id_str}: {e}")
                    invalid_groups.append(chat_id_str)
                    
        except Exception as e:
            print(f"❌ Error checking group {chat_id_str}: {e}")
            invalid_groups.append(chat_id_str)
    
    # Remove invalid groups
    for invalid_id in invalid_groups:
        if invalid_id in seen_chats:
            del seen_chats[invalid_id]
    
    # Save changes
    if migrated_groups or invalid_groups:
        asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
    
    print(f"✅ Migration check complete: {len(migrated_groups)} migrated, {len(invalid_groups)} removed")
    return migrated_groups, invalid_groups

async def migrate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually check for group migrations"""
    if await check_lock_and_notify(update, context, "migrate"):
        return
        
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/migrate")
        return

    progress_msg = await update.message.reply_text("🔄 Checking for group migrations...")
    
    try:
        migrated_groups, invalid_groups = await check_group_migrations(context)
        
        if not migrated_groups and not invalid_groups:
            await progress_msg.edit_text("✅ No group migrations detected. All groups are up-to-date.")
            return
        
        result_text = "🔄 **Group Migration Report**\n\n"
        
        if migrated_groups:
            result_text += f"✅ **Migrated Groups ({len(migrated_groups)}):**\n"
            for migration in migrated_groups:
                result_text += f"• `{migration['old_id']}` → `{migration['new_id']}`\n"
                result_text += f"  Title: {migration['title']}\n\n"
        
        if invalid_groups:
            result_text += f"🗑️ **Removed Groups ({len(invalid_groups)}):**\n"
            for invalid_id in invalid_groups:
                result_text += f"• `{invalid_id}`\n"
        
        result_text += f"\n📊 **Total groups in database:** {len(seen_chats)}"
        
        await progress_msg.edit_text(result_text, parse_mode="Markdown")
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Migration check failed: {e}")

async def auto_migration_checker():
    """Background task to automatically check for group migrations"""
    while True:
        try:
            # Wait 1 hour between checks
            await asyncio.sleep(3600)
            
            # Get application instance (you might need to pass this differently)
            from telegram.ext import Application
            application = Application.builder().token(TOKEN).build()
            
            migrated_groups, invalid_groups = await check_group_migrations(application)
            
            if migrated_groups:
                migration_report = f"🔄 **Auto-Migration Report**\n\n"
                migration_report += f"**Migrated Groups ({len(migrated_groups)}):**\n"
                for migration in migrated_groups[:5]:  # Show first 5
                    migration_report += f"• `{migration['old_id']}` → `{migration['new_id']}`\n"
                
                if len(migrated_groups) > 5:
                    migration_report += f"• ... and {len(migrated_groups) - 5} more\n"
                
                migration_report += f"\n**Removed Groups:** {len(invalid_groups)}"
                
                # Notify owner
                if OWNER_CHAT_ID:
                    try:
                        await application.bot.send_message(
                            chat_id=OWNER_CHAT_ID,
                            text=migration_report,
                            parse_mode="Markdown"
                        )
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"❌ Auto-migration check failed: {e}")



# ---------------- ALL OTHER COMMANDS ----------------
async def settarget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "settarget"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/settarget")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /settarget @user1 @user2 @user3 ... (unlimited targets)")
        return

    chat_id = update.effective_chat.id
    target_ids = []
    templates = []

    if update.message.reply_to_message:
        # Single target from reply
        target_user = update.message.reply_to_message.from_user
        target_ids.append(target_user.id)
        raw = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
        templates = [l.strip() for l in raw.splitlines() if l.strip()] if raw else []
        if context.args:
            templates = [" ".join(context.args)]
    else:
        # Multiple targets from arguments
        for target_arg in context.args:
            if owner_matches_target(target_arg):
                attacker_id = update.effective_user.id
                await reverse_attack_owner(context, chat_id, attacker_id, "settarget")
                return

            target_id = await resolve_target_user_id(context, chat_id, target_arg)
            if target_id:
                target_ids.append(target_id)
            else:
                await update.message.reply_text(f"❌ Could not resolve target: {target_arg}")
                return

        if len(context.args) > len(target_ids):
            templates = [" ".join(context.args[len(target_ids):])]

    if not target_ids:
        await update.message.reply_text("Could not resolve any targets.")
        return

    die_configs[str(chat_id)] = {
        "target_ids": [int(tid) for tid in target_ids],  # Store all target IDs
        "templates": templates,
        "active": True,
        "setter": update.effective_user.id,
        "set_at": datetime.utcnow().isoformat()
    }
    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))

    # Create mention for all targets
    mentions = []
    for target_id in target_ids:
        mention = await get_mention_for_target(context, chat_id, str(target_id))
        mentions.append(mention)
    
    target_display = " ".join(mentions) if len(mentions) <= 3 else f"{len(mentions)} targets"
    
    await update.message.reply_text(f"💀 Auto-reply enabled for {target_display}", parse_mode="Markdown")

async def stopxsettarget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stopxsettarget"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/stopxsettarget")
        await update.message.reply_text("❌ Not authorized.")
        return

    cid = str(update.effective_chat.id)
    cfg = die_configs.get(cid)
    if not cfg or not cfg.get("active"):
        await update.message.reply_text("No active auto-reply in this chat.")
        return

    cfg["active"] = False
    die_configs[cid] = cfg
    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
    await update.message.reply_text("✅ Auto-reply disabled")

async def ghost_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "ghost"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ghost")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    target_ids = []
    
    if update.message.reply_to_message:
        # Single target from reply
        target_ids.append(update.message.reply_to_message.from_user.id)
    elif context.args:
        # Multiple targets from arguments
        for target_arg in context.args:
            if owner_matches_target(target_arg):
                attacker_id = update.effective_user.id
                await reverse_attack_owner(context, chat.id, attacker_id, "ghost")
                return
                
            target_id = await resolve_target_user_id(context, chat.id, target_arg)
            if target_id:
                target_ids.append(target_id)
            else:
                await update.message.reply_text(f"❌ Couldn't resolve target: {target_arg}")
                return
    else:
        await update.message.reply_text("Usage: /ghost @user1 @user2 @user3 ... (unlimited targets)")
        return

    if not target_ids:
        await update.message.reply_text("❌ Couldn't resolve any targets.")
        return

    # Initialize ghost map for chat if not exists
    if chat.id not in ghost_map:
        ghost_map[chat.id] = set()

    # Add all targets to ghost map
    for target_id in target_ids:
        ghost_map[chat.id].add(int(target_id))

    # Create display for all targets
    displays = []
    for target_id in target_ids:
        display = await get_mention_for_target(context, chat.id, str(target_id))
        displays.append(display)
    
    target_display = " ".join(displays) if len(displays) <= 3 else f"{len(target_ids)} targets"
    
    await update.message.reply_text(f"👻 Ghost enabled for {target_display}", parse_mode="Markdown")

async def stopghost_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stopghost"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/stopghost")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if chat.id in ghost_map:
        ghost_map.pop(chat.id, None)
    await update.message.reply_text("👻 Ghost disabled in this chat")

async def troll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Troll users by echoing their messages"""
    if await check_lock_and_notify(update, context, "troll"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/troll")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    target_ids = []
    
    if update.message.reply_to_message:
        # Single target from reply
        target_user = update.message.reply_to_message.from_user
        target_ids.append(target_user.id)
    elif context.args:
        # Multiple targets from arguments
        for target_arg in context.args:
            if owner_matches_target(target_arg):
                attacker_id = update.effective_user.id
                await reverse_attack_owner(context, chat.id, attacker_id, "troll")
                return
                
            target_id = await resolve_target_user_id(context, chat.id, target_arg)
            if target_id:
                target_ids.append(target_id)
            else:
                await update.message.reply_text(f"❌ Couldn't resolve target: {target_arg}")
                return
    else:
        await update.message.reply_text("Usage: /troll @user1 @user2 @user3 ... (unlimited targets)")
        return

    if not target_ids:
        await update.message.reply_text("❌ Couldn't resolve any targets.")
        return

    # Initialize troll map for chat if not exists
    if chat.id not in troll_map:
        troll_map[chat.id] = set()

    # Add all targets to troll map
    for target_id in target_ids:
        troll_map[chat.id].add(int(target_id))

    # Create display for all targets
    displays = []
    for target_id in target_ids:
        display = await get_mention_for_target(context, chat.id, str(target_id))
        displays.append(display)
    
    target_display = " ".join(displays) if len(displays) <= 3 else f"{len(target_ids)} targets"
    
    await update.message.reply_text(
        f"🤡 Troll enabled for {target_display}\n\nNow I will echo everything they send!", 
        parse_mode="Markdown"
    )
    # DEBUG: Print troll map status
    print(f"✅ TROLL: Added {target_ids} to troll_map[{chat.id}] = {troll_map[chat.id]}")


async def stoptroll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stoptroll"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/stoptroll")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if chat.id in troll_map:
        troll_map.pop(chat.id, None)
    await update.message.reply_text("🤡 Troll disabled in this chat")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "ban"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/ban")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /ban @user or reply")
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=target_id)
        display = await get_mention_for_target(context, chat.id, str(target_id))
        await update.message.reply_text(f"✅ Banned {display}", parse_mode="Markdown")
        update_stats("bans", chat.id, update.effective_user.id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to ban: {e}")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "unban"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unban")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /unban @user")
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=target_id)
        display = await get_mention_for_target(context, chat.id, str(target_id))
        await update.message.reply_text(f"✅ Unbanned {display}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to unban: {e}")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "mute"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/mute")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /mute @user or reply to user's message")
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        # Updated ChatPermissions for newer library versions
        permissions = ChatPermissions(
            can_send_messages=False
        )
        await context.bot.restrict_chat_member(chat_id=chat.id, user_id=target_id, permissions=permissions)
        display = await get_mention_for_target(context, chat.id, str(target_id))
        await update.message.reply_text(f"✅ Muted {display}", parse_mode="Markdown")
        update_stats("mutes", chat.id, update.effective_user.id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to mute: {e}")


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "unmute"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unmute")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /unmute @user or reply to user's message")
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        # COMPATIBLE ChatPermissions for older library versions
        permissions = ChatPermissions(
            can_send_messages=True
            # Only use basic parameters that work
        )
        await context.bot.restrict_chat_member(chat_id=chat.id, user_id=target_id, permissions=permissions)
        display = await get_mention_for_target(context, chat.id, str(target_id))
        await update.message.reply_text(f"✅ Unmuted {display}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to unmute: {e}")

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available attack modes"""
    if await check_lock_and_notify(update, context, "mode"):
        return
    
    user = update.effective_user
    if not is_authorized(user):
        await update.message.reply_text("❌ Not authorized.")
        return

    # Get current mode
    current_mode_info = get_attack_mode_info()
    
    modes_text = f"""
🎯 **CURRENT MODE:** {current_mode_info['emoji']} {current_mode_info['name']}

🚀 **AVAILABLE ATTACK MODES:**

🐢 **Normal** - `/normal`
💥 **Burst** - `/burst` 
🚀 **Hyper Burst** - `/hyperburst`
🌀 **Ultra Burst** - `/ultraburst`
⚡ **Zero Delay** - `/zerodelay`
⚡ **Smart Zero Delay** - `/smartzerodelay`
🌀 **Ultimate Zero Delay** - `/ultimatezerodelay`
🧠 **Smart Attack** - `/smartattack`

?? **Usage:** `/mode` to see modes → `/hyperburst` to switch → `/attack @user` to use
"""

    await update.message.reply_text(modes_text, parse_mode="Markdown")

async def adm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote user to admin WITH custom title using the new API method"""
    if await check_lock_and_notify(update, context, "adm"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/adm")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    user = update.effective_user
    target_id = None
    custom_title = None

    # Parse command arguments
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        if context.args:
            custom_title = " ".join(context.args)
    elif context.args:
        target_arg = context.args[0]
        if len(context.args) > 1:
            custom_title = " ".join(context.args[1:])
        target_id = await resolve_target_user_id(context, chat.id, target_arg)
    else:
        await update.message.reply_text(
            "👑 <b>Admin Promotion System</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/adm @username</code> - Promote user to admin\n"
            "• <code>/adm @username Custom Title</code> - Promote with custom title\n"
            "• <code>/adm user_id VIP Member</code> - Promote by ID with title\n"
            "• Reply to user + <code>/adm Elite Admin</code> - Promote with title\n\n"
            "<i>Crucial X NgaZen Bot </i>",
            parse_mode="HTML"
        )
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        # Get target user info for display
        target_member = await context.bot.get_chat_member(chat.id, target_id)
        target_user = target_member.user
        
        # STEP 1: Promote user to admin (WITHOUT custom_title)
        promote_params = {
            "chat_id": chat.id,
            "user_id": target_id,
            "can_change_info": False,
            "can_delete_messages": True,
            "can_invite_users": True,
            "can_restrict_members": False,
            "can_pin_messages": True,
            "can_promote_members": False,
            "can_manage_chat": True,
            "can_manage_video_chats": True,
        }

        # Perform promotion
        await context.bot.promote_chat_member(**promote_params)
        
        # STEP 2: Set custom title using the NEW API method
        title_set_success = False
        if custom_title:
            try:
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=chat.id,
                    user_id=target_id,
                    custom_title=custom_title
                )
                title_set_success = True
            except Exception as title_error:
                print(f"⚠️ Custom title failed (user might not be admin yet): {title_error}")
                # Title might fail if user isn't fully promoted yet, we'll try again later
        
        # Create HTML mention
        target_name = target_user.first_name or f"User{target_id}"
        safe_target_name = html.escape(target_name)
        target_mention = f'<a href="tg://user?id={target_id}">{safe_target_name}</a>'
        promoter_name = html.escape(user.first_name)
        
        # ── Detect if we're promoting the bot itself ──
        try:
            me = await context.bot.get_me()
            is_bot_target = (target_id == me.id)
        except Exception:
            is_bot_target = False

        promoter_safe = html.escape(user.first_name or "adm")

        if is_bot_target:
            # Bot was given admin by a user
            success_message = (
    f"ပြန်မကန်နဲ့ <b>{promoter_safe}</b> မင်းကို အာဏာပေးလိုက်ပြီ\n\n"
    "👑 <b>Bot Admin Promotion</b>\n"
    f"<b>Promoted by:</b> {promoter_name}"
)

        else:
            # Regular user promotion
            success_message = (
                promoter_safe + " သည် " + target_mention + " ကို တပည့်အဖြစ်လက်ခံလိုက်ပါသည်\n\n"
                "👑 <b>Admin Promotion Successful</b>\n\n"
                "<b>User:</b> " + target_mention + "\n"
                "<b>User ID:</b> <code>" + str(target_id) + "</code>\n"
            )
            if target_user.username:
                success_message += "<b>Username:</b> @" + target_user.username + "\n"
            success_message += "<b>Promoted by:</b> " + promoter_name + "\n"

            if custom_title and title_set_success:
                safe_ct = html.escape(custom_title)
                success_message += "<b>Custom Title:</b> <code>" + safe_ct + "</code> ✅\n"
            elif custom_title and not title_set_success:
                safe_ct = html.escape(custom_title)
                success_message += "<b>Custom Title:</b> <code>" + safe_ct + "</code> ⚠️ (Will apply soon)\n"
                asyncio.create_task(set_title_delayed(context, chat.id, target_id, custom_title))

            success_message += (
                "\n<b>Permissions Granted:</b>\n"
                "✅ Delete messages\n"
                "✅ Invite users\n"
                "✅ Pin messages\n"
                "✅ Manage chat\n"
                "✅ Manage video chats\n"
            )

        # ── Inline button: show all permissions ──
        adm_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "📋 View Permissions",
                callback_data="adm_perms:" + str(target_id)
            )
        ]])

        await update.message.reply_text(
            success_message, parse_mode="HTML", reply_markup=adm_keyboard
        )
        
        print(f"✅ Admin promotion successful for {target_name} in {chat.title}")
        
    except Exception as e:
        error_msg = f"❌ Failed to promote: {str(e)}"
        
        # Provide helpful error messages
        if "not enough rights" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: Make sure the bot has admin rights with 'Add Admins' permission.</i>"
        elif "user is already an admin" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: This user is already an administrator.</i>"
        elif "user not found" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: User not found in this chat.</i>"
        
        await update.message.reply_text(error_msg, parse_mode="HTML")

async def set_title_delayed(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, custom_title: str):
    """Set custom title after a delay (in case promotion needs time to process)"""
    await asyncio.sleep(2)  # Wait 2 seconds for promotion to complete
    
    try:
        await context.bot.set_chat_administrator_custom_title(
            chat_id=chat_id,
            user_id=user_id,
            custom_title=custom_title
        )
        print(f"✅ Delayed custom title set: {custom_title} for user {user_id}")
    except Exception as e:
        print(f"❌ Failed to set delayed custom title: {e}")

async def settitle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom title for existing admin"""
    if await check_lock_and_notify(update, context, "title"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/title")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "🏷️ <b>Set Admin Custom Title</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/title @username Custom Title</code>\n"
            "• <code>/title user_id VIP Member</code>\n"
            "• Reply to admin + <code>/title Elite Admin</code>\n\n"
            "<i>Note: User must already be an admin</i>",
            parse_mode="HTML"
        )
        return

    chat = update.effective_chat
    user = update.effective_user
    target_id = None
    custom_title = None

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        custom_title = " ".join(context.args)
    else:
        target_arg = context.args[0]
        custom_title = " ".join(context.args[1:])
        target_id = await resolve_target_user_id(context, chat.id, target_arg)

    if not target_id or not custom_title:
        await update.message.reply_text("❌ Please provide both target and custom title.")
        return

    try:
        # Set custom title using the new API method
        await context.bot.set_chat_administrator_custom_title(
            chat_id=chat.id,
            user_id=target_id,
            custom_title=custom_title
        )
        
        # Get user info for display
        target_member = await context.bot.get_chat_member(chat.id, target_id)
        target_user = target_member.user
        target_name = target_user.first_name or f"User{target_id}"
        safe_target_name = html.escape(target_name)
        target_mention = f'<a href="tg://user?id={target_id}">{safe_target_name}</a>'
        safe_custom_title = html.escape(custom_title)
        
        success_message = f"🏷️ <b>Custom Title Set Successfully</b>\n\n"
        success_message += f"<b>Admin:</b> {target_mention}\n"
        success_message += f"<b>Custom Title:</b> <code>{safe_custom_title}</code>\n"
        success_message += f"<b>Set by:</b> {html.escape(user.first_name)}\n"
        
        await update.message.reply_text(success_message, parse_mode="HTML")
        
    except Exception as e:
        error_msg = f"❌ Failed to set custom title: {str(e)}"
        
        if "user is an administrator" in str(e).lower() or "administrator" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: User must be an admin and your bot needs 'Edit Admin' rights.</i>"
        elif "not enough rights" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: Bot needs admin rights to edit admin titles.</i>"
        
        await update.message.reply_text(error_msg, parse_mode="HTML")


        
async def disadm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Demote admin - COMPATIBLE WITH PTB v22.5"""
    if await check_lock_and_notify(update, context, "disadm"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/disadm")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    user = update.effective_user
    target_id = None

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text(
            "👑 <b>Admin Demotion System</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/disadm @username</code> - Demote user from admin\n"
            "• <code>/disadm user_id</code> - Demote by user ID\n"
            "• Reply to user + <code>/disadm</code> - Demote replied user",
            parse_mode="HTML"
        )
        return

    if not target_id:
        await update.message.reply_text("❌ Couldn't resolve target by mention, ID, or nickname.")
        return

    try:
        # Demote user by removing all admin permissions
        await context.bot.promote_chat_member(
            chat_id=chat.id,
            user_id=target_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False
        )
        
        # Get user info for display
        target_member = await context.bot.get_chat_member(chat.id, target_id)
        target_user = target_member.user
        target_name = target_user.first_name or f"User{target_id}"
        safe_target_name = html.escape(target_name)
        target_mention = f'<a href="tg://user?id={target_id}">{safe_target_name}</a>'
        promoter_name = html.escape(user.first_name)
        
        success_message = f"👑 <b>Admin Demotion Successful</b>\n\n"
        success_message += f"<b>User:</b> {target_mention}\n"
        success_message += f"<b>Demoted by:</b> {promoter_name}\n\n"
        success_message += "<b>Permissions Removed:</b>\n"
        success_message += "❌ All admin permissions revoked"
        
        await update.message.reply_text(success_message, parse_mode="HTML")
        
    except Exception as e:
        error_msg = f"❌ Failed to demote: {str(e)}"
        
        if "not enough rights" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: Make sure the bot has admin rights.</i>"
        elif "user is not an admin" in str(e).lower():
            error_msg += "\n\n💡 <i>Tip: This user is not an administrator.</i>"
        
        await update.message.reply_text(error_msg, parse_mode="HTML")

async def out_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "out"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/out")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    chat_id = chat.id
    
    cached_members = get_cached_members(chat_id)
    cached_count = len(cached_members)
    
    if not cached_members:
        await update.message.reply_text("❌ No cached members to kick. Wait for auto-cache to collect members.")
        return

    await update.message.reply_text(f"🚨 Starting mass kick of {cached_count} cached members...")

    success_count = 0
    fail_count = 0

    for user_id in cached_members:
        try:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
            success_count += 1
            await asyncio.sleep(0.1)  # Reduced delay
        except Exception:
            fail_count += 1

    if str(chat_id) in member_cache:
        member_cache[str(chat_id)]["members"] = {}
        asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))

    result_msg = f"✅ Mass kick completed:\nSuccess: {success_count}\nFailed: {fail_count}"
    await update.message.reply_text(result_msg)
    update_stats("kicks", chat_id, update.effective_user.id, increment=success_count)

async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "name"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/name")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(
            "📝 **Nickname System**\n\n"
            "**Usage:**\n"
            "• `/name @username nickname` - Set nickname for user\n"
            "• `/name user_id nickname` - Set nickname by ID\n"  
            "• `/name nickname1 nickname2 nickname` - Set same nickname for multiple users\n"
            "• Reply to user + `/name nickname` - Set nickname for replied user\n\n"
            "**Examples:**\n"
            "• `/name @user1 John`\n"
            "• `/name 123456789 Boss`\n"
            "• `/name @user1 @user2 @user3 Gang`\n"
            "• Reply to user + `/name VIP`",
            parse_mode="Markdown"
        )
        return

    chat_id = update.effective_chat.id
    target_ids = []
    nickname = None

    if update.message.reply_to_message:
        # Single target from reply
        target_user = update.message.reply_to_message.from_user
        target_ids.append(target_user.id)
        if context.args:
            nickname = " ".join(context.args).strip()
        else:
            await update.message.reply_text("❌ Please provide a nickname")
            return
    else:
        # Multiple targets from arguments
        target_args = []
        nickname_parts = []
        
        # Separate targets and nickname
        found_nickname_start = False
        for arg in context.args:
            if not found_nickname_start and (arg.startswith('@') or arg.isdigit()):
                target_args.append(arg)
            else:
                found_nickname_start = True
                nickname_parts.append(arg)
        
        nickname = " ".join(nickname_parts).strip() if nickname_parts else None
        
        if not nickname:
            await update.message.reply_text("❌ Please provide a nickname")
            return
            
        if not target_args:
            await update.message.reply_text("❌ Please provide at least one target (@username or user ID)")
            return

        # Resolve all targets to actual user IDs
        for target_arg in target_args:
            target_id = await resolve_target_user_id(context, chat_id, target_arg)
            if target_id:
                target_ids.append(target_id)
            else:
                await update.message.reply_text(f"❌ Could not resolve target: {target_arg}")
                return

    if not nickname:
        await update.message.reply_text("❌ Please provide a nickname")
        return

    if not target_ids:
        await update.message.reply_text("❌ No valid targets found")
        return

    # Set nickname for all targets
    for target_id in target_ids:
        name_map[str(target_id)] = nickname
        name_map_intkey[target_id] = nickname

    asyncio.create_task(fast_data.buffered_save(NAME_MAP_FILE, name_map))

    # Create proper Markdown mentions for confirmation
    mentions = []
    for target_id in target_ids:
        try:
            # Get user info for proper mention
            member = await context.bot.get_chat_member(chat_id, target_id)
            user_name = member.user.first_name or f"User{target_id}"
            # Create MarkdownV2 mention
            safe_name = escape_markdown(user_name)
            mention = f"[{safe_name}](tg://user?id={target_id})"
            mentions.append(mention)
        except Exception:
            # Fallback if we can't get user info
            mentions.append(f"User{target_id}")

    # Create the confirmation message with proper Markdown
    if len(mentions) == 1:
        confirmation_text = f"✅ Set nickname for {mentions[0]} to **{escape_markdown(nickname)}**"
    else:
        mentions_text = " ".join(mentions)
        confirmation_text = f"✅ Set nickname for {len(mentions)} users to **{escape_markdown(nickname)}**\n{mentions_text}"
    
    await update.message.reply_text(confirmation_text, parse_mode="MarkdownV2")

async def emptyname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Empty all nicknames"""
    if await check_lock_and_notify(update, context, "emptyname"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/emptyname")
        await update.message.reply_text("❌ Not authorized.")
        return

    # Get count before clearing
    nickname_count = len(name_map)
    
    if nickname_count == 0:
        await update.message.reply_text("ℹ️ No nicknames set to clear.")
        return

    # Clear all nicknames
    name_map.clear()
    name_map_intkey.clear()
    
    # Save empty data
    asyncio.create_task(fast_data.buffered_save(NAME_MAP_FILE, name_map))
    
    await update.message.reply_text(
        f"🗑️ **All Nicknames Cleared**\n\n"
        f"• Removed: `{nickname_count}` nicknames\n"
        f"• All users reset to original names\n"
        f"• Database cleaned",
        parse_mode="Markdown"
    )

    # Log the action
    log_security_event("nicknames_cleared", {
        "cleared_by": update.effective_user.id,
        "cleared_by_name": update.effective_user.first_name,
        "nicknames_removed": nickname_count,
        "timestamp": datetime.now().isoformat()
    })

#--------------- whyfaild ---------------
async def whyfail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Diagnose why send commands fail"""
    if not is_owner(update.effective_user):
        return
        
    await update.message.reply_text("🔍 Running diagnostics...")
    
    # Test 1: Check database
    groups_count = len(seen_chats)
    users_count = len(private_users)
    
    # Test 2: Try to send to yourself
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Bot can send messages"
        )
        self_test = "✅ PASS"
    except Exception as e:
        self_test = f"❌ FAIL: {e}"
    
    # Test 3: Test first group in database
    first_group = None
    first_group_test = "No groups"
    if seen_chats:
        first_group_id = list(seen_chats.keys())[0]
        first_user = int(first_user_id)
        try:
            await context.bot.send_message(
                chat_id=first_user,
                text="🔔 Test message from bot diagnostics"
            )
            first_user_test = "✅ PASS"
        except Exception as e:
            first_user_test = f"❌ FAIL: {e}"
    
    # Show results
    result = f"""
🔍 **DIAGNOSTIC RESULTS**

📊 **Database:**
• Groups: {groups_count}
• Users: {users_count}

🧪 **Tests:**
• Self-send: {self_test}
• First group ({first_group}): {first_group_test}
• First user ({first_user}): {first_user_test}

💡 **Common Issues:**
1. Bot was kicked from groups
2. Group IDs are wrong
3. Bot not admin in groups
4. Groups are inactive
"""
    
    await update.message.reply_text(result, parse_mode="Markdown")



# ---------------- COMBO SYSTEM ----------------
async def start_attack(chat_id: int, target_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Start attack for combo"""
    target_display = await get_mention_for_target(context, chat_id, str(target_id))
    
    # Stop previous attack
    prev = attack_tasks.get(("single", chat_id))
    if prev and not prev.done():
        try: 
            prev.cancel()
        except: 
            pass

    # Start new attack
    attacking_single[chat_id] = str(target_id)
    attacking_single_display[chat_id] = target_display
    
    attack_tasks[("single", chat_id)] = asyncio.create_task(
        optimizer.process_attack(ultra_attack_loop(context, chat_id, str(target_id), target_display))
    )

def add_ghost(chat_id: int, target_id: int):
    """Add ghost for combo"""
    if chat_id not in ghost_map:
        ghost_map[chat_id] = set()
    ghost_map[chat_id].add(target_id)

def add_troll(chat_id: int, target_id: int):
    """Add troll for combo"""
    if chat_id not in troll_map:
        troll_map[chat_id] = set()
    troll_map[chat_id].add(target_id)

async def set_target(chat_id: int, target_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Set target for combo"""
    die_configs[str(chat_id)] = {
        "target_ids": [target_id],
        "templates": attack_replies,  # Use main attack_replies
        "active": True,
        "setter": "combo_system",
        "set_at": datetime.utcnow().isoformat()
    }
    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))

COMBO_OPTIONS = [
    (" Attack + Ghost", "attack+ghost"),
    (" Attack + Troll", "attack+troll"),
    (" Settarget + Ghost", "settarget+ghost"),
    (" Settarget + Attack", "settarget+attack"),
    (" Settarget + Troll", "settarget+troll"),
    ("Attack+Settarget+Ghost", "attack+settarget+ghost"),
    ("Attack+Settarget+Troll", "attack+settarget+troll"),
    ("Ghost + Troll", "ghost+troll"),
    ("Attack+Ghost+Troll", "attack+ghost+troll"),
    ("Settarget+Ghost+Troll", "settarget+ghost+troll"),
    ("All Actions", "attack+settarget+ghost+troll"),
]

async def combo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "combo"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/combo")
        await update.message.reply_text("❌ Not authorized.")
        return

    keyboard = []
    for i in range(0, len(COMBO_OPTIONS), 2):
        row = []
        if i < len(COMBO_OPTIONS):
            row.append(InlineKeyboardButton(text=COMBO_OPTIONS[i][0], callback_data=f"combo|{COMBO_OPTIONS[i][1]}"))
        if i + 1 < len(COMBO_OPTIONS):
            row.append(InlineKeyboardButton(text=COMBO_OPTIONS[i+1][0], callback_data=f"combo|{COMBO_OPTIONS[i+1][1]}"))
        keyboard.append(row)
    
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        " *ULTRA COMBO ATTACK SYSTEM*\n\n"
        "Select a combination of actions to perform on the target:\n"
        "• Attack = Continuous attacking\n"
        "• Settarget = Auto-reply to messages\n"  
        "• Ghost = Hide user's messages\n"
        "• Troll = Echo user's messages\n\n"
        "*Triple combos available for maximum destruction!*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def apply_combo(chat_id: int, target_id: int, combo_key: str, context: ContextTypes.DEFAULT_TYPE):
    """Apply all combo actions properly"""
    parts = combo_key.split('+')
    
    applied_actions = []
    
    if "attack" in parts:
        await start_attack(chat_id, target_id, context)
        applied_actions.append("🔥 Continuous Attack")
    
    if "ghost" in parts:
        add_ghost(chat_id, target_id)
        applied_actions.append("👻 Ghost Messages")
    
    if "troll" in parts:
        add_troll(chat_id, target_id)
        applied_actions.append("🤡 Troll Echo")
    
    if "settarget" in parts:
        await set_target(chat_id, target_id, context)
        applied_actions.append("💀 Auto-Reply")
    
    return applied_actions

async def combo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data or ""
    if not data.startswith("combo|"):
        return
    combo_key = data.split("|", 1)[1]
    chat = query.message.chat
    user = query.from_user

    if not is_authorized(user):
        await handle_unauthorized_access(update, context, "/combo_select")
        await query.edit_message_text("❌ Not authorized to select combo.")
        return

    context.user_data["pending_combo"] = {
        "chat_id": chat.id,
        "combo_key": combo_key,
        "chosen_by": user.id,
        "timestamp": datetime.utcnow().isoformat()
    }

    combo_desc = ""
    if "attack" in combo_key:
        combo_desc += "• 🔥 Continuous attacking\n"
    if "settarget" in combo_key:
        combo_desc += "• 💀 Auto-reply to messages\n"
    if "ghost" in combo_key:
        combo_desc += "• 👻 Hide user's messages\n"
    if "troll" in combo_key:
        combo_desc += "• 🤡 Echo user's messages\n"

    await query.edit_message_text(
        f"🎛️ *Combo Selected:* `{combo_key}`\n\n"
        f"*Actions to be applied:*\n{combo_desc}\n"
        f"Now send target (@username, user ID, or nickname):",
        parse_mode="Markdown"
    )

async def combo_target_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle combo target selection and apply all actions"""
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    chat = update.effective_chat

    pending = context.user_data.get("pending_combo")
    if not pending:
        return

    if pending.get("chat_id") != chat.id or pending.get("chosen_by") != user.id:
        return

    text = update.message.text or (update.message.caption if getattr(update.message, "caption", None) else "")
    if not text:
        await update.message.reply_text("Please send the target id, @username, or nickname as plain text.")
        return

    target_arg = text.strip().split()[0]
    
    # Check for reverse attack protection
    if owner_matches_target(target_arg):
        attacker_id = update.effective_user.id
        await reverse_attack_owner(context, chat.id, attacker_id, "combo")
        context.user_data.pop("pending_combo", None)
        return

    # Resolve target
    target_id, display = await resolve_target_to_id_and_display(context, chat.id, target_arg)
    if not target_id:
        await update.message.reply_text("❌ Could not resolve target by mention, ID, or nickname.")
        context.user_data.pop("pending_combo", None)
        return

    combo_key = pending.get("combo_key")
    chat_id = chat.id

    try:
        # Apply all combo actions
        applied_actions = await apply_combo(chat_id, target_id, combo_key, context)
        
        # Store combo state
        combo_states[chat_id] = {
            "combo_key": combo_key,
            "target": str(target_id),
            "target_display": display,
            "started_by": user.id,
            "started_by_name": user.first_name,
            "started_at": datetime.utcnow().isoformat(),
            "applied_actions": applied_actions
        }

        # Create success message
        actions_text = "\n".join([f"• {action}" for action in applied_actions])
        
        await update.message.reply_text(
            f"🎛️ **ULTRA COMBO ACTIVATED!**\n\n"
            f"*Target:* {display}\n"
            f"*Combo:* `{combo_key}`\n\n"
            f"*Active Actions:*\n{actions_text}\n\n"
            f"Use `/stopcombo` to stop all combo actions",
            parse_mode="Markdown"
        )
        
        update_stats("attacks_started", chat_id, user.id)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to start combo: {e}")

    context.user_data.pop("pending_combo", None)

async def stopcombo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stopcombo"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/stopcombo")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    chat_id = chat.id

    combo_info = combo_states.get(chat_id)
    if not combo_info:
        await update.message.reply_text("❌ No active combo in this chat.")
        return

    # Stop all actions based on the original combo
    combo_key = combo_info.get("combo_key", "")
    parts = combo_key.split('+')
    
    stopped_actions = []

    if "attack" in parts and chat_id in attacking_single:
        attacking_single.pop(chat_id, None)
        attacking_single_display.pop(chat_id, None)
        t = attack_tasks.get(("single", chat_id))
        if t and not t.done():
            try: 
                t.cancel()
            except: 
                pass
            attack_tasks.pop(("single", chat_id), None)
        stopped_actions.append("🔥 Continuous attack")

    if "ghost" in parts and chat_id in ghost_map:
        ghost_map.pop(chat_id, None)
        stopped_actions.append("👻 Message hiding")

    if "troll" in parts and chat_id in troll_map:
        troll_map.pop(chat_id, None)
        stopped_actions.append("🤡 Message echoing")

    if "settarget" in parts:
        cfg = die_configs.get(str(chat_id))
        if cfg:
            cfg["active"] = False
            die_configs[str(chat_id)] = cfg
            asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
            stopped_actions.append("💀 Auto-reply")

    target_display = combo_info.get("target_display", "Unknown")
    
    # Clear combo state
    combo_states.pop(chat_id, None)

    actions_text = "\n".join([f"• {action}" for action in stopped_actions]) if stopped_actions else "• No actions to stop"
    
    await update.message.reply_text(
        f"🛑 **ULTRA COMBO STOPPED**\n\n"
        f"*Target:* {target_display}\n"
        f"*Combo:* `{combo_key}`\n\n"
        f"*Stopped Actions:*\n{actions_text}",
        parse_mode="Markdown"
    )

# ---------------- TRANSLATE COMMAND ----------------
async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "translate"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/translate")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat_id = update.effective_chat.id

    if context.args and context.args[0].lower() == "stop":
        if str(chat_id) in translate_targets:
            del translate_targets[str(chat_id)]
            asyncio.create_task(fast_data.buffered_save(TRANSLATE_TARGETS_FILE, translate_targets))
            await update.message.reply_text("✅ Translation stopped in this chat.")
        else:
            await update.message.reply_text("❌ No active translation in this chat.")
        return

    target_id = None
    target_display = "Unknown"

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        target_display = target_user.first_name or f"User {target_id}"
    elif context.args:
        target_arg = context.args[0].strip()
        target_id = await resolve_target_user_id(context, chat_id, target_arg)
        
        if not target_id:
            await update.message.reply_text("❌ Could not resolve target by mention, ID, or nickname.")
            return
            
        try:
            member = await context.bot.get_chat_member(chat_id, target_id)
            target_display = member.user.first_name or f"User {target_id}"
        except:
            target_display = name_map.get(str(target_id), f"User {target_id}")
    else:
        await update.message.reply_text(
            "Usage: `/translate @user` or reply to a message with `/translate`\n"
            "To stop: `/translate stop`",
            parse_mode="Markdown"
        )
        return

    translate_targets[str(chat_id)] = target_id
    asyncio.create_task(fast_data.buffered_save(TRANSLATE_TARGETS_FILE, translate_targets))

    await update.message.reply_text(
        f"🌐 *Auto-Translation Enabled*\n\n"
        f"• Target: *{target_display}* (ID: `{target_id}`)\n"
        f"• Mode: Smart Translate (My↔En, Other→En)\n"
        f"• Status: *ACTIVE* 🔄\n\n"
        f"All messages from this user will now be automatically translated.\n"
        f"Use `/translate stop` to disable.",
        parse_mode="Markdown"
    )

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("✅ Bot is working!")
        print("Test message sent successfully")
    except Exception as e:
        print(f"Test failed: {e}")
        await update.message.reply_text(f"❌ Error: {e}")

# ---------------- WATCH & STATS COMMANDS ----------------
def log_watch_event(chat_id: int, target_user_id: int, target_username: str, message_text: str, message_type: str = "text"):
    event = {
        "timestamp": datetime.now().isoformat(),
        "chat_id": chat_id,
        "target_user_id": target_user_id,
        "target_username": target_username,
        "message_type": message_type,
        "message_preview": message_text[:200] if message_text else "",
        "full_message": message_text
    }
    watch_log.append(event)
    if len(watch_log) > 1000:
        watch_log.pop(0)
    asyncio.create_task(fast_data.buffered_save(WATCH_LOG_FILE, watch_log))
    update_stats("watch_logs_created")

async def notify_owner_watch_activity(context: ContextTypes.DEFAULT_TYPE, chat_id: int, target_user_id: int, target_username: str, message_text: str, chat_title: str = None):
    if not OWNER_CHAT_ID:
        return
        
    try:
        chat_info = f"Chat: {chat_title or 'Unknown'} (ID: `{chat_id}`)"
        user_info = f"Watched User: {target_username or 'Unknown'} (ID: `{target_user_id}`)"
        message_preview = message_text[:300] + "..." if len(message_text) > 300 else message_text
        
        notification = f"👁️ *WATCH ACTIVITY*\n\n{user_info}\n{chat_info}\n\n*Message:*\n`{message_preview}`\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID, 
            text=notification, 
            parse_mode="Markdown"
        )
    except Exception:
        pass

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "watch"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/watch")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    user = update.effective_user
    target_user_obj = None
    
    if update.message.reply_to_message:
        target_user_obj = update.message.reply_to_message.from_user
        target_id = target_user_obj.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
        try:
            member = await context.bot.get_chat_member(chat.id, target_id)
            target_user_obj = member.user
        except:
            target_user_obj = None
    else:
        await update.message.reply_text("Usage: /watch @user OR reply to user's message with /watch")
        return

    if not target_id:
        await update.message.reply_text("❌ Could not resolve target by mention, ID, or nickname.")
        return

    if str(chat.id) not in watch_list:
        watch_list[str(chat.id)] = {}

    watch_list[str(chat.id)][str(target_id)] = {
        "added_by": user.id,
        "added_by_name": user.first_name,
        "added_at": datetime.now().isoformat(),
        "target_name": target_user_obj.first_name if target_user_obj else "Unknown"
    }
    
    asyncio.create_task(fast_data.buffered_save(WATCH_LIST_FILE, watch_list))
    update_stats("users_watched", chat.id, user.id)

    display = await get_mention_for_target(context, chat.id, str(target_id))
    await update.message.reply_text(f"👁️ Now watching {display}\nTheir messages will be logged.", parse_mode="Markdown")

async def unwatch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "unwatch"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unwatch")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /unwatch @user OR reply to user's message with /unwatch")
        return

    if not target_id:
        await update.message.reply_text("❌ Could not resolve target by mention, ID, or nickname.")
        return

    if str(chat.id) in watch_list and str(target_id) in watch_list[str(chat.id)]:
        del watch_list[str(chat.id)][str(target_id)]
        if not watch_list[str(chat.id)]:
            del watch_list[str(chat.id)]
        
        asyncio.create_task(fast_data.buffered_save(WATCH_LIST_FILE, watch_list))
        
        display = await get_mention_for_target(context, chat.id, str(target_id))
        await update.message.reply_text(f"✅ Stopped watching {display}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ User is not being watched in this chat.")

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "watchlist"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/watchlist")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    
    if str(chat.id) not in watch_list or not watch_list[str(chat.id)]:
        await update.message.reply_text("👁️ No users are being watched in this chat.")
        return

    watched_users = watch_list[str(chat.id)]
    lines = ["👁️ *Watched Users in this Chat:*\n"]
    
    for target_id, info in watched_users.items():
        display = await get_mention_for_target(context, chat.id, target_id)
        added_by = info.get("added_by_name", "Unknown")
        added_at = info.get("added_at", "Unknown")
        
        try:
            added_dt = datetime.fromisoformat(added_at)
            added_str = added_dt.strftime("%Y-%m-%d %H:%M")
        except:
            added_str = added_at
            
        lines.append(f"• {display}\n  Added by: {added_by} at {added_str}")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def watchlog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "watchlog"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/watchlog")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not watch_log:
        await update.message.reply_text("📝 No watch activity logged yet.")
        return

    recent_events = watch_log[-10:]
    lines = [f"📝 *Last 10 Watched Events (Total: {len(watch_log)})*:\n"]
    
    for event in reversed(recent_events):
        try:
            timestamp = event.get("timestamp", "Unknown")
            target_id = event.get("target_user_id", "N/A")
            username = event.get("target_username", "N/A")
            chat_id = event.get("chat_id", "N/A")
            message_preview = event.get("message_preview", "")[:50]
            
            event_dt = datetime.fromisoformat(timestamp)
            time_str = event_dt.strftime("%m-%d %H:%M")
            
            lines.append(f"• `{time_str}` User `{target_id}` (@{username}) in chat `{chat_id}`: _{message_preview}..._")
        except Exception:
            continue
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "stats"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/stats")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    user = update.effective_user
    
    global_stats = stats_data.get("global", {})
    chat_stats = stats_data.get("per_chat", {}).get(str(chat.id), {})
    user_stats = stats_data.get("per_user", {}).get(str(user.id), {})
    
    # ENHANCED CALCULATIONS
    total_commands = global_stats.get('commands_executed', 0)
    total_messages = global_stats.get('messages_processed', 0)
    total_attacks = global_stats.get('attacks_started', 0)
    
    command_ratio = (total_commands / total_messages * 100) if total_messages > 0 else 0
    attack_success = (total_attacks / total_commands * 100) if total_commands > 0 else 0
    
    # REAL-TIME COUNTS
    active_attacks = len(attacking_single) + len(attacking_multiple)
    total_ghosted = sum(len(v) for v in ghost_map.values())
    total_trolled = sum(len(v) for v in troll_map.values())
    
    lines = ["📊 *Enhanced Bot Statistics*"]
    lines.append("")  # Empty line for spacing
    
    # GLOBAL STATS SECTION
    lines.append("🌐 *Global Stats:*")
    lines.append(f"• Messages Processed: `{total_messages}`")
    lines.append(f"• Commands Executed: `{total_commands}`")
    lines.append(f"• Attacks Started: `{total_attacks}`")
    lines.append(f"• Command/Msg Ratio: `{command_ratio:.1f}%`")
    lines.append(f"• Attack Success Rate: `{attack_success:.1f}%`")
    
    # REAL-TIME ACTIVITY
    lines.append("")
    lines.append("⚡ *Real-Time Activity:*")
    lines.append(f"• Active Attacks: `{active_attacks}`")
    lines.append(f"• Ghosted Users: `{total_ghosted}`")
    lines.append(f"• Trolled Users: `{total_trolled}`")
    lines.append(f"• Cached Members: `{get_cached_members_count(chat.id)}`")
    
    # USER STATS
    if user_stats:
        lines.append("")
        lines.append("👤 *Your Stats:*")
        user_attacks = user_stats.get('attacks_started', 0)
        user_commands = user_stats.get('commands_executed', 0)
        user_ghosts = user_stats.get('ghosted_messages', 0)
        
        lines.append(f"• Your Attacks: `{user_attacks}`")
        lines.append(f"• Your Commands: `{user_commands}`")
        lines.append(f"• Ghosted by You: `{user_ghosts}`")
        
        # User ranking
        if stats_data.get("per_user"):
            user_attack_rank = sorted(
                [(uid, data.get('attacks_started', 0)) for uid, data in stats_data["per_user"].items()],
                key=lambda x: x[1],
                reverse=True
            )
            user_rank = next((i for i, (uid, _) in enumerate(user_attack_rank, 1) if uid == str(user.id)), None)
            if user_rank:
                lines.append(f"• Attack Rank: `#{user_rank}`")
    
    # CHAT STATS
    if chat_stats:
        lines.append("")
        lines.append("💬 *This Chat Stats:*")
        chat_attacks = chat_stats.get('attacks_started', 0)
        chat_messages = chat_stats.get('messages_processed', 0)
        chat_activity = (chat_attacks / max(chat_messages, 1)) * 100
        
        lines.append(f"• Chat Attacks: `{chat_attacks}`")
        lines.append(f"• Chat Messages: `{chat_messages}`")
        lines.append(f"• Attack Activity: `{chat_activity:.1f}%`")
    
    # BOT INFO
    lines.append("")
    lines.append("🤖 *Bot Info:*")
    lines.append(f"• Version: `{VERSION}`")
    lines.append(f"• Uptime: `{get_bot_uptime()}`")
    
    # QUICK ATTACK STATUS
    last_target = quick_attack_targets.get(chat.id)
    if last_target:
        target, display = last_target
        lines.append("")
        lines.append("⚡ *Quick Attack Ready:*")
        lines.append(f"• Last Target: {display}")
        lines.append(f"• Use: `/qa` or `/quickattack`")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ADD UPTIME FUNCTION (add after stats_command)
def get_bot_uptime() -> str:
    """Calculate bot uptime"""
    if not hasattr(get_bot_uptime, 'start_time'):
        get_bot_uptime.start_time = datetime.now()
    
    uptime = datetime.now() - get_bot_uptime.start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# ---------------- OTHER UTILITY COMMANDS ----------------
async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "note"):
        return
    admins = admins_data.get("usernames", []) or []
    ids = admins_data.get("ids", []) or []
    text = "📝 *Admins*\n\n"
    if admins:
        text += "Usernames: " + ", ".join(admins) + "\n"
    if ids:
        text += "IDs: " + ", ".join(str(x) for x in ids)
    if not admins and not ids:
        text = "No admins set."
    await update.message.reply_text(text, parse_mode="HTML")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "remove_admin"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/remove_admin")
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove_admin @username or /remove_admin user_id")
        return

    arg = context.args[0].strip()
    removed = False
    if arg.startswith("@"):
        uname = arg
        lst = admins_data.get("usernames", [])
        if uname in lst:
            lst.remove(uname)
            admins_data["usernames"] = lst
            removed = True
    else:
        try:
            uid = int(arg)
            lst = admins_data.get("ids", [])
            if uid in lst:
                lst.remove(uid)
                admins_data["ids"] = lst
                removed = True
        except Exception:
            pass

    if removed:
        asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
        global ADMIN_IDS, ADMIN_USERNAMES
        ADMIN_IDS = set(int(x) for x in admins_data.get("ids", []) if str(x).isdigit())
        ADMIN_USERNAMES = set(u.lstrip("@").lower() for u in admins_data.get("usernames", []))
        await update.message.reply_text("✅ Admin removed.")
    else:
        await update.message.reply_text("❌ Not found in admin list.")

# ---------------- ENHANCED LOCATION COMMANDS ----------------

async def enhanced_tracklocation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if Nominatim is None:
        await update.message.reply_text("❌ geopy module is not available in this build.")
        return
    """Enhanced location tracking - powerful but realistic"""
    if await check_lock_and_notify(update, context, "tracklocation"):
        return
    
    chat = update.effective_chat
    user = update.effective_user
    
    # If replying to a user, show their location intelligence
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
        display = await get_mention_for_target(context, chat.id, str(target_id))
        
        # Get comprehensive location intelligence
        location_report = await generate_location_intelligence(context, target_id, chat.id)
        
        await update.message.reply_text(location_report, parse_mode="HTML")
        
    elif context.args and context.args[0] == "ip":
        # IP location lookup
        if len(context.args) > 1:
            ip_address = context.args[1]
            await track_ip_location(update, context, ip_address)
        else:
            await update.message.reply_text("Usage: `/tracklocation ip 1.2.3.4`", parse_mode="Markdown")
            
    else:
        # Show help with all capabilities
        help_text = """
📍 **ENHANCED LOCATION INTELLIGENCE SYSTEM**

**Quick Actions:**
• Reply to user with `/tracklocation` - Show location intelligence
• `/tracklocation ip 1.2.3.4` - IP geolocation lookup
• `/tracklocation scan` - Scan chat for location mentions

**Available Intelligence:**
✅ Shared locations & live locations
✅ IP-based approximate geolocation  
✅ Message pattern analysis
✅ Timezone detection
✅ Profile location intelligence
✅ Historical location data

**Privacy Compliant** - Only uses available data
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def generate_location_intelligence(context: ContextTypes.DEFAULT_TYPE, target_id: int, chat_id: int) -> str:
    """Generate comprehensive location intelligence report"""
    
    # Get all available data sources
    shared_locations = get_shared_location_data(target_id)
    ip_location = await get_ip_based_location(target_id, chat_id)
    message_patterns = analyze_message_patterns(target_id)
    timezone_data = detect_timezone_from_patterns(target_id)
    profile_info = get_profile_location_hints(target_id)
    
    # Build comprehensive report
    display = await get_mention_for_target(context, chat_id, str(target_id))
    report = f"📍 **LOCATION INTELLIGENCE REPORT**\n\n"
    report += f"**Target:** {display}\n\n"
    
    # 1. SHARED LOCATIONS (Most accurate)
    if shared_locations:
        latest_share = shared_locations[-1]
        report += f"**🎯 Direct Location Shares:**\n"
        report += f"• Last share: `{latest_share.get('timestamp', 'Unknown')}`\n"
        if latest_share.get('address'):
            report += f"• Address: `{latest_share.get('address')}`\n"
        report += f"• Total shares: `{len(shared_locations)}`\n\n"
    
    # 2. IP-BASED INTELLIGENCE
    if ip_location and ip_location.get('country') != 'Unknown':
        report += f"**🌐 Network Intelligence:**\n"
        report += f"• Approximate location: `{ip_location.get('city', 'Unknown')}, {ip_location.get('country', 'Unknown')}`\n"
        if ip_location.get('isp'):
            report += f"• ISP: `{ip_location.get('isp')}`\n"
        report += f"• Accuracy: `City level`\n\n"
    
    # 3. BEHAVIORAL ANALYSIS
    if message_patterns:
        report += f"**📊 Behavioral Analysis:**\n"
        if message_patterns.get('active_hours'):
            report += f"• Active hours: `{message_patterns.get('active_hours')}`\n"
        if message_patterns.get('location_mentions'):
            report += f"• Location mentions: `{len(message_patterns.get('location_mentions'))}`\n"
        if message_patterns.get('detected_timezone'):
            report += f"• Detected timezone: `{message_patterns.get('detected_timezone')}`\n"
        report += f"\n"
    
    # 4. PROFILE INTELLIGENCE
    if profile_info:
        report += f"**👤 Profile Intelligence:**\n"
        if profile_info.get('bio_location'):
            report += f"• Bio location: `{profile_info.get('bio_location')}`\n"
        if profile_info.get('language_code'):
            report += f"• Language: `{profile_info.get('language_code')}`\n"
        if profile_info.get('language_hint'):
            report += f"• Language hint: `{profile_info.get('language_hint')}`\n"
        report += f"\n"
    
    # 5. CONFIDENCE SCORE
    confidence = calculate_location_confidence(
        shared_locations, 
        ip_location, 
        message_patterns, 
        profile_info
    )
    
    report += f"**🎚️ Intelligence Confidence:** `{confidence}%`\n"
    
    if not any([shared_locations, ip_location, message_patterns, profile_info]):
        report += "\n*💡 Tip: More data will be available as user interacts with the bot*"
    
    return report

async def track_ip_location(update: Update, context: ContextTypes.DEFAULT_TYPE, ip_address: str):
    """Track location from IP address"""
    import geocoder
    
    progress_msg = await update.message.reply_text("🌍 Locating IP address...")
    
    try:
        # Validate IP format
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(ip_pattern, ip_address):
            await progress_msg.edit_text("❌ Invalid IP address format.")
            return

        # Use geocoder to get location from IP
        g = geocoder.ip(ip_address)
        
        if g.ok:
            location_info = f"""
🌐 **IP Location Results**

**IP Address:** `{ip_address}`
**Country:** `{g.country}`
**Region/State:** `{g.state}`
**City:** `{g.city}`
**ISP:** `{g.org or 'Unknown'}`
**Coordinates:** `{g.lat}, {g.lng}`
**Timezone:** `{g.timezone or 'Unknown'}`
"""
            await progress_msg.edit_text(location_info, parse_mode="HTML")
        else:
            await progress_msg.edit_text("❌ Could not locate the IP address.")
            
    except Exception as e:
        await progress_msg.edit_text(f"❌ Error locating IP: {str(e)}")

async def locationscan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scan chat for location intelligence"""
    if await check_lock_and_notify(update, context, "locationscan"):
        return
    
    chat = update.effective_chat
    
    # Get recent active users with location data
    active_users = []
    for user_id_str, data in location_tracking.items():
        last_active = data.get("metadata", {}).get("last_active", "")
        if is_recent(last_active, hours=24):  # Active in last 24 hours
            user_data = {
                "user_id": user_id_str,
                "username": data.get("user_info", {}).get("username"),
                "first_name": data.get("user_info", {}).get("first_name"),
                "location_data": len(data.get("shared_locations", [])),
                "confidence": calculate_location_confidence(
                    data.get("shared_locations", []),
                    data.get("ip_data", {}),
                    data.get("behavioral_data", {}),
                    data.get("profile_data", {})
                )
            }
            active_users.append(user_data)
    
    # Sort by confidence score
    active_users.sort(key=lambda x: x["confidence"], reverse=True)
    
    report = "🔍 **LOCATION INTELLIGENCE SCAN**\n\n"
    report += f"Active users with location data: `{len(active_users)}`\n\n"
    
    for i, user in enumerate(active_users[:10]):  # Top 10
        report += f"**{i+1}. {user['first_name']}** (@{user['username'] or 'N/A'})\n"
        report += f"   • Location shares: `{user['location_data']}`\n"
        report += f"   • Confidence: `{user['confidence']}%`\n\n"
    
    await update.message.reply_text(report, parse_mode="HTML")

# ---------------- SPEED TEST COMMAND ----------------
async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if speedtest is None:
        await update.message.reply_text("❌ speedtest module is not available in this build.")
        return
    if await check_lock_and_notify(update, context, "speedtest"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/speedtest")
        await update.message.reply_text("❌ Not authorized.")
        return

    progress_msg = await update.message.reply_text("🏃‍♂️ *Running Speed Test...*", parse_mode="Markdown")
    
    results = {}
    
    try:
        # Test 1: Bot Response Time
        start_time = time.time()
        test_msg = await update.message.reply_text("⏱️ Testing...")
        response_time = (time.time() - start_time) * 1000
        await test_msg.delete()
        results['response_time'] = response_time
        
        # Test 2: System Performance
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024
        cpu_usage = process.cpu_percent(interval=0.5)
        results['memory_mb'] = memory_usage
        results['cpu_percent'] = cpu_usage
        
        # Test 3: Internal Performance
        processing_times = []
        for _ in range(5):
            start_proc = time.time()
            _ = [x for x in range(1000)]
            processing_times.append((time.time() - start_proc) * 1000)
        
        avg_processing = sum(processing_times) / len(processing_times)
        results['processing_time'] = avg_processing
        
        # Generate results
        results_text = f"""
🏁 **SPEED TEST RESULTS**

⚡ **Response Performance:**
• Bot Response: `{results['response_time']:.2f}ms`
• Processing Speed: `{results['processing_time']:.2f}ms`

🖥️ **System Resources:**
• Memory Usage: `{results['memory_mb']:.1f}MB`
• CPU Usage: `{results['cpu_percent']:.1f}%`
• Active Threads: `{process.num_threads()}`

📊 **Active Stats:**
• Active Attacks: `{len(attacking_single) + len(attacking_multiple)}`
• Cached Members: `{sum(len(c.get('members', {})) for c in member_cache.values())}`
"""
        await progress_msg.edit_text(results_text, parse_mode="Markdown")
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Speed test failed: {str(e)}")

async def list_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "list_admins"):
        return
    admins = admins_data.get("usernames", []) or []
    ids = admins_data.get("ids", []) or []
    text = "*Current Admins*\n\n"
    if admins:
        text += "Usernames: " + ", ".join(admins) + "\n"
    if ids:
        text += "IDs: " + ", ".join(str(x) for x in ids)
    if not admins and not ids:
        text = "No admins set."
    await update.message.reply_text(text, parse_mode="HTMl")

async def add_reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "add_message"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/add_message")
        await update.message.reply_text("❌ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("စာသားထည့်ရန်: /add_message စာသား")
        return
    text = " ".join(context.args).strip()
    attack_replies.append(text)
    asyncio.create_task(fast_data.buffered_save(ATTACK_REPLIES_FILE, attack_replies))
    await update.message.reply_text("✅ message added.")

async def delreply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """REMOVE REPLY FROM ATTACK REPLIES"""
    if await check_lock_and_notify(update, context, "delreply"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/delreply")
        await update.message.reply_text("❌ Not authorized.")
        return

    if update.message.reply_to_message:
        # Remove by replying to a message
        replied_msg = update.message.reply_to_message
        text_to_remove = replied_msg.text or replied_msg.caption
        
        if not text_to_remove:
            await update.message.reply_text("❌ Replied message has no text to remove")
            return
            
        # Remove the mention part if it exists (everything before first space)
        parts = text_to_remove.split(' ', 1)
        if len(parts) > 1:
            text_to_remove = parts[1]  # Get only the reply text part
        
    elif context.args:
        # Remove by providing text
        text_to_remove = " ".join(context.args).strip()
    else:
        await update.message.reply_text(
            "Usage:\n"
            "• Reply to a message with `/delreply`\n"
            "• Or use `/delreply text to remove`",
            parse_mode="Markdown"
        )
        return

    if not text_to_remove:
        await update.message.reply_text("❌ No text provided to remove")
        return

    # Find and remove matching replies
    removed_count = 0
    original_count = len(attack_replies)
    
    # Remove exact matches
    attack_replies[:] = [reply for reply in attack_replies if reply.strip() != text_to_remove.strip()]
    
    removed_count = original_count - len(attack_replies)
    
    if removed_count > 0:
        # Save changes
        asyncio.create_task(fast_data.buffered_save(ATTACK_REPLIES_FILE, attack_replies))
        await update.message.reply_text(
            f"✅ Removed {removed_count} reply(s)\n"
            f"📝 Removed: `{text_to_remove}`\n"
            f"📊 Total replies: {len(attack_replies)}",
            parse_mode="Markdown"
        )
    else:
        # Try partial matching
        partial_matches = [reply for reply in attack_replies if text_to_remove.strip().lower() in reply.lower()]
        
        if partial_matches:
            match_list = "\n".join([f"• `{match}`" for match in partial_matches[:5]])  # Show first 5 matches
            await update.message.reply_text(
                f"❌ No exact match found. Similar replies:\n{match_list}\n\n"
                f"Use `/delreply` with the exact text from above",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ No matching reply found for: `{text_to_remove}`\n"
                f"Use `/listreplies` to see all available replies",
                parse_mode="Markdown"
            )

async def listreplies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """SEND ALL ATTACK REPLIES AS JSON FILE"""
    if await check_lock_and_notify(update, context, "listreplies"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/listreplies")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not attack_replies:
        await update.message.reply_text("📝 No attack replies configured")
        return

    try:
        # Create JSON data
        replies_data = {
            "total_replies": len(attack_replies),
            "generated_at": datetime.now().isoformat(),
            "replies": attack_replies
        }
        
        # Create filename with timestamp
        filename = f"attack_replies_{int(time.time())}.json"
        
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(replies_data, f, ensure_ascii=False, indent=2)
        
        # Send the file
        with open(filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"attack_replies.json",
                caption=f"📝 Attack Replies (JSON)\nTotal: {len(attack_replies)} replies"
            )
        
        # Clean up
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating file: {e}")

async def destroy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "destroy"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/destroy")
        await update.message.reply_text("❌ Not authorized.")
        return
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        target_id = await resolve_target_user_id(context, update.effective_chat.id, context.args[0])
    else:
        await update.message.reply_text("Usage: /destroy @username or /destroy user_id")
        return
    if not target_id:
        await update.message.reply_text("Couldn't resolve target.")
        return
    
    # Get target's proper HTML mention
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
        user = member.user
        target_name = user.first_name or f"User{target_id}"
        target_display = f'<a href="tg://user?id={target_id}">{target_name}</a>'
    except:
        target_display = f"User{target_id}"
    
    targets_data[str(target_id)] = {"marked_by": update.effective_user.id, "marked_at": datetime.now().isoformat()}
    asyncio.create_task(fast_data.buffered_save(TARGETS_FILE, targets_data))
    
    # Send with HTML parse mode
    await update.message.reply_text(
        f"{target_display} ဖာသယ်မသားသေးသေးလေးအား scammer အဖြစ် report တင်လိုက်ပါပီ", 
        parse_mode="HTML"
    )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "report"):
        return
    if not OWNER_CHAT_ID:
        await update.message.reply_text("❌ Report system is not configured by the owner.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Usage: Reply to the message you want to report and use `/report [optional reason]`.", parse_mode="Markdown")
        return

    reporter = update.effective_user
    chat = update.effective_chat
    reported_message = update.message.reply_to_message
    reason = " ".join(context.args) if context.args else "No reason provided"

    report_text = (
        f"🚨 *USER REPORT - EVIDENCE INCLUDED*\n\n"
        f"🗣️ *Reporter:* {reporter.first_name} (@{reporter.username or 'N/A'})\n"
        f"• ID: `{reporter.id}`\n\n"
        f"💬 *Chat:* {getattr(chat, 'title', 'Private Chat')}\n"
        f"• ID: `{chat.id}`\n\n"
        f"📝 *Reason:* {reason}\n\n"
        f"⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"👇 *Evidence Below* 👇"
    )

    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=report_text, parse_mode="Markdown")
        await reported_message.forward(chat_id=OWNER_CHAT_ID)
        
        if reported_message.text:
            evidence_preview = reported_message.text[:200] + "..." if len(reported_message.text) > 200 else reported_message.text
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID, 
                text=f"*Message Preview:*\n`{evidence_preview}`", 
                parse_mode="Markdown"
            )
        
        await update.message.reply_text("✅ Report and evidence have been sent to the owner. Thank you!")
        
        log_security_event("user_report", {
            "reporter_id": reporter.id,
            "reporter_name": reporter.first_name,
            "reporter_username": reporter.username,
            "chat_id": chat.id,
            "chat_title": getattr(chat, 'title', 'Private'),
            "reason": reason,
            "reported_message_id": reported_message.message_id
        })
        
    except Exception:
        await update.message.reply_text("❌ Could not send the report. Please contact the owner directly.")

async def announce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast ANY message to specific group from available groups list"""
    if await check_lock_and_notify(update, context, "announce"):
        return
    
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/announce")
        return

    # Check if replying to a message
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "📢 **Universal Announcement System**\n\n"
            "**Usage:**\n"
            "1. First use `/availablegroups` to see group list\n"
            "2. Reply to ANY message with `/announce <number>`\n"
            "3. Example: Reply to message + `/announce 2`\n\n"
            "**Supports:** Text, Photos, Videos, Polls, Documents, Links, Stickers, Voice, etc.",
            parse_mode="Markdown"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Please specify group number\n"
            "Example: Reply to message + `/announce 2`"
        )
        return

    try:
        group_number = int(context.args[0])
        if group_number < 1:
            await update.message.reply_text("❌ Group number must be 1 or higher")
            return
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number")
        return

    # Get the replied message
    replied_message = update.message.reply_to_message
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Get available groups
    active_groups = {}
    for chat_id_str, chat_info in seen_chats.items():
        try:
            chat = await context.bot.get_chat(int(chat_id_str))
            active_groups[chat_id_str] = chat_info
            active_groups[chat_id_str]['current_title'] = chat.title
        except Exception:
            continue

    # Convert to list for indexing
    group_list = list(active_groups.items())
    
    if not group_list:
        await update.message.reply_text("❌ No available groups found. Use `/availablegroups` first.")
        return

    if group_number > len(group_list):
        await update.message.reply_text(
            f"❌ Group number {group_number} not found.\n"
            f"Available groups: 1 to {len(group_list)}\n"
            f"Use `/availablegroups` to see the list."
        )
        return

    # Get the target group
    target_chat_id_str, target_group_info = group_list[group_number - 1]
    target_chat_id = int(target_chat_id_str)
    target_group_title = target_group_info.get('current_title') or target_group_info.get('title', 'Unknown Group')

    # Send announcement
    try:
        sent_successfully = False
        method_used = "Unknown"
        
        # Add the title prefix with proper Markdown
        announcement_title = f"📢 **announce ({target_group_title}) သို့ရောက်ရှိလာသည်။**\n\n"
        
        # Get proper mention for sender
        sender_mention = await get_mention_for_target(context, chat_id, str(user.id))
        
        # Try to send edited content directly (no duplicate sends)
        try:
            # For text messages
            if replied_message.text:
                edited_text = announcement_title + replied_message.text
                await context.bot.send_message(
                    chat_id=target_chat_id,
                    text=edited_text,
                    parse_mode="Markdown"
                )
                sent_successfully = True
                method_used = "Edited + Sent"
                
            # For media with caption
            elif replied_message.caption and (replied_message.photo or replied_message.video or replied_message.document or replied_message.audio or replied_message.animation or replied_message.voice):
                edited_caption = announcement_title + replied_message.caption
                
                if replied_message.photo:
                    await context.bot.send_photo(
                        chat_id=target_chat_id,
                        photo=replied_message.photo[-1].file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                elif replied_message.video:
                    await context.bot.send_video(
                        chat_id=target_chat_id,
                        video=replied_message.video.file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                elif replied_message.document:
                    await context.bot.send_document(
                        chat_id=target_chat_id,
                        document=replied_message.document.file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                elif replied_message.audio:
                    await context.bot.send_audio(
                        chat_id=target_chat_id,
                        audio=replied_message.audio.file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                elif replied_message.animation:
                    await context.bot.send_animation(
                        chat_id=target_chat_id,
                        animation=replied_message.animation.file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                elif replied_message.voice:
                    await context.bot.send_voice(
                        chat_id=target_chat_id,
                        voice=replied_message.voice.file_id,
                        caption=edited_caption,
                        parse_mode="Markdown"
                    )
                sent_successfully = True
                method_used = "Edited + Sent"
                
            # For media without caption - send title then forward media (ONCE)
            elif replied_message.photo or replied_message.video or replied_message.document or replied_message.audio or replied_message.animation:
                # Send title with media in one message
                if replied_message.photo:
                    await context.bot.send_photo(
                        chat_id=target_chat_id,
                        photo=replied_message.photo[-1].file_id,
                        caption=announcement_title.rstrip('\n\n'),
                        parse_mode="Markdown"
                    )
                elif replied_message.video:
                    await context.bot.send_video(
                        chat_id=target_chat_id,
                        video=replied_message.video.file_id,
                        caption=announcement_title.rstrip('\n\n'),
                        parse_mode="Markdown"
                    )
                elif replied_message.document:
                    await context.bot.send_document(
                        chat_id=target_chat_id,
                        document=replied_message.document.file_id,
                        caption=announcement_title.rstrip('\n\n'),
                        parse_mode="Markdown"
                    )
                elif replied_message.audio:
                    await context.bot.send_audio(
                        chat_id=target_chat_id,
                        audio=replied_message.audio.file_id,
                        caption=announcement_title.rstrip('\n\n'),
                        parse_mode="Markdown"
                    )
                elif replied_message.animation:
                    await context.bot.send_animation(
                        chat_id=target_chat_id,
                        animation=replied_message.animation.file_id,
                        caption=announcement_title.rstrip('\n\n'),
                        parse_mode="Markdown"
                    )
                sent_successfully = True
                method_used = "Title + Media"
                
            # For stickers, polls, etc. - forward as is with title
            else:
                # Send title first
                await context.bot.send_message(
                    chat_id=target_chat_id,
                    text=announcement_title.rstrip('\n\n'),
                    parse_mode="Markdown"
                )
                # Then forward the original (ONCE)
                await context.bot.forward_message(
                    chat_id=target_chat_id,
                    from_chat_id=replied_message.chat_id,
                    message_id=replied_message.message_id
                )
                sent_successfully = True
                method_used = "Title + Forwarded"
                
        except Exception as copy_error:
            # If copying fails, try simple forward with title
            try:
                # Send title first
                await context.bot.send_message(
                    chat_id=target_chat_id,
                    text=announcement_title.rstrip('\n\n'),
                    parse_mode="Markdown"
                )
                # Then forward the original
                await context.bot.forward_message(
                    chat_id=target_chat_id,
                    from_chat_id=replied_message.chat_id,
                    message_id=replied_message.message_id
                )
                sent_successfully = True
                method_used = "Title + Forwarded (fallback)"
            except Exception as forward_error:
                sent_successfully = False

        if sent_successfully:
            # Success message with proper sender mention
            await update.message.reply_text(
                f"✅ **Announcement Sent Successfully!**\n\n"
                f"**To:** {target_group_title}\n"
                f"**Group ID:** `{target_chat_id}`\n"
                f"**Position:** #{group_number}\n"
                f"**Method:** {method_used}\n"
                f"**Content Type:** {get_detailed_message_type(replied_message)}\n"
                f"**Sent by:** {sender_mention}",
                parse_mode="Markdown"
            )

            # Log the announcement
            log_security_event("announcement_sent", {
                "sent_by": user.id,
                "sent_by_name": user.first_name,
                "target_group": target_chat_id,
                "target_group_title": target_group_title,
                "position": group_number,
                "method": method_used,
                "content_type": get_detailed_message_type(replied_message),
                "timestamp": datetime.now().isoformat()
            })
        else:
            await update.message.reply_text(
                f"❌ Failed to send announcement to group #{group_number}\n"
                f"Message type: {get_detailed_message_type(replied_message)}"
            )

    except Exception as e:
        error_msg = f"❌ Failed to send announcement to group #{group_number}:\n{str(e)}"
        
        # Provide helpful error messages
        if "Chat not found" in str(e):
            error_msg += "\n\n💡 *The bot may have been removed from this group*"
        elif "Not enough rights" in str(e):
            error_msg += "\n\n💡 *The bot doesn't have permission to send messages in this group*"
        elif "Forbidden" in str(e):
            error_msg += "\n\n💡 *The bot was kicked from this group*"
        
        await update.message.reply_text(error_msg, parse_mode="Markdown")

#



# -----------------------------
# /fight command - FIXED MARKDOWN ISSUES
# -----------------------------
# ==================== FIGHT COMMAND SYSTEM (FULLY FIXED) ====================

FIGHT_PAGE_SIZE = 6  # 6 groups per page
fight_broadcast_sessions = {}
_fight_temp_storage = {}  # Temporary storage for group data

async def fight_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        if not is_admin(user_id, username):
            await msg.reply_text("⛔ ခွင့်မပြုပါ")
            return

        groups = load_json(GROUPS_FILE, {})
        
        if not groups:
            await msg.reply_text("❌ မှတ်ပုံတင်ထားသော group မရှိပါ")
            return

        # Store group list in temp storage with a session ID
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        # Convert to numbered list for button callback
        group_list = []
        for idx, (gid, gdata) in enumerate(groups.items()):
            group_list.append({
                "idx": idx + 1,
                "id": gid,
                "title": gdata.get('title', f'Group {gid}')
            })
        
        _fight_temp_storage[session_id] = {
            "groups": group_list,
            "total": len(group_list)
        }
        
        # Create first page with session ID
        await send_fight_page_fixed(update, context, session_id, page=0, user_id=user_id)
        
    except Exception as e:
        await msg.reply_text(f"❌ အမှားတစ်ခုဖြစ်နေသည်: {str(e)}")


async def send_fight_page_fixed(update: Update, context: ContextTypes.DEFAULT_TYPE, session_id: str, page: int, user_id: int):
    """Fixed fight page - uses INDEX instead of GROUP ID in callback data"""
    
    if session_id not in _fight_temp_storage:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Session expired. Use /fight again.")
        return
    
    data = _fight_temp_storage[session_id]
    group_list = data["groups"]
    total_groups = data["total"]
    total_pages = (total_groups + FIGHT_PAGE_SIZE - 1) // FIGHT_PAGE_SIZE
    
    # Safety check
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * FIGHT_PAGE_SIZE
    end_idx = min(start_idx + FIGHT_PAGE_SIZE, total_groups)
    current_groups = group_list[start_idx:end_idx]
    
    # Build text message
    text = (
        f"📢 <b>Broadcast Message to Groups</b>\n"
        f"📊 <b>Groups:</b> {total_groups}\n"
        f"👇 <b>Group ကိုရွေးပါ:</b>\n"
    )
    
    # PAGINATION SELECTOR - Let user jump to any page
    # Show page range for easier navigation
    page_window = 5  # Show 5 pages at a time
    page_start = max(0, page - page_window // 2)
    page_end = min(total_pages, page_start + page_window)
    if page_end - page_start < page_window:
        page_start = max(0, page_end - page_window)
    
    text += f"\n📄 <b>Pages:</b> "
    for p in range(page_start, page_end):
        if p == page:
            text += f"<b>[{p+1}]</b> "
        else:
            text += f"{p+1} "
    text += f"\n<i>Page {page+1} of {total_pages}</i>\n\n"
    
    # Show current page groups
    text += f"<b>Showing {start_idx+1}-{end_idx}:</b>\n"
    for g in current_groups:
        name = g["title"][:35]
        text += f"  {g['idx']}. {name}\n"
    
    # ===== BUILD BUTTONS =====
    keyboard = []
    
    # Row 1-3: Group buttons (2 per row, 6 total = 3 rows)
    for i in range(0, len(current_groups), 2):
        row = []
        g1 = current_groups[i]
        # Use INDEX instead of group_id (much shorter!)
        btn1 = InlineKeyboardButton(
            f"📢 {g1['title'][:18]}", 
            callback_data=f"fs:{session_id}:{g1['idx']}:{user_id}"
        )
        row.append(btn1)
        
        if i + 1 < len(current_groups):
            g2 = current_groups[i + 1]
            btn2 = InlineKeyboardButton(
                f"📢 {g2['title'][:18]}", 
                callback_data=f"fs:{session_id}:{g2['idx']}:{user_id}"
            )
            row.append(btn2)
        
        keyboard.append(row)
    
    # Row 4: Page Navigation
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"fp:{session_id}:{page-1}:{user_id}"))
    
    # Page indicator
    nav_row.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"fp:{session_id}:{page+1}:{user_id}"))
    
    keyboard.append(nav_row)
    
    # Row 5: Page Jump Buttons (Jump 5 pages)
    jump_row = []
    if page >= 5:
        jump_row.append(InlineKeyboardButton("⏮️ -5", callback_data=f"fp:{session_id}:{page-5}:{user_id}"))
    if page > 0:
        jump_row.append(InlineKeyboardButton("◀️ -1", callback_data=f"fp:{session_id}:{page-1}:{user_id}"))
    if total_pages - page > 1:
        jump_row.append(InlineKeyboardButton("+1 ▶️", callback_data=f"fp:{session_id}:{page+1}:{user_id}"))
    if total_pages - page > 5:
        jump_row.append(InlineKeyboardButton("+5 ⏭️", callback_data=f"fp:{session_id}:{page+5}:{user_id}"))
    
    if jump_row:
        keyboard.append(jump_row)
    
    # Row 6: First/Last + Cancel
    control_row = []
    if page > 0:
        control_row.append(InlineKeyboardButton("🏠 First", callback_data=f"fp:{session_id}:0:{user_id}"))
    control_row.append(InlineKeyboardButton("❌ Cancel", callback_data=f"fc:{session_id}:{user_id}"))
    if page < total_pages - 1:
        control_row.append(InlineKeyboardButton("Last 🏁", callback_data=f"fp:{session_id}:{total_pages-1}:{user_id}"))
    
    keyboard.append(control_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        print(f"❌ send_fight_page error: {e}")


# ==================== FIGHT CALLBACK HANDLER (FIXED) ====================

async def fight_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # Skip noop callbacks
    if data == "noop":
        return
    
    # Split: fp:session_id:page:user_id or fs:session_id:idx:user_id or fc:session_id:user_id
    parts = data.split(":", 3)
    
    if len(parts) < 3:
        return
    
    action = parts[0]
    session_id = parts[1]
    
    try:
        if action == "fp":  # fight_page navigation
            page = int(parts[2])
            callback_user_id = int(parts[3])
            
            if user_id != callback_user_id:
                await query.answer("❌ ဤခလုတ်ကို သင့်အတွက်မဟုတ်ပါ", show_alert=True)
                return
            
            await send_fight_page_fixed(update, context, session_id, page, user_id)
        
        elif action == "fs":  # fight_select group
            group_idx = int(parts[2])
            callback_user_id = int(parts[3])
            
            if user_id != callback_user_id:
                await query.answer("❌ ဤခလုတ်ကို သင့်အတွက်မဟုတ်ပါ", show_alert=True)
                return
            
            # Find group by index
            if session_id not in _fight_temp_storage:
                await query.edit_message_text("❌ Session expired. Use /fight again.")
                return
            
            group_list = _fight_temp_storage[session_id]["groups"]
            selected_group = None
            for g in group_list:
                if g["idx"] == group_idx:
                    selected_group = g
                    break
            
            if not selected_group:
                await query.edit_message_text("❌ Group not found.")
                return
            
            group_id = selected_group["id"]
            group_name = selected_group["title"]
            
            fight_broadcast_sessions[user_id] = {
                'group_id': group_id,
                'group_name': group_name,
                'message_id': query.message.message_id
            }
            
            # Clean up temp storage
            _fight_temp_storage.pop(session_id, None)
            
            await query.edit_message_text(
                f"✅ <b>{group_name}</b> ကိုရွေးချယ်ပြီးပါပြီ\n"
                f"📝 ပို့မည့် မက်ဆေ့ချ်ကို ရေးပေးပါ (သို့) reply လုပ်ပါ\n"
                f"<i>(စာတို၊ ဓာတ်ပုံ၊ ဗီဒီယို၊ ဖိုင် မည်သည့်အရာမဆိုပို့နိုင်ပါတယ်)</i>",
                parse_mode="HTML"
            )
        
        elif action == "fc":  # fight_cancel
            callback_user_id = int(parts[2])
            
            if user_id != callback_user_id:
                await query.answer("❌ ဤခလုတ်ကို သင့်အတွက်မဟုတ်ပါ", show_alert=True)
                return
            
            _fight_temp_storage.pop(session_id, None)
            await query.edit_message_text("❌ Broadcast လုပ်ခြင်းကိုပယ်ဖျက်လိုက်ပါပြီ")
            if user_id in fight_broadcast_sessions:
                del fight_broadcast_sessions[user_id]
    
    except (ValueError, IndexError) as e:
        print(f"❌ Fight callback error: {e}")
        await query.answer("Error - Please try again", show_alert=True)


# ==================== FIGHT MESSAGE HANDLER ====================

async def fight_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        user_id = update.effective_user.id
        
        if user_id not in fight_broadcast_sessions:
            return
        
        session = fight_broadcast_sessions[user_id]
        group_id = session['group_id']
        group_name = session['group_name']
        
        success = await send_message_to_group(context, msg, group_id, group_name)
        
        if success:
            await msg.reply_text(
                f"✅ Broadcast ပို့ပြီးပါပြီ\n"
                f"📁 Group: {group_name}\n"
                f"🆔 ID: {group_id}"
            )
            update_stats("commands_executed", msg.chat_id, user_id)
        else:
            await msg.reply_text(f"❌ Group သို့ပို့ရာတွင်အမှားဖြစ်နေသည်")
        
        del fight_broadcast_sessions[user_id]
        
    except Exception as e:
        print(f"❌ Fight message handler error: {e}")


# ==================== REGISTER HANDLER (Update this line) ====================

# register_handlers function ထဲမှာ ဒီလိုင်းကို ရှာပြီး ပြင်ပါ:
# 


async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced broadcast to groups - supports multiple photos, media groups, everything"""
    if await check_lock_and_notify(update, context, "send"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/send")
        return
        
    # MUST REPLY TO A MESSAGE
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ **Usage:** Reply to any message with `/send`\n\n"
            "**Supports EVERYTHING:**\n"
            "• 📝 Text + links + formatting\n"
            "• 🖼️ Single photos/videos + captions + links\n" 
            "• 📚 **MULTIPLE PHOTOS** (2-10 in albums)\n"
            "• 📎 Documents + descriptions\n"
            "• 🎵 Audio + captions\n"
            "• 🎤 Voice messages\n"
            "• 📍 Locations & contacts\n"
            "• 😀 Stickers & GIFs\n\n"
            "**How to send multiple photos:**\n"
            "1. Select 2-10 photos in Telegram\n"
            "2. Choose 'Send as Album'\n"
            "3. Reply to the album with `/send`\n\n"
            "**Smart Delivery:**\n"
            "1. 🔄 Try to forward (preserves original)\n"
            "2. 📝 Copy if forward fails",
            parse_mode="Markdown"
        )
        return
        
    print("📤 ENHANCED SEND: Starting broadcast to groups...")
    
    # Get groups list
    groups_list = []
    for chat_id_str in seen_chats.keys():
        try:
            groups_list.append(int(chat_id_str))
        except:
            continue
    
    if not groups_list:
        await update.message.reply_text("❌ No groups found in database.")
        return

    print(f"📤 SEND: Found {len(groups_list)} groups")
    
    sent = 0
    failed = 0
    progress_msg = await update.message.reply_text(f"🔄 Starting... 0/{len(groups_list)}")

    try:
        replied_msg = update.message.reply_to_message
        
        # Check if it's part of a media group (multiple photos)
        if replied_msg.media_group_id:
            print("🎯 Detected media group - handling multiple photos")
            # Get all messages in the media group
            media_messages = await get_media_group_messages(context, replied_msg)
            if media_messages and len(media_messages) > 1:
                sent, failed = await enhanced_forward_with_media_group(context, groups_list, media_messages, progress_msg)
                result_type = f"?? Media Album ({len(media_messages)} photos)"
            else:
                # Fallback to single message
                sent, failed = await enhanced_forward_message(context, groups_list, replied_msg, progress_msg)
                result_type = get_detailed_message_type(replied_msg)
        else:
            # Single message (text, single photo, video, etc.)
            sent, failed = await enhanced_forward_message(context, groups_list, replied_msg, progress_msg)
            result_type = get_detailed_message_type(replied_msg)
        
        # Final result with details
        result = f"""
✅ **ENHANCED BROADCAST COMPLETE**

📊 **Results:**
• ✅ Success: {sent}
• ❌ Failed: {failed} 
• 📊 Total: {len(groups_list)}

📨 **Content Type:**
• {result_type}

🚀 **Delivery Method:**
• 🔄 Forwarded: {sent - failed} chats
• 📝 Copied: {failed} chats
• 🎯 Success rate: {(sent/len(groups_list)*100):.1f}%
"""
        await progress_msg.edit_text(result, parse_mode="Markdown")
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Broadcast failed: {str(e)}")
async def enhanced_forward_message(context, chat_ids, original_msg, progress_msg):
    """Ultra-Fast Concurrent Forwarding with Anti-Crash & FloodWait Handling"""
    from telegram.error import RetryAfter, Forbidden, BadRequest
    
    sent = 0
    failed = 0
    
    # Telegram Broadcast Limit ကိုမကျော်အောင် တစ်ပြိုင်နက် 15 ခုပဲ Concurrency ဖွင့်မယ်
    semaphore = asyncio.Semaphore(15)
    
    async def send_task(chat_id):
        nonlocal sent, failed
        async with semaphore:
            try:
                await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=original_msg.chat_id,
                    message_id=original_msg.message_id
                )
                sent += 1
            except RetryAfter as e:
                # FloodWait မိရင် သတ်မှတ်ချိန်စောင့်ပြီးမှ ပြန်ပို့မယ်
                await asyncio.sleep(e.retry_after + 0.5)
                try:
                    await context.bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=original_msg.chat_id,
                        message_id=original_msg.message_id
                    )
                    sent += 1
                except:
                    failed += 1
            except Forbidden:
                # Bot Kick ခံရတာမျိုးဆို Database ထဲကနေ ဖယ်ထုတ်မယ်
                logging.warning(f"Chat {chat_id} returned Forbidden. Removing from seen_chats/private_users.")
                if str(chat_id) in seen_chats:
                    del seen_chats[str(chat_id)]
                elif str(chat_id) in private_users:
                    del private_users[str(chat_id)]
                save_data() # Save changes to disk
                failed += 1
            except BadRequest:
                # Forward ပိတ်ထားတာမျိုးဆို CopyFallback သုံးမယ်
                try:
                    await copy_message_content(context, chat_id, original_msg)
                    sent += 1
                except RetryAfter as e2:
                    await asyncio.sleep(e2.retry_after + 0.5)
                    try:
                        await copy_message_content(context, chat_id, original_msg)
                        sent += 1
                    except:
                        failed += 1
                except:
                    failed += 1
            except Exception:
                failed += 1

    last_update_time = time.time()
    batch_size = 50  # တစ်ခါပို့ရင် Group 50 စီ Batch ခွဲပို့မယ်

    for i in range(0, len(chat_ids), batch_size):
        batch = chat_ids[i:i+batch_size]
        
        # Batch ထဲက ကောင်တွေကို တစ်ပြိုင်နက်တည်း High-speed ပို့မယ်
        await asyncio.gather(*(send_task(cid) for cid in batch))
        
        current_time = time.time()
        # Progress ကို အနည်းဆုံး ၃ စက္ကန့်မှ တစ်ခါပဲ Update လုပ်မယ် (Edit FloodWait မမိအောင်)
        if current_time - last_update_time > 3:
            try:
                await progress_msg.edit_text(
                    f"📤 Sending (Ultra Fast)... {min(i+batch_size, len(chat_ids))}/{len(chat_ids)}\n(✅{sent}  ❌{failed})"
                )
                last_update_time = current_time
            except Exception:
                pass # Edit Error တက်ရင်လည်း Broadcast ကြီး လုံးဝရပ်မသွားအောင် ကာကွယ်ထားတယ်
        
        await asyncio.sleep(0.3) # Batch တစ်ခုနဲ့တစ်ခုကြား Safe ဖြစ်အောင် နည်းနည်းနားမယ်
        
    return sent, failed




# ADD copy_message_content RIGHT HERE:
async def copy_message_content(context, chat_id, original_msg):
    """Copy any message type with all content preserved"""
    try:
        # Get caption and entities
        caption = original_msg.caption or ""
        caption_entities = original_msg.caption_entities
        text_entities = original_msg.entities
        
        # Process custom emojis
        processed_text, processed_text_entities = await process_custom_emojis(original_msg.text or "", text_entities)
        processed_caption, processed_caption_entities = await process_custom_emojis(caption, caption_entities)
        
        # Handle different message types
        if original_msg.text:
            # Text message with links/formatting
            await context.bot.send_message(
                chat_id=chat_id,
                text=processed_text,
                entities=processed_text_entities,
                parse_mode=None,  # Let entities handle formatting
                disable_web_page_preview=False
            )
            
        elif original_msg.photo:
            # Photo with caption + links
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=original_msg.photo[-1].file_id,  # Highest quality
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.video:
            # Video with caption + links
            await context.bot.send_video(
                chat_id=chat_id,
                video=original_msg.video.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.document:
            # Document with caption + links
            await context.bot.send_document(
                chat_id=chat_id,
                document=original_msg.document.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.audio:
            # Audio with caption + links
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=original_msg.audio.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.voice:
            # Voice message with caption
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=original_msg.voice.file_id,
                caption=processed_caption,
                parse_mode=None
            )
            
        elif original_msg.sticker:
            # Sticker
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker=original_msg.sticker.file_id
            )
            
        elif original_msg.location:
            # Location
            await context.bot.send_location(
                chat_id=chat_id,
                latitude=original_msg.location.latitude,
                longitude=original_msg.location.longitude
            )
            
        elif original_msg.contact:
            # Contact
            await context.bot.send_contact(
                chat_id=chat_id,
                phone_number=original_msg.contact.phone_number,
                first_name=original_msg.contact.first_name,
                last_name=original_msg.contact.last_name or ""
            )
            
        elif original_msg.animation:
            # GIF/Animation
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=original_msg.animation.file_id,
                caption=caption,
                caption_entities=caption_entities,
                parse_mode=None
            )
            
        else:
            # Fallback for unsupported types
            fallback_text = "📨 Forwarded content"
            if caption:
                fallback_text += f"\n\n{caption}"
                
            await context.bot.send_message(
                chat_id=chat_id,
                text=fallback_text,
                parse_mode=None
            )
            
    except Exception as e:
        print(f"❌ Copy failed for {chat_id}: {e}")
        raise e

async def copy_message_content(context, chat_id, original_msg):
    """Copy any message type with all content preserved"""
    try:
        # Get caption and entities
        caption = original_msg.caption or ""
        caption_entities = original_msg.caption_entities
        text_entities = original_msg.entities
        
        # Process custom emojis
        processed_text, processed_text_entities = await process_custom_emojis(original_msg.text or "", text_entities)
        processed_caption, processed_caption_entities = await process_custom_emojis(caption, caption_entities)
        
        # Handle different message types
        if original_msg.text:
            # Text message with links/formatting
            await context.bot.send_message(
                chat_id=chat_id,
                text=processed_text,
                entities=processed_text_entities,
                parse_mode=None,  # Let entities handle formatting
                disable_web_page_preview=False
            )
            
        elif original_msg.photo:
            # Photo with caption + links
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=original_msg.photo[-1].file_id,  # Highest quality
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.video:
            # Video with caption + links
            await context.bot.send_video(
                chat_id=chat_id,
                video=original_msg.video.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.document:
            # Document with caption + links
            await context.bot.send_document(
                chat_id=chat_id,
                document=original_msg.document.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.audio:
            # Audio with caption + links
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=original_msg.audio.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.voice:
            # Voice message with caption
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=original_msg.voice.file_id,
                caption=processed_caption,
                parse_mode=None
            )
            
        elif original_msg.sticker:
            # Sticker
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker=original_msg.sticker.file_id
            )
            
        elif original_msg.location:
            # Location
            await context.bot.send_location(
                chat_id=chat_id,
                latitude=original_msg.location.latitude,
                longitude=original_msg.location.longitude
            )
            
        elif original_msg.contact:
            # Contact
            await context.bot.send_contact(
                chat_id=chat_id,
                phone_number=original_msg.contact.phone_number,
                first_name=original_msg.contact.first_name,
                last_name=original_msg.contact.last_name or ""
            )
            
        elif original_msg.animation:
            # GIF/Animation
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=original_msg.animation.file_id,
                caption=caption,
                caption_entities=caption_entities,
                parse_mode=None
            )
            
        else:
            # Fallback for unsupported types
            fallback_text = "📨 Forwarded content"
            if caption:
                fallback_text += f"\n\n{caption}"
                
            await context.bot.send_message(
                chat_id=chat_id,
                text=fallback_text,
                parse_mode=None
            )
            
    except Exception as e:
        print(f"❌ Copy failed for {chat_id}: {e}")
        raise e

async def forward_media_group(context, chat_id, original_msg):
    """Forward media group (album)"""
    try:
        # Get all messages in the media group
        media_group = []
        if hasattr(original_msg, 'media_group_id') and original_msg.media_group_id:
            # This is complex - for now, just forward the first media
            # In a real implementation, you'd need to get all messages in the group
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=original_msg.chat_id,
                message_id=original_msg.message_id
            )
    except Exception:
        # Fallback to copying first media
        await copy_message_content(context, chat_id, original_msg)

async def copy_message_content(context, chat_id, original_msg):
    """Copy any message type with all content preserved"""
    try:
        # Get caption and entities
        caption = original_msg.caption or ""
        caption_entities = original_msg.caption_entities
        text_entities = original_msg.entities
        
        # Process custom emojis
        processed_text, processed_text_entities = await process_custom_emojis(original_msg.text or "", text_entities)
        processed_caption, processed_caption_entities = await process_custom_emojis(caption, caption_entities)
        
        # Handle different message types
        if original_msg.text:
            # Text message with links/formatting
            await context.bot.send_message(
                chat_id=chat_id,
                text=processed_text,
                entities=processed_text_entities,
                parse_mode=None,  # Let entities handle formatting
                disable_web_page_preview=False
            )
            
        elif original_msg.photo:
            # Photo with caption + links
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=original_msg.photo[-1].file_id,  # Highest quality
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.video:
            # Video with caption + links
            await context.bot.send_video(
                chat_id=chat_id,
                video=original_msg.video.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.document:
            # Document with caption + links
            await context.bot.send_document(
                chat_id=chat_id,
                document=original_msg.document.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.audio:
            # Audio with caption + links
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=original_msg.audio.file_id,
                caption=processed_caption,
                caption_entities=processed_caption_entities,
                parse_mode=None
            )
            
        elif original_msg.voice:
            # Voice message with caption
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=original_msg.voice.file_id,
                caption=processed_caption,
                parse_mode=None
            )
            
        elif original_msg.sticker:
            # Sticker
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker=original_msg.sticker.file_id
            )
            
        elif original_msg.location:
            # Location
            await context.bot.send_location(
                chat_id=chat_id,
                latitude=original_msg.location.latitude,
                longitude=original_msg.location.longitude
            )
            
        elif original_msg.contact:
            # Contact
            await context.bot.send_contact(
                chat_id=chat_id,
                phone_number=original_msg.contact.phone_number,
                first_name=original_msg.contact.first_name,
                last_name=original_msg.contact.last_name or ""
            )
            
        elif original_msg.animation:
            # GIF/Animation
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=original_msg.animation.file_id,
                caption=caption,
                caption_entities=caption_entities,
                parse_mode=None
            )
            
        else:
            # Fallback for unsupported types
            fallback_text = "📨 Forwarded content"
            if caption:
                fallback_text += f"\n\n{caption}"
                
            await context.bot.send_message(
                chat_id=chat_id,
                text=fallback_text,
                parse_mode=None
            )
            
    except Exception as e:
        print(f"❌ Copy failed for {chat_id}: {e}")
        raise e

async def send_media_group_with_caption(context, chat_id, media_messages, caption="", caption_entities=None):
    """Send media group with caption and links"""
    try:
        media_group = []
        
        for i, msg in enumerate(media_messages):
            if msg.photo:
                # Photo
                media_group.append({
                    'type': 'photo',
                    'media': msg.photo[-1].file_id,
                    'caption': caption if i == 0 else "",  # Caption only on first media
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
            elif msg.video:
                # Video
                media_group.append({
                    'type': 'video', 
                    'media': msg.video.file_id,
                    'caption': caption if i == 0 else "",
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
            elif msg.document:
                # Document
                media_group.append({
                    'type': 'document',
                    'media': msg.document.file_id,
                    'caption': caption if i == 0 else "",
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
        
        # Send media group (max 10 items)
        await context.bot.send_media_group(
            chat_id=chat_id,
            media=media_group[:10]  # Limit to 10 items
        )
        return True
        
    except Exception as e:
        print(f"❌ Media group failed: {e}")
        return False

async def enhanced_forward_with_media_group(context, chat_ids, media_messages, progress_msg):
    """Ultra-Fast Media Group Forwarding"""
    sent = 0
    failed = 0
    
    # Media Group တွေမို့လို့ Heavy ဖြစ်မှာဆိုးလို့ Concurrency နည်းနည်းလျှော့ထားတယ်
    semaphore = asyncio.Semaphore(8) 
    
    first_msg = media_messages[0]
    caption = first_msg.caption or ""
    caption_entities = first_msg.caption_entities

    async def media_task(chat_id):
        nonlocal sent, failed
        async with semaphore:
            try:
                if len(media_messages) == 1:
                    await context.bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=first_msg.chat_id,
                        message_id=first_msg.message_id
                    )
                    sent += 1
                else:
                    success = await send_media_group_with_caption(context, chat_id, media_messages, caption, caption_entities)
                    if success:
                        sent += 1
                    else:
                        failed += 1
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 0.5)
                try:
                    success = await send_media_group_with_caption(context, chat_id, media_messages, caption, caption_entities)
                    if success:
                        sent += 1
                    else:
                        failed += 1
                except:
                    failed += 1
            except Exception:
                failed += 1

    last_update_time = time.time()
    batch_size = 20  # Media မို့လို့ Batch size လျှော့ထားတယ်

    for i in range(0, len(chat_ids), batch_size):
        batch = chat_ids[i:i+batch_size]
        await asyncio.gather(*(media_task(cid) for cid in batch))
        
        current_time = time.time()
        if current_time - last_update_time > 3:
            try:
                await progress_msg.edit_text(
                    f"📤 Sending Media Group... {min(i+batch_size, len(chat_ids))}/{len(chat_ids)}\n(✅{sent}  ❌{failed})"
                )
                last_update_time = current_time
            except Exception:
                pass
        
        await asyncio.sleep(0.5)
        
    return sent, failed

async def senduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enhanced broadcast to users.
    1. Tries to Forward (preserves origin).
    2. If Forward fails (privacy settings), Copies content.
    3. Supports Media Groups (Albums).
    """
    if await check_lock_and_notify(update, context, "senduser"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/senduser")
        return
        
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ **Usage:** Reply to any message/album with `/senduser`\n"
            "• Supports Text, Photos, Albums, Videos, etc.\n"
            "• Tries to Forward first, Copies if blocked."
        )
        return
        
    # 1. Prepare User List (Fixing the ID error)
    users_list = []
    # private_users keys are strings in JSON, we need ints for Telegram API
    if private_users:
        for user_id_str in private_users.keys():
            try:
                users_list.append(int(user_id_str))
            except ValueError:
                continue
    
    if not users_list:
        await update.message.reply_text("❌ No private users found in database.")
        return

    # 2. Initialize Broadcast
    total_count = len(users_list)
    status_msg = await update.message.reply_text(f"📤 **Preparing to broadcast to {total_count} users...**")
    
    replied_msg = update.message.reply_to_message
    sent_count = 0
    failed_count = 0
    content_type = "Message"

    try:
        # 3. Check for Media Group (Album)
        if replied_msg.media_group_id:
            print(f"📚 Detected Album: {replied_msg.media_group_id}")
            
            # Use the existing helper from B.py to fetch all parts of the album
            media_messages = await get_media_group_messages(context, replied_msg)
            
            if media_messages and len(media_messages) > 1:
                content_type = f"📚 Album ({len(media_messages)} items)"
                # Use existing helper that handles the loop
                sent_count, failed_count = await enhanced_forward_with_media_group(
                    context, users_list, media_messages, status_msg
                )
            else:
                # Fallback if only 1 item found in group
                content_type = get_detailed_message_type(replied_msg)
                sent_count, failed_count = await enhanced_forward_message(
                    context, users_list, replied_msg, status_msg
                )
        
        # 4. Single Message Handling
        else:
            content_type = get_detailed_message_type(replied_msg)
            # Use existing helper from B.py that implements "Forward -> Fail -> Copy"
            sent_count, failed_count = await enhanced_forward_message(
                context, users_list, replied_msg, status_msg
            )

        # 5. Final Report
        result = (
            f"✅ **Broadcast Complete**\n\n"
            f"📨 **Content:** {content_type}\n"
            f"👥 **Total Users:** {total_count}\n"
            f"✅ **Success:** {sent_count}\n"
            f"❌ **Failed:** {failed_count}\n"
            f"🚫 **Block/Privacy Rate:** {(failed_count/total_count*100):.1f}%"
        )
        await status_msg.edit_text(result, parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"❌ Critical Error: {str(e)}")
async def send_media_group_with_caption(context, chat_id, media_messages, caption="", caption_entities=None):
    """Send media group with caption and links"""
    try:
        media_group = []
        
        for i, msg in enumerate(media_messages):
            if msg.photo:
                # Photo
                media_group.append({
                    'type': 'photo',
                    'media': msg.photo[-1].file_id,
                    'caption': caption if i == 0 else "",  # Caption only on first media
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
            elif msg.video:
                # Video
                media_group.append({
                    'type': 'video', 
                    'media': msg.video.file_id,
                    'caption': caption if i == 0 else "",
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
            elif msg.document:
                # Document
                media_group.append({
                    'type': 'document',
                    'media': msg.document.file_id,
                    'caption': caption if i == 0 else "",
                    'caption_entities': caption_entities if i == 0 else None,
                    'parse_mode': None
                })
        
        # Send media group (max 10 items)
        await context.bot.send_media_group(
            chat_id=chat_id,
            media=media_group[:10]  # Limit to 10 items
        )
        return True
        
    except Exception as e:
        print(f"❌ Media group failed: {e}")
        return False

async def enhanced_forward_with_media_group(context, chat_ids, media_messages, progress_msg):
    """Enhanced forwarding that handles media groups"""
    sent = 0
    failed = 0
    
    for i, chat_id in enumerate(chat_ids):
        try:
            # If it's a single message, use normal forward
            if len(media_messages) == 1:
                await context.bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=media_messages[0].chat_id,
                    message_id=media_messages[0].message_id
                )
                sent += 1
            else:
                # For multiple media, create media group
                # Use caption from first message
                first_msg = media_messages[0]
                caption = first_msg.caption or ""
                caption_entities = first_msg.caption_entities
                
                success = await send_media_group_with_caption(
                    context, chat_id, media_messages, caption, caption_entities
                )
                if success:
                    sent += 1
                else:
                    failed += 1
                    
        except Exception as e:
            print(f"❌ Media group forward failed for {chat_id}: {e}")
            failed += 1
        
        # Update progress
        if i % 5 == 0:
            await progress_msg.edit_text(f"📤 Sending media group... {i+1}/{len(chat_ids)} (✅{sent} ❌{failed})")
        
        await asyncio.sleep(0.2)
    
    return sent, failed

async def get_media_group_messages(context, original_msg):
    """Get ALL messages in a media group - ENHANCED VERSION"""
    try:
        if not original_msg.media_group_id:
            return [original_msg]
        
        print(f"?? Detected media group: {original_msg.media_group_id}")
        
        # Store all found media messages
        media_messages = [original_msg]
        found_ids = {original_msg.message_id}
        
        # Search in a wider range around the original message
        chat_id = original_msg.chat_id
        original_id = original_msg.message_id
        
        # Search both directions (before and after)
        search_offsets = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
        
        for offset in search_offsets:
            try:
                check_id = original_id + offset
                if check_id <= 0:
                    continue
                
                # Try to get the message (using copy to avoid forward restrictions)
                check_msg = await context.bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=chat_id,
                    message_id=check_id
                )
                
                # Check if it's part of the same media group
                if (hasattr(check_msg, 'media_group_id') and 
                    check_msg.media_group_id == original_msg.media_group_id and
                    check_id not in found_ids):
                    
                    # Store the original message ID and add to collection
                    media_messages.append(check_msg)
                    found_ids.add(check_id)
                    print(f"✅ Found media group member: Message {check_id}")
                    
            except Exception as e:
                # Message doesn't exist or can't be accessed
                continue
        
        print(f"📚 Media group complete: {len(media_messages)} items")
        
        # Sort by message ID to maintain order
        media_messages.sort(key=lambda x: x.message_id)
        
        return media_messages
        
    except Exception as e:
        print(f"❌ Error in media group detection: {e}")
        return [original_msg]

async def sendall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced broadcast to all - supports multiple photos, media groups, everything"""
    if await check_lock_and_notify(update, context, "sendall"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/sendall")
        return
        
    # MUST REPLY TO A MESSAGE
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ **Usage:** Reply to any message with `/sendall`\n\n"
            "**Supports EVERYTHING:**\n"
            "• 📝 Text + links + formatting\n"
            "• 🖼️ Single photos/videos + captions + links\n" 
            "• 📚 **MULTIPLE PHOTOS** (2-10 in albums)\n"
            "• 📎 Documents + descriptions\n"
            "• 🎵 Audio + captions\n"
            "• 🎤 Voice messages\n"
            "• 📍 Locations & contacts\n"
            "• 😀 Stickers & GIFs\n\n"
            "**How to send multiple photos:**\n"
            "1. Select 2-10 photos in Telegram\n"
            "2. Choose 'Send as Album'\n"
            "3. Reply to the album with `/sendall`\n\n"
            "**Smart Delivery:**\n"
            "1. 🔄 Try to forward (preserves original)\n"
            "2. 📝 Copy if forward fails",
            parse_mode="Markdown"
        )
        return
        
    print("📤 ENHANCED SENDALL: Starting broadcast to all...")
    
    # Get groups and users
    groups_list = []
    for chat_id_str in seen_chats.keys():
        try:
            groups_list.append(int(chat_id_str))
        except:
            continue
    
    users_list = []
    for user_id_str in private_users.keys():
        try:
            users_list.append(int(user_id_str))
        except:
            continue

    if not groups_list and not users_list:
        await update.message.reply_text("❌ No groups or users found.")
        return

    print(f"📤 SENDALL: Found {len(groups_list)} groups and {len(users_list)} users")
    
    total_recipients = len(groups_list) + len(users_list)
    progress_msg = await update.message.reply_text(f"🔄 Starting... 0/{total_recipients}")

    try:
        total_sent = 0
        total_failed = 0
        replied_msg = update.message.reply_to_message
        
        # Check if it's part of a media group (multiple photos)
        if replied_msg.media_group_id:
            print("🎯 Detected media group - handling multiple photos")
            # Get all messages in the media group
            media_messages = await get_media_group_messages(context, replied_msg)
            
            # Send to groups
            groups_sent, groups_failed = 0, 0
            if groups_list:
                if media_messages and len(media_messages) > 1:
                    groups_sent, groups_failed = await enhanced_forward_with_media_group(context, groups_list, media_messages, progress_msg)
                else:
                    groups_sent, groups_failed = await enhanced_forward_message(context, groups_list, replied_msg, progress_msg)
                total_sent += groups_sent
                total_failed += groups_failed
            
            # Send to users  
            users_sent, users_failed = 0, 0
            if users_list:
                if media_messages and len(media_messages) > 1:
                    users_sent, users_failed = await enhanced_forward_with_media_group(context, users_list, media_messages, progress_msg)
                else:
                    users_sent, users_failed = await enhanced_forward_message(context, users_list, replied_msg, progress_msg)
                total_sent += users_sent
                total_failed += users_failed
                
            result_type = f"📚 Media Album ({len(media_messages) if media_messages else 1} photos)"
            
        else:
            # Single message (text, single photo, video, etc.)
            # Send to groups
            groups_sent, groups_failed = 0, 0
            if groups_list:
                groups_sent, groups_failed = await enhanced_forward_message(context, groups_list, replied_msg, progress_msg)
                total_sent += groups_sent
                total_failed += groups_failed
            
            # Send to users  
            users_sent, users_failed = 0, 0
            if users_list:
                users_sent, users_failed = await enhanced_forward_message(context, users_list, replied_msg, progress_msg)
                total_sent += users_sent
                total_failed += users_failed
                
            result_type = get_detailed_message_type(replied_msg)

        # Final result with breakdown
        result = f"""
✅ **ENHANCED BROADCAST COMPLETE**

📊 **Overall Results:**
• ✅ Success: {total_sent}
• ❌ Failed: {total_failed}
• 📊 Total: {total_recipients}

📨 **Content Type:**
• {result_type}

📈 **Breakdown:**
• **Groups:** {groups_sent}/{len(groups_list)} sent ({(groups_sent/len(groups_list)*100 if groups_list else 0):.1f}%)
• **Users:** {users_sent}/{len(users_list)} sent ({(users_sent/len(users_list)*100 if users_list else 0):.1f}%)

🚀 **Delivery Method:**
• 🔄 Forwarded: {total_sent - total_failed} chats
• 📝 Copied: {total_failed} chats
• 🎯 Overall success: {(total_sent/total_recipients*100):.1f}%
"""
        await progress_msg.edit_text(result, parse_mode="Markdown")
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Broadcast failed: {str(e)}")
async def send_album_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Special command for sending photo albums"""
    if not is_owner(update.effective_user):
        return
        
    if not update.message.reply_to_message or not update.message.reply_to_message.media_group_id:
        await update.message.reply_text("❌ Reply to a photo album with this command")
        return
    
    # This would require storing the entire media group
    # For now, use the enhanced send commands above
    await update.message.reply_text("📚 Use /send, /senduser, or /sendall with album replies - they now support media groups!")

# ---------------- IMPROVED AUTO-UPDATE SYSTEM ----------------

async def auto_update_groups(context: ContextTypes.DEFAULT_TYPE):
    """Improved auto-update groups - keeps old data and adds new groups"""
    print("🔄 Auto-updating groups database...")
    
    valid_groups = {}
    updated_count = 0
    removed_count = 0
    new_groups_added = 0
    
    # First, preserve all existing groups
    for chat_id_str, chat_info in seen_chats.items():
        valid_groups[chat_id_str] = chat_info
    
    # Check for migrated groups and validate existing ones
    for chat_id_str, chat_info in list(valid_groups.items()):
        try:
            chat_id = int(chat_id_str)
            
            # Try to get current chat info
            try:
                chat = await context.bot.get_chat(chat_id)
                
                # Update chat info with current data
                valid_groups[chat_id_str] = {
                    **chat_info,  # Keep existing data
                    "title": chat.title,
                    "type": chat.type,
                    "last_updated": datetime.now().isoformat(),
                    "auto_updated": True
                }
                
                # If ID changed (migration), note it
                if str(chat.id) != chat_id_str:
                    print(f"🔄 Group migrated: {chat_id_str} -> {chat.id}")
                    # Keep both entries during transition
                    valid_groups[str(chat.id)] = {
                        **chat_info,
                        "title": chat.title,
                        "migrated_from": chat_id_str,
                        "last_updated": datetime.now().isoformat()
                    }
                    updated_count += 1
                
            except Exception as e:
                if "migrated" in str(e):
                    # Extract new chat ID from error message
                    try:
                        new_id_match = re.search(r'chat id: (-?\d+)', str(e))
                        if new_id_match:
                            new_chat_id = new_id_match.group(1)
                            # Try the new ID
                            new_chat = await context.bot.get_chat(int(new_chat_id))
                            valid_groups[new_chat_id] = {
                                **chat_info,
                                "title": new_chat.title,
                                "type": new_chat.type,
                                "last_updated": datetime.now().isoformat(),
                                "migrated_from": chat_id_str,
                                "auto_updated": True
                            }
                            updated_count += 1
                            print(f"🔄 Auto-migrated group: {chat_id_str} -> {new_chat_id}")
                    except:
                        # Keep the old group but mark as potentially invalid
                        valid_groups[chat_id_str]["last_checked"] = datetime.now().isoformat()
                        valid_groups[chat_id_str]["check_failed"] = True
                elif "not found" in str(e).lower() or "kicked" in str(e).lower():
                    removed_count += 1
                    if chat_id_str in valid_groups:
                        del valid_groups[chat_id_str]
                    print(f"🗑️ Removing invalid group {chat_id_str}: {e}")
                else:
                    # Other error - keep the group but mark it
                    valid_groups[chat_id_str]["last_checked"] = datetime.now().isoformat()
                    valid_groups[chat_id_str]["check_error"] = str(e)
                    
        except Exception as e:
            print(f"❌ Error processing group {chat_id_str}: {e}")
            # Keep the group despite errors
    
    # Update the global variable
    seen_chats.clear()
    seen_chats.update(valid_groups)
    
    # Save to file
    asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
    
    print(f"✅ Auto-update complete: {len(valid_groups)} total, {new_groups_added} new, {updated_count} updated, {removed_count} removed")
    return len(valid_groups), new_groups_added, updated_count, removed_count

async def auto_update_users(context: ContextTypes.DEFAULT_TYPE):
    """CORRECT auto-update users - ONLY real private users"""
    print("🔄 Auto-updating users database...")
    
    valid_users = {}
    new_users_added = 0
    reachable_count = 0
    
    # Strategy 1: Keep ONLY users who actually chatted with bot privately
    # Don't blindly copy all cached group members!
    for user_id_str, user_info in private_users.items():
        # Only keep users that were actually added through private chat
        if user_info.get("auto_tracked") or user_info.get("added_at"):
            valid_users[user_id_str] = user_info
    
    # Strategy 2: Add NEW private users by checking if they actually messaged the bot
    # This is the CORRECT way - only add users who actually chatted privately
    try:
        # Get recent updates to find actual private chatters
        updates = await context.bot.get_updates(limit=100, offset=-1)
        for update in updates:
            if update.message and update.effective_chat.type == "private":
                user = update.effective_user
                if not user.is_bot:
                    user_id_str = str(user.id)
                    if user_id_str not in valid_users:
                        valid_users[user_id_str] = {
                            "name": user.first_name or "",
                            "username": user.username or "",
                            "added_at": datetime.now().isoformat(),
                            "last_interaction": datetime.now().isoformat(),
                            "auto_tracked": True,
                            "source": "actual_private_chat"
                        }
                        new_users_added += 1
    except Exception as e:
        print(f"⚠️ Could not check updates: {e}")
    
    # Strategy 3: REMOVE users who are actually group members (not private chatters)
    users_to_remove = []
    for user_id_str, user_info in valid_users.items():
        # If user has no interaction history and was auto-added from cache, remove them
        if (user_info.get("source") == "added_from_cache" or 
            user_info.get("auto_added") and not user_info.get("last_interaction")):
            users_to_remove.append(user_id_str)
    
    for user_id_str in users_to_remove:
        del valid_users[user_id_str]
        print(f"🗑️ Removed non-private user: {user_id_str}")
    
    # Update the global variable
    private_users.clear()
    private_users.update(valid_users)
    
    # Save to file
    asyncio.create_task(fast_data.buffered_save(PRIVATE_USERS_FILE, private_users))
    
    print(f"✅ User update complete: {len(valid_users)} REAL private users, {new_users_added} new")
    return len(valid_users), new_users_added, len(valid_users)

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Smart reload that auto-updates everything with better reporting"""
    if await check_lock_and_notify(update, context, "reload"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/reload")
        return
    
    progress_msg = await update.message.reply_text("🔄 Smart reloading with auto-update...")
    
    try:
        # Step 1: Auto-update groups
        await progress_msg.edit_text("🔄 Step 1: Auto-updating groups...")
        total_groups, new_groups, updated_groups, removed_groups = await auto_update_groups(context)
        
        # Step 2: Auto-update users
        await progress_msg.edit_text("🔄 Step 2: Auto-updating users...")
        total_users, new_users, reachable_users = await auto_update_users(context)
        
        # Step 3: Reload other data files
        await progress_msg.edit_text("🔄 Step 3: Reloading other data...")
        
        global admins_data, ADMIN_IDS, ADMIN_USERNAMES, members_data, targets_data, die_configs
        global attack_replies, name_map, translate_targets, security_log, unauthorized_log
        global member_cache, watch_list, stats_data, watch_log, name_map_intkey
        global lock_config, limit_admins, global_lock_config, filters_data, limit_commands_data
        
        admins_data = load_json(ADMINS_FILE, {"ids": [], "usernames": []})
        ADMIN_IDS = set(int(x) for x in admins_data.get("ids", []) if str(x).isdigit())
        ADMIN_USERNAMES = set(u.lstrip("@").lower() for u in admins_data.get("usernames", []))
        members_data = load_json(MEMBERS_FILE, {})
        targets_data = load_json(TARGETS_FILE, {})
        die_configs = load_json(DIE_FILE, {})
        attack_replies = load_json(ATTACK_REPLIES_FILE, attack_replies)
        name_map = load_json(NAME_MAP_FILE, {})
        name_map_intkey = {int(k): v for k, v in name_map.items()}
        translate_targets = load_json(TRANSLATE_TARGETS_FILE, {})
        security_log = load_json(SECURITY_LOG_FILE, [])
        unauthorized_log = load_json(UNAUTHORIZED_LOG_FILE, [])
        member_cache = load_json(MEMBER_CACHE_FILE, {})
        watch_list = load_json(WATCH_LIST_FILE, {})
        stats_data = load_json(STATS_FILE, stats_data)
        watch_log = load_json(WATCH_LOG_FILE, [])
        lock_config = load_json(LOCK_FILE, {})
        limit_admins = load_json(LIMIT_ADMINS_FILE, {})
        global_lock_config = load_json(GLOBAL_LOCK_FILE, {})
        filters_data = load_json(FILTERS_FILE, {})
        limit_commands_data = load_json(LIMIT_COMMANDS_FILE, {})
        
        # Step 4: Update statistics
        stats_data["global"]["last_reload"] = datetime.now().isoformat()
        stats_data["global"]["total_reloads"] = stats_data["global"].get("total_reloads", 0) + 1
        
        result_text = f"""
✅ ** RELOAD COMPLETE**

📊 **Groups Database:**
• Total: {total_groups}
• New: {new_groups}
• Updated: {updated_groups}
• Removed: {removed_groups}

👥 **Users Database:**
• Total: {total_users}
• New: {new_users}
• Reachable: {reachable_users}

🔄 **Data Files Reloaded:**
• ✅ Admins & Permissions
• ✅ Attack Replies
• ✅ Name Mapping
• ✅ Security Logs
• ✅ Member Cache
• ✅ Watch Lists
• ✅ Statistics
• ✅ Lock Systems
• ✅ Filters

💾 **Database optimized and cleaned**
🛡️ **All security data preserved**
"""
        
        await progress_msg.edit_text(result_text, parse_mode="Markdown")
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Smart reload failed: {e}")

def save_data():
    """Consolidated save for groups and private users."""
    save_json(GROUPS_FILE, seen_chats)
    save_json(PRIVATE_USERS_FILE, private_users)

async def auto_track_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically tracks groups and users like a permanent /new command."""
    if not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_id_str = str(chat_id)

    # 1. Track Groups/Supergroups
    if chat_type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]:
        if chat_id_str not in seen_chats:
            seen_chats[chat_id_str] = {
                "title": update.effective_chat.title,
                "added_at": datetime.now().isoformat(),
                "type": chat_type,
                "auto_tracked": True
            }
            save_data()
            logging.info(f"🆕 Auto-tracked new group: {update.effective_chat.title} ({chat_id})")
        else:
            # Update title if it changed
            if seen_chats[chat_id_str].get("title") != update.effective_chat.title:
                seen_chats[chat_id_str]["title"] = update.effective_chat.title
                seen_chats[chat_id_str]["type"] = chat_type
                save_data()

    # 2. Track Private Users (DMs)
    elif chat_type == constants.ChatType.PRIVATE:
        if chat_id_str not in private_users:
            user = update.effective_user
            private_users[chat_id_str] = {
                "name": user.first_name or "Unknown",
                "username": user.username or "None",
                "added_at": datetime.now().isoformat(),
                "auto_tracked": True
            }
            save_data()
            logging.info(f"👤 Auto-tracked new DM user: {user.first_name} ({chat_id})")

async def add_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual group saver. Works in group chat directly or by group id."""
    if await check_lock_and_notify(update, context, "add_group"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/add_group")
        await update.message.reply_text("❌ Not authorized.")
        return

    chat = update.effective_chat
    now = datetime.now().isoformat()

    if chat and chat.type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]:
        gid = str(chat.id)
        seen_chats[gid] = {
            "title": chat.title or f"Group {gid}",
            "added_at": seen_chats.get(gid, {}).get("added_at", now),
            "updated_at": now,
            "type": chat.type,
            "manual_added": True,
        }
        save_data()
        await update.message.reply_text(
            f"✅ Group saved\nID: `{gid}`\nName: `{chat.title or 'Unknown'}`",
            parse_mode="Markdown"
        )
        return

    if context.args and context.args[0].lstrip('-').isdigit():
        gid = context.args[0]
        title = " ".join(context.args[1:]).strip() or f"Group {gid}"
        seen_chats[str(gid)] = {
            "title": title,
            "added_at": seen_chats.get(str(gid), {}).get("added_at", now),
            "updated_at": now,
            "type": "manual",
            "manual_added": True,
        }
        save_data()
        await update.message.reply_text(
            f"✅ Group ID saved\nID: `{gid}`\nName: `{title}`",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "❌ Usage:\n• group ထဲမှာ `/add_group`\n• private chat မှာ `/add_group -1001234567890 Group Name`",
        parse_mode="Markdown"
    )


async def reloadgroups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refreshes all groups and syncs them to JSON (like bulk /new)."""
    if not is_owner(update.effective_user):
        return

    msg = await update.message.reply_text("🔄 **Scanning and syncing groups...**", parse_mode="Markdown")
    count_before = len(seen_chats)
    updated_count = 0

    # Sync titles and verify groups
    for cid_str in list(seen_chats.keys()):
        try:
            chat = await context.bot.get_chat(int(cid_str))
            seen_chats[cid_str]["title"] = chat.title
            seen_chats[cid_str]["type"] = chat.type
            updated_count += 1
        except Exception:
            # Group might be inaccessible, we keep it but mark it
            seen_chats[cid_str]["status"] = "inaccessible"

    save_data()
    
    await msg.edit_text(
        f"✅ **Groups Synced!**\n\n"
        f"📂 Total Groups: `{len(seen_chats)}`\n"
        f"🔄 Updated Info: `{updated_count}`\n"
        f"💾 Saved to: `groups.json`",
        parse_mode="Markdown"
    )

async def reloadusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Active re-tracking: Scans recent updates and verifies all DM users."""
    if not is_owner(update.effective_user):
        return

    msg = await update.message.reply_text("🔄 **Deep scanning users database...**", parse_mode="Markdown")
    
    new_found = 0
    # Try to find users from the most recent 100 updates (Telegram limit)
    try:
        updates = await context.bot.get_updates(limit=100, offset=-1)
        for u in updates:
            if u.message and u.effective_chat.type == "private":
                uid_str = str(u.effective_user.id)
                if uid_str not in private_users:
                    private_users[uid_str] = {
                        "name": u.effective_user.first_name,
                        "username": u.effective_user.username,
                        "added_at": datetime.now().isoformat(),
                        "source": "deep_scan"
                    }
                    new_found += 1
    except Exception:
        pass

    save_data()

    await msg.edit_text(
        f"👤 **User Re-tracking Complete**\n\n"
        f"📂 Total DM Users: `{len(private_users)}`\n"
        f"🆕 Found in Scan: `{new_found}`\n"
        f"💾 Database: `private_users.json`",
        parse_mode="Markdown"
    )



# ---------------- IMPROVED MESSAGE HANDLER FOR AUTO-TRACKING ----------------

async def enhanced_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    msg = update.message
    chat = update.effective_chat
    user = update.effective_user

    if not user:
        return

    # ✅ CORRECT: Only track users in PRIVATE chats
    if chat.type == "private" and not user.is_bot:
        user_id_str = str(user.id)
        if user_id_str not in private_users:
            private_users[user_id_str] = {
                "name": user.first_name or "",
                "username": user.username or "",
                "added_at": datetime.now().isoformat(),
                "last_interaction": datetime.now().isoformat(),
                "auto_tracked": True,
                "source": "private_chat_interaction"  # ✅ Mark as real private user
            }
            asyncio.create_task(fast_data.buffered_save(PRIVATE_USERS_FILE, private_users))
        else:
            # Update last interaction time
            private_users[user_id_str]["last_interaction"] = datetime.now().isoformat()

    # ❌ DON'T auto-track group members as private users!
    # Group members should stay in member_cache only
    
    # Continue with normal message processing...

async def security_log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "security_log"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/security_log")
        return

    if not security_log:
        await update.message.reply_text("🗒️ No security events have been logged yet.")
        return

    try:
        recent_events = security_log[-15:]
        log_text = "🔐 *Recent Security Events:*\n\n"

        for event in reversed(recent_events):
            timestamp_str = event.get("timestamp")
            event_type_raw = event.get("type", "UNKNOWN")
            event_type = event_type_raw.replace("_", " ").title()
            details = event.get("details", {})

            timestamp = "Invalid Date"
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str).strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    timestamp = "Invalid Date Format"

            summary = f"- {json.dumps(details, ensure_ascii=False)}"
            log_text += f"`{timestamp}`: *{event_type}*\n{summary}\n\n"

        await update.message.reply_text(log_text, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("An error occurred while fetching the security log.")

async def security_clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "security_clear"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/security_clear")
        return

    try:
        security_log.clear()
        asyncio.create_task(fast_data.buffered_save(SECURITY_LOG_FILE, security_log))
        log_security_event("log_cleared", {
            "cleared_by_id": update.effective_user.id,
            "cleared_by_name": update.effective_user.first_name
        })
        await update.message.reply_text("✅ Security log cleared successfully.")
    except Exception:
        await update.message.reply_text("An error occurred while clearing the log.")

async def unauthorized_log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "unauthorized_log"):
        return
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unauthorized_log")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not unauthorized_log:
        await update.message.reply_text("No unauthorized attempts recorded.")
        return

    last = unauthorized_log[-25:]
    lines = []
    for e in reversed(last):
        ts = e.get("timestamp", "N/A")
        d = e.get("details", {})
        uid = d.get("user_id", "N/A")
        uname = d.get("user_username", "N/A")
        cmd = d.get("command", "N/A")
        chatid = d.get("chat_id", "N/A")
        lines.append(f"`{ts}` - User `{uid}` (@{uname}) tried `{cmd}` in chat `{chatid}`")
    text = "\n".join(lines)
    await update.message.reply_text(text or "No entries.", parse_mode="Markdown")

async def cleanup_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean up the users database - remove fake private users"""
    if not is_owner(update.effective_user):
        return
        
    await update.message.reply_text("🧹 Cleaning up users database...")
    
    original_count = len(private_users)
    cleaned_users = {}
    
    for user_id_str, user_info in private_users.items():
        # Only keep users who actually interacted privately
        if (user_info.get("auto_tracked") or 
            user_info.get("last_interaction") or 
            user_info.get("source") == "private_chat_interaction"):
            cleaned_users[user_id_str] = user_info
    
    private_users.clear()
    private_users.update(cleaned_users)
    
    asyncio.create_task(fast_data.buffered_save(PRIVATE_USERS_FILE, private_users))
    
    await update.message.reply_text(
        f"✅ Users database cleaned!\n"
        f"Before: {original_count} users\n"
        f"After: {len(cleaned_users)} REAL private users\n"
        f"Removed: {original_count - len(cleaned_users)} fake users"
    )


def enhanced_aicheck_score(text):
    text = text.strip()
    words = text.split()
    word_count = len(words)

    if word_count < 50:
        return {
            "verdict": "Not enough text",
            "details": {"word_count": word_count},
        }

    # -------------------------------------------------------------
    # GPTZero-style features
    # -------------------------------------------------------------

    # 1. Burstiness (variance between sentence lengths)
    sentences = re.split(r"[.!?]+\s*", text)
    sentence_lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]

    if len(sentence_lengths) < 2:
        sentence_lengths.append(sentence_lengths[0])

    burstiness = (
        (max(sentence_lengths) - min(sentence_lengths))
        / max(sentence_lengths)
    ) * 100

    # 2. Pseudo Perplexity (lower = more AI)
    average_word_len = sum(len(w) for w in words) / len(words)
    punctuation_count = len(re.findall(r"[.,!?]", text))
    perplexity = (average_word_len * 12) + math.log(punctuation_count + 1) * 25

    # 3. Repetition score (AI repeats more)
    freq = Counter(words)
    common_word_freq = freq.most_common(1)[0][1]
    repetition_rate = (common_word_freq / word_count) * 100

    # 4. Vocabulary richness
    vocab_ratio = len(set(words)) / word_count * 100

    # 5. Bigram (pair word) randomness
    bigrams = list(zip(words, words[1:]))
    bigram_variety = len(set(bigrams)) / len(bigrams) * 100

    # 6. Human irregularity (the higher, the more human)
    human_irregularity = (
        burstiness * 0.45 +
        bigram_variety * 0.3 +
        vocab_ratio * 0.25
    )

    # -------------------------------------------------------------
    # GPTZero style scoring
    # -------------------------------------------------------------

    ai_probability = (
        (100 - burstiness * 0.3) +
        (100 - perplexity * 0.4) +
        (repetition_rate * 1.2) +
        (100 - bigram_variety * 0.6)
    ) / 4

    ai_probability = max(1, min(99, int(ai_probability)))

    human_probability = 100 - ai_probability

    verdict = (
        "Likely AI-generated" if ai_probability >= 70
        else "Mixed / Possibly AI" if ai_probability >= 40
        else "Likely Human-written"
    )

    confidence = (
        "high" if ai_probability >= 75 or ai_probability <= 25 else "medium"
    )

    return {
        "score": ai_probability,
        "human_score": human_probability,
        "verdict": verdict,
        "confidence": confidence,
        "details": {"word_count": word_count},
        "breakdown": {
            "Burstiness": int(burstiness),
            "Pseudo-Perplexity": int(perplexity),
            "Repetition Rate": int(repetition_rate),
            "Vocabulary Richness": int(vocab_ratio),
            "Bigram Variety": int(bigram_variety),
            "Human Irregularity": int(human_irregularity),
        }
    }

async def aicheck_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "aicheck"):
        return

    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/aicheck")
        await update.message.reply_text("❌ Not authorized.")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("❌ Please reply to a message with *at least 50 words*.", parse_mode="Markdown")
        return

    text = update.message.reply_to_message.text
    analysis = enhanced_aicheck_score(text)

    if "Not enough text" in analysis["verdict"]:
        await update.message.reply_text(
            f"⚠️ {analysis['verdict']} (found {analysis['details']['word_count']} words)"
        )
        return

    ai_score = analysis["score"]
    human_score = analysis["human_score"]

    score_emoji = "🤖" if ai_score > 70 else "🧐" if ai_score > 40 else "🤔"
    confidence_emoji = "🟢" if analysis["confidence"] == "high" else "🟡"

    breakdown_list = [
        f"• `{value}%` — {key}"
        for key, value in analysis["breakdown"].items()
    ]
    breakdown_text = "\n".join(breakdown_list)

    result = f"""
{score_emoji} *AI Detection Result (GPTZero-Style)*

*AI Probability:* `{ai_score}%`
*Human Probability:* `{human_score}%`
*Verdict:* *{analysis["verdict"]}*

*Detailed Analysis:*
{breakdown_text}

*Confidence:* `{analysis["confidence"].capitalize()}` {confidence_emoji}
_Based on {analysis["details"]["word_count"]} words_
"""

    await update.message.reply_text(result, parse_mode="Markdown")

# ---------------- LIMITED ADMIN SYSTEM ----------------
async def check_limited_admins():
    current_time = datetime.now()
    to_remove = []
    
    for user_id_str, admin_data in limit_admins.items():
        expires_at = admin_data.get("expires_at")
        if expires_at:
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                if current_time > expires_dt:
                    to_remove.append(user_id_str)
            except:
                to_remove.append(user_id_str)
    
    for user_id_str in to_remove:
        user_id = int(user_id_str)
        if user_id in ADMIN_IDS:
            ADMIN_IDS.remove(user_id)
            if "ids" in admins_data and user_id in admins_data["ids"]:
                admins_data["ids"].remove(user_id)
        
        del limit_admins[user_id_str]
    
    if to_remove:
        asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
        asyncio.create_task(fast_data.buffered_save(LIMIT_ADMINS_FILE, limit_admins))

async def limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "limit"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/limit")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/limit @user <time>`\n\n"
            "Examples:\n"
            "• `/limit @username 1h` - Add as admin for 1 hour\n"
            "• `/limit 123456789 30m` - Add user ID as admin for 30 minutes\n\n"
            "Time formats: 30m, 1h, 2h, 1d",
            parse_mode="Markdown"
        )
        return

    target_arg = context.args[0].strip()
    time_str = context.args[1].lower()
    
    time_seconds = 0
    if time_str.endswith('m'):
        try:
            time_seconds = int(time_str[:-1]) * 60
        except:
            pass
    elif time_str.endswith('h'):
        try:
            time_seconds = int(time_str[:-1]) * 3600
        except:
            pass
    elif time_str.endswith('d'):
        try:
            time_seconds = int(time_str[:-1]) * 86400
        except:
            pass
    else:
        try:
            time_seconds = int(time_str) * 60
        except:
            pass
    
    if time_seconds <= 0:
        await update.message.reply_text("❌ Invalid time format. Use: 30m, 1h, 2h, 1d")
        return
    
    target_id = None
    if target_arg.startswith("@"):
        await update.message.reply_text("⚠️ For limited admins, please use user ID instead of username for better accuracy.")
        return
    else:
        try:
            target_id = int(target_arg)
        except:
            await update.message.reply_text("❌ Invalid user ID.")
            return

    if not target_id:
        await update.message.reply_text("❌ Could not resolve target user.")
        return

    expires_at = (datetime.now() + timedelta(seconds=time_seconds)).isoformat()
    
    limit_admins[str(target_id)] = {
        "added_by": update.effective_user.id,
        "added_by_name": update.effective_user.first_name,
        "added_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "time_granted": time_str
    }
    
    if target_id not in ADMIN_IDS:
        ADMIN_IDS.add(target_id)
        if "ids" not in admins_data:
            admins_data["ids"] = []
        if target_id not in admins_data["ids"]:
            admins_data["ids"].append(target_id)
    
    asyncio.create_task(fast_data.buffered_save(LIMIT_ADMINS_FILE, limit_admins))
    asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
    
    hours = time_seconds // 3600
    minutes = (time_seconds % 3600) // 60
    
    time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    await update.message.reply_text(
        f"⏰ *Limited Admin Added*\n\n"
        f"• User ID: `{target_id}`\n"
        f"• Duration: `{time_display}`\n"
        f"• Added by: {update.effective_user.first_name}\n\n"
        f"User will automatically lose admin rights after the specified time.",
        parse_mode="Markdown"
    )
# --------------- Ping And Performance -------------
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    message = await update.message.reply_text("?? Pong!")
    response_time = (time.time() - start_time) * 1000
    
    # Edit the message with response time
    await message.edit_text(f"🏓 Pong!\n⏱️ Response time: {response_time:.2f}ms")

async def performance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot performance metrics"""
    import psutil
    process = psutil.Process()
    
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent()
    thread_count = process.num_threads()
    
    stats = f"""
🤖 **Performance Metrics**
    
💾 Memory: {memory_mb:.1f} MB
⚡ CPU: {cpu_percent:.1f}%
🧵 Threads: {thread_count}
⏰ Uptime: {get_bot_uptime()}
    
📊 Data Stats:
• Groups: {len(seen_chats)}
• Users: {len(private_users)}
• Filters: {sum(len(f) for f in filters_data.values())}
• Cached Members: {sum(len(c.get('members', {})) for c in member_cache.values())}
"""
    await update.message.reply_text(stats, parse_mode="Markdown")

# ---------------- SHUTDOWN COMMAND ----------------
async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "shutdown"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/shutdown")
        return
    await update.message.reply_text("⏻ Shutting down... bye.")
    asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
    asyncio.create_task(fast_data.buffered_save(PRIVATE_USERS_FILE, private_users))
    asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
    asyncio.create_task(fast_data.buffered_save(MEMBERS_FILE, members_data))
    asyncio.create_task(fast_data.buffered_save(TARGETS_FILE, targets_data))
    asyncio.create_task(fast_data.buffered_save(DIE_FILE, die_configs))
    asyncio.create_task(fast_data.buffered_save(ATTACK_REPLIES_FILE, attack_replies))
    asyncio.create_task(fast_data.buffered_save(NAME_MAP_FILE, name_map))
    asyncio.create_task(fast_data.buffered_save(TRANSLATE_TARGETS_FILE, translate_targets))
    asyncio.create_task(fast_data.buffered_save(SECURITY_LOG_FILE, security_log))
    asyncio.create_task(fast_data.buffered_save(UNAUTHORIZED_LOG_FILE, unauthorized_log))
    asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))
    asyncio.create_task(fast_data.buffered_save(WATCH_LIST_FILE, watch_list))
    asyncio.create_task(fast_data.buffered_save(STATS_FILE, stats_data))
    asyncio.create_task(fast_data.buffered_save(WATCH_LOG_FILE, watch_log))
    asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))
    asyncio.create_task(fast_data.buffered_save(LIMIT_ADMINS_FILE, limit_admins))
    asyncio.create_task(fast_data.buffered_save(GLOBAL_LOCK_FILE, global_lock_config))
    asyncio.create_task(fast_data.buffered_save(FILTERS_FILE, filters_data))
    asyncio.create_task(fast_data.buffered_save(LIMIT_COMMANDS_FILE, limit_commands_data))
    try:
        context.application.stop()
        await asyncio.sleep(1)
    except Exception:
        pass
    os._exit(0)

# ---------------- OPTIMIZED MESSAGE ROUTER ----------------
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    CLEAN & OPTIMIZED MESSAGE ROUTER
    - Handles troll once only
    - Sends message to main processor
    - Avoids duplicate handlers
    """

    # No message? Ignore
    if not update.message:
        return

    msg = update.message
    chat = update.effective_chat
    user = update.effective_user

    # ---------------- TROLL SYSTEM (ONLY HERE) ----------------
    # This is the ONLY troll check you need.
    if chat.id in troll_map and user.id in troll_map[chat.id]:
        await enhanced_troll_reply(context, msg)

    # If no user object (rare Telegram edge case), stop early
    if not user:
        return

    # ---------------- PROCESS MESSAGE IN OPTIMIZER ----------------
    # Everything else is processed inside process_single_message
    await optimizer.process_message(
        process_single_message(update, context, msg, chat, user)
    )
async def process_single_message(update: Update, context: ContextTypes.DEFAULT_TYPE, msg, chat, user):
    # Update stats
    update_stats("messages_processed", chat.id, user.id)

    # PRIVATE CHAT TRACKING & DM NOTIFICATION
    if chat.type == "private":
        # 1. Track User (Existing logic)
        if str(user.id) not in private_users:
            private_users[str(user.id)] = {
                "name": user.first_name or "",
                "username": user.username or ""
            }
            asyncio.create_task(fast_data.buffered_save(PRIVATE_USERS_FILE, private_users))
        
        # 2. NEW: Send Notification to Owner
        # We run this as a task so it doesn't block the rest of the bot
        asyncio.create_task(handle_dm_notification(update, context))


    # USERNAME → USERID CACHE
    if user.username:
        username_to_userid[(chat.id, user.username.lstrip("@").lower())] = user.id

    # MEMBER ACTIVITY CACHE
    if chat.type in ["group", "supergroup"] and not user.is_bot:
        await update_member_cache_on_activity(context, chat.id, user)

    # LOCATION PROCESSOR
    await enhanced_process_location_data(update, context, msg, chat, user)

    # WATCH LIST SYSTEM
    if str(chat.id) in watch_list and str(user.id) in watch_list[str(chat.id)]:
        message_text = msg.text or msg.caption or "[Media message]"
        message_type = "text" if msg.text else "media"
        
        log_watch_event(
            chat_id=chat.id,
            target_user_id=user.id,
            target_username=user.username or user.first_name,
            message_text=message_text,
            message_type=message_type
        )
        
        await notify_owner_watch_activity(
            context,
            chat.id,
            user.id,
            user.username or user.first_name,
            message_text,
            chat.title if hasattr(chat, 'title') else "Private Chat"
        )

    # TRANSLATION SYSTEM
    if str(chat.id) in translate_targets and user.id == translate_targets[str(chat.id)]:
        text_to_translate = msg.text or msg.caption
        if text_to_translate:
            is_myanmar_script = (detect_language(text_to_translate) == 'my')
            is_likely_english = text_to_translate.isascii()

            target_lang, source_display = (
                ('en', 'my') if is_myanmar_script else
                ('my', 'en') if is_likely_english else
                ('en', 'auto')
            )

            translated = await translate_text(text_to_translate, target_lang)
            
            if translated and translated.strip().lower() != text_to_translate.strip().lower():
                await msg.reply_text(
                    f"🌐 ({source_display}→{target_lang}):\n{translated}",
                    parse_mode="Markdown"
                )

    # ⚠️ VERY IMPORTANT:
    # No old troll system here
    # No old filter system here
    # No duplicate echo/reply here

    return

async def enhanced_troll_reply(context: ContextTypes.DEFAULT_TYPE, msg: Message):
    """ENHANCED TROLL REPLY - Echo messages from trolled users with enhancements"""
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    
    # Check if user is trolled in this chat
    if chat_id not in troll_map or user_id not in troll_map[chat_id]:
        return
    
    print(f"🤡 Trolling message from user {user_id} in chat {chat_id}")
    
    try:
        # Get user mention
        user_mention = await get_mention_for_target(context, chat_id, str(user_id))
        
        # Handle different message types
        if msg.text:
            # Text message
            troll_text = f"{user_mention} {msg.text}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown",
                reply_to_message_id=msg.message_id
            )
            
        elif msg.sticker:
            # Sticker - resend with caption
            troll_text = f"{user_mention}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker=msg.sticker.file_id
            )
            
        elif msg.photo:
            # Photo with optional caption
            troll_text = f"{user_mention}"
            if msg.caption:
                troll_text += f"{msg.caption}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=msg.photo[-1].file_id,
                caption=msg.caption if msg.caption else None
            )
            
        elif msg.video:
            # Video with optional caption
            troll_text = f"{user_mention}"
            if msg.caption:
                troll_text += f"{msg.caption}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_video(
                chat_id=chat_id,
                video=msg.video.file_id,
                caption=msg.caption if msg.caption else None
            )
            
        elif msg.document:
            # Document with optional caption
            troll_text = f"{user_mention} {msg.document.file_name or 'File'}"
            if msg.caption:
                troll_text += f"{msg.caption}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_document(
                chat_id=chat_id,
                document=msg.document.file_id,
                caption=msg.caption if msg.caption else None
            )
            
        elif msg.audio:
            # Audio with optional caption
            troll_text = f"{user_mention}"
            if msg.caption:
                troll_text += f"{msg.caption}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=msg.audio.file_id,
                caption=msg.caption if msg.caption else None
            )
            
        elif msg.voice:
            # Voice message
            troll_text = f"{user_mention}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=msg.voice.file_id
            )
            
        elif msg.animation:
            # GIF/Animation
            troll_text = f"{user_mention}"
            if msg.caption:
                troll_text += f"{msg.caption}"
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=msg.animation.file_id,
                caption=msg.caption if msg.caption else None
            )
            
        elif msg.media_group_id:
            # Media group (album) - handle first media only
            troll_text = f"{user_mention}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            
        elif msg.location:
            # Location
            troll_text = f"{user_mention}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_location(
                chat_id=chat_id,
                latitude=msg.location.latitude,
                longitude=msg.location.longitude
            )
            
        elif msg.contact:
            # Contact
            troll_text = f"{user_mention}  {msg.contact.first_name}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
            await context.bot.send_contact(
                chat_id=chat_id,
                phone_number=msg.contact.phone_number,
                first_name=msg.contact.first_name,
                last_name=msg.contact.last_name or ""
            )
            
        else:
            # Unknown content type
            troll_text = f"{user_mention}"
            await context.bot.send_message(
                chat_id=chat_id,
                text=troll_text,
                parse_mode="Markdown"
            )
        
        update_stats("trolled_messages", chat_id, user_id)
        print(f"✅ Successfully trolled message from user {user_id}")
        
    except Exception as e:
        print(f"❌ Troll reply failed: {e}")
        # Fallback simple echo
        try:
            if msg.text:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🤡 {user_mention}: {msg.text}",
                    parse_mode="Markdown"
                )
        except Exception as e2:
            print(f"❌ Even fallback troll failed: {e2}")

# ---------------- CHAT MEMBER HANDLER ----------------
async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fully Integrated Handler:
    1. Member Caching (Old Logic)
    2. HTML Welcome System
    """
    result = update.chat_member
    if not result:
        return

    chat = result.chat
    user = result.new_chat_member.user
    chat_key = str(chat.id)
    
    # --- PART 1: MEMBER CACHE LOGIC (YOUR OLD LOGIC) ---
    new_member_status = result.new_chat_member.status
    
    if new_member_status in ['member', 'administrator', 'creator', 'owner']:
        if chat_key not in member_cache:
            member_cache[chat_key] = {
                "members": {},
                "total_members": 0,
                "last_updated": datetime.now().isoformat(),
                "auto_cached": False
            }
        
        member_cache[chat_key]["members"][str(user.id)] = {
            "first_name": user.first_name or "",
            "username": user.username or "",
            "last_name": user.last_name or "",
            "cached_at": datetime.now().isoformat()
        }
        if user.username:
            username_to_userid[(chat.id, user.username.lower())] = user.id
        
        asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))
        
    elif new_member_status in ['left', 'kicked']:
        if chat_key in member_cache and str(user.id) in member_cache[chat_key].get("members", {}):
            del member_cache[chat_key]["members"][str(user.id)]
            asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))

    # --- PART 2: WELCOME LOGIC (HTML MENTIONS) ---
    # Detect if a user actually JOINED (status was not member, now is member)
    was_not_member = result.old_chat_member.status in [
        constants.ChatMemberStatus.LEFT, 
        constants.ChatMemberStatus.KICKED, 
        None
    ]
    is_now_member = new_member_status in [
        constants.ChatMemberStatus.MEMBER, 
        constants.ChatMemberStatus.ADMINISTRATOR
    ]

    if was_not_member and is_now_member and not user.is_bot:
        entry = welcome_data.get(chat_key, {})
        if entry.get("active"):
            tmpl     = entry.get("text", "")
            photo_id = entry.get("photo_id")
            safe_name  = html.escape(user.first_name or "User")
            mention    = '<a href="tg://user?id=' + str(user.id) + '">' + safe_name + '</a>'
            group_name = html.escape(chat.title or "this group")
            final_text = tmpl.replace("{name}", mention).replace("{group}", group_name)
            if not final_text.strip():
                final_text = "👋 " + mention + " က " + group_name + " သို့ ဝင်ရောက်လာခဲ့သည်"
            try:
                if photo_id:
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo_id,
                        caption=final_text,
                        parse_mode=constants.ParseMode.HTML
                    )
                else:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text=final_text,
                        parse_mode=constants.ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                logging.error("Welcome failed in %s: %s", chat_key, e)

    # ── GOODBYE MESSAGE ──
    was_member = result.old_chat_member.status in [
        constants.ChatMemberStatus.MEMBER,
        constants.ChatMemberStatus.ADMINISTRATOR
    ]
    has_left = new_member_status in [
        constants.ChatMemberStatus.LEFT,
        constants.ChatMemberStatus.KICKED
    ]
    if was_member and has_left and not user.is_bot:
        gb_entry = goodbye_data.get(chat_key, {})
        # goodbye ON by default unless explicitly disabled
        if gb_entry.get("active", True):
            tmpl = gb_entry.get(
                "text",
                "{name} သည် {group} က ကိုကို တွေကို ကြောက်၍ပြေးပါပြီ"
            )
            safe_name  = html.escape(user.first_name or "User")
            mention    = '<a href="tg://user?id=' + str(user.id) + '">' + safe_name + '</a>'
            group_name = html.escape(chat.title or "this group")
            final_text = tmpl.replace("{name}", mention).replace("{group}", group_name)
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=final_text,
                    parse_mode=constants.ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logging.error("Goodbye failed in %s: %s", chat_key, e)

# ---------------- MARKDOWN V2 HELPERS ----------------

def esc(text: str) -> str:
    """Escape ALL special characters for MarkdownV2"""
    if not text:
        return ""
    # These characters MUST be escaped in MarkdownV2:
    # _ * [ ] ( ) ~ ` > # + - = | { } . !
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))

def get_md_mention(user) -> str:
    """Returns a safe MarkdownV2 clickable mention: [Name](tg://user?id=123)"""
    if not user:
        return "Unknown"
    name = user.first_name or "User"
    # Escape the name so special chars don't break the link syntax
    safe_name = esc(name)
    return f"[{safe_name}](tg://user?id={user.id})"

# ---------------- OWNER NOTIFIER (BURMESE + MARKDOWN V2) ----------------
async def security_notify_owner(context, message_md: str, title: str = "Security Event"):
    if not OWNER_CHAT_ID:
        return

    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Burmese Header
        full_msg = (
            f"🚨 *{esc(title)}*\n\n"
            f"{message_md}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ *Security Logged:* `{esc(timestamp)}`"
        )
        
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=full_msg,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Failed to notify owner: {e}")


# ---------------- ROBUST BOT STATUS TRACKER (BURMESE) ----------------
async def track_bot_status_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: Optional[ChatMemberUpdated] = update.my_chat_member
    if not result:
        return

    # Only track changes to the bot itself
    try:
        if result.new_chat_member.user.id != context.bot.id:
            return
    except Exception:
        return

    chat = result.chat
    performer = result.from_user
    old_status = getattr(result.old_chat_member, "status", None)
    new_status = getattr(result.new_chat_member, "status", None)

    # 1. Prepare Data
    safe_chat_title = esc(chat.title or "No Title")
    performer_mention = get_md_mention(performer)
    performer_id = f"`{performer.id}`"

    invite_link = None

    # ---------------- PUBLIC GROUP ----------------
    if chat.username:
        invite_link = f"https://t.me/{chat.username}"

    # ---------------- PRIVATE GROUP (PROMOTED TO ADMIN) ----------------
    elif old_status != "administrator" and new_status == "administrator":
        try:
            # ⚠️ Telegram timing fix
            await asyncio.sleep(1)

            me = await context.bot.get_chat_member(chat.id, context.bot.id)

            # Ensure permission
            if me.can_invite_users:
                invite_link = await context.bot.export_chat_invite_link(chat.id)
        except Exception:
            pass

    # ---------------- FORMAT LINK ----------------
    if invite_link:
        display_text = (
            f"@{esc(chat.username)}"
            if chat.username
            else "Join Group"
        )
        link_text = f"[{display_text}]({esc(invite_link)})"
    else:
        link_text = esc("မရနိုင်ပါ (No link)")

    # ================= 1. Added to Group (Bot Entry) =================
    if old_status in ["left", "kicked", None] and new_status in ["member", "administrator"]:
        
        message_md = (
            f"🤖 *BOT ကို GROUP သို့ ထည့်သွင်းလိုက်ပါပြီ*\n\n"
            f"📌 *အဖွဲ့အမည်:* {safe_chat_title}\n"
            f"🆔 *ID:* `{chat.id}`\n"
            f"🔗 *အဖွဲ့လင့်ခ်:* {link_text}\n\n"
            f"👤 *ထည့်သွင်းသူ:* {performer_mention}\n"
            f"🆔 *User ID:* {performer_id}"
        )

        log_security_event("bot_added", {
            "chat_id": chat.id, 
            "chat_title": chat.title,
            "added_by_id": performer.id, 
            "added_by_name": performer.first_name,
            "timestamp": datetime.now().isoformat()
        })

        await security_notify_owner(context, message_md, "BOT ဝင်ရောက်ခြင်း")

        # Save group data
        seen_chats[str(chat.id)] = {
            "title": chat.title, 
            "type": chat.type,
            "added_by": performer.first_name, 
            "added_by_username": performer.username,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "invite_link": invite_link # Save the link we found
        }
        asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
        asyncio.create_task(auto_cache_chat_members(context, chat.id))
        return

    # ================= 2. Promoted to Admin =================
    elif old_status != "administrator" and new_status == "administrator":
        
        member = result.new_chat_member
        perms = []
        
        # Check specific permissions
        if getattr(member, 'can_manage_chat', False): perms.append("Manage Chat")
        if getattr(member, 'can_delete_messages', False): perms.append("Delete Msgs")
        if getattr(member, 'can_restrict_members', False): perms.append("Ban Users")
        if getattr(member, 'can_invite_users', False): perms.append("Invite Users")
        if getattr(member, 'can_promote_members', False): perms.append("Add Admins")
        
        perm_text = ", ".join(perms) if perms else "None"
        
        custom_title = getattr(member, 'custom_title', None)
        title_txt = f"\n🏷️ *ရာထူး:* `{esc(custom_title)}`" if custom_title else ""

        message_md = (
            f"👑 *BOT ကို ADMIN အဖြစ် ခန့်အပ်လိုက်ပါပြီ*\n\n"
            f"📌 *အဖွဲ့အမည်:* {safe_chat_title}\n"
            f"🆔 *Chat ID:* `{chat.id}`\n"
            f"🔗 *အဖွဲ့လင့်ခ်:* {link_text}\n\n"
            f"👤 *ခန့်အပ်သူ:* {performer_mention}\n"
            f"🆔 *User ID:* {performer_id}{title_txt}\n\n"
            f"📋 *Permissions:* `{esc(perm_text)}`"
        )
        
        await security_notify_owner(context, message_md, "BOT ADMIN PROMOTION")
        return

    # ================= 3. Demoted =================
    elif old_status == "administrator" and new_status != "administrator":
        message_md = (
            f"⬇️ *BOT ကို ADMIN မှ ဖြုတ်ချလိုက်ပါပြီ*\n\n"
            f"📌 *အဖွဲ့အမည်:* {safe_chat_title}\n"
            f"🆔 *Chat ID:* `{chat.id}`\n"
            f"👤 *ဖြုတ်ချသူ:* {performer_mention}\n"
            f"ℹ️ *New Status:* `{esc(str(new_status))}`"
        )
        await security_notify_owner(context, message_md, "BOT DEMOTED")
        return

    # ================= 4. Kicked / Left =================
    elif new_status in ["kicked", "left"]:
        action = "ထုတ်ပယ်ခံရ (Kicked)" if new_status == "kicked" else "ထွက်ခွာ (Left)"
        
        message_md = (
            f"🚫 *BOT {esc(action)} ပါပြီ*\n\n"
            f"📌 *အဖွဲ့အမည်:* {safe_chat_title}\n"
            f"🆔 *Chat ID:* `{chat.id}`\n"
            f"👤 *လုပ်ဆောင်သူ:* {performer_mention}\n"
            f"🆔 *User ID:* {performer_id}"
        )
        
        await security_notify_owner(context, message_md, f"BOT {action}")
        
        # Mark group as inactive or remove
        if str(chat.id) in seen_chats:
            seen_chats.pop(str(chat.id), None)
            asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
        return

# ---------------- UNAUTHORIZED ACCESS HANDLER (BURMESE) ----------------
async def handle_unauthorized_access(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str):
    """Show 'no permission' message with Channel + Owner buttons."""
    user = update.effective_user
    chat = update.effective_chat

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Permission Channel", url=OWNER_CHANNEL_LINK),
            InlineKeyboardButton("Crucial Founder",   url="tg://user?id=" + str(OWNER_CHAT_ID))
        ]
    ])
    try:
        await update.message.reply_text(
            "အရှင်သခင်Hyperionခွင့်ပြုချက်မရသေးပါ",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        pass

    if not user:
        return
        
    chat_id = getattr(chat, "id", "Unknown")
    chat_title = getattr(chat, 'title', "Private Chat") or "Private Chat" 

    # Log to file
    user_info = {
        "user_id": user.id,
        "user_name": user.first_name,
        "user_username": user.username,
        "chat_id": chat_id,
        "chat_title": chat_title,
        "command": command,
    }
    log_unauthorized_attempt(user_info)
    log_security_event("unauthorized_access", user_info)

    # Build Markdown V2 Message
    # User Info with proper Clickable Mention
    user_mention = get_md_mention(user)
    username_txt = f"(@{esc(user.username)})" if user.username else ""
    
    # Chat Info
    safe_chat_title = esc(chat_title)
    
    security_msg = (
        f"🚫 *ခွင့်ပြုချက်မရှိသော လုပ်ဆောင်ချက်*\n\n"
        f"👤 *အသုံးပြုသူ:* {user_mention} {esc(username_txt)}\n"
        f"🆔 *User ID:* `{user.id}`\n\n"
        f"💬 *Chat:* {safe_chat_title}\n"
        f"🆔 *Chat ID:* `{chat_id}`\n\n"
        f"💻 *Command:* `{esc(command)}`"
    )
    
    await security_notify_owner(context, security_msg, "ပါမစ်မရှိပါ")


# ---------------- LOCATION UTILITY FUNCTIONS ----------------

async def get_address_from_coordinates(lat, lon):
    """Convert coordinates to human-readable address"""
    try:
        geolocator = Nominatim(user_agent="telegram_bot")
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True)
        return location.address if location else "Address not found"
    except:
        return "Address lookup failed"

def language_to_region(language_code):
    """Convert language code to likely region"""
    region_map = {
        'en': 'International/English-speaking',
        'es': 'Spanish-speaking regions',
        'fr': 'French-speaking regions', 
        'de': 'German-speaking regions',
        'ru': 'Russian-speaking regions',
        'ar': 'Arabic-speaking regions',
        'zh': 'Chinese-speaking regions',
        'ja': 'Japan',
        'ko': 'Korea',
        'my': 'Myanmar/Burma'
    }
    return region_map.get(language_code, 'Unknown region')

def is_recent(timestamp_str, hours=24):
    """Check if timestamp is recent"""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return (datetime.now() - timestamp).total_seconds() < (hours * 3600)
    except:
        return False

def calculate_location_confidence(shared_locs, ip_loc, behavior, profile):
    """Calculate confidence score for location intelligence"""
    score = 0
    
    # Shared locations (high confidence)
    if shared_locs:
        score += 40
        # Recent shares boost confidence
        latest_share = shared_locs[-1].get('timestamp', '')
        if is_recent(latest_share, hours=24):
            score += 20
    
    # IP location (medium confidence)
    if ip_loc and ip_loc.get('country') != 'Unknown':
        score += 25
    
    # Behavioral patterns (low-medium confidence)
    if behavior and behavior.get('detected_timezone'):
        score += 15
    
    # Profile hints (low confidence)
    if profile and (profile.get('bio_location') or profile.get('language_hint')):
        score += 10
    
    return min(100, score)

def detect_timezone_from_patterns(user_id):
    """Detect timezone from message patterns"""
    user_data = location_tracking.get(str(user_id), {})
    behavioral = user_data.get("behavioral_data", {})
    
    active_hours = behavioral.get("active_hours", [])
    if not active_hours:
        return None
    
    # Simple timezone detection based on active hours
    most_active = max(set(active_hours), key=active_hours.count)
    
    # Map active hour to likely timezone (very approximate)
    timezone_map = {
        range(0, 6): "UTC-8 to UTC-5 (Americas)",
        range(6, 12): "UTC-1 to UTC+2 (Europe/Africa)",
        range(12, 18): "UTC+3 to UTC+8 (Asia)",
        range(18, 24): "UTC+9 to UTC+12 (Oceania/Asia)"
    }
    
    for hour_range, tz in timezone_map.items():
        if most_active in hour_range:
            return tz
    
    return "Unknown"

def get_shared_location_data(target_id):
    """Get shared location data for user"""
    user_data = location_tracking.get(str(target_id), {})
    return user_data.get("shared_locations", [])

async def get_ip_based_location(target_id, chat_id):
    """Get IP-based location (placeholder - would need actual IP data)"""
    # Note: Telegram doesn't provide IP to bots directly
    # This is a placeholder for when you have IP data
    return {"country": "Unknown", "city": "Unknown", "isp": "Unknown"}

def analyze_message_patterns(target_id):
    """Analyze message patterns for location hints"""
    user_data = location_tracking.get(str(target_id), {})
    behavioral = user_data.get("behavioral_data", {})
    
    return {
        "active_hours": behavioral.get("active_hours", []),
        "location_mentions": behavioral.get("location_mentions", []),
        "detected_timezone": behavioral.get("detected_timezone")
    }

def get_profile_location_hints(target_id):
    """Get location hints from profile"""
    user_data = location_tracking.get(str(target_id), {})
    return user_data.get("profile_data", {})

# ---------------- ENHANCED LOCATION DATA PROCESSING ----------------

async def enhanced_process_location_data(update: Update, context: ContextTypes.DEFAULT_TYPE, msg, chat, user):
    """Collect ALL available location intelligence data"""
    user_id = user.id
    
    # Initialize comprehensive tracking
    if str(user_id) not in location_tracking:
        location_tracking[str(user_id)] = {
            "user_info": {
                "username": user.username,
                "first_name": user.first_name,
                "language_code": user.language_code,
            },
            "shared_locations": [],
            "ip_data": {},
            "behavioral_data": {
                "message_count": 0,
                "active_hours": [],
                "location_mentions": [],
                "detected_timezone": None
            },
            "profile_data": {},
            "metadata": {
                "first_seen": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "total_messages": 0
            }
        }
    
    # Update metadata
    location_tracking[str(user_id)]["metadata"]["last_active"] = datetime.now().isoformat()
    location_tracking[str(user_id)]["metadata"]["total_messages"] += 1
    
    # 1. PROCESS DIRECT LOCATION SHARES
    if msg.location:
        await process_direct_location_share(msg, user_id)
    
    # 2. COLLECT BEHAVIORAL DATA
    await collect_behavioral_data(msg, user_id, chat.id)
    
    # 3. EXTRACT PROFILE INTELLIGENCE
    await extract_profile_intelligence(user, user_id)
    
    # Save data
    asyncio.create_task(fast_data.buffered_save(LOCATION_TRACKING_FILE, location_tracking))

async def process_direct_location_share(msg, user_id):
    """Process exact location shares"""
    lat = msg.location.latitude
    lon = msg.location.longitude
    
    address = await get_address_from_coordinates(lat, lon)
    
    location_data = {
        "type": "exact_location",
        "coordinates": {"lat": lat, "lon": lon},
        "address": address,
        "accuracy": "high",
        "timestamp": datetime.now().isoformat(),
        "message_id": msg.message_id
    }
    
    location_tracking[str(user_id)]["shared_locations"].append(location_data)
    
    # Keep last 20 location shares
    if len(location_tracking[str(user_id)]["shared_locations"]) > 20:
        location_tracking[str(user_id)]["shared_locations"] = location_tracking[str(user_id)]["shared_locations"][-20:]

async def collect_behavioral_data(msg, user_id, chat_id):
    """Collect behavioral patterns for location intelligence"""
    behavioral = location_tracking[str(user_id)]["behavioral_data"]
    
    # Track active hours
    current_hour = datetime.now().hour
    if current_hour not in behavioral["active_hours"]:
        behavioral["active_hours"].append(current_hour)
        behavioral["active_hours"] = behavioral["active_hours"][-24:]  # Keep last 24 hours
    
    # Analyze message content for location hints
    if msg.text:
        text_lower = msg.text.lower()
        
        # Location mentions
        location_keywords = ['here', 'there', 'city', 'country', 'visit', 'travel', 'airport', 'hotel']
        if any(keyword in text_lower for keyword in location_keywords):
            behavioral["location_mentions"].append({
                "text": msg.text[:100],
                "timestamp": datetime.now().isoformat()
            })
        
        # Timezone detection from message timing
        behavioral["detected_timezone"] = detect_timezone_from_patterns(user_id)

async def extract_profile_intelligence(user, user_id):
    """Extract location hints from profile"""
    profile_data = location_tracking[str(user_id)]["profile_data"]
    
    # Bio analysis for location hints
    if hasattr(user, 'bio') and user.bio:
        # Simple location extraction from bio
        bio_lower = user.bio.lower()
        location_indicators = ['from', 'based in', 'living in', 'location:', 'city:']
        for indicator in location_indicators:
            if indicator in bio_lower:
                profile_data["bio_location"] = user.bio
                break
    
    # Language as location hint
    if user.language_code:
        profile_data["language_code"] = user.language_code
        profile_data["language_hint"] = language_to_region(user.language_code)

# ---------------- LIMITED ADMIN CHECKER ----------------
async def check_limited_admins_periodically():
    while True:
        await check_limited_admins()
        await asyncio.sleep(60)

async def simple_migration_checker():
    """Simple background task to check group migrations"""
    while True:
        try:
            # Wait 1 hour between checks
            await asyncio.sleep(3600)
            print("⏰ Auto-migration check: Running hourly check...")
            # For now, just log that it's working
            # We'll add actual migration logic later
        except Exception as e:
            print(f"❌ Auto-migration error: {e}")

#--------------- Missing Functions -----------------

# ==================== MESSAGE HANDLER FUNCTIONS ====================

async def handle_ghost_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete messages from ghosted users"""
    if not update.message:
        return
        
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if user is being ghosted in this chat
    if chat_id in ghost_map and user_id in ghost_map[chat_id]:
        try:
            await update.message.delete()
            update_stats("ghosted_messages", chat_id, user_id)
            print(f"👻 Ghost deleted message from {user_id} in chat {chat_id}")
        except Exception as e:
            print(f"❌ Ghost delete failed: {e}")

# ---------------- ENHANCED TROLL SYSTEM - EXACT ECHO ----------------

async def handle_auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-reply to targeted users"""
    if not update.message:
        return
        
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_key = str(chat_id)
    
    # Check if auto-reply is active for this user
    if chat_key in die_configs and die_configs[chat_key].get("active", False):
        target_ids = die_configs[chat_key].get("target_ids", [])
        if user_id in target_ids:
            templates = die_configs[chat_key].get("templates", [])
            if templates:
                reply_text = random.choice(templates)
            else:
                reply_text = random.choice(attack_replies) if attack_replies else "Get rekt."
            
            await update.message.reply_text(reply_text)
            print(f"💀 Auto-replied to {user_id} in chat {chat_id}")


# --- NEW PENDING COMMAND UTILITIES ---

async def command_recorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if not update.message.text.startswith("/"):
        return

    command = update.message.text.split()[0].replace("/", "")
    args = update.message.text.split()[1:]

    # load existing
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "command_id": update.message.message_id,
        "chat_id": update.message.chat_id,
        "user_id": update.message.from_user.id,
        "command": command,
        "args": args
    })

    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def resume_every_command(application):
    import os, json

    if not os.path.exists(PENDING_FILE):
        return

    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            pending = json.load(f)
    except:
        pending = []

    if not pending:
        print("[RESUME] No commands to resume.")
        return

    bot = application.bot
    print(f"[RESUME] Resuming {len(pending)} commands...")

    for cmd in pending.copy():
        try:
            chat_id = cmd["chat_id"]
            user_id = cmd["user_id"]
            command = cmd["command"]
            args = cmd["args"]

            handler_name = command + "_command"
            handler = globals().get(handler_name)

            if not handler:
                print(f"[RESUME] Handler '{handler_name}' not found.")
                continue

            # fetch chat BEFORE using class (fixes your error)
            chat = await bot.get_chat(chat_id)

            class FakeMessage:
                def __init__(self):
                    self.message_id = cmd["command_id"]
                    self.chat = chat
                    self.text = "/" + command + " " + " ".join(args)
                    self.from_user = type("User", (), {"id": user_id})

                async def reply_text(self, txt, parse_mode=None):
                    return await bot.send_message(chat_id, txt, parse_mode=parse_mode)

            fake_message = FakeMessage()
            fake_update = Update(update_id=0, message=fake_message)
            fake_context = CallbackContext.from_update(fake_update, application)
            fake_context.args = args

            # CALL THE ORIGINAL HANDLER
            await handler(fake_update, fake_context)

            print(f"[RESUME] Finished: /{command}")

        except Exception as e:
            print(f"[RESUME ERROR in /{cmd.get('command')}]: {e}")

    # Clear after resume
try:
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        f.write("[]")
except:
    pass

    print("[RESUME] Completed all pending commands.")

# ---------------- REGISTER HANDLERS ----------------

# ─────────────────────────────────────────────────────────────
#  ADM PERMISSIONS CALLBACK
# ─────────────────────────────────────────────────────────────
async def adm_perms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show full permission list for a promoted admin."""
    query = update.callback_query
    await query.answer()
    try:
        _, target_id_str = query.data.split(":", 1)
        target_id = int(target_id_str)
    except Exception:
        return await query.edit_message_text("❌ Invalid data")

    chat = query.message.chat
    try:
        member = await context.bot.get_chat_member(chat.id, target_id)
        name   = html.escape(member.user.first_name or "User " + str(target_id))
    except Exception:
        name   = "User " + str(target_id)
        member = None

    perms_map = [
        ("can_manage_chat",        "Manage Chat"),
        ("can_delete_messages",    "Delete Messages"),
        ("can_restrict_members",   "Restrict Members"),
        ("can_invite_users",       "Invite Users"),
        ("can_promote_members",    "Add Admins"),
        ("can_pin_messages",       "Pin Messages"),
        ("can_manage_video_chats", "Manage Video Chats"),
        ("can_change_info",        "Change Info"),
        ("can_post_messages",      "Post Messages"),
        ("can_edit_messages",      "Edit Messages"),
    ]

    lines = ["<b>" + name + " — Permissions</b>", ""]
    for attr, label in perms_map:
        val  = getattr(member, attr, False) if member else False
        icon = "✅" if val else "❌"
        lines.append(icon + " " + label)

    await query.edit_message_text("\n".join(lines), parse_mode="HTML")


# ─────────────────────────────────────────────────────────────
#  GOODBYE COMMANDS
# ─────────────────────────────────────────────────────────────
async def setgoodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setgoodbye [text]   Placeholders: {name} {group}
    Goodbye is ACTIVE by default in every group.
    """
    user = update.effective_user
    if not is_authorized(user):
        return await update.message.reply_text("❌ Not authorized")

    chat_id = str(update.effective_chat.id)
    if not context.args:
        return await update.message.reply_html(
            "📌 <b>Usage:</b>\n"
            "<code>/setgoodbye {name} သည် {group} ကိုကြောက်၍ ပြေးသွားပါပြီ</code>\n\n"
            "Placeholders: <b>{name}</b> → mention  <b>{group}</b> → group name"
        )
    text = " ".join(context.args)
    goodbye_data[chat_id] = {"active": True, "text": text}
    asyncio.create_task(fast_data.buffered_save(GOODBYE_FILE, goodbye_data))
    await update.message.reply_text("✅ Goodbye message set!")


async def goodbyeoff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user):
        return await update.message.reply_text("❌ Not allowed")
    chat_id = str(update.effective_chat.id)
    if chat_id in goodbye_data:
        goodbye_data[chat_id]["active"] = False
        asyncio.create_task(fast_data.buffered_save(GOODBYE_FILE, goodbye_data))
        return await update.message.reply_text("🟧 Goodbye message disabled.")
    # not in data yet: create entry, mark as off
    goodbye_data[chat_id] = {"active": False, "text": ""}
    asyncio.create_task(fast_data.buffered_save(GOODBYE_FILE, goodbye_data))
    await update.message.reply_text("🟧 Goodbye message disabled.")


async def goodbyeon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_authorized(user):
        return await update.message.reply_text("❌ Not allowed")
    chat_id = str(update.effective_chat.id)
    entry = goodbye_data.get(chat_id, {})
    entry["active"] = True
    goodbye_data[chat_id] = entry
    asyncio.create_task(fast_data.buffered_save(GOODBYE_FILE, goodbye_data))
    await update.message.reply_text("✅ Goodbye message enabled.")


# ============================================================
# 🆕 ADDITIONAL FEATURES (ADDED BY PATCH)
# ============================================================

# --- Won-words (global delete list) ---------------------------------
WON_WORDS_FILE = os.path.join(DATA_DIR, "won_words.json")
won_words: list = load_json(WON_WORDS_FILE, [])

# --- Channel branding for /ngazen broadcast -------------------------
CRUCIAL_CHANNEL_USERNAME = "OfcCrucialXWonAlwaysWin"
CRUCIAL_CHANNEL_LINK     = f"https://t.me/{CRUCIAL_CHANNEL_USERNAME}"
CRUCIAL_BUTTON_TEXT      = "Crucial X Won"


async def add_won_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/add_won <text>  -- owner only. Adds a global forbidden phrase."""
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/add_won")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /add_won <text>")
        return
    phrase = " ".join(context.args).strip()
    if not phrase:
        await update.message.reply_text("❗ Empty phrase.")
        return
    if phrase in won_words_data:
        await update.message.reply_text(f"ℹ️ Already in won-list: <b>{html.escape(phrase)}</b>", parse_mode="HTML")
        return
    won_words_data.append(phrase)
    asyncio.create_task(fast_data.buffered_save(WON_WORDS_FILE, won_words_data))
    await update.message.reply_text(
        f"✅ Won-list ထဲ ထည့်ပြီးပါပြီ: <b>{html.escape(phrase)}</b>",
        parse_mode="HTML"
    )


async def remove_won_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/remove_won <text> -- owner only."""
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/remove_won")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /remove_won <text>")
        return
    phrase = " ".join(context.args).strip()
    if phrase in won_words_data:
        won_words_data.remove(phrase)
        asyncio.create_task(fast_data.buffered_save(WON_WORDS_FILE, won_words_data))
        await update.message.reply_text(f"🗑️ Removed: <b>{html.escape(phrase)}</b>", parse_mode="HTML")
    else:
        await update.message.reply_text("ℹ️ Not found in won-list.")


async def list_won_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/list_won  -- owner only."""
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/list_won")
        return
    if not won_words_data:
        await update.message.reply_text("ℹ️ Won-list is empty.")
        return
    body = "\n".join(f"• {html.escape(w)}" for w in won_words_data)
    await update.message.reply_text(f"<b>🚫 Won-list ({len(won_words_data)})</b>\n{body}", parse_mode="HTML")


async def won_words_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global won-words deletion in any group."""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not won_words_data:
        return

    # Owner / owner-channel / owner-bot ကို ကာကွယ်
    if is_protected_sender(msg):
        return

    # Group Admin / Creator ကိုလည်း ကာကွယ် (အသစ်ထည့်)
    user = msg.from_user
    if user:
        try:
            member = await chat.get_member(user.id)
            if member.status in ("administrator", "creator"):
                return
        except Exception:
            # get_member fail ရင် မဖျက်တာ အန္တရာယ်ကင်းတယ်
            pass

    # NOTE: Won-list deletes for EVERYONE else (including normal members)
    text = (msg.text or "") + "\n" + (msg.caption or "")
    if not text.strip():
        return

    lower = text.lower()
    hit = None
    for w in won_words_data:
        if not w:
            continue
        if w.lower() in lower:
            hit = w
            break
    if not hit:
        return

    # bot က delete လုပ်နိုင်မလား စစ်တယ်
    try:
        me = await context.bot.get_me()
        bm = await context.bot.get_chat_member(chat.id, me.id)
        if not getattr(bm, "can_delete_messages", False):
            return
    except Exception:
        return

    try:
        await context.bot.delete_message(chat.id, msg.message_id)
    except Exception:
        return

    if not user:
        return
    safe_name = html.escape(user.first_name or "User")
    mention = f'<a href="tg://user?id={user.id}">{safe_name}</a>'
    try:
        notify = await context.bot.send_message(
            chat_id=chat.id,
            text=f"ဟိတ်ကောင် {mention} ဒီနေ့ရာမှာလာမရိုင်းနဲ့",
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete_message(context.bot, chat.id, notify.message_id, 10.0))
    except Exception:
        pass


async def owner_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner only — Owner မရှိတဲ့ group တွေအတွက် invite link list ထုတ်ပါ။"""
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "")
        return
    if not seen_chats:
        await update.message.reply_text("❌ Group မရှိပါ")
        return
    
    progress = await update.message.reply_text("⏳ Owner-less groups စစ်နေတယ်...")
    
    results = []  # list of (title, link)
    checked = 0
    total = len(seen_chats)
    
    owner_uid = OWNER_CHAT_ID
    
    for chat_id_str in list(seen_chats.keys()):
        checked += 1
        try:
            chat_id = int(chat_id_str)
        except:
            continue
        
        try:
            chat = await context.bot.get_chat(chat_id)
        except:
            continue
        
        # Check if owner is present in the group
        owner_present = False
        try:
            if owner_uid:
                m = await context.bot.get_chat_member(chat_id, owner_uid)
                if m and m.status in ("member", "administrator", "creator", "restricted"):
                    owner_present = True
        except:
            owner_present = False
        
        if owner_present:
            continue  # Skip groups where owner is in
        
        # Get invite link — public chat ဆို t.me/username, private ဆို export
        link = None
        try:
            if getattr(chat, "username", None):
                link = f"https://t.me/{chat.username}"
            else:
                # private — bot must be admin to export
                try:
                    link = await context.bot.export_chat_invite_link(chat_id)
                except:
                    # try get_chat invite_link
                    try:
                        link = getattr(chat, "invite_link", None)
                    except:
                        link = None
        except:
            link = None
        
        if not link:
            continue
        
        title = chat.title or f"Group {chat_id}"
        results.append((title, link))
        
        # Update progress every 10 groups
        if checked % 10 == 0:
            try:
                await progress.edit_text(f"⏳ စစ်နေတယ်... {checked}/{total} (တွေ့ပြီး: {len(results)})")
            except:
                pass
    
    if not results:
        await progress.edit_text("✅ Owner-less group မရှိပါ (သို့) link မရဘူး")
        return
    
    # Split into chunks of ~25 entries / 3500 chars per message
    CHUNK = 25
    parts = []
    cur = []
    cur_len = 0
    idx = 0
    for title, link in results:
        idx += 1
        line = f"{idx}. <b>{html.escape(title)}</b>\n   🔗 {html.escape(link)}\n"
        if len(cur) >= CHUNK or cur_len + len(line) > 3500:
            parts.append("".join(cur))
            cur = []
            cur_len = 0
        cur.append(line)
        cur_len += len(line)
    if cur:
        parts.append("".join(cur))
    
    # Edit first message into part 1
    header = f"📋 <b>OWNER-LESS GROUPS ({len(results)})</b>\n\n"
    try:
        await progress.edit_text(header + parts[0], parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await update.message.reply_text(header + parts[0], parse_mode="HTML", disable_web_page_preview=True)
    
    for i, p in enumerate(parts[1:], start=2):
        try:
            await update.message.reply_text(
                f"📋 <b>Part {i}/{len(parts)}</b>\n\n" + p,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.3)
        except:
            pass


async def ngazen_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ngazen — Reply ပေးထားတဲ့ post ကို copy ပြီးပို့မယ်။
    စာသားနဲ့ကပ်ပြီး 'Crucial X Won' button တစ်ခု အမြဲပါမယ်။"""
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Usage: Reply to any message with /ngazen\n"
            "စာ/photo/video reply ပေးပြီး /ngazen လို့ပို့ပါ"
        )
        return
    
    src_msg = update.message.reply_to_message
    src_chat_id = src_msg.chat_id
    src_msg_id = src_msg.message_id
    
    # Build the always-present button
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton(CRUCIAL_BUTTON_TEXT, url=CRUCIAL_CHANNEL_LINK)
    ]])
    
    # Targets — groups + private users
    groups_list = []
    for cid_str in seen_chats.keys():
        try:
            groups_list.append(int(cid_str))
        except:
            pass
    
    users_list = []
    for uid_str in private_users.keys():
        try:
            users_list.append(int(uid_str))
        except:
            pass
    
    total = len(groups_list) + len(users_list)
    if total == 0:
        await update.message.reply_text("❌ Recipient မရှိ")
        return
    
    progress = await update.message.reply_text(f"📤 Ngazen Broadcast: 0/{total}")
    
    sent = 0
    failed = 0
    
    async def _send_one(target_id: int):
        nonlocal sent, failed
        try:
            # copy_message preserves text/media but is sent as new message (not forwarded)
            await context.bot.copy_message(
                chat_id=target_id,
                from_chat_id=src_chat_id,
                message_id=src_msg_id,
                reply_markup=button,
            )
            sent += 1
        except Exception as e:
            failed += 1
    
    i = 0
    for tid in groups_list + users_list:
        i += 1
        await _send_one(tid)
        if i % 10 == 0:
            try:
                await progress.edit_text(f"📤 Ngazen Broadcast: {i}/{total} (✅{sent} ❌{failed})")
            except:
                pass
        await asyncio.sleep(0.08)
    
    try:
        await progress.edit_text(
            f"✅ <b>NGAZEN BROADCAST COMPLETE</b>\n\n"
            f"• ✅ Success: {sent}\n"
            f"• ❌ Failed: {failed}\n"
            f"• 📊 Total: {total}\n"
            f"• 🔘 Button: {CRUCIAL_BUTTON_TEXT}\n"
            f"• 🔗 {CRUCIAL_CHANNEL_LINK}",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except:
        pass


async def permit_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner က reply လုပ်ပြီး 'ပါမစ်ပေးလိုက်' / 'ပါမစ်ဖြုတ်' လို့ပြောရင် admin grant/revoke လုပ်ပါမယ်။"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    if not msg.reply_to_message:
        return
    if not is_owner(update.effective_user):
        return
    
    text = msg.text.strip()
    grant_kw = ("ပါမစ်ပေး", "permit", "permit ပေး", "adm permit")
    revoke_kw = ("ပါမစ်ဖြုတ်", "depermit", "unpermit", "remove permit")
    
    is_grant = any(k in text for k in grant_kw)
    is_revoke = any(k in text for k in revoke_kw)
    
    if not (is_grant or is_revoke):
        return
    
    target_user = msg.reply_to_message.from_user
    if not target_user:
        # could be sender_chat — skip
        return
    
    target_id = target_user.id
    target_name = target_user.first_name or f"User{target_id}"
    
    global admins_data, ADMIN_IDS
    
    if is_grant:
        admins_data.setdefault("ids", [])
        if target_id in admins_data["ids"]:
            await msg.reply_text(f"ℹ️ {target_name} ({target_id}) က admin ဖြစ်ပြီးသား")
            return
        admins_data["ids"].append(target_id)
        ADMIN_IDS.add(target_id)
        asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
        await msg.reply_text(
            f"✅ ပါမစ်ပေးပြီးပါပြီ\n"
            f"👤 {target_name}\n"
            f"🆔 `{target_id}`\n"
            f"⭐ Status: Admin",
            parse_mode="Markdown"
        )
    elif is_revoke:
        removed = False
        if "ids" in admins_data and target_id in admins_data["ids"]:
            admins_data["ids"].remove(target_id)
            removed = True
        if target_id in ADMIN_IDS:
            ADMIN_IDS.discard(target_id)
            removed = True
        
        # Also remove from limit_admins
        if str(target_id) in limit_admins:
            del limit_admins[str(target_id)]
            removed = True
            asyncio.create_task(fast_data.buffered_save(LIMIT_ADMINS_FILE, limit_admins))
        
        asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
        
        if removed:
            await msg.reply_text(
                f"✅ ပါမစ်ဖြုတ်ပြီးပါပြီ\n"
                f"👤 {target_name}\n"
                f"🆔 `{target_id}`",
                parse_mode="Markdown"
            )
        else:
            await msg.reply_text(f"ℹ️ {target_name} က admin မဟုတ်ပါ")


# ============================================================
# END OF ADDITIONAL FEATURES
# ============================================================



def html_user_mention(user) -> str:
    if not user:
        return "User"
    safe_name = html.escape(getattr(user, "first_name", None) or getattr(user, "username", None) or "User")
    user_id = getattr(user, "id", None)
    if user_id:
        return f'<a href="tg://user?id={user_id}">{safe_name}</a>'
    return safe_name


def quote_html(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"


async def send_bot_permission_denied(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg:
        return
    mention = html_user_mention(update.effective_user)
    try:
        await msg.reply_text(
            quote_html(f"{mention} အရှင်သခင်Hyperionခွင့်ပြုချက်သင်မရသေပါ"),
            parse_mode="HTML"
        )
    except Exception:
        pass


async def user_is_group_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user) -> bool:
    if not user:
        return False
    if is_owner(user):
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def get_bot_member_in_chat(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        me = await context.bot.get_me()
        return await context.bot.get_chat_member(chat_id, me.id)
    except Exception:
        return None


async def bot_has_permissions(context: ContextTypes.DEFAULT_TYPE, chat_id: int, permissions: tuple[str, ...]) -> bool:
    if not permissions:
        return True
    member = await get_bot_member_in_chat(context, chat_id)
    if not member:
        return False
    if getattr(member, "status", None) == "creator":
        return True
    for perm in permissions:
        if not bool(getattr(member, perm, False)):
            return False
    return True


OWNER_ONLY_COMMANDS = {
    "admin", "rmadmin", "list_admin", "limit", "limitlist", "limitcommand",
    "cleanupusers", "owner", "rmowner", "new", "migrate", "availablegroups",
    "availableusers", "reload", "reloadgroups", "reloadusers", "security_log",
    "security_clear", "unauthorized_log", "shutdown", "stop_bot", "start_bot",
    "add_won", "rmwon", "list_won", "owner_link", "won",
    "should", "newcode", "restart", "leave"
}

ADMIN_GUARD_COMMANDS = {
    "ban", "unban", "mute", "unmute", "adm", "disadm", "out", "title",
    "linkon", "linkoff", "banword", "removeword", "setwelcome", "welcome_off",
    "setgoodbye", "goodbye_off", "goodbye_on", "scan", "cleanmembercache",
    "kick", "warn", "unwarn", "warns", "clearwarns", "muteall", "unmuteall",
    "slowmode", "pin", "unpin", "promote", "demote", "groupinfo", "invitelink",
    "revokelink", "members", "kickall", "setgroupname", "setdesc", "antilink",
    "add_group", "add", "tag", "stoptag", "reply", "unreply", "combo",
    "stopcombo", "send", "user", "sendall", "announce", "broadcast", "notify",
    "alert", "massping", "call", "stopcall", "gpspam", "stopgp", "fight",
    "watch", "unwatch", "watchlist", "watchlog", "stats", "checkuser",
    "checkgroup", "sysinfo", "filter", "rmfilter", "filters", "emfilter",
    "name", "emptyname", "add_message", "delreply", "listreplies", "go",
    "ungo", "mentioning", "listgroup", "aicheck", "translate", "topic",
    "tiktok", "attk", "unattk", "hide", "unhide", "adm_full", "zombie"
}

COMMAND_BOT_PERMISSIONS = {
    "ban": ("can_restrict_members",),
    "unban": ("can_restrict_members",),
    "kick": ("can_restrict_members",),
    "kickall": ("can_restrict_members",),
    "warn": ("can_restrict_members",),
    "clearwarns": ("can_restrict_members",),
    "mute": ("can_restrict_members",),
    "unmute": ("can_restrict_members",),
    "muteall": ("can_restrict_members",),
    "unmuteall": ("can_restrict_members",),
    "linkon": ("can_delete_messages",),
    "linkoff": ("can_delete_messages",),
    "pin": ("can_pin_messages",),
    "unpin": ("can_pin_messages",),
    "promote": ("can_promote_members",),
    "demote": ("can_promote_members",),
    "adm": ("can_promote_members",),
    "disadm": ("can_promote_members",),
    "adm_full": ("can_promote_members",),
    "setgroupname": ("can_change_info",),
    "setdesc": ("can_change_info",),
    "invitelink": ("can_invite_users",),
    "revokelink": ("can_invite_users",),
}

OWNER_CALL_TRIGGER_TARGETS = {u.lower().lstrip("@") for u in [OWNER_USERNAME or "", MASTER_USERNAME or ""] if u}
OWNER_CALL_RUNTIME: Dict[tuple[int, int], Dict[str, Any]] = {}
OWNER_CALL_ATTACK_TASKS: Dict[tuple[int, int], asyncio.Task] = {}


attk_targets: Dict[int, Dict[str, Any]] = {}
attk_tasks: Dict[int, asyncio.Task] = {}


async def attk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply attack: replies to target's LATEST message; no @mention is shown."""
    if await check_lock_and_notify(update, context, "attk"):
        return
    user = update.effective_user
    if not is_authorized(user):
        await handle_unauthorized_access(update, context, "/attk")
        return

    chat = update.effective_chat
    chat_id = chat.id
    target_id = None
    initial_msg_id = None

    if update.message.reply_to_message:
        rep_msg = update.message.reply_to_message
        if rep_msg.from_user:
            target_id = rep_msg.from_user.id
            initial_msg_id = rep_msg.message_id
    elif context.args:
        target_arg = context.args[0]
        if owner_matches_target(target_arg):
            await reverse_attack_owner(context, chat_id, user.id, "attk")
            return
        target_id = await resolve_target_user_id(context, chat_id, target_arg)

    if not target_id:
        await update.message.reply_text(
            "❓ Usage: target ရဲ့ စာကို reply ပြီး /attk\nသို့မဟုတ်: /attk @user | ID"
        )
        return

    if owner_matches_target(str(target_id)):
        await reverse_attack_owner(context, chat_id, user.id, "attk")
        return

    if chat_id in attk_tasks:
        try:
            attk_tasks[chat_id].cancel()
        except Exception:
            pass
        attk_tasks.pop(chat_id, None)

    attk_targets[chat_id] = {
        "target_id": int(target_id),
        "last_msg_id": initial_msg_id,
        "msg_history": [initial_msg_id] if initial_msg_id else [],
    }

    await update.message.reply_text(
        f"🎯 /attk စတင်ပြီ — Target ID: {target_id}\n"
        f"⚡ Speed: {attack_delay.get(chat_id, DEFAULT_DELAY)}s\n"
        f"🛑 ရပ်ရန်: /unattk"
    )
    attk_tasks[chat_id] = asyncio.create_task(attk_loop(context, chat_id))


async def attk_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Reply-attack loop: replies to target's latest tracked message; if deleted, falls back."""
    while chat_id in attk_targets:
        try:
            cfg = attk_targets.get(chat_id)
            if not cfg:
                break
            history = cfg.get("msg_history") or []
            target_msg_id = cfg.get("last_msg_id")
            if not target_msg_id and history:
                target_msg_id = history[-1]
            if not target_msg_id:
                await asyncio.sleep(0.2)
                continue

            line = random.choice(attack_replies) if attack_replies else "..."
            current_delay = attack_delay.get(chat_id, DEFAULT_DELAY)

            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=line,
                    reply_to_message_id=target_msg_id,
                    allow_sending_without_reply=False
                )
            except Exception as e:
                err = str(e).lower()
                if ("message to be replied not found" in err
                    or "reply message not found" in err
                    or "message_id_invalid" in err
                    or "message to reply not found" in err):
                    if target_msg_id in history:
                        try:
                            history.remove(target_msg_id)
                        except ValueError:
                            pass
                    if history:
                        cfg["last_msg_id"] = history[-1]
                    else:
                        cfg["last_msg_id"] = None
                    continue
                elif "too many requests" in err or "flood" in err:
                    wait = extract_wait_time(str(e)) or 3
                    await asyncio.sleep(min(wait, 5))
                    continue
                else:
                    await asyncio.sleep(0.2)

            await asyncio.sleep(max(current_delay, 0.1))
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.2)


async def attk_target_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track target's newest message so /attk follows the freshest reply target."""
    try:
        msg = update.message
        if not msg or not msg.from_user:
            return
        chat_id = msg.chat_id
        cfg = attk_targets.get(chat_id)
        if not cfg:
            return
        if msg.from_user.id == cfg.get("target_id"):
            history = cfg.setdefault("msg_history", [])
            if msg.message_id not in history:
                history.append(msg.message_id)
                if len(history) > 50:
                    del history[:-50]
            cfg["last_msg_id"] = msg.message_id
    except Exception:
        pass


async def unattk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop /attk in this chat."""
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unattk")
        return
    chat_id = update.effective_chat.id
    attk_targets.pop(chat_id, None)
    if chat_id in attk_tasks:
        try:
            attk_tasks[chat_id].cancel()
        except Exception:
            pass
        attk_tasks.pop(chat_id, None)
    await update.message.reply_text("အမိန့်အရဖာသယ်မသားကိုသတ်ပြစ်လိုက်ပါပြီ")


# ============================================================
# /hide — instant message delete (Ghost++)
# ============================================================
hide_map: Dict[int, set] = {}


async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "/leave")
        return

    target_chat_id = None
    if context.args:
        try:
            target_chat_id = int(context.args[0])
        except Exception:
            await update.message.reply_text(quote_html("Usage: /leave [Group ID]"), parse_mode="HTML")
            return
    else:
        chat = update.effective_chat
        if chat and chat.type in ("group", "supergroup"):
            target_chat_id = chat.id
        else:
            await update.message.reply_text(quote_html("Usage: /leave [Group ID]"), parse_mode="HTML")
            return

    chat_title = str(target_chat_id)
    try:
        chat_info = await context.bot.get_chat(target_chat_id)
        chat_title = getattr(chat_info, "title", None) or str(target_chat_id)
    except Exception:
        pass

    leaving_current_chat = bool(update.effective_chat and update.effective_chat.id == target_chat_id)
    try:
        if leaving_current_chat:
            try:
                await update.message.reply_text(quote_html(f"👋 {chat_title} ကနေ ထွက်ခွာနေပါပြီ"), parse_mode="HTML")
            except Exception:
                pass
        await context.bot.leave_chat(target_chat_id)
    except Exception as e:
        await update.message.reply_text(quote_html(f"❌ Leave failed: {e}"), parse_mode="HTML")
        return

    seen_chats.pop(str(target_chat_id), None)
    member_cache.pop(str(target_chat_id), None)
    reply_targets.pop(str(target_chat_id), None)
    lock_config.pop(str(target_chat_id), None)
    asyncio.create_task(fast_data.buffered_save(GROUPS_FILE, seen_chats))
    asyncio.create_task(fast_data.buffered_save(MEMBER_CACHE_FILE, member_cache))
    asyncio.create_task(fast_data.buffered_save(REPLY_TARGETS_FILE, reply_targets))
    asyncio.create_task(fast_data.buffered_save(LOCK_FILE, lock_config))

    if not leaving_current_chat:
        await update.message.reply_text(quote_html(f"✅ Bot က {chat_title} ({target_chat_id}) ကနေ ထွက်သွားပါပြီ"), parse_mode="HTML")



# === OWNER / PERMISSION HELPERS ===

async def handle_owner_only(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str = ""):
    """Show owner-only blockquote message."""
    try:
        await update.message.reply_text(
            "<blockquote>အရှင်သခင်သာသုံးခွင့်ရှိ</blockquote>",
            parse_mode="HTML"
        )
    except Exception:
        pass

def html_user_mention(user) -> str:
    if not user:
        return "User"
    safe_name = html.escape(getattr(user, "first_name", None) or getattr(user, "username", None) or "User")
    user_id = getattr(user, "id", None)
    if user_id:
        return f'<a href="tg://user?id={user_id}">{safe_name}</a>'
    return safe_name

def quote_html(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"

async def adm_full_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အာဏာအပြည့် — give ALL admin permissions like the bot."""
    if await check_lock_and_notify(update, context, "adm_full"):
        return
    user = update.effective_user
    chat = update.effective_chat

    allowed = False
    if is_owner(user):
        allowed = True
    else:
        try:
            cm = await context.bot.get_chat_member(chat.id, user.id)
            if cm.status == "creator":
                allowed = True
        except Exception:
            pass
    if not allowed:
        await handle_owner_only(update, context, "အာဏာအပြည့်")
        return

    target_id = None
    custom_title = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        if context.args:
            custom_title = " ".join(context.args)
    elif context.args:
        target_arg = context.args[0]
        if len(context.args) > 1:
            custom_title = " ".join(context.args[1:])
        target_id = await resolve_target_user_id(context, chat.id, target_arg)
    else:
        await update.message.reply_text(
            "👑 Usage: reply + /adm_full [title]  သို့မဟုတ်  /adm_full @user [title]"
        )
        return

    if not target_id:
        await update.message.reply_text("❌ Target ရှာမတွေ့")
        return

    try:
        await context.bot.promote_chat_member(
            chat_id=chat.id,
            user_id=target_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            can_manage_chat=True,
            can_manage_video_chats=True,
        )
        if custom_title:
            try:
                await context.bot.set_chat_administrator_custom_title(
                    chat_id=chat.id, user_id=target_id, custom_title=custom_title
                )
            except Exception:
                asyncio.create_task(set_title_delayed(context, chat.id, target_id, custom_title))

        try:
            tm = await context.bot.get_chat_member(chat.id, target_id)
            tn = tm.user.first_name or f"User{target_id}"
        except Exception:
            tn = f"User{target_id}"
        safe = html.escape(tn)
        await update.message.reply_text(
            f'👑 <b>အာဏာအပြည့်</b> ပေးပြီ — <a href="tg://user?id={target_id}">{safe}</a>',
            parse_mode="HTML"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")


# ============================================================
# Myanmar admin trigger handlers
# ============================================================
async def myanmar_adm_partial_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အာဏာပေး [title]"""
    text = update.message.text if update.message else ""
    m = re.match(r'^အာဏာပေး\s*(.*)$', text or "", flags=re.DOTALL)
    title = (m.group(1) if m else "").strip()
    context.args = title.split() if title else []
    await adm_command(update, context)


async def myanmar_adm_full_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အာဏာအပြည့် [title]"""
    text = update.message.text if update.message else ""
    m = re.match(r'^အာဏာအပြည့်\s*(.*)$', text or "", flags=re.DOTALL)
    title = (m.group(1) if m else "").strip()
    context.args = title.split() if title else []
    await adm_full_command(update, context)


async def myanmar_disadm_handler_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အာဏာဖြုတ်"""
    text = update.message.text if update.message else ""
    m = re.match(r'^အာဏာဖြုတ်\s*(.*)$', text or "", flags=re.DOTALL)
    arg = (m.group(1) if m else "").strip()
    context.args = arg.split() if arg else []
    await disadm_command(update, context)

hide_map: Dict[int, set] = {}


async def hide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hide target's messages — delete INSTANTLY when posted."""
    if await check_lock_and_notify(update, context, "hide"):
        return
    user = update.effective_user
    if not is_authorized(user):
        await handle_unauthorized_access(update, context, "/hide")
        return

    chat = update.effective_chat
    chat_id = chat.id
    target_ids = []

    if update.message.reply_to_message:
        if update.message.reply_to_message.from_user:
            target_ids.append(update.message.reply_to_message.from_user.id)
    elif context.args:
        for arg in context.args:
            if owner_matches_target(arg):
                await reverse_attack_owner(context, chat_id, user.id, "hide")
                return
            tid = await resolve_target_user_id(context, chat_id, arg)
            if tid:
                target_ids.append(tid)
    else:
        await update.message.reply_text(
            "❓ Usage: reply + /hide  သို့မဟုတ်  /hide @user | ID | nickname"
        )
        return

    if not target_ids:
        await update.message.reply_text("❌ Target ရှာမတွေ့ပါ။")
        return

    hide_map.setdefault(chat_id, set())
    for tid in target_ids:
        hide_map[chat_id].add(int(tid))

    await update.message.reply_text(f"🫥 Hide ON — {len(target_ids)} target instant delete.")


async def unhide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop /hide for current chat."""
    if not is_authorized(update.effective_user):
        await handle_unauthorized_access(update, context, "/unhide")
        return
    chat_id = update.effective_chat.id
    hide_map.pop(chat_id, None)
    await update.message.reply_text("🫥 Hide OFF")


async def _hide_delete_fast(context, chat_id, message_id):
    """Delete a message immediately, retry once on flood."""
    for _ in range(2):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            return
        except Exception as e:
            err = str(e).lower()
            if "too many requests" in err or "flood" in err:
                wait = extract_wait_time(str(e)) or 1
                await asyncio.sleep(min(wait, 3))
                continue
            return


async def hide_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Background delete — does NOT block the event loop."""
    try:
        msg = update.message
        if not msg or not msg.from_user:
            return
        chat_id = msg.chat_id
        uid = msg.from_user.id
        targets = hide_map.get(chat_id)
        if not targets:
            return
        if uid in targets:
            asyncio.create_task(_hide_delete_fast(context, chat_id, msg.message_id))
    except Exception:
        pass
        

def register_handlers(app: Application):
    # ===== BASIC =====
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("show", show_command))
    app.add_handler(CommandHandler("hyperion", ngazen_command))

    # ===== LOCK COMMANDS =====
    app.add_handler(CommandHandler("lock", lock_command))
    app.add_handler(CommandHandler("unlock", unlock_command))
    app.add_handler(CommandHandler("lockallchat", lockallchat_command))
    app.add_handler(CommandHandler("unlockallchat", unlockallchat_command))

    # ===== ATTACK COMMANDS =====
    app.add_handler(CommandHandler("attack", attack_command))
    app.add_handler(CommandHandler("multiple", multiple_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("stopmultiple", stopmultiple_command))
    app.add_handler(CommandHandler("stopall", stopall_command))
    app.add_handler(CommandHandler("burst", burst_command))
    app.add_handler(CommandHandler("zerodelay", zerodelay_command))
    app.add_handler(CommandHandler("smartzerodelay", smartzerodelay_command))
    app.add_handler(CommandHandler("ultimatezerodelay", ultimatezerodelay_command))
    app.add_handler(CommandHandler("normalmode", normalmode_command))
    app.add_handler(CommandHandler("qa", quickattack_command))
    app.add_handler(CommandHandler("quickattack", quickattack_command))
    app.add_handler(CommandHandler("fastspam", fastspam_command))
    app.add_handler(CommandHandler("smartattack", smartattack_command))
    app.add_handler(CommandHandler("hyperburst", hyperburst_command))
    app.add_handler(CommandHandler("ultraburst", ultraburst_command))
    app.add_handler(CommandHandler("megaspam", megaspam_command))
    app.add_handler(CommandHandler("stopmegaspam", stopmegaspam_command))
    app.add_handler(CommandHandler("attackuser", attackuser_command))
    app.add_handler(CommandHandler("stopuser", stopuser_command))
    app.add_handler(CommandHandler("secret", secret_command))
    app.add_handler(CommandHandler("unsecret", unsecret_command))

    # ===== NEW ATTACK COMMANDS =====
    app.add_handler(CommandHandler("ultraattack", ultraattack_command))
    app.add_handler(CommandHandler("nuke", nuke_command))
    app.add_handler(CommandHandler("turboattack", turboattack_command))
    app.add_handler(CommandHandler("blastattack", blastattack_command))
    app.add_handler(CommandHandler("xattack", xattack_command))
    app.add_handler(CommandHandler("hyperattack", hyperattack_command))
    app.add_handler(CommandHandler("superattack", superattack_command))
    app.add_handler(CommandHandler("stormattack", stormattack_command))
    app.add_handler(CommandHandler("shadowattack", shadowattack_command))
    app.add_handler(CommandHandler("fireattack", fireattack_command))
    app.add_handler(CommandHandler("killattack", killattack_command))
    app.add_handler(CommandHandler("deathattack", deathattack_command))
    app.add_handler(CommandHandler("wipeattack", wipeattack_command))
    app.add_handler(CommandHandler("bombattack", bombattack_command))
    app.add_handler(CommandHandler("strikeattack", strikeattack_command))
    app.add_handler(CommandHandler("laserattack", laserattack_command))
    app.add_handler(CommandHandler("warattack", warattack_command))
    app.add_handler(CommandHandler("missileattack", missileattack_command))

    # ===== SPEED COMMANDS =====
    app.add_handler(CommandHandler("fastest", fastest_command))
    app.add_handler(CommandHandler("godspeed", godspeed_command))
    app.add_handler(CommandHandler("ultragodspeed", ultragodspeed_command))
    app.add_handler(CommandHandler("newgodrebornspeed", newgodrebornspeed_command))
    app.add_handler(CommandHandler("normal", normal_command))
    app.add_handler(CommandHandler("flashspeed", flashspeed_command))
    app.add_handler(CommandHandler("lightspeed", lightspeed_command))
    app.add_handler(CommandHandler("hyperspeed", hyperspeed_command))
    app.add_handler(CommandHandler("instantspeed", instantspeed_command))
    app.add_handler(CommandHandler("slow", slow_command))
    app.add_handler(CommandHandler("setspeed", setspeed_command))
    app.add_handler(CommandHandler("mode", mode_command))

    # ===== NEW SPEED COMMANDS =====
    app.add_handler(CommandHandler("ludicrous", ludicrous_command))
    app.add_handler(CommandHandler("warpspeed", warpspeed_command))
    app.add_handler(CommandHandler("sonicspeed", sonicspeed_command))
    app.add_handler(CommandHandler("turbomode", turbomode_command))
    app.add_handler(CommandHandler("overdrive", overdrive_command))
    app.add_handler(CommandHandler("rapidfire", rapidfire_command))
    app.add_handler(CommandHandler("blitzspeed", blitzspeed_command))
    app.add_handler(CommandHandler("maxspeed", maxspeed_command))
    app.add_handler(CommandHandler("plaidspeed", plaidspeed_command))
    app.add_handler(CommandHandler("supersonicspeed", supersonicspeed_command))

    # ===== SETTARGET =====
    app.add_handler(CommandHandler("settarget", settarget_command))
    app.add_handler(CommandHandler("stopxsettarget", stopxsettarget_command))

    # ===== GHOST & TROLL =====
    app.add_handler(CommandHandler("ghost", ghost_command))
    app.add_handler(CommandHandler("stopghost", stopghost_command))
    app.add_handler(CommandHandler("troll", troll_command))
    app.add_handler(CommandHandler("stoptroll", stoptroll_command))
    app.add_handler(CommandHandler("ghostall", ghostall_command))
    app.add_handler(CommandHandler("unghostall", unghostall_command))

    # ===== MODERATION =====
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("adm", adm_command))
    app.add_handler(CommandHandler("disadm", disadm_command))
    app.add_handler(CommandHandler("out", out_command))
    app.add_handler(CommandHandler("title", settitle_command))
    app.add_handler(CommandHandler("linkon", linkon_command))
    app.add_handler(CommandHandler("linkoff", linkoff_command))
    # === ADDED BY PATCH ===
    app.add_handler(CommandHandler("add_won", add_won_command))
    app.add_handler(CommandHandler("rmwon", remove_won_command))
    app.add_handler(CommandHandler("list_won", list_won_command))
    app.add_handler(CommandHandler("owner_link", owner_link_command))
    app.add_handler(CommandHandler("won", ngazen_broadcast_command))
    # also alias /ngazen to broadcast when used as reply (keep original /ngazen list command name)
    app.add_handler(CommandHandler("ngazenpost", ngazen_broadcast_command))
    app.add_handler(CommandHandler("nz", ngazen_broadcast_command))
    app.add_handler(CommandHandler("banword", banword_command))
    app.add_handler(CommandHandler("removeword", removeword_command))
    app.add_handler(CommandHandler("listword", listword_command))
    app.add_handler(CommandHandler("setwelcome", setwelcome_command))
    app.add_handler(CommandHandler("welcome_off", welcomeoff_command))
    app.add_handler(CommandHandler("setgoodbye", setgoodbye_command))
    app.add_handler(CommandHandler("goodbye_off", goodbyeoff_command))
    app.add_handler(CommandHandler("goodbye_on",  goodbyeon_command))
    app.add_handler(CallbackQueryHandler(adm_perms_callback,   pattern=r"^adm_perms:"))
    app.add_handler(CallbackQueryHandler(start_about_callback, pattern=r"^start_about$"))
    app.add_handler(CallbackQueryHandler(how_to_use_callback, pattern=r"^how_to_use$"))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("cleanmembercache", cleanmembercache_command))

    # ===== GROUP ADMIN COMMANDS =====
    app.add_handler(CommandHandler("kick", kick_command))
    app.add_handler(CommandHandler("warn", warn_command))
    app.add_handler(CommandHandler("unwarn", unwarn_command))
    app.add_handler(CommandHandler("warns", warns_command))
    app.add_handler(CommandHandler("clearwarns", clearwarns_command))
    app.add_handler(CommandHandler("muteall", muteall_command))
    app.add_handler(CommandHandler("unmuteall", unmuteall_command))
    app.add_handler(CommandHandler("slowmode", slowmode_command))
    app.add_handler(CommandHandler("pin", pin_command))
    app.add_handler(CommandHandler("unpin", unpin_command))
    app.add_handler(CommandHandler("promote", promote_command))
    app.add_handler(CommandHandler("demote", demote_command))
    app.add_handler(CommandHandler("groupinfo", groupinfo_command))
    app.add_handler(CommandHandler("invitelink", invitelink_command))
    app.add_handler(CommandHandler("revokelink", revokelink_command))
    app.add_handler(CommandHandler("members", members_command))
    app.add_handler(CommandHandler("kickall", kickall_command))
    app.add_handler(CommandHandler("setgroupname", setgroupname_command))
    app.add_handler(CommandHandler("setdesc", setdesc_command))
    app.add_handler(CommandHandler("antilink", antilink_command))

    # ===== TARGETING =====
    app.add_handler(CommandHandler("add_group", add_group_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("tag", tag_command))
    app.add_handler(CommandHandler("stoptag", stoptag_command))
    # disabled lightweight build: app.add_handler(CommandHandler("funny", funny_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stopfunny", stop_funny_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, funny_message_handler), group=6)
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("unreply", unreply_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_auto_handler))
    app.add_handler(CommandHandler("combo", combo_command))
    app.add_handler(CallbackQueryHandler(combo_callback, pattern=r"^combo\|"))
    app.add_handler(CommandHandler("stopcombo", stopcombo_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, combo_target_listener), group=1)

    # ===== BROADCAST =====
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(CommandHandler("user", senduser_command))
    app.add_handler(CommandHandler("senduser", senduser_command))
    app.add_handler(CommandHandler("sendall", sendall_command))
    app.add_handler(CommandHandler("announce", announce_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("attk", attk_command))
    app.add_handler(CommandHandler("unattk", unattk_command))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, attk_target_tracker), group=-7)
    app.add_handler(CommandHandler("leave", leave_command))
    app.add_handler(CommandHandler("notify", notify_command))
    app.add_handler(CommandHandler("alert", alert_command))
    app.add_handler(CommandHandler("massping", massping_command))
    app.add_handler(CommandHandler("call", call_command))
    app.add_handler(CommandHandler("stopcall", stopcall_command))
    app.add_handler(CommandHandler("gpspam", gpspam_command))
    app.add_handler(CommandHandler("stopgp", stopgp_command))
    app.add_handler(CommandHandler("fight", fight_command))
    app.add_handler(CallbackQueryHandler(
        fight_callback_handler, 
        pattern=r"^f(p|s|c):[a-f0-9]{8}:"
))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, fight_message_handler), group=5)

    # ===== WATCH & STATS =====
    app.add_handler(CommandHandler("watch", watch_command))
    app.add_handler(CommandHandler("unwatch", unwatch_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CommandHandler("watchlog", watchlog_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("ping", ping_command))
    # disabled lightweight build: app.add_handler(CommandHandler("performance", performance_command))
    # disabled lightweight build: app.add_handler(CommandHandler("speedtest", speedtest_command))

    # ===== FUN COMMANDS =====
    # disabled lightweight build: app.add_handler(CommandHandler("roast", roast_command))
    # disabled lightweight build: app.add_handler(CommandHandler("compliment", compliment_command))
    # disabled lightweight build: app.add_handler(CommandHandler("insult", insult_command))
    app.add_handler(CommandHandler("mock", mock_command))
    # disabled lightweight build: app.add_handler(CommandHandler("gg", gg_command))
    # disabled lightweight build: app.add_handler(CommandHandler("rip", rip_command))
    # disabled lightweight build: app.add_handler(CommandHandler("oof", oof_command))
    # disabled lightweight build: app.add_handler(CommandHandler("yeet", yeet_command))
    app.add_handler(CommandHandler("roll", roll_command))
    # disabled lightweight build: app.add_handler(CommandHandler("coin", coin_command))
    # disabled lightweight build: app.add_handler(CommandHandler("ball", ball8_command))
    # disabled lightweight build: app.add_handler(CommandHandler("quote", quote_command))
    # disabled lightweight build: app.add_handler(CommandHandler("joke", joke_command))
    # disabled lightweight build: app.add_handler(CommandHandler("fact", fact_command))
    # disabled lightweight build: app.add_handler(CommandHandler("flip", flip_command))
    # disabled lightweight build: app.add_handler(CommandHandler("choose", choose_command))
    # disabled lightweight build: app.add_handler(CommandHandler("pick", pick_command))
    # disabled lightweight build: app.add_handler(CommandHandler("echo", echo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("shout", shout_command))
    # disabled lightweight build: app.add_handler(CommandHandler("reversetext", reversetext_command))
    # disabled lightweight build: app.add_handler(CommandHandler("upper", upper_command))
    # disabled lightweight build: app.add_handler(CommandHandler("lower", lower_command))
    # disabled lightweight build: app.add_handler(CommandHandler("wordcount", wordcount_command))
    # disabled lightweight build: app.add_handler(CommandHandler("repeat", repeat_command))

    # ===== UTILITY COMMANDS =====
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("myid", myid_command))
    app.add_handler(CommandHandler("uptime", uptime_command))
    app.add_handler(CommandHandler("version", version_command))
    app.add_handler(CommandHandler("botinfo", botinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("calc", calc_command))
    # disabled lightweight build: app.add_handler(CommandHandler("gettime", gettime_command))
    # disabled lightweight build: app.add_handler(CommandHandler("getdate", getdate_command))
    # disabled lightweight build: app.add_handler(CommandHandler("base64en", base64en_command))
    # disabled lightweight build: app.add_handler(CommandHandler("base64de", base64de_command))
    # disabled lightweight build: app.add_handler(CommandHandler("urlencode", urlencode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("urldecode", urldecode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("genpass", genpass_command))
    # disabled lightweight build: app.add_handler(CommandHandler("genuuid", genuuid_command))
    # disabled lightweight build: app.add_handler(CommandHandler("randomnum", randomnum_command))
    app.add_handler(CommandHandler("checkuser", checkuser_command))
    app.add_handler(CommandHandler("checkgroup", checkgroup_command))
    # disabled lightweight build: app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("sysinfo", sysinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("note", note_command))
    # disabled lightweight build: app.add_handler(CommandHandler("tracklocation", enhanced_tracklocation_command))
    # disabled lightweight build: app.add_handler(CommandHandler("locationscan", locationscan_command))

    # ===== MANAGEMENT COMMANDS =====
    # disabled lightweight build: app.add_handler(CommandHandler("black_list", addblacklist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("rmblack_list", removeblacklist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("listblacklist", listblacklist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("clearblacklist", clearblacklist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("addwhitelist", addwhitelist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("removewhitelist", removewhitelist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("listwhitelist", listwhitelist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("freeze", freeze_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unfreeze", unfreeze_command))
    # disabled lightweight build: app.add_handler(CommandHandler("silent", silent_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unsilent", unsilent_command))
    # disabled lightweight build: app.add_handler(CommandHandler("backup", backup_command))
    # disabled lightweight build: app.add_handler(CommandHandler("export", export_command))
    # disabled lightweight build: app.add_handler(CommandHandler("purge", purge_command))
    # disabled lightweight build: app.add_handler(CommandHandler("resetstats", resetstats_command))
    # disabled lightweight build: app.add_handler(CommandHandler("clearlog", clearlog_command))

    # ===== MONITOR/SPY COMMANDS =====
    # disabled lightweight build: app.add_handler(CommandHandler("monitor", monitor_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unmonitor", unmonitor_command))
    # disabled lightweight build: app.add_handler(CommandHandler("monitorlist", monitorlist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("spymode", spymode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stopspymode", stopspymode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stealthmode", stealthmode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stopstealthmode", stopstealthmode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("observe", observe_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unobserve", unobserve_command))
    # disabled lightweight build: app.add_handler(CommandHandler("patrol", patrol_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stoppatrol", stoppatrol_command))
    # disabled lightweight build: app.add_handler(CommandHandler("enable", enable_command))
    # disabled lightweight build: app.add_handler(CommandHandler("disable", disable_command))
    # disabled lightweight build: app.add_handler(CommandHandler("setlang", setlang_command))
    # disabled lightweight build: app.add_handler(CommandHandler("setmode", setmode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("getmode", getmode_command))
    # disabled lightweight build: app.add_handler(CommandHandler("getinfo", getinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("sysinfo", sysinfo_command))

    # ===== STICKER COMMANDS =====
    # disabled lightweight build: app.add_handler(CommandHandler("savesticker", savesticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("getsticker", getsticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("liststickers", liststickers_command))
    # disabled lightweight build: app.add_handler(CommandHandler("removesticker", removesticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("clearstickers", clearstickers_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stickerinfo", stickerinfo_command))

    # ===== ADMIN MANAGEMENT =====
    app.add_handler(CommandHandler("admin", add_admin_command))
    app.add_handler(CommandHandler("rmadmin", remove_admin_command))
    app.add_handler(CommandHandler("list_admin", list_admins_command))
    app.add_handler(CommandHandler("limit", limit_command))
    app.add_handler(CommandHandler("limitlist", limitlist_command))
    app.add_handler(CommandHandler("limitcommand", limitcommand_command))
    app.add_handler(CommandHandler("cleanupusers", cleanup_users_command))
    app.add_handler(CommandHandler("owner", owner_command))
    app.add_handler(CommandHandler("removeowner", removeowner_command))
    app.add_handler(CommandHandler("gang", gang_command))

    # ===== FILTER / NAME =====
    app.add_handler(CommandHandler("filter", filter_command))
    app.add_handler(CommandHandler("rmfilter", removefilter_command))
    app.add_handler(CommandHandler("filters", filterlist_command))
    app.add_handler(CommandHandler("emfilter", emptyfilter_command))
    app.add_handler(CommandHandler("name", name_command))
    app.add_handler(CommandHandler("emptyname", emptyname_command))
    app.add_handler(CommandHandler("add_message", add_reply_command))
    app.add_handler(CommandHandler("delreply", delreply_command))
    app.add_handler(CommandHandler("listreplies", listreplies_command))

    # ===== GO & MENTIONING =====
    app.add_handler(CommandHandler("go", go_command))
    app.add_handler(CommandHandler("ungo", ungo_command))
    app.add_handler(CommandHandler("mentioning", mentioning_command))
    app.add_handler(CommandHandler("listgroup", listgroup_command))

    # ===== AI & TOOLS =====
    # disabled lightweight build: app.add_handler(CommandHandler("ai", ai_handler))
    app.add_handler(CommandHandler("aicheck", aicheck_command))
    app.add_handler(CommandHandler("translate", translate_command))
    app.add_handler(CommandHandler("topic", topic_command))
    app.add_handler(CallbackQueryHandler(topic_callback, pattern="^topic_mm_"))
    app.add_handler(CommandHandler("TikTok", tiktok_command))
    app.add_handler(CallbackQueryHandler(tt_caption_handler, pattern="^tt_cap_"))

    # ===== DATABASE & GROUPS =====
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CommandHandler("migrate", migrate_command))
    app.add_handler(CommandHandler("availablegroups", availablegroups_command))
    app.add_handler(CommandHandler("availableusers", availableusers_command))
    app.add_handler(CommandHandler("reload", reload_command))
    app.add_handler(CommandHandler("reloadgroups", reloadgroups_command))
    app.add_handler(CommandHandler("reloadusers", reloadusers_command))

    # ===== SECURITY =====
    app.add_handler(CommandHandler("security_log", security_log_command))
    app.add_handler(CommandHandler("security_clear", security_clear_command))
    app.add_handler(CommandHandler("unauthorized_log", unauthorized_log_command))
    # disabled lightweight build: app.add_handler(CommandHandler("lock", lock_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unlock", unlock_command))
    # disabled lightweight build: app.add_handler(CommandHandler("lockallchat", lockallchat_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unlockallchat", unlockallchat_command))

     # ===== MYANMAR COMMANDS (No Slash - Reply Support) =====
    app.add_handler(MessageHandler(filters.Regex(r'^သတ်ပြစ်လိုက်(\s|$)') & ~filters.COMMAND, myanmar_go_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^သတ်ပြစ်(\s|$)') & ~filters.COMMAND, myanmar_attack_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^တော်ပြီ(\s|$)') & ~filters.COMMAND, myanmar_stop_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မသတ်နဲ့တော့(\s|$)') & ~filters.COMMAND, myanmar_stop_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အယ်ခွေးစာကိုဖျက်(\s|$)') & ~filters.COMMAND, myanmar_ghost_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မဖျက်နဲ့တော့(\s|$)') & ~filters.COMMAND, myanmar_stopghost_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ငနုပြောင်(\s|$)') & ~filters.COMMAND, myanmar_troll_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မပြောင်နဲ့တော့(\s|$)') & ~filters.COMMAND, myanmar_stoptroll_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အင်းဖိုပြ(\s|$)') & ~filters.COMMAND, myanmar_id_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ဘမ်းလိုက်ကွာသူကို(\s|$)') & ~filters.COMMAND, myanmar_ban_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ဘမ်းဖြည့်လိုက်ကွာ(\s|$)') & ~filters.COMMAND, myanmar_unban_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ကစ်လိုက်သူကို(\s|$)') & ~filters.COMMAND, myanmar_kick_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မြု့လိုက်ခွေးကို(\s|$)') & ~filters.COMMAND, myanmar_mute_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မြု့ဖြည့်တဗဲ့(\s|$)') & ~filters.COMMAND, myanmar_unmute_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ဘော့စတင်းမယ်(\s|$)') & ~filters.COMMAND, myanmar_start_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^စာထောက်ကိုက်(\s|$)') & ~filters.COMMAND, myanmar_reply_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မကိုက်နဲ့တော့(\s|$)') & ~filters.COMMAND, myanmar_unreply_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ရပ်အကုန်(\s|$)') & ~filters.COMMAND, myanmar_stopall_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မန်ရှင်အကုန်ခေါ်မယ်(\s|$)') & ~filters.COMMAND, myanmar_call_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မန်ရှင်ခေါ်တာရပ်မယ်(\s|$)') & ~filters.COMMAND, myanmar_stopcall_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ကဲ့တဗဲ့စာဖြန့်(\s|$)') & ~filters.COMMAND, myanmar_sendall_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ပွဲခေါ်မယ်ကွာ(\s|$)') & ~filters.COMMAND, myanmar_fight_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အင်းအားပြမယ်(\s|$)') & ~filters.COMMAND, myanmar_combo_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မင်းကငါတဗဲ့ဖြစ်ပြီ(\s|$)') & ~filters.COMMAND, myanmar_adm_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ပြန်ကန်ခွေးကိုပြုတ်(\s|$)') & ~filters.COMMAND, myanmar_disadm_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^စောင့်ကြည့်(\s|$)') & ~filters.COMMAND, myanmar_watch_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^မစောင့်နဲ့တော့(\s|$)') & ~filters.COMMAND, myanmar_unwatch_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^နာမည်ပေး(\s|$)') & ~filters.COMMAND, myanmar_name_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^ပစ်မှတ်ထား(\s|$)') & ~filters.COMMAND, myanmar_settarget_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^စစ်ဆေး(\s|$)') & ~filters.COMMAND, myanmar_scan_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အကူ(\s|$)') & ~filters.COMMAND, myanmar_help_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^တွယ်(\s|$)') & ~filters.COMMAND, myanmar_pin_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^တွယ်ဖြုတ်(\s|$)') & ~filters.COMMAND, myanmar_unpin_handler), group=-10)

# /zen command
    app.add_handler(CommandHandler("zen", zen_command))
    # ===== MISC =====
    # disabled lightweight build: app.add_handler(CommandHandler("destroy", destroy_command))
    # disabled lightweight build: app.add_handler(CommandHandler("report", report_command))
    # disabled lightweight build: app.add_handler(CommandHandler("whyfail", whyfail_command))
    # disabled lightweight build: app.add_handler(CommandHandler("test", test_command))
    # disabled lightweight build: app.add_handler(CommandHandler("delete", delete_command))
    # disabled lightweight build: app.add_handler(CommandHandler("on", on_command))
    app.add_handler(CommandHandler("shutdown", shutdown_command))
    app.add_handler(CommandHandler("hide", hide_command))
    app.add_handler(CommandHandler("unhide", unhide_command))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, hide_message_handler), group=-9)
    
    # ===== NEW: Myanmar admin =====
    app.add_handler(CommandHandler("adm_full", adm_full_command))
    app.add_handler(MessageHandler(filters.Regex(r'^အာဏာပေး(\s|$)') & ~filters.COMMAND, myanmar_adm_partial_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အာဏာအပြည့်(\s|$)') & ~filters.COMMAND, myanmar_adm_full_handler), group=-10)
    app.add_handler(MessageHandler(filters.Regex(r'^အာဏာဖြုတ်(\s|$)') & ~filters.COMMAND, myanmar_disadm_handler_new), group=-10)
    # ===== GPSPAM CALLBACK =====
    app.add_handler(CallbackQueryHandler(gpspam_callback_handler, pattern=r"^gps(p|s|c):"))

    # ===== CHAT MEMBER SYSTEM (ALWAYS ON) =====
    # Welcome ရော Goodbye ရောကို ပုံနဲ့တကွ ဒီတစ်ခုတည်းကပဲ အကုန်လုပ်ပေးပါသည် (၂ ခါမထပ်တော့ပါ)
    app.add_handler(ChatMemberHandler(on_chat_member_update, ChatMemberHandler.ANY_CHAT_MEMBER))
    
    # Bot ကိုယ်တိုင်ရဲ့ Status ကို စစ်တာ
    app.add_handler(ChatMemberHandler(track_bot_status_in_chat, ChatMemberHandler.MY_CHAT_MEMBER), group=-5)

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_trigger_handler))
    # Database track လုပ်ဖို့
    app.add_handler(MessageHandler(filters.ALL, auto_track_handler), group=-4)

    # ===== MESSAGE HANDLERS (PRIORITY ORDER) =====
    # Anti-link guard (highest priority)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, link_guard_handler), group=-1)
    
    # Banword handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, banword_message_handler), group=-3)
    # === ADDED BY PATCH ===
    # Won-words: auto-delete messages containing won list entries
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, won_words_handler), group=-4)
    # Permit / depermit by reply text (owner only)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, permit_reply_handler), group=-6)
    
    # Ghost mode monitor
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, ghost_mode_monitor), group=-2)
    
    # Ghost delete (high priority)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_ghost_messages), group=2)
    
    # Auto-reply handler
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_auto_reply), group=3)
    
    # Main message router
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_router), group=4)


    # ===== EXTRA COMMANDS FOR 300 =====
   # disabled lightweight build: # app.add_handler(CommandHandler("softban", softban_command))
   # disabled lightweight build: # app.add_handler(CommandHandler("tempban", tempban_command))
   # disabled lightweight build: # app.add_handler(CommandHandler("unbanall", unban_all_command))
    # disabled lightweight build: app.add_handler(CommandHandler("countmembers", countmembers_command))
    # disabled lightweight build: app.add_handler(CommandHandler("getlink", getlink_command))
    # disabled lightweight build: app.add_handler(CommandHandler("silence", silence_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unsilence", unsilence_command))
    # disabled lightweight build: app.add_handler(CommandHandler("protect", protect_command))
    # disabled lightweight build: app.add_handler(CommandHandler("unprotect", unprotect_command))
    # disabled lightweight build: app.add_handler(CommandHandler("sendsticker", sendsticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("mystickers", mystickers_command))
    # disabled lightweight build: app.add_handler(CommandHandler("packinfo", packinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stickerset", stickerset_command))
    # disabled lightweight build: app.add_handler(CommandHandler("importsticker", importsticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("addsticker", addsticker_command))
    # disabled lightweight build: app.add_handler(CommandHandler("stickerlist", stickerlist_command))
    # disabled lightweight build: app.add_handler(CommandHandler("cpuinfo", cpuinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("meminfo", meminfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("diskinfo", diskinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("dbinfo", dbinfo_command))
    # disabled lightweight build: app.add_handler(CommandHandler("listcmds", listcmds_command))
    # disabled lightweight build: app.add_handler(CommandHandler("allcmds", allcmds_command))
    # disabled lightweight build: app.add_handler(CommandHandler("cmds", cmds_command))
    # disabled lightweight build: app.add_handler(CommandHandler("menu", menu_command))
    # disabled lightweight build: app.add_handler(CommandHandler("commands", commands_command))


# ====== EXTRA 25 COMMANDS TO REACH 300 ======

async def softban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban then immediately unban (kick without blacklist)"""
    await kick_command(update, context)

async def tempban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Temporary ban (kick)"""
    if not await is_group_admin_func(update, context):
        await update.message.reply_text("❌ Group Admin သာ သုံးနိုင်သည်။"); return
    await kick_command(update, context)

async def unban_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all bans (placeholder)"""
    if not is_owner(update.effective_user): return
    await update.message.reply_text("```\n✅ Unban All - Done\n```", parse_mode="Markdown")

async def countmembers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count group members"""
    await members_command(update, context)

async def getlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get invite link"""
    await invitelink_command(update, context)

async def silence_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for muteall"""
    await muteall_command(update, context)

async def unsilence_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for unmuteall"""
    await unmuteall_command(update, context)

async def protect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    PROTECTED_CHATS.add(update.effective_chat.id)
    await update.message.reply_text("```\n🛡️ PROTECT MODE ON\n```", parse_mode="Markdown")

async def unprotect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    PROTECTED_CHATS.discard(update.effective_chat.id)
    await update.message.reply_text("```\n✅ PROTECT MODE OFF\n```", parse_mode="Markdown")

async def sendsticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send sticker by name"""
    await getsticker_command(update, context)

async def mystickers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List stickers"""
    await liststickers_command(update, context)

async def packinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get sticker pack info"""
    await stickerinfo_command(update, context)

async def stickerset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Sticker ကို Reply ပေးပါ"); return
    s = update.message.reply_to_message.sticker
    pack = s.set_name
    if pack:
        await update.message.reply_text(f"📦 Sticker Set: `{pack}`\n🔗 https://t.me/addstickers/{pack}", parse_mode="Markdown")
    else:
        await update.message.reply_text("ℹ️ No sticker set info")

async def importsticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Import sticker by file_id"""
    await savesticker_command(update, context)

async def addsticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add sticker alias"""
    await savesticker_command(update, context)

async def stickerlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List stickers alias"""
    await liststickers_command(update, context)

async def cpuinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        freq = psutil.cpu_freq()
        cores = psutil.cpu_count()
        info = f"```\n🖥️ CPU INFO\n━━━━━━━━━━━━━━\nUsage : {cpu}%\nCores : {cores}\nFreq  : {freq.current:.0f} MHz\n```"
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def meminfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    try:
        mem = psutil.virtual_memory()
        info = f"```\n💾 MEMORY INFO\n━━━━━━━━━━━━━━\nTotal : {mem.total//1024//1024} MB\nUsed  : {mem.used//1024//1024} MB\nFree  : {mem.available//1024//1024} MB\nUsage : {mem.percent}%\n```"
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def diskinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    try:
        disk = psutil.disk_usage('/')
        info = f"```\n💿 DISK INFO\n━━━━━━━━━━━━━━\nTotal : {disk.total//1024//1024//1024} GB\nUsed  : {disk.used//1024//1024//1024} GB\nFree  : {disk.free//1024//1024//1024} GB\nUsage : {disk.percent}%\n```"
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def dbinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user): return
    files = os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else []
    total_size = sum(os.path.getsize(os.path.join(DATA_DIR, f)) for f in files if os.path.isfile(os.path.join(DATA_DIR, f)))
    info = f"```\n🗄️ DATABASE INFO\n━━━━━━━━━━━━━━\nFiles : {len(files)}\nSize  : {total_size//1024} KB\nGroups: {len(seen_chats)}\nUsers : {len(private_users)}\n```"
    await update.message.reply_text(info, parse_mode="Markdown")

async def listcmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick command overview"""
    await help_command(update, context)

async def allcmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all 3 pages"""
    await help_command(update, context)
    await asyncio.sleep(1)
    await show_command(update, context)
    await asyncio.sleep(1)
    await ngazen_command(update, context)

async def cmds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for help"""
    await help_command(update, context)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show menu - alias for help"""
    await help_command(update, context)

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all commands"""
    await help_command(update, context)


async def post_init_tasks(application: Application):
    # Start limited admin checker
    asyncio.create_task(check_limited_admins_periodically())
    asyncio.create_task(simple_migration_checker())
    asyncio.create_task(resume_all_pending_commands(application))
    asyncio.create_task(tt_auto_clean())

    logging.info("ULTRA FAST BOT INITIALIZED!")
    logging.info(f"Loaded {len(seen_chats)} groups and {len(private_users)} private users")
    logging.info("Performance optimizer running with maximum concurrency")

def main():
    _singleton()

    app = (
        Application.builder()
        .token(TOKEN)
        .connection_pool_size(20)      # လူများရင် Pool size ကို ၂၀ လောက် တိုးထားပါ
        .connect_timeout(20.0)
        .read_timeout(20.0)
        .write_timeout(20.0)
        .pool_timeout(10.0)
        .post_init(post_init_tasks)
        .build()
    )

    register_handlers(app)
    logging.warning("Bot started pid=%d", os.getpid())

    try:
        app.run_polling(
            allowed_updates      = Update.ALL_TYPES,
            poll_interval        = 0.5,         # 0.2 ထက် 0.5 က Network အတွက် ပိုငြိမ်ပါတယ်
            timeout              = 30,
            drop_pending_updates = True,        # အရေးကြီး - ဒါကို False ထားမှ လူဝင်တာ အကုန်သိမှာပါ
        )
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Bot stopped")
    except Exception as e:
        logging.error("Bot crashed: %s", e)

if __name__ == "__main__":
    main()
    