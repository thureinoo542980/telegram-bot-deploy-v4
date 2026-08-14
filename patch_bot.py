import os
import re

main_path = "/home/ubuntu/bot-deploy-v4/main.py"

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add import for apex_features
if "import apex_features" not in content:
    content = "import apex_features\n" + content

# 2. Fix add_admin_command to be more robust
# We'll replace the existing add_admin_command with a version that supports reply_to_message
new_add_admin = """
async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_lock_and_notify(update, context, "admin"):
        return
    if not is_owner(update.effective_user):
        await handle_owner_only(update, context, "")
        return

    target_id = None
    target_uname = None

    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_id = update.message.reply_to_message.from_user.id
        target_uname = update.message.reply_to_message.from_user.username
    elif context.args:
        arg = context.args[0].strip()
        if arg.startswith("@"):
            target_uname = arg.lstrip("@")
        else:
            try:
                target_id = int(arg)
            except:
                await update.message.reply_text("❌ Invalid ID.")
                return
    else:
        await update.message.reply_text("❓ Usage: Reply to a user or use `/add_admin id/@username`")
        return

    admins_data.setdefault("ids", [])
    admins_data.setdefault("usernames", [])

    if target_id:
        if target_id not in admins_data["ids"]:
            admins_data["ids"].append(target_id)
    if target_uname:
        if target_uname not in admins_data["usernames"]:
            admins_data["usernames"].append(target_uname)

    asyncio.create_task(fast_data.buffered_save(ADMINS_FILE, admins_data))
    global ADMIN_IDS, ADMIN_USERNAMES
    ADMIN_IDS = set(int(x) for x in admins_data.get("ids", []) if str(x).isdigit())
    ADMIN_USERNAMES = set(u.lstrip("@").lower() for u in admins_data.get("usernames", []))
    await update.message.reply_text("✅ Admin added successfully.")
"""

# Replace the old function. We'll find it by its start and end.
content = re.sub(r'async def add_admin_command\(update: Update, context: ContextTypes.DEFAULT_TYPE\):.*?await update\.message\.reply_text\("✅ Admin added\."\)', new_add_admin, content, flags=re.DOTALL)

# 3. Add Owner Panel Handler
panel_handler = """
async def owner_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user):
        return
    await update.message.reply_text(
        "⚡ **DRAKE EXTREME OWNER PANEL** ⚡\\n"
        "Select an advanced operation below:",
        reply_markup=apex_features.get_owner_panel_markup(),
        parse_mode="Markdown"
    )

async def panel_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "nuke_panel":
        await query.edit_message_text("🔥 **ULTRA NUKE MODE**\\nUsage: `/ultranuke <url>`\\nStatus: READY", parse_mode="Markdown")
    elif data == "sys_stats":
        await query.edit_message_text("⚙️ **SYSTEM STATS**\\nUptime: 24/7\\nMode: EXTREME\\nProxies: Active", parse_mode="Markdown")
    elif data == "close_panel":
        await query.message.delete()
"""

if "async def owner_panel_command" not in content:
    # Insert before register_handlers
    content = content.replace("def register_handlers(app: Application):", panel_handler + "\n\ndef register_handlers(app: Application):")

# 4. Register new handlers
new_registrations = """
    app.add_handler(CommandHandler("panel", owner_panel_command))
    app.add_handler(CallbackQueryHandler(panel_callback_handler, pattern="^(nuke_panel|ghost_panel|osint_panel|sentinel_panel|sys_stats|close_panel)$"))
    app.add_handler(CommandHandler("ultranuke", lambda u, c: asyncio.create_task(apex_features.execute_ultra_nuke(c.args[0] if c.args else ""))))
"""

if 'app.add_handler(CommandHandler("panel", owner_panel_command))' not in content:
    content = content.replace('app.add_handler(CommandHandler("start", start_command))', 'app.add_handler(CommandHandler("start", start_command))\n' + new_registrations)

# 5. Inject Sentinel into message handler
if "await apex_features.sentinel.check_and_counter(update, context)" not in content:
    # Find the main message handler
    content = content.replace("async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):", 
                              "async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):\n    await apex_features.sentinel.check_and_counter(update, context)")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patch applied successfully.")
