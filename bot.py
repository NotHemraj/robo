import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = os.getenv('BOT_NAME', 'ᴘʀᴏ ʀᴏʙᴏᴛ')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate config
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found! Please set it in .env file")
    exit(1)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin"""
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get target user from reply or mention"""
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    elif context.args and context.args[0].startswith('@'):
        try:
            username = context.args[0][1:]
            member = await context.bot.get_chat_member(update.effective_chat.id, f"@{username}")
            return member.user
        except:
            return None
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        f"🤖 **{BOT_NAME}** - Group Manager\n\n"
        "Commands:\n"
        "/mute - Mute user\n"
        "/unmute - Unmute user\n"
        "/ban - Ban user\n"
        "/unban - Unban user\n"
        "/kick - Kick user\n"
        "/pin - Pin message\n"
        "/unpin - Unpin message\n\n"
        "Reply to message or mention user to use commands.",
        parse_mode='Markdown'
    )

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Reply to message or mention user")
        return
    
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, user.id, permissions={"can_send_messages": False}
        )
        await update.message.reply_text(f"🔇 Muted {user.full_name}")
        logger.info(f"Muted user: {user.full_name} ({user.id})")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to mute user: {e}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Reply to message or mention user")
        return
    
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, user.id, 
            permissions={
                "can_send_messages": True, "can_send_media_messages": True,
                "can_send_polls": True, "can_send_other_messages": True,
                "can_add_web_page_previews": True
            }
        )
        await update.message.reply_text(f"🔊 Unmuted {user.full_name}")
        logger.info(f"Unmuted user: {user.full_name} ({user.id})")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to unmute user: {e}")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Reply to message or mention user")
        return
    
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"🚫 Banned {user.full_name}")
        logger.info(f"Banned user: {user.full_name} ({user.id})")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to ban user: {e}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Provide user ID or username")
        return
    
    try:
        user_id = context.args[0].replace('@', '')
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ User unbanned")
        logger.info(f"Unbanned user ID: {user_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to unban user: {e}")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kick user"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    user = await get_target_user(update, context)
    if not user:
        await update.message.reply_text("❌ Reply to message or mention user")
        return
    
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await context.bot.unban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"👢 Kicked {user.full_name}")
        logger.info(f"Kicked user: {user.full_name} ({user.id})")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to kick user: {e}")

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin message"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to message to pin")
        return
    
    try:
        await context.bot.pin_chat_message(
            update.effective_chat.id, 
            update.message.reply_to_message.message_id,
            disable_notification=True
        )
        await update.message.reply_text("📌 Message pinned")
        logger.info(f"Pinned message ID: {update.message.reply_to_message.message_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to pin message: {e}")

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unpin message"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Admin only")
        return
    
    try:
        if update.message.reply_to_message:
            await context.bot.unpin_chat_message(
                update.effective_chat.id, 
                update.message.reply_to_message.message_id
            )
        else:
            await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("📌 Message unpinned")
        logger.info("Unpinned message")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")
        logger.error(f"Failed to unpin message: {e}")

def main():
    """Main function"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    
    logger.info(f"🤖 {BOT_NAME} started successfully")
    print(f"🤖 {BOT_NAME} is running...")
    
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == '__main__':
    main()
