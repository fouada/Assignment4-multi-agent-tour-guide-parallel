"""
Multi-Agent Tour Guide - Agent Package

Contains specialized agents for finding content:
- VideoAgent: Finds relevant YouTube videos
- MusicAgent: Finds relevant songs
- TextAgent: Finds historical/interesting facts
- JudgeAgent: Evaluates and selects best content
"""

from agents.base_agent import BaseAgent
from agents.video_agent import VideoAgent
from agents.music_agent import MusicAgent
from agents.text_agent import TextAgent
from agents.judge_agent import JudgeAgent

__all__ = [
    'BaseAgent',
    'VideoAgent', 
    'MusicAgent',
    'TextAgent',
    'JudgeAgent'
]

