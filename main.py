from flask import Flask, request, jsonify
import requests
from keep_alive import keep_alive
keep_alive()

app = Flask(__name__)

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

        followers = user['edge_followed_by']['count']
        posts = user['edge_owner_to_timeline_media']['count']
        meta = followers >= 10 and posts >= 2

        info = {
            "full_name": user['full_name'] or 'N/A',
            "username": user['username'],
            "id": user['id'],
            "creation_year": creation_year,
            "bio": user['biography'] or 'N/A',
            "url": user['external_url'] or 'N/A',
            "followers": followers,
            "following": user['edge_follow']['count'],
            "posts": posts,
            "is_private": user['is_private'],
            "is_verified": user['is_verified'],
            "is_business": user.get('is_business_account', False),
            "meta_enabled": meta,
            "reset_email": reset_email,
            "profile_pic_url": user['profile_pic_url_hd']
        }

        return info, None
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/instainfo', methods=['GET'])
def insta_info():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing 'username' parameter"}), 400

    info, error = get_instagram_info(username)
    if error:
        return jsonify({"error": error}), 500

    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
