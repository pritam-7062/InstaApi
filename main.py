import instaloader
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

x = instaloader.Instaloader()

# Set proxy here (only https proxy as you provided)
x.context._session.proxies = {
    "https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"
}

OWNER_ID = 1284660863  # Replace with your Telegram ID


def date(hy: int):
    try:
        ranges = [
            (1278889, 2010), (17750000, 2011), (279760000, 2012),
            (900990000, 2013), (1629010000, 2014), (2369359761, 2015),
            (4239516754, 2016), (6345108209, 2017), (10016232395, 2018),
            (27238602159, 2019), (43464475395, 2020), (50289297647, 2021),
            (57464707082, 2022), (63313426938, 2023)
        ]
        for upper, year in ranges:
            if hy <= upper:
                return year
        return 2024
    except:
        return "Unknown"


async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can use this command.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Provide a valid Instagram username.\nUsage: `/insta username`",
            parse_mode='Markdown'
        )
        return

    username = context.args[0]

    msg = await update.message.reply_text("Fetching Instagram info... Please wait.")

    try:
        profile = instaloader.Profile.from_username(x.context, username)
        creation_year = date(int(profile.userid))
        meta = profile.followers >= 10 and profile.mediacount >= 2

        text = f"""**🔍 Instagram User Info by @wamphire:**
👤 **Name** : {profile.full_name or 'N/A'}
🔗 **Username** : [@{profile.username}](https://www.instagram.com/{profile.username})
🆔 **User ID** : `{profile.userid}`
📅 **Account Created** : `{creation_year}`
📝 **Biography** : {profile.biography or 'N/A'}
🏢 **Business Category** : {profile.business_category_name or 'N/A'}
🌐 **External URL** : {profile.external_url or 'N/A'}
👥 **Followers** : {profile.followers}
👤 **Following** : {profile.followees}
📮 **Total Posts** : {profile.mediacount}
🔒 **Private Account** : {'Yes' if profile.is_private else 'No'}
✅ **Verified Account** : {'Yes' if profile.is_verified else 'No'}
🏢 **Business Account** : {'Yes' if profile.is_business_account else 'No'}
🔍 **Meta Enabled** : {'Yes' if meta else 'No'}
📸 **Profile Picture** : [Click Here]({profile.profile_pic_url})

**[𝐅𝐭~ || Pritam ||](tg://user?id={OWNER_ID})**
"""
        await msg.edit_text(text, parse_mode='Markdown', disable_web_page_preview=False)

    except instaloader.exceptions.ProfileNotExistsException:
        await msg.edit_text("❌ **User not found! Please check the username.**", parse_mode='Markdown')
    except instaloader.exceptions.ConnectionException:
        await msg.edit_text("❌ **Connection error! Try again later.**", parse_mode='Markdown')
    except instaloader.exceptions.BadResponseException:
        await msg.edit_text("❌ **Instagram API error! Try again later.**", parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f"❌ **Error:** `{str(e)}`", parse_mode='Markdown')


if __name__ == '__main__':
    bot_token = "7591583598:AAED8BdysvzMby5cPr3DU1UOMRLGb0jI5do"  # Replace with your bot token
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("insta", insta_command))

    application.run_polling()
