import requests, uuid, random, string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_all import keep_alive
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
    {"http": "http://bhcdwbbk-rotate:93ht6poh1443@p.webshare.io:80/", "https": "http://hxifftfr-rotate:h3ayfibgazbo@p.webshare.io:80/"},
    {"http": "http://mdcpzjeo-rotate:r2eozqbb21b8@p.webshare.io:80/", "https": "http://bdpusfsa-rotate:mjs2uwp6m3u3@p.webshare.io:80/"},
    {"http": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
    {"https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"},
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

# Reset Email Fetcher
def get_reset_usr(username):
    try:
        url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
        headers = {
            "User-Agent": "Instagram 295.0.0.19.119",
            "x-ig-app-id": "936619743392459",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = {"query": username}
        response = requests.post(url, headers=headers, data=data, timeout=10)
        return response.json().get("email", "Not Available") if response.status_code == 200 else "Hidden or Not Available"
    except:
        return "Error fetching email"

# Instagram User Info Fetcher
def get_instagram_info(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for _ in range(3):  # Try 3 proxy attempts
        proxy = random.choice(proxies_list)
        try:
            response = requests.get(url, headers=generate_headers(), timeout=30)
            if response.status_code == 200:
                user = response.json()["data"]["user"]
                userid = int(user["id"])
                creation_year = estimate_year(userid)
                reset_email = get_reset_usr(username)

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
📩 **Reset Email**: `{reset_email}`
📸 **Profile Pic**: [Click Here]({user['profile_pic_url_hd']})
"""
                return info, None
        except Exception as e:
            continue
    return None, "❌ Failed to fetch user info (check username or proxy access)"

# Telegram Command Handler
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /insta <username>")
        return
    username = context.args[0]
    await update.message.chat.send_action("typing")
    info, error = get_instagram_info(username)
    await update.message.reply_text(info if info else error, parse_mode="Markdown")

# Main Function
def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("insta", insta_command))
    app.run_polling()

if __name__ == "__main__":
    main()
