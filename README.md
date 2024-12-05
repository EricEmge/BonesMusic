# BonesMusic
Developer: Eric Emge
Graphic Design: Mason Starkweather
A Discord Music Bot For Personal Use

To get working:

-Go to https://discord.com/developers
-Make a new application
-Go to Bot tab
-Turn on all 3 Privileged Gateway Intents
-scroll down on Bot Permissions click URL and copy link
-click and execute link and add to the server
-give bot administrator privileges

-Go to https://replit.com/
-Make a free account
-copy and paste main.py into your python Replit
-type in replit.nix
-paste in this
{pkgs}: {
  deps = [
    pkgs.ffmpeg-full
    pkgs.python311
    pkgs.ffmpeg
    pkgs.libopus
  ];
}

-pip install these packages
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

-click run

-on discord can use !help to see commands
