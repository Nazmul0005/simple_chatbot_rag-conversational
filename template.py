import os
from pathlib import Path

project_name="com"

list_of_files=[
    f"{project_name}/mhire/app/config/config.py",

    f"{project_name}/mhire/app/database/database_connection.py",
    f"{project_name}/mhire/app/database/database_manager.py",

    f"{project_name}/mhire/app/services/chat_stream/chat_stream_schema.py",
    f"{project_name}/mhire/app/services/chat_stream/chat_stream.py",
    f"{project_name}/mhire/app/services/chat_stream/chat_stream_router.py",

    f"{project_name}/mhire/app/services/chat/chat_schema.py",
    f"{project_name}/mhire/app/services/chat/chat.py",
    f"{project_name}/mhire/app/services/chat/chat_router.py",

    f"{project_name}/mhire/app/services/conversation/conversation_schema.py",
    f"{project_name}/mhire/app/services/conversation/conversation.py",
    f"{project_name}/mhire/app/services/conversation/conversation_router.py",

    f"{project_name}/mhire/app/services/history_get/history_get_schema.py",
    f"{project_name}/mhire/app/services/history_get/history_get.py",
    f"{project_name}/mhire/app/services/history_get/history_get_router.py",

    f"{project_name}/mhire/app/services/history_delete/history_delete_schema.py",
    f"{project_name}/mhire/app/services/history_delete/history_delete.py",
    f"{project_name}/mhire/app/services/history_delete/history_delete_router.py",

    f"{project_name}/mhire/app/services/session/session_schema.py",
    f"{project_name}/mhire/app/services/session/session.py",
    f"{project_name}/mhire/app/services/session/session_router.py",

    f"{project_name}/mhire/app/main.py",

    f"nginx/nginx.conf",
    "requirements.txt",
    "Dockerfile",
    ".dockerignore",
    "docker-compose.yml",
    ".env",
    "README.md",
    ".gitignore",
    
]


for filepath in list_of_files:
    filepath=Path(filepath)
    filedir, filename=os.path.split(filepath)

    if filedir!="":
        os.makedirs(filedir , exist_ok=True)

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath)==0):
        with open (filepath , "w") as f:
            pass

    else:
        print(f"File already exists : {filepath}")