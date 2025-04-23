import os
from time import sleep
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('profile_manager')

import EmailManager

profile_database = {
    "": {
        "username": "Default User",
        "profile_image": "https://avatar.iran.liara.run/public/2",
        "temperature_threshold": 20,
        "intensity_threshold": 2000,
    },
    
    "13a0a6a5": {
        "username": "RFID User 1",
        "profile_image": "https://avatar.iran.liara.run/public/60",
        "temperature_threshold": 22,
        "intensity_threshold": 1800
    },

    "13eedf95": {
        "username": "RFID User 2",
        "profile_image": "https://avatar.iran.liara.run/public/80",
        "temperature_threshold": 24,
        "intensity_threshold": 2200
    },
}

userID = ""
userTempThreshold = 20  # base value
userLightThreshold = 2000  # base value

def get_all_profiles():
    """Return all available profiles for debugging"""
    return profile_database

def profileData():
    """Return user profile data with consistent structure"""
    try:
        result = {
            "userID": userID,
            "data": {
                "username": "Default User",
                "profile_image": "https://avatar.iran.liara.run/public/2",
                "temperature_threshold": userTempThreshold,
                "intensity_threshold": userLightThreshold
            }
        }
        
        # Override with profile data if exists
        if userID in profile_database:
            result["data"] = profile_database[userID]
            logger.info(f"Returning profile for user: {userID}")
        else:
            logger.info(f"Using default profile, userID '{userID}' not found")
            
        return result
    except Exception as e:
        logger.error(f"Error in profileData: {e}")
        # Return a safe default with consistent structure
        return {
            "userID": "",
            "data": {
                "username": "Error",
                "profile_image": "https://avatar.iran.liara.run/public/1",
                "temperature_threshold": userTempThreshold,
                "intensity_threshold": userLightThreshold
            }
        }

def set_Profile():
    """Set user profile based on userID"""
    global userTempThreshold, userLightThreshold
    
    try:
        # Check if userID exists 
        if userID in profile_database:
            userProfile = profile_database[userID]
            
            # Update  thresholds
            userTempThreshold = userProfile['temperature_threshold']
            userLightThreshold = userProfile['intensity_threshold']
            
            # Log update
            logger.info(f"Profile set for user: {userID}")
            logger.info(f"Temperature threshold: {userTempThreshold}")
            logger.info(f"Light threshold: {userLightThreshold}")
            
            # Send email notif
            try:
                message = f"User profile updated: {userProfile['username']} at {EmailManager.get_formatted_time()}"
                subject = f"Profile Update: {userProfile['username']}"
                EmailManager.email_notification(message, subject=subject, email_type='RFID')
            except Exception as email_error:
                logger.error(f"Error sending profile email: {email_error}")
        else:
            logger.warning(f"User ID not found in profile database: {userID}")
    except Exception as e:
        logger.error(f"Error in set_Profile: {e}")

def normalize_tag(tag):
    """Fix RFID tag format"""
    if not tag:
        return ""
    normalized = tag.strip().lower()
    normalized = normalized.replace(':', '').replace('-', '').replace(' ', '')
    logger.info(f"Normalized tag '{tag}' to '{normalized}'")
    return normalized

def set_UserID(mqtt_message):
    """Set userID from MQTT message with tag format normalization"""
    global userID
    
    try:
        if not mqtt_message:
            logger.warning("Received empty MQTT message")
            return
            
        # Normalize the tag 
        normalized_tag = normalize_tag(mqtt_message)
        
        # Debug logging
        logger.info(f"Received RFID tag: '{mqtt_message}', normalized to: '{normalized_tag}'")
        logger.info(f"Available profiles: {list(profile_database.keys())}")
        
        # Look for exact match first
        if normalized_tag in profile_database:
            userID = normalized_tag
            logger.info(f"Found exact profile match for: {userID}")
        else:
            # Try case-insensitive match
            for key in profile_database.keys():
                normalized_key = normalize_tag(key)
                if normalized_key == normalized_tag:
                    userID = key
                    logger.info(f"Found case-insensitive match: {userID}")
                    break
            else:
                # No match found
                userID = normalized_tag
                logger.warning(f"No profile match found, using tag directly: {userID}")
        
        # Set the profile
        set_Profile()
    except Exception as e:
        logger.error(f"Error in set_UserID: {e}")