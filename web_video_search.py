"""
Use web search to find videos for each scene
"""

import json
from pathlib import Path

# Load the production plan
plan_path = "output/test_production_plan.json"
with open(plan_path, 'r', encoding='utf-8') as f:
    plan = json.load(f)

print("=" * 80)
print("VIDEO SEARCH USING WEB")
print("=" * 80)
print(f"\nTitle: {plan['title']}")
print(f"Scenes: {len(plan['scenes'])}\n")

# For each scene, show what we'd search for
for scene in plan['scenes'][:3]:  # First 3 scenes
    print(f"\n{'='*80}")
    print(f"SCENE {scene['scene_number']}: {scene['scene_description']}")
    print(f"{'='*80}")
    print(f"Duration: {scene['duration_seconds']}s")
    print(f"Context: {scene['visual_context'][:100]}...")
    
    for query_obj in scene['search_queries']:
        query = query_obj['query']
        platform = query_obj['platform']
        
        print(f"\n🔍 Search Query: \"{query}\"")
        print(f"   Platform: {platform}")
        print(f"   Reasoning: {query_obj['reasoning'][:80]}...")
        
        # Construct actual search URLs
        if platform.lower() == 'youtube':
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        elif platform.lower() == 'pexels':
            search_url = f"https://www.pexels.com/search/videos/{query.replace(' ', '%20')}/"
        elif platform.lower() == 'pixabay':
            search_url = f"https://pixabay.com/videos/search/{query.replace(' ', '%20')}/"
        else:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        print(f"   🔗 Search URL: {search_url}")

print("\n" + "=" * 80)
print("✅ SEARCH QUERIES READY")
print("=" * 80)
print("\nYou can:")
print("1. Visit these URLs manually to find videos")
print("2. Use browser automation (Selenium/Playwright)")
print("3. Use platform APIs when available")
