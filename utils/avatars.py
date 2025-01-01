# Description: This file contains the list of avatars that can be used by the user.
AVATAR_CHOICES = [
    {"name": "Judy", "file": "./templates/judy_sitting.mp4", "voice": "c8e176c17f814004885fd590e03ff99f",
     "avatar": "Judy_Teacher_Sitting_public"},
    {"name": "Bryan", "file": "./templates/bryan_fitness.mp4", "voice": "1985984feded457b9d013b4f6551ac94",
     "avatar": "Bryan_FitnessCoach_public"},
    {"name": "Silas", "file": "./templates/silas_customer.mp4", "voice": "42d598350e7a4d339a3875eb1b0169fd",
     "avatar": "Silas_CustomerSupport_public"}
]

AVATAR_NAMES = [avatar["name"] for avatar in AVATAR_CHOICES]
AVATAR_FILES = {avatar["name"]: avatar["file"] for avatar in AVATAR_CHOICES}
AVATAR_VOICES = {avatar["name"]: avatar["voice"] for avatar in AVATAR_CHOICES}
AVATAR_IDS = {avatar["name"]: avatar["avatar"] for avatar in AVATAR_CHOICES}