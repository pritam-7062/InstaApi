import requests, uuid, random, string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive

keep_alive()
API_TOKEN = "8015804901:AAH9pBwCCISOJZJK2phGkUrUyPM4pI92wag"

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
    {"http": "http://gglemtja-rotate:a0m16t677tmf@p.webshare.io:80/", "https": "http://wrfsjyrn-rotate:aurq4k93285j@p.webshare.io:80/"},
    {"https": "http://bdpusfsa-rotate:mjs2uwp6m3u3@p.webshare.io:80/"},
    {"http": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
    {"https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
    {"http": "http://fepgpvaz-rotate:jyv905f8hjv3@p.webshare.io:80"},
    {"https": "http://fepgpvaz-rotate:jyv905f8hjv3@p.webshare.io:80"},
    {"http": "http://tyxgkhty-rotate:1bxkvycbytnq@p.webshare.io:80"},
    {"https": "http://tyxgkhty-rotate:1bxkvycbytnq@p.webshare.io:80"}
]

# Creation Year Estimator
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

# Instagram User Info Fetcher
def get_instagram_info(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for _ in range(3):  # Try 3 proxy attempts
        proxy = random.choice(proxies_list)
        try:
            response = requests.get(url, headers=generate_headers(), timeout=20)
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
                return info, None
        except Exception:
            continue
    return None, response.text

# Fetch Instagram Reset Email (Masked)
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
                    # Sometimes it may say no such user/email
                    return False, json_resp.get("message", "No obfuscated email found.")
        except Exception:
            continue
    return False, response.text

# Telegram Command Handlers
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /insta <username>")
        return
    username = context.args[0]
    await update.message.chat.send_action("typing")
    info, error = get_instagram_info(username)
    await update.message.reply_text(info if info else error, parse_mode="Markdown")

async def resetmail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /resetmail <username_or_email>")
        return
    username_or_email = context.args[0]
    await update.message.chat.send_action("typing")
    success, result = fetch_reset_email(username_or_email)
    if success:
        await update.message.reply_text(f"🔐 Masked reset email: `{result}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Failed: {result}")

# Main Function
def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("insta", insta_command))
    app.add_handler(CommandHandler("resetm", resetmail_command))
    app.run_polling()

if __name__ == "__main__":
    main()
