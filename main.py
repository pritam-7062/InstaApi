import requests, uuid, random, string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive
keep_alive()

API_TOKEN = "8015804901:AAH9pBwCCISOJZJK2phGkUrUyPM4pI92wag"
OWNER_ID = 1284660863  # Replace with your actual Telegram user ID

# Random Device Info for User-Agent
def generate_headers():
    random_device_info = random.choice(["samsung", "xiaomi", "oneplus", "google", "huawei", "oppo", "vivo"])
    return {
        "user-agent": (
            f"Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; "
            f"{random_device_info}/{random_device_info}; {random_device_info}; {random_device_info}; en_GB;)"
        ),
        "x-ig-app-id": "936619743392459",
        "x-requested-with": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/"
    }

# Webshare Proxy List
proxies_list = [
    {"http": "http://bhcdwbbk-rotate:93ht6poh1443@p.webshare.io:80/", "https": "http://hxifftfr-rotate:h3ayfibgazbo@p.webshare.io:80/"},
    {"http": "http://mdcpzjeo-rotate:r2eozqbb21b8@p.webshare.io:80/", "https": "http://bdpusfsa-rotate:mjs2uwp6m3u3@p.webshare.io:80/"},
    {"http": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
    {"https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
]

# Estimate IG Account Creation Year from UID
def estimate_year(user_id: int):
    ranges = [
        (1278889, 2010), (17750000, 2011), (279760000, 2012), (900990000, 2013),
        (1629010000, 2014), (2369359761, 2015), (4239516754, 2016),
        (6345108209, 2017), (10016232395, 2018), (27238602159, 2019),
        (43464475395, 2020), (50289297647, 2021), (57464707082, 2022),
        (63313426938, 2023)
    ]
    for max_id, year in ranges:
        if user_id <= max_id:
            return year
    return 2024

# Instagram Info Fetcher
def get_instagram_info(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for _ in range(3):
        proxy = random.choice(proxies_list)
        try:
            response = requests.get(url, headers=generate_headers(), proxies=proxy, timeout=30)
            if response.status_code == 200:
                user = response.json()["data"]["user"]
                userid = int(user["id"])
                creation_year = estimate_year(userid)

                followers = user['edge_followed_by']['count']
                posts = user['edge_owner_to_timeline_media']['count']
                meta = followers >= 10 and posts >= 2

                info = f"""**🔍 Instagram User Info:**
👤 **Name**: {user['full_name'] or 'N/A'}
🔗 **Username**: [@{user['username']}](https://instagram.com/{user['username']})
🆔 **User ID**: `{user['id']}`
📅 **Created**: `{creation_year}`
📝 **Bio**: {user['biography'] or 'N/A'}
🌐 **URL**: {user['external_url'] or 'N/A'}
👥 **Followers**: {followers}
👤 **Following**: {user['edge_follow']['count']}
📮 **Posts**: {posts}
🔒 **Private**: {'Yes' if user['is_private'] else 'No'}
✅ **Verified**: {'Yes' if user['is_verified'] else 'No'}
🏢 **Business**: {'Yes' if user.get('is_business_account') else 'No'}
🔍 **Meta Enabled**: {'Yes' if meta else 'No'}
📸 **Profile Pic**: [Click Here]({user['profile_pic_url_hd']})
"""
                return info, user['username'], None
        except Exception:
            continue
    return None, None, "❌ Failed to fetch user info (check username or proxy access)"

# Reset Email Fetcher
def fetch_reset_email(username_or_email):
    for proxy in proxies_list:
        try:
            data = {
                "_csrftoken": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
                "guid": str(uuid.uuid4()),
                "device_id": str(uuid.uuid4()),
            }
            if "@" in username_or_email:
                data["user_email"] = username_or_email
            else:
                data["username"] = username_or_email

            response = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                headers=generate_headers(),
                data=data,
                proxies=proxy,
                timeout=10
            )
            if response.status_code == 200:
                json_resp = response.json()
                if "obfuscated_email" in json_resp:
                    return True, json_resp["obfuscated_email"]
                else:
                    return False, json_resp.get("message", "No obfuscated email found.")
        except Exception:
            continue
    return False, "Failed to fetch reset email info using proxies."

# /insta Command Handler
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.type not in ["group", "supergroup"]:
        #await update.message.reply_text("❌ This command can only be used in group chats.")
        #return

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /insta <username>")
        return

    username = context.args[0]
    fetching_msg = await update.message.reply_text("⏳ Fetching Instagram info...")

    info, clean_username, error = get_instagram_info(username)
    if clean_username:
        reset_success, reset_email = fetch_reset_email(clean_username)
        reset_text = f"\n🔐 **Reset Email (masked):** `{reset_email}`" if reset_success else f"\n🔐 **Reset Email:** {reset_email}"
    else:
        reset_text = ""

    await fetching_msg.delete()
    await update.message.reply_text(info + reset_text if info else error, parse_mode="Markdown")

# Main Entrypoint
def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("insta", insta_command))
    app.run_polling()

if __name__ == "__main__":
    main()
