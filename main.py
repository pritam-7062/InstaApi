from flask import Flask, request, jsonify
import requests
import codecs
from keep_alive import keep_alive
keep_alive()

app = Flask(__name__)

# Helper function to determine account creation year based on user ID
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

# Helper function to fetch reset email for an Instagram account
def get_reset_usr(username):
    try:
        url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
        headers = {
            "User-Agent": "Instagram 295.0.0.19.119",
            "x-ig-app-id": "936619743392459",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = {"query": username}
        response = requests.post(url, headers=headers, data=data)
        return response.json().get("email", "Not Available") if response.status_code == 200 else "Hidden or Not Available"
    except:
        return "Error fetching email"

# Function to fetch Instagram user info
def get_instagram_info(username):
    try:
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'x-csrftoken': 'REPLACE_WITH_CSRF_TOKEN',
            'x-ig-app-id': '936619743392459',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': 'csrftoken=REPLACE; sessionid=REPLACE; mid=REPLACE; ig_did=REPLACE; datr=REPLACE',
        }

        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None, "Failed to fetch user info (possibly private or unavailable)."

        user = response.json()["data"]["user"]
        userid = int(user["id"])
        creation_year = date(userid)
        reset_email = get_reset_usr(username)

        # Decode bio to human-readable format
        bio = user['biography']
        if bio:
            bio = codecs.decode(bio, 'unicode_escape')  # Decoding the bio

        followers = user['edge_followed_by']['count']
        posts = user['edge_owner_to_timeline_media']['count']
        meta = followers >= 10 and posts >= 2

        info = {
            "Name": user['full_name'] or 'N/A',
            "Username": f"@{user['username']}",
            "User ID": user['id'],
            "Account Created": creation_year,
            "Bio": bio or 'N/A',
            "URL": user['external_url'] or 'N/A',
            "Followers": followers,
            "Following": user['edge_follow']['count'],
            "Posts": posts,
            "Private": 'Yes' if user['is_private'] else 'No',
            "Verified": 'Yes' if user['is_verified'] else 'No',
            "Business": 'Yes' if user.get('is_business_account') else 'No',
            "Meta Enabled": 'Yes' if meta else 'No',
            "Reset Email": reset_email,
            "Profile Pic": user['profile_pic_url_hd']
        }

        return info, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Flask route to get Instagram user info
@app.route('/instagram_info', methods=['GET'])
def instagram_info():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    info, error = get_instagram_info(username)
    if error:
        return jsonify({"error": error}), 500

    return jsonify(info), 200

if __name__ == '__main__':
    app.run(debug=True)
