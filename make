#!/bin/bash
ROUTES_FILE="app/auth/routes.py"

# Check if auth_bp is defined in routes.py
if ! grep -q "^auth_bp = Blueprint" "$ROUTES_FILE"; then
  echo "Adding auth_bp Blueprint definition and required imports to $ROUTES_FILE..."

  # Backup the original file
  cp "$ROUTES_FILE" "${ROUTES_FILE}.bak"

  # Insert imports and auth_bp definition at the top of the file
  sed -i '1i\
from flask import Blueprint, render_template, redirect, url_for, flash, request\n\
from werkzeug.security import generate_password_hash\n\
from app import db\n\
from app.models import User, Worker, Requester, ServiceType\n\
from app.forms import UserCredentialsForm, WorkerForm, RequesterForm\n\
\nauth_bp = Blueprint("auth", __name__, url_prefix="/auth")\n' "$ROUTES_FILE"

  echo "Done."
else
  echo "auth_bp Blueprint already defined in $ROUTES_FILE, skipping."
fi
