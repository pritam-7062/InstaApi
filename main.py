import instaloader
import requests
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from keep_alive import keep_alive
keep_alive()

# FastAPI app initialization
app = FastAPI()
x = instaloader.Instaloader()

# Set the proxy for Instaloader
PROXY = {
    "http": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80",
    "https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"
}

# Set proxy for requests (if you plan to use requests directly with proxy)
requests_session = requests.Session()
requests_session.proxies.update(PROXY)

# Set the proxy for Instaloader (using requests session)
x.context._session.proxies.update(PROXY)

# Calculate account creation year from user ID
def date(hy):
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

# Fetch reset email
def get_reset_usr(username):
    try:
        url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
        headers = {
            "User-Agent": "Instagram 295.0.0.19.119",
            "x-ig-app-id": "936619743392459",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = {"query": username}
        response = requests_session.post(url, headers=headers, data=data)  # Use the proxy session here
        return response.json().get("email", "Not Available") if response.status_code == 200 else "Hidden or Not Available"
    except:
        return "Error fetching email"

# Define API model
class InstaInfo(BaseModel):
    name: Optional[str]
    username: str
    userid: str
    creation_year: Optional[int]
    biography: Optional[str]
    business_category: Optional[str]
    external_url: Optional[str]
    followers: int
    following: int
    posts: int
    is_private: bool
    is_verified: bool
    is_business: bool
    meta_enabled: bool
    reset_email: str
    profile_pic: str

@app.get("/insta", response_model=InstaInfo)
def insta_lookup(username: str = Query(..., description="Instagram username to lookup")):
    try:
        f = instaloader.Profile.from_username(x.context, username)
        reset_email = get_reset_usr(username)
        creation_year = date(int(f.userid))
        meta = f.followers >= 10 and f.mediacount >= 2

        return {
            "name": f.full_name or None,
            "username": f.username,
            "userid": f.userid,
            "creation_year": creation_year,
            "biography": f.biography or None,
            "business_category": f.business_category_name or None,
            "external_url": f.external_url or None,
            "followers": f.followers,
            "following": f.followees,
            "posts": f.mediacount,
            "is_private": f.is_private,
            "is_verified": f.is_verified,
            "is_business": f.is_business_account,
            "meta_enabled": meta,
            "reset_email": reset_email,
            "profile_pic": f.profile_pic_url
        }

    except instaloader.exceptions.ProfileNotExistsException:
        return {"error": "User not found"}
    except instaloader.exceptions.ConnectionException:
        return {"error": "Connection error"}
    except instaloader.exceptions.BadResponseException:
        return {"error": "Instagram API error"}
    except Exception as e:
        return {"error": str(e)}
