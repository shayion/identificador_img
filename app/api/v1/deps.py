# app/api/v1/deps.py
from fastapi import Depends
# Importa as funções de segurança do core
from app.core.security import get_current_user