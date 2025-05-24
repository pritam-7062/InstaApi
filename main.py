import requests, uuid, random, string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keep_alive import keep_alive
keep_alive()

API_TOKEN = "7591583598:AAED8BdysvzMby5cPr3DU1UOMRLGb0jI5do"  # Replace with your actual token


def generate_instagram_headers():
    csrf_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    session_id = str(uuid.uuid4())
    mid = str(uuid.uuid4())
    ig_did = str(uuid.uuid4())
    datr = ''.join(random.choices(string.ascii_letters + string.digits, k=22))

    return {
        'authority': 'www.instagram.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'x-ig-app-id': '936619743392459',
        'x-requested-with': 'XMLHttpRequest',
        'cookie': f'csrftoken={csrf_token}; sessionid={session_id}; mid={mid}; ig_did={ig_did}; datr={datr};',
    }


def date(hy: int):
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


def get_instagram_info(username):
    try:
        headers = generate_instagram_headers()
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None, "Failed to fetch user info (possibly private or unavailable)."

        user = response.json()["data"]["user"]
        userid = int(user["id"])
        creation_year = date(userid)
        reset_email = get_reset_usr(username)

        followers = user['edge_followed_by']['count']
        posts = user['edge_owner_to_timeline_media']['count']
        meta = followers >= 10 and posts >= 2

        info = f"""**🔍 Instagram User Info By @Wamphire:**
👤 **Name**: {user['full_name'] or 'N/A'}
🔗 **Username**: [@{user['username']}](https://instagram.com/{user['username']})
🆔 **User ID**: `{user['id']}`
📅 **Account Created**: `{creation_year}`
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
        return None, f"Error: {str(e)}"


async def insta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /insta <username>")
        return

    username = context.args[0]
    await update.message.chat.send_action("typing")

    info, error = get_instagram_info(username)

    if error:
        await update.message.reply_text(f"❌ {error}")
    else:
        await update.message.reply_text(info, parse_mode="Markdown")


def main():
    app = Application.builder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("insta", insta_command))
    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
