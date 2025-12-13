#!/usr/bin/env python3
"""
Setup script to create database schema in Supabase.
This script reads the SQL from database_schema.sql and executes it.
"""

import os
import sys
from app.services.database import get_supabase_client

def read_sql_file(filepath):
    """Read SQL file and return commands"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by semicolons to get individual commands
    commands = [cmd.strip() for cmd in content.split(';') if cmd.strip()]
    return commands

def setup_database():
    """Execute SQL schema to setup database"""
    try:
        supabase = get_supabase_client()
        
        # Read SQL commands from database_schema.sql
        sql_file = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
        commands = read_sql_file(sql_file)
        
        print(f"Found {len(commands)} SQL commands to execute")
        
        # Execute each command using Supabase's RPC or raw query
        # Since Supabase Python client doesn't have direct SQL execution,
        # we'll use the REST API approach
        
        for i, command in enumerate(commands, 1):
            try:
                # Try to execute the command
                # For table creation, we use the table creation method if available
                print(f"Executing command {i}/{len(commands)}...")
                # Note: This is a limitation of the Python SDK - it's designed for REST API queries
                # To execute raw SQL, you would need to use the Supabase SQL editor or
                # expose an RPC function that executes the SQL
                print(f"Command: {command[:100]}...")
            except Exception as e:
                print(f"Error executing command {i}: {e}")
        
        print("\n⚠️  Note: The Supabase Python SDK is limited for direct SQL execution.")
        print("To complete the database setup, please:")
        print("1. Go to your Supabase project dashboard")
        print("2. Open the SQL Editor")
        print("3. Copy the contents of database_schema.sql")
        print("4. Paste and execute in the SQL Editor")
        print(f"\nSQL file location: {sql_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
