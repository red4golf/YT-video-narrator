import json
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from openai import OpenAI
from dotenv import load_dotenv

class ProgressWindow:
    def __init__(self, title="Creating Narrative"):
        self.root = tk.Tk()
        self.root.title(title)
        
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (window_width/2)
        y = (screen_height/2) - (window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
        
        self.label = ttk.Label(self.root, text="Initializing narrative creation...", padding=10)
        self.label.pack()
        
        self.progress = ttk.Progressbar(self.root, length=300, mode='indeterminate')
        self.progress.pack(pady=20)
        
        self.status = ttk.Label(self.root, text="", padding=10)
        self.status.pack()
        
        self.progress.start()
        self.root.update()
    
    def update_status(self, message):
        self.label.config(text=message)
        self.root.update()
    
    def close(self):
        self.root.destroy()

class NaturalNarrativeFormatter:
    def __init__(self, progress_window):
        self.progress = progress_window
        load_dotenv()
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OpenAI API key not found in environment variables")

        self.script_header = """NARRATION SCRIPT
{title}
Duration: {duration}
Generated: {date}

Narrator: Veteran Tour Guide
- Natural, conversational style
- Clear and direct descriptions
- Simple location transitions
- Practical observations

=====================================================

"""

    def format_time(self, seconds):
        minutes = int(seconds) // 60
        remaining_seconds = int(seconds) % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def identify_scene_changes(self, frames):
        """Group frames by major scene changes"""
        self.progress.update_status("Identifying scene changes...")
        scenes = []
        current_scene = []
        
        for i, frame in enumerate(frames):
            # Start a new scene if this is a transition frame
            description = frame['narration'].lower()
            is_transition = any(term in description for term in [
                'moving to', 'entering', 'stepping into', 'next we have',
                'moving into', 'heading to', 'walking into', 'now in'
            ])
            
            if is_transition and current_scene:
                scenes.append(current_scene)
                current_scene = [frame]
            else:
                current_scene.append(frame)
                
            # Handle last frame
            if i == len(frames) - 1 and current_scene:
                scenes.append(current_scene)
                
        if not scenes and current_scene:
            scenes.append(current_scene)
            
        return scenes

    def create_natural_narrative(self, grouped_scenes):
        """Create a natural, conversational narrative"""
        try:
            self.progress.update_status("Creating natural narrative...")
            
            narrative_prompt = """You are a 50-year-old retired Army veteran giving a video tour. 
            Write exactly as you would naturally speak while showing someone around.

            Essential guidelines:
            - Use everyday language you'd use in normal conversation
            - NO marketing language or flowery descriptions
            - Speak like you're talking to a friend or family member
            - Keep transitions simple ("Let's head to the kitchen" not "Moving along to our next space")
            - Only mention things worth pointing out
            - Keep descriptions brief and practical
            - Include timestamps only when changing locations or pointing out something specific

            Write like this:
            "Here's the living room. Big windows give you plenty of natural light. Nice view of the mountains from here."

            Not like this:
            "As we gracefully transition into this elegantly appointed living space, you'll be captivated by the abundant natural illumination..."

            Remember: You're a regular person showing someone around - not a marketing writer."""

            # Prepare scene descriptions
            scene_content = []
            for scene in grouped_scenes:
                scene_start = self.format_time(scene[0]['timestamp'])
                descriptions = [frame['narration'] for frame in scene]
                scene_content.append(f"Location starting at [{scene_start}]:\n" + 
                                   "\n".join(descriptions))
            
            full_context = "\n\n=== Location Change ===\n\n".join(scene_content)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": narrative_prompt},
                    {"role": "user", "content": f"Give a natural tour based on these scenes. Talk like you normally would:\n\n{full_context}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error generating narrative: {str(e)}")

    def create_narrative_script(self, json_path):
        """Create the complete narrative script"""
        try:
            self.progress.update_status("Reading analysis data...")
            
            with open(json_path, 'r') as f:
                data = json.load(f)

            output_dir = Path(json_path).parent
            video_name = data['video_name']
            total_duration = data['metadata']['duration']
            current_date = datetime.now().strftime("%B %d, %Y")

            self.progress.update_status("Analyzing scenes...")
            grouped_scenes = self.identify_scene_changes(data['frames'])

            script_content = self.script_header.format(
                title=video_name.replace('_', ' ').title(),
                date=current_date,
                duration=self.format_time(total_duration)
            )

            self.progress.update_status("Creating natural narrative...")
            narrative = self.create_natural_narrative(grouped_scenes)
            script_content += narrative

            self.progress.update_status("Saving script...")
            output_path = output_dir / f"{video_name}_natural_narrative.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            return str(output_path)

        except Exception as e:
            raise Exception(f"Error creating script: {str(e)}")

def main():
    root = tk.Tk()
    root.withdraw()

    try:
        json_path = filedialog.askopenfilename(
            title="Select narration_results.json file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~\\Documents")
        )

        if json_path:
            progress_window = ProgressWindow("Creating Natural Narrative")
            formatter = NaturalNarrativeFormatter(progress_window)
            output_path = formatter.create_narrative_script(json_path)
            progress_window.close()
            
            messagebox.showinfo(
                "Success", 
                f"Natural narrative script generated successfully!\n\nSaved to:\n{output_path}"
            )
        
    except Exception as e:
        messagebox.showerror("Error", str(e))
    
    finally:
        root.destroy()

if __name__ == "__main__":
    main()