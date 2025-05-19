import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes
from telegram.ext.filters import TEXT, COMMAND
import requests
import uuid
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot token
TELEGRAM_TOKEN = "7952764381:AAExpdzIoFIvfmXmU0n-GWZSh36AjZCx6sQ"

# AI model descriptions (simplified)
AI_MODELS = {
    "gemini_flash_1.5": {
        "name": "Gemini Flash 1.5",
        "description": "Fast and efficient AI for text and image analysis.",
        "image_url": "https://picsum.photos/200/200?random=1",
        "api_key": "AIzaSyCl381pJTRkgyskaL27KMOMg4T0xghHCLU"
    },
    "deepseek_prover_v2": {
        "name": "DeepSeek Prover V2",
        "description": "Advanced reasoning for complex queries.",
        "image_url": "https://picsum.photos/200/200?random=2",
        "api_key": "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"
    },
    "qwen2.5_vl_3b": {
        "name": "Qwen2.5 VL 3B Instruct",
        "description": "Vision-language model for text and image tasks.",
        "image_url": "https://picsum.photos/200/200?random=8",
        "api_key": "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"
    }
}

IMAGE_APIS = {
    "stable_diffusion": {
        "name": "Stable Diffusion",
        "description": "Generate images from text prompts.",
        "api_url": "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        "api_key": "sk-G9yHyLKbEdw6M3IQi1o1AP5xFEB5AsC5UjeEQAJFy9FEROrx"
    },
    "pexels": {
        "name": "Pexels Search",
        "description": "Search for high-quality stock photos.",
        "api_url": "https://www.pexels.com",
        "api_key": "WPzH8f1Izt6TPE2FRIv2cu8Poe5qLk4laPkknwU3wo5e784SAuC0XeZQ"
    },
    "picsum": {
        "name": "Picsum Random",
        "description": "Fetch a random photo.",
        "api_url": "https://picsum.photos/200/200"
    },
    "nasa": {
        "name": "NASA API",
        "description": "Access space images, e.g., from Curiosity rover.",
        "api_key": "9Cvc8ZidhJknpfZitmlPatR4pC8eSflFfw6D2Brh"
    }
}

# Store user dialogs (user_id -> {model: str, messages: list})
USER_DIALOGS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    try:
        user_id = update.effective_user.id
        USER_DIALOGS[user_id] = {"model": None, "messages": []}
        
        keyboard = [[InlineKeyboardButton("Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to the AI Bot! I integrate multiple AI models for text, image analysis, and image generation. Click 'Menu' to choose an option.",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error in start: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        if query.data == "menu":
            keyboard = [
                [InlineKeyboardButton("Text & Image Analysis", callback_data="text_image")],
                [InlineKeyboardButton("Image Generation/Search", callback_data="image_gen")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Choose an option:", reply_markup=reply_markup)
        
        elif query.data == "text_image":
            keyboard = [[InlineKeyboardButton(model["name"], callback_data=f"model_{key}")]
                       for key, model in AI_MODELS.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Select an AI model for text/image analysis:", reply_markup=reply_markup)
        
        elif query.data == "image_gen":
            keyboard = [[InlineKeyboardButton(api["name"], callback_data=f"image_{key}")]
                       for key, api in IMAGE_APIS.items()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Select an image-related option:", reply_markup=reply_markup)
        
        elif query.data.startswith("model_"):
            model_key = query.data