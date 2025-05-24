import requests, uuid, random, string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

# Proxy List
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

# Instagram Info Fetcher
def get_instagram_info(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for _ in range(3):
        proxy = random.choice(proxies_list)
        try:
            response = requests.get(url, headers=generate_headers(), proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json(), None
        except Exception:
            continue
    return None, "❌ Failed to fetch user info"

# Reset Email Fetcher
def fetch_reset_email(target):
    data = {
        "_csrftoken": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        "guid": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4()),
    }
    if "@" in target:
        data["user_email"] = target
    else:
        data["username"] = target

    for proxy in proxies_list:
        headers = generate_headers()
        try:
            response = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                headers=headers,
                data=data,
                proxies=proxy,
                timeout=30
            )
            if response.status_code == 200 and "obfuscated_email" in response.text:
                return True, response.json().get("obfuscated_email", None)
        except requests.RequestException:
            continue
    return False, None

# Insta Command Handler
async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: `/insta <username>`", parse_mode="Markdown")
        return

    username = context.args[0].lstrip("@")
    await update.message.reply_text("⏳ Fetching Instagram info...")

    info, error = get_instagram_info(username)
    reset_success, reset_email = fetch_reset_email(username)

    if not info:
        await update.message.reply_text(error)
        return

    user_data = info.get("data", {}).get("user", {})
    if not user_data:
        await update.message.reply_text("❌ Invalid username or user not found.")
        return

    full_name = user_data.get("full_name", "N/A")
    is_private = user_data.get("is_private", False)
    followers = user_data.get("edge_followed_by", {}).get("count", 0)
    following = user_data.get("edge_follow", {}).get("count", 0)
    posts = user_data.get("edge_owner_to_timeline_media", {}).get("count", 0)
    verified = user_data.get("is_verified", False)
    bio = user_data.get("biography", "N/A") or "N/A"
    user_id = int(user_data.get("id", 0))
    created_year = estimate_year(user_id)

    info_text = (
        f"🔍 *Username:* `{username}`\n"
        f"👤 *Full Name:* `{full_name}`\n"
        f"📅 *Estimated Year Created:* `{created_year}`\n"
        f"✅ *Verified:* `{verified}`\n"
        f"🔒 *Private:* `{is_private}`\n"
        f"📸 *Posts:* `{posts}`\n"
        f"👥 *Followers:* `{followers}`\n"
        f"➡️ *Following:* `{following}`\n"
        f"📝 *Bio:* `{bio}`\n"
    )

    if reset_success:
        info_text += f"🔐 *Reset Email:* `{reset_email}`"

    await update.message.reply_text(info_text, parse_mode="Markdown")

# Main Setup
def run_bot():
    TOKEN = "7591583598:AAED8BdysvzMby5cPr3DU1UOMRLGb0jI5do"
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("insta", insta_command))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
