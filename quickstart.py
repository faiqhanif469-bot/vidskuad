"""
Quick start script - minimal setup to test the system
"""

import os
from pathlib import Path


def check_env():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("\nCreating .env file...")
        
        api_key = input("\nEnter your GEMINI_API_KEY (get from https://aistudio.google.com/app/apikey): ").strip()
        
        if not api_key:
            print("❌ API key required")
            return False
        
        with open('.env', 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
            f.write("# Optional:\n")
            f.write("# PEXELS_API_KEY=\n")
            f.write("# PIXABAY_API_KEY=\n")
        
        print("✓ .env file created")
    else:
        print("✓ .env file found")
    
    return True


def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import crewai
        import google.generativeai
        import yt_dlp
        print("✓ Dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        os.system("pip install -r requirements.txt")
        return True


def run_test():
    """Run a quick test"""
    print("\n" + "=" * 80)
    print("RUNNING QUICK TEST")
    print("=" * 80)
    
    try:
        from src.core.config import Config
        config = Config.load()
        print("✓ Configuration loaded successfully")
        
        from src.tools.search_engine import VideoSearchEngine
        engine = VideoSearchEngine(config)
        print("✓ Search engine initialized")
        
        print("\nTesting YouTube search...")
        results = engine.search_youtube("sunset", max_results=3)
        print(f"✓ Found {len(results)} videos")
        
        if results:
            print(f"\nExample result:")
            print(f"  Title: {results[0].title[:50]}...")
            print(f"  URL: {results[0].url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Quick start"""
    print("=" * 80)
    print("AI VIDEO PRODUCTION SYSTEM - QUICK START")
    print("=" * 80)
    
    print("\n1. Checking environment...")
    if not check_env():
        return
    
    print("\n2. Checking dependencies...")
    if not check_dependencies():
        return
    
    print("\n3. Running test...")
    if not run_test():
        return
    
    print("\n" + "=" * 80)
    print("✓ SETUP COMPLETE!")
    print("=" * 80)
    print("\nYou're ready to go! Run:")
    print("  python main.py")
    print("\nOr test search:")
    print("  python test_search.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
