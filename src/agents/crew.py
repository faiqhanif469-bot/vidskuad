"""
Multi-agent crew for video production planning
"""

from crewai import Agent, Task, Crew, Process, LLM
from src.core.config import Config
from src.agents.prompts import (
    SCRIPT_ANALYST_PROMPT,
    SCENE_DIRECTOR_PROMPT,
    FOOTAGE_STRATEGIST_PROMPT,
    SEARCH_SPECIALIST_PROMPT,
    PLATFORM_SELECTOR_PROMPT,
    PRODUCTION_COORDINATOR_PROMPT
)
from src.tools.crew_tools import SEARCH_TOOLS, initialize_search_tools


class ProductionCrew:
    """Multi-agent crew for intelligent video production planning"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Verify API key is present
        if not config.model.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment. Please check your .env file.")
        
        # Use CrewAI's LLM wrapper for Groq
        import os
        os.environ['GROQ_API_KEY'] = config.model.groq_api_key
        
        self.llm = LLM(
            model=f"groq/{config.model.model_name}",
            api_key=config.model.groq_api_key
        )
        
        # Initialize search tools
        initialize_search_tools(config)
    
    def _create_agents(self):
        """Create specialized agents (NO TOOLS - just analysis)"""
        
        script_analyst = Agent(
            role='Elite Script Analyst',
            goal='Deeply understand script narrative, themes, and visual requirements',
            backstory=SCRIPT_ANALYST_PROMPT,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        scene_director = Agent(
            role='Master Scene Director',
            goal='Break scripts into visual scenes with perfect timing',
            backstory=SCENE_DIRECTOR_PROMPT,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        footage_strategist = Agent(
            role='Footage Strategist',
            goal='Determine clip requirements and footage types',
            backstory=FOOTAGE_STRATEGIST_PROMPT,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        production_coordinator = Agent(
            role='Production Coordinator',
            goal='Synthesize all inputs into executable production plan',
            backstory=PRODUCTION_COORDINATOR_PROMPT,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return {
            'script_analyst': script_analyst,
            'scene_director': scene_director,
            'footage_strategist': footage_strategist,
            'production_coordinator': production_coordinator
        }
    
    def _create_tasks(self, script: str, duration: float, agents: dict):
        """Create sequential tasks (NO SEARCH - just analysis)"""
        
        analyze_task = Task(
            description=f"""Analyze this script in depth:

SCRIPT:
{script}

TARGET DURATION: {duration} seconds

Provide:
1. Overall theme and core message
2. Emotional arc and key emotional beats
3. Target audience and appropriate tone
4. Visual style recommendations
5. Key moments needing strong visual support
6. Pacing recommendations""",
            agent=agents['script_analyst'],
            expected_output="Detailed script analysis with theme, emotion, audience, and visual style"
        )
        
        scene_task = Task(
            description=f"""Break this script into logical visual scenes:

SCRIPT:
{script}

TARGET DURATION: {duration} seconds

CRITICAL RULES:
- Each scene should be 4-6 seconds (one B-roll clip per scene)
- For a {duration}s video, you need approximately {duration // 5} scenes
- Each scene = 1 visual moment = 1 B-roll clip
- STAY LITERAL TO THE SCRIPT - don't over-interpret or add metaphorical meanings
- If script says "rocket launching", write "rocket launching" - not "space exploration"
- Match the script's EXACT words and intent

For each scene provide:
1. Scene number and LITERAL description from script
2. Duration: 4-6 seconds (recommend 5s per scene)
3. Visual context - ONE specific visual moment (LITERAL, not interpreted)
4. Mood and tone
5. Shot type (wide/medium/close-up/establishing)

Example for 60s video = 12 scenes of 5s each
Example for 300s video = 60 scenes of 5s each
Example for 1620s video = 324 scenes of 5s each""",
            agent=agents['scene_director'],
            expected_output="Complete scene breakdown with 4-6s scenes, LITERAL to script, total adding up to target duration",
            context=[analyze_task]
        )
        
        footage_task = Task(
            description="""For each scene, determine footage requirements:

1. How many different clips needed? (be realistic)
2. What types of footage? (action, establishing, close-ups, etc.)
3. How long should each clip hold?
4. What visual variety is needed?
5. Any specific visual requirements?

Simple scenes: 1-2 clips
Complex scenes: 4-6 clips
Consider pacing and visual interest.""",
            agent=agents['footage_strategist'],
            expected_output="Detailed footage requirements with clip counts and types",
            context=[analyze_task, scene_task]
        )
        
        final_task = Task(
            description=f"""Create the final production plan as JSON:

{{
    "title": "Video title/topic",
    "total_duration": {duration},
    "overall_theme": "from script analysis",
    "target_audience": "from script analysis",
    "visual_style": "from script analysis",
    "scenes": [
        {{
            "scene_number": 1,
            "scene_description": "ONE specific visual moment - LITERAL from script",
            "duration_seconds": 5,
            "visual_context": "LITERAL visual description matching script exactly",
            "mood_tone": "from scene director",
            "required_clips": 1,
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }}
    ]
}}

CRITICAL RULES:
- Each scene = 4-6 seconds (recommend 5s)
- Each scene = 1 B-roll clip
- For {duration}s video, create approximately {duration // 5} scenes
- Total duration MUST equal {duration}s
- Scene descriptions must be LITERAL to the script - no over-interpretation
- If script says "factory workers", write "factory workers" not "industrial revolution"

KEYWORDS:
- Extract 5-7 specific keywords DIRECTLY from the script's literal meaning
- Keywords should match what the script ACTUALLY says, not deeper interpretations
- Be specific and searchable (e.g., "rocket launching", "mission control", "astronaut spacewalk")
- Focus on visual elements that can be found in historical video archives
- Don't add metaphorical or thematic keywords

VERIFY:
- All scene durations add up to {duration}s
- Each scene is 4-6 seconds
- Each scene has 1 clip (required_clips: 1)
- Scene descriptions are LITERAL to script
- Keywords match script's actual words
- Everything is production-ready""",
            agent=agents['production_coordinator'],
            expected_output="Complete production plan in JSON format with {duration // 5} scenes of 5s each, LITERAL to script",
            context=[analyze_task, scene_task, footage_task]
        )
        
        return [analyze_task, scene_task, footage_task, final_task]
    
    def analyze_script(self, script: str, duration: float = 60):
        """Run the crew to analyze script"""
        print("🎬 Initializing Production Crew")
        print("=" * 80)
        
        agents = self._create_agents()
        print(f"✓ Created {len(agents)} specialized agents")
        
        tasks = self._create_tasks(script, duration, agents)
        print(f"✓ Created {len(tasks)} sequential tasks")
        
        # Use hierarchical=False to avoid manager LLM requirement
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🚀 Starting analysis...")
        print("=" * 80 + "\n")
        
        result = crew.kickoff()
        return result
