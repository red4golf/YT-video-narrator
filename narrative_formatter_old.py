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
        
        # Center window
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (window_width/2)
        y = (screen_height/2) - (window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
        
        # Progress label
        self.label = ttk.Label(self.root, text="Initializing narrative creation...", padding=10)
        self.label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=300, mode='indeterminate')
        self.progress.pack(pady=20)
        
        # Status label
        self.status = ttk.Label(self.root, text="", padding=10)
        self.status.pack()
        
        self.progress.start()
        self.root.update()
    
    def update_status(self, message):
        self.label.config(text=message)
        self.root.update()
    
    def close(self):
        self.root.destroy()

class UnifiedNarrativeFormatter:
    def __init__(self, progress_window):
        self.progress = progress_window
        load_dotenv()
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OpenAI API key not found in environment variables")

        self.script_header = """PROFESSIONAL NARRATION SCRIPT
{title}
Duration: {duration}
Generated: {date}

Narrator Profile: Male, 50s, Army veteran
Style Notes:
- Clear, direct communication style
- Professional but conversational tone
- Straightforward descriptions
- Natural, measured pacing
- Military precision without being rigid

=====================================================

"""

    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds) // 60
        remaining_seconds = int(seconds) % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def create_unified_narrative(self, frames):
        """Create a single, unified narrative from all frame descriptions"""
        try:
            self.progress.update_status("Creating unified narrative...")
            
            # Prepare all timestamps and descriptions
            scene_descriptions = []
            for frame in frames:
                timestamp = self.format_time(frame['timestamp'])
                description = frame['narration']
                scene_descriptions.append(f"[{timestamp}] {description}")
            
            # Combine all descriptions
            full_context = "\n\n".join(scene_descriptions)
            
            system_content = ("Create a single, flowing narrative script from these scene descriptions. "
                            "The narrator is a 50-year-old retired Army veteran. Key points:\n\n"
                            "- Combine all descriptions into one coherent story\n"
                            "- Use clear, direct language\n"
                            "- Keep a professional but approachable tone\n"
                            "- Create smooth transitions between scenes\n"
                            "- Maintain timestamps but integrate them naturally\n"
                            "- Focus on practical details and clear directions\n"
                            "The narrative should flow naturally as one complete script, "
                            "not as separate scene descriptions.")
            
            user_content = f"Create a single, flowing narrative that combines all these scenes into one coherent script:\n\n{full_context}"
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating unified narrative: {str(e)}")

    def create_narrative_script(self, json_path):
        """Create a unified narrative script from the JSON analysis"""
        try:
            self.progress.update_status("Reading analysis data...")
            
            with open(json_path, 'r') as f:
                data = json.load(f)

            output_dir = Path(json_path).parent
            video_name = data['video_name']
            total_duration = data['metadata']['duration']
            current_date = datetime.now().strftime("%B %d, %Y")

            self.progress.update_status("Organizing content...")
            
            # Initialize script with professional header
            script_content = self.script_header.format(
                title=video_name.replace('_', ' ').title(),
                date=current_date,
                duration=self.format_time(total_duration)
            )

            # Create unified narrative
            narrative = self.create_unified_narrative(data['frames'])
            script_content += narrative

            self.progress.update_status("Saving final script...")
            
            # Save the enhanced script
            output_path = output_dir / f"{video_name}_unified_narrative.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            return str(output_path)

        except Exception as e:
            raise Exception(f"Error creating narrative script: {str(e)}")

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
            progress_window = ProgressWindow("Creating Unified Narrative")
            formatter = UnifiedNarrativeFormatter(progress_window)
            output_path = formatter.create_narrative_script(json_path)
            progress_window.close()
            
            messagebox.showinfo(
                "Success", 
                f"Unified narrative script generated successfully!\n\nSaved to:\n{output_path}"
            )
        
    except Exception as e:
        messagebox.showerror("Error", str(e))
    
    finally:
        root.destroy()

if __name__ == "__main__":
    main()