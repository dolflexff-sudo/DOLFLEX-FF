import os
import logging
import edge_tts
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8882267375:AAGNe-ozTFLVGBMivPdHuTZQS-DyQGnsb84")
AUDIO_DIR = "tts_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)

VOICES = {
    "m_davis":       {"voice": "en-US-DavisNeural",       "desc": "🎙 Davis",       "tag": "Deep & Smooth"},
    "m_tony":        {"voice": "en-US-TonyNeural",        "desc": "🎙 Tony",        "tag": "Confident"},
    "m_jason":       {"voice": "en-US-JasonNeural",       "desc": "🎙 Jason",       "tag": "Strong"},
    "m_christopher": {"voice": "en-US-ChristopherNeural", "desc": "🎙 Christopher", "tag": "Authoritative"},
    "m_eric":        {"voice": "en-US-EricNeural",        "desc": "🎙 Eric",        "tag": "Smooth"},
    "m_roger":       {"voice": "en-US-RogerNeural",       "desc": "🎙 Roger",       "tag": "Calm"},
    "m_steffan":     {"voice": "en-US-SteffanNeural",     "desc": "🎙 Steffan",     "tag": "Clear"},
    "m_guy":         {"voice": "en-US-GuyNeural",         "desc": "🎙 Guy",         "tag": "Rich"},
    "m_brandon":     {"voice": "en-US-BrandonNeural",     "desc": "🎙 Brandon",     "tag": "Warm"},
    "m_adam":        {"voice": "en-GB-RyanNeural",        "desc": "🎙 Ryan",        "tag": "British"},
    "m_madhur":      {"voice": "hi-IN-MadhurNeural",      "desc": "🎙 Madhur",      "tag": "Hindi Male"},
    "m_prabhat":     {"voice": "en-IN-PrabhatNeural",     "desc": "🎙 Prabhat",     "tag": "Indian Male"},
    "f_aria":        {"voice": "en-US-AriaNeural",        "desc": "🎀 Aria",        "tag": "Warm"},
    "f_jenny":       {"voice": "en-US-JennyNeural",       "desc": "🎀 Jenny",       "tag": "Friendly"},
    "f_sara":        {"voice": "en-US-SaraNeural",        "desc": "🎀 Sara",        "tag": "Soft"},
    "f_swara":       {"voice": "hi-IN-SwaraNeural",       "desc": "🎀 Swara",       "tag": "Hindi Female"},
    "f_neerja":      {"voice": "en-IN-NeerjaNeural",      "desc": "🎀 Neerja",      "tag": "Indian Female"},
}

STYLES = {
    "default":      {"desc": "⚡ Normal",         "rate": "-3%"},
    "teacher":      {"desc": "👩‍🏫 Teacher",        "rate": "-12%"},
    "influencer":   {"desc": "🌟 Influencer",      "rate": "+5%"},
    "gamer":        {"desc": "🎮 Gamer",           "rate": "+18%"},
    "intro":        {"desc": "🎬 Intro / Promo",   "rate": "-8%"},
    "news":         {"desc": "📰 News Anchor",      "rate": "-10%"},
    "story":        {"desc": "📖 Storyteller",     "rate": "-15%"},
    "motivational": {"desc": "💪 Motivational",    "rate": "+10%"},
    "podcast":      {"desc": "🎙️ Podcast Host",    "rate": "-5%"},
    "kids":         {"desc": "🧒 Kids / Cartoon",  "rate": "+12%"},
    "horror":       {"desc": "👻 Horror",          "rate": "-22%"},
    "assistant":    {"desc": "🤖 AI Assistant",    "rate": "-3%"},
    "angry":        {"desc": "😠 Angry",           "rate": "+22%"},
    "sad":          {"desc": "😢 Sad",             "rate": "-18%"},
    "romantic":     {"desc": "❤️ Romantic",        "rate": "-12%"},
    "meditation":   {"desc": "🧘 Meditation",      "rate": "-25%"},
    "sports":       {"desc": "⚽ Sports Caster",   "rate": "+20%"},
    "documentary":  {"desc": "🎥 Documentary",     "rate": "-8%"},
    "whispering":   {"desc": "🤫 Whispering",      "rate": "-10%"},
    "announcement": {"desc": "📢 Announcement",    "rate": "-5%"},
}

PITCH_MAP = {
    "p1": ("-20Hz", "⬇️⬇️⬇️ Bahut Deep"),
    "p2": ("-12Hz", "⬇️⬇️ Deep"),
    "p3": ("-6Hz",  "⬇️ Thoda Deep"),
    "p4": ("+0Hz",  "➡️ Normal"),
    "p5": ("+6Hz",  "⬆️ Thoda High"),
    "p6": ("+12Hz", "⬆️⬆️ High"),
    "p7": ("+20Hz", "⬆️⬆️⬆️ Bahut High"),
}

DEFAULT_VOICE = "m_davis"
DEFAULT_STYLE = "default"
DEFAULT_PITCH = "p4"


async def synthesize(text, vk, sk, pk, filepath):
    voice = VOICES[vk]["voice"]
    style = STYLES[sk]
    pitch_hz = PITCH_MAP[pk][0]
    communicate = edge_tts.Communicate(
        text, voice,
        rate=style["rate"],
        pitch=pitch_hz,
    )
    await communicate.save(filepath)


def get_settings(ud):
    vk = ud.get("voice", DEFAULT_VOICE)
    sk = ud.get("style", DEFAULT_STYLE)
    pk = ud.get("pitch", DEFAULT_PITCH)
    return vk, sk, pk


def settings_text(vk, sk, pk):
    return (
        f"🎙 *{VOICES[vk]['desc']}* — _{VOICES[vk]['tag']}_\n"
        f"🎭 *{STYLES[sk]['desc']}*\n"
        f"🎚 *{PITCH_MAP[pk][1]}*"
    )


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎙 Voice",  callback_data="menu_voice"),
         InlineKeyboardButton("🎭 Style",  callback_data="menu_style")],
        [InlineKeyboardButton("🎚 Pitch",  callback_data="menu_pitch"),
         InlineKeyboardButton("⚙️ Settings", callback_data="menu_info")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vk, sk, pk = get_settings(context.user_data)
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎙️  *PRO TTS BOT*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Microsoft Neural Voices\n"
        "17 Voices • 19 Styles • 7 Pitch Levels\n\n"
        f"*Current:*\n{settings_text(vk, sk, pk)}\n\n"
        "📝 Koi bhi text bhejo → voice aayegi\n"
        "📥 Voice file bhi download kar sakte ho!",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
    )


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vk, sk, pk = get_settings(context.user_data)
    await update.message.reply_text(
        "⚙️ *Settings Panel*\n\n"
        f"{settings_text(vk, sk, pk)}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
    )


async def menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data.split("_", 1)[1]

    if action == "voice":
        keyboard = []
        row = []
        for k, v in VOICES.items():
            row.append(InlineKeyboardButton(
                f"{v['desc']} · {v['tag']}", callback_data=f"vc_{k}"
            ))
            if len(row) == 1:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="menu_back")])
        await q.edit_message_text(
            "🎙 *Voice Choose Karo:*\n\n"
            "🎙 = Male   🎀 = Female",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif action == "style":
        keyboard = []
        row = []
        for k, v in STYLES.items():
            row.append(InlineKeyboardButton(v["desc"], callback_data=f"st_{k}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="menu_back")])
        await q.edit_message_text(
            "🎭 *Style Choose Karo:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif action == "pitch":
        keyboard = []
        for k, (hz, label) in PITCH_MAP.items():
            keyboard.append([InlineKeyboardButton(
                f"{label}  ({hz})", callback_data=f"pt_{k}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="menu_back")])
        await q.edit_message_text(
            "🎚 *Pitch Choose Karo:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif action == "info":
        vk, sk, pk = get_settings(context.user_data)
        await q.edit_message_text(
            "⚙️ *Current Settings:*\n\n"
            f"{settings_text(vk, sk, pk)}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu_back")]
            ]),
        )

    elif action == "back":
        vk, sk, pk = get_settings(context.user_data)
        await q.edit_message_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎙️  *PRO TTS BOT*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Current:*\n{settings_text(vk, sk, pk)}\n\n"
            "📝 Text bhejo → voice aayegi",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(),
        )


async def voice_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    vk = q.data[3:]
    context.user_data["voice"] = vk
    await q.edit_message_text(
        f"✅ Voice set!\n\n"
        f"🎙 *{VOICES[vk]['desc']}* — _{VOICES[vk]['tag']}_\n\n"
        "Ab text bhejo 👇",
        parse_mode="Markdown",
    )


async def style_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    sk = q.data[3:]
    context.user_data["style"] = sk
    await q.edit_message_text(
        f"✅ Style set!\n\n"
        f"🎭 *{STYLES[sk]['desc']}*\n\n"
        "Ab text bhejo 👇",
        parse_mode="Markdown",
    )


async def pitch_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pk = q.data[3:]
    context.user_data["pitch"] = pk
    hz, label = PITCH_MAP[pk]
    await q.edit_message_text(
        f"✅ Pitch set!\n\n"
        f"🎚 *{label}* ({hz})\n\n"
        "Ab text bhejo 👇",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return
    if len(text) > 600:
        await update.message.reply_text("⚠️ 600 characters se zyada nahi.")
        return

    uid = update.effective_user.id
    vk, sk, pk = get_settings(context.user_data)
    hz, plabel = PITCH_MAP[pk]

    status = await update.message.reply_text(
        f"🔄 *Generating...*\n\n"
        f"🎙 {VOICES[vk]['desc']}  •  🎭 {STYLES[sk]['desc']}  •  🎚 {plabel}",
        parse_mode="Markdown",
    )

    filepath = os.path.join(AUDIO_DIR, f"{uid}.mp3")
    dl_path  = os.path.join(AUDIO_DIR, f"{uid}_dl.mp3")

    try:
        await synthesize(text, vk, sk, pk, filepath)

        with open(filepath, "rb") as f:
            await update.message.reply_voice(
                voice=f,
                caption=(
                    f"🎙 {VOICES[vk]['desc']} · {VOICES[vk]['tag']}\n"
                    f"🎭 {STYLES[sk]['desc']}  🎚 {plabel}"
                ),
            )

        import shutil
        shutil.copy(filepath, dl_path)
        with open(dl_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"tts_{VOICES[vk]['desc'].replace(' ','_')}_{sk}.mp3",
                caption="📥 *Download MP3*",
                parse_mode="Markdown",
            )

        os.remove(filepath)
        os.remove(dl_path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("settings", settings_cmd))
    app.add_handler(CallbackQueryHandler(menu_cb,    pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(voice_cb,   pattern="^vc_"))
    app.add_handler(CallbackQueryHandler(style_cb,   pattern="^st_"))
    app.add_handler(CallbackQueryHandler(pitch_cb,   pattern="^pt_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ PRO TTS Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
