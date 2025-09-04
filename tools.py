import logging
import asyncio
import requests
import time
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional

# Simple cache for weather lookups
_weather_cache = {}

async def _safe_call(fn, *args, timeout=3, **kwargs):
    """
    Run a blocking or async function safely with timeout + cancellation.
    """
    try:
        return await asyncio.wait_for(fn(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logging.warning(f"{fn.__name__} timed out")
        return f"{fn.__name__} request timed out."
    except asyncio.CancelledError:
        logging.warning(f"{fn.__name__} was cancelled by server")
        return f"{fn.__name__} request was cancelled."
    except Exception as e:
        logging.error(f"Error in {fn.__name__}: {e}")
        return f"An error occurred in {fn.__name__}: {str(e)}"


@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """
    Get the current weather for a given city.
    """
    now = time.time()
    if city in _weather_cache and now - _weather_cache[city]["time"] < 300:
        return _weather_cache[city]["data"]

    async def fetch_weather():
        resp = await asyncio.to_thread(requests.get, f"https://wttr.in/{city}?format=3")
        if resp.status_code == 200:
            return resp.text.strip()
        return f"Could not retrieve weather for {city}."

    result = await _safe_call(fetch_weather)
    if "error" not in result.lower() and "could not" not in result.lower():
        _weather_cache[city] = {"time": now, "data": result}
    logging.info(f"Weather for {city}: {result}")
    return result


@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    async def do_search():
        return await asyncio.to_thread(DuckDuckGoSearchRun().run, query)

    result = await _safe_call(do_search, timeout=5)
    logging.info(f"Search results for '{query}': {result}")
    return result


@function_tool()    
async def send_email(
    context: RunContext,  
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    """
    async def do_send():
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  

        if not gmail_user or not gmail_password:
            return "Email sending failed: Gmail credentials not configured."

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject

        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.quit()

        return f"Email sent successfully to {to_email}"

    return await _safe_call(do_send, timeout=10)
