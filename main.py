from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import instaloader
import requests
from keep_alive import keep_alive

# Start keep-alive server (optional for uptime robot hosting)
keep_alive()

# Initialize FastAPI app
app = FastAPI()

# Configure proxy
PROXY = {
    "http": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80",
    "https": "http://xvcgftgw-rotate:9vm1bt8kvocy@p.webshare.io:80"
}

# Setup requests session with proxy
requests_session = requests.Session()
requests_session.proxies.update(PROXY)

# Initialize Instaloader and apply proxy
L = instaloader.Instaloader()
L.context._session.proxies.update(PROXY)

# Account creation year estimator from user ID
def get_creation_year(uid: int) -> int:
    ranges = [
        (1278889, 2010), (17750000, 2011), (279760000, 2012),
        (900990000, 2013), (1629010000, 2014), (2369359761, 2015),
        (4239516754, 2016), (6345108209, 2017), (10016232395, 2018),
        (27238602159, 2019), (43464475395, 2020), (50289297647, 2021),
        (57464707082, 2022), (63313426938, 2023)
    ]
    for upper, year in ranges:
        if uid <= upper:
            return year
    return 2024

# Fetch Instagram reset email (may be hidden or unavailable)
def get_reset_email(username: str) -> str:
    try:
        url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'eng',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'csrftoken=vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV; ig_did=5D80D38A-797B-482D-A407-4B51217E09E7; ig_nrcb=1; mid=ZEqtPgALAAE-IVt6zG-ZazKzI4qN; datr=jrJKZGOaV4gHwa-Znj2QCVyB',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/password/reset/?next=%2Faccounts%2Flogout%2F',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-csrftoken': 'vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV',
            'x-ig-app-id': '936619743392459',
            'x-instagram-ajax': '1007389883',
        }
        data = {"query": username}
        res = requests_session.post(url, headers=headers, data=data)
        return res.json().get("email", "Hidden or Not Available") if res.status_code == 200 else "Hidden or Not Available"
    except:
        return "Error fetching email"

# Define Pydantic model
class InstaInfo(BaseModel):
    name: Optional[str]
    username: str
    userid: Optional[int]
    creation_year: Optional[int]
    biography: Optional[str]
    business_category: Optional[str]
    external_url: Optional[str]
    followers: Optional[int]
    following: Optional[int]
    posts: Optional[int]
    is_private: Optional[bool]
    is_verified: Optional[bool]
    is_business: Optional[bool]
    meta_enabled: Optional[bool]
    reset_email: Optional[str]
    profile_pic: Optional[str]

@app.get("/insta", response_model=InstaInfo)
def get_instagram_info(username: str = Query(..., description="Instagram username to lookup")):
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        # Calculate account creation year
        creation_year = get_creation_year(int(profile.userid))

        # Determine "meta enabled" condition
        meta_enabled = profile.followers >= 10 and profile.mediacount >= 2

        return InstaInfo(
            name=profile.full_name or None,
            username=profile.username,
            userid=profile.userid,
            creation_year=creation_year,
            biography=profile.biography or None,
            business_category=profile.business_category_name or None,
            external_url=profile.external_url or None,
            followers=profile.followers,
            following=profile.followees,
            posts=profile.mediacount,
            is_private=profile.is_private,
            is_verified=profile.is_verified,
            is_business=profile.is_business_account,
            meta_enabled=meta_enabled,
            reset_email=get_reset_email(username),
            profile_pic=profile.profile_pic_url
        )

    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail="User not found")
    except instaloader.exceptions.ConnectionException:
        raise HTTPException(status_code=503, detail="Connection error to Instagram")
    except instaloader.exceptions.BadResponseException:
        raise HTTPException(status_code=502, detail="Instagram API returned a bad response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
