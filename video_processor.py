from moviepy import VideoFileClip
import os
from pathlib import Path
from PIL import Image
from openai import OpenAI
import base64
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog, ttk
import logging
from datetime import datetime
import json
import time

class ProgressWindow:
    def __init__(self, title="Processing Video"):
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
        self.label = ttk.Label(self.root, text="Initializing...", padding=10)
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

class EnhancedVideoAnalyzer:
    def __init__(self, video_path, progress_window=None):
        """Initialize the enhanced video analyzer."""
        load_dotenv()
        
        self.progress = progress_window
        self.video_path = video_path
        self.video_name = Path(video_path).stem
        self.output_dir = Path(f"{self.video_name}_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OpenAI API key not found in environment variables")

        # Configure logging
        logging.basicConfig(
            filename=self.output_dir / 'analysis.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def update_status(self, message):
        """Update progress window if available."""
        if self.progress:
            self.progress.update_status(message)
        logging.info(message)

    def analyze_frame(self, frame_path, frame_number, total_frames):
        """Generate experiential descriptions of frames using GPT-4 Vision."""
        try:
            self.update_status(f"Analyzing frame {frame_number} of {total_frames}")
            
            with open(frame_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": """Describe this scene in an engaging, experiential way. 
                    Focus on creating atmosphere and emotional connection. Use sensory details and 
                    descriptive language that helps viewers feel present in the space. Avoid clinical 
                    observations - instead, describe how the space feels and what makes it special.
                    Consider:
                    - The mood and atmosphere
                    - How the space might make someone feel
                    - Interesting details that catch the eye
                    - The flow and relationship between elements
                    - Any unique or distinctive features
                    Write as if you're guiding someone through a personal tour."""},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please provide an engaging, atmospheric description of this scene:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error analyzing frame {frame_number}: {str(e)}")
            return f"Error analyzing frame: {str(e)}"

    def process_video(self):
        """Process video frames and generate enhanced descriptions."""
        try:
            self.update_status("Loading video...")
            with VideoFileClip(self.video_path) as video:
                # Store video metadata
                metadata = {
                    'duration': video.duration,
                    'fps': video.fps,
                    'size': video.size,
                    'filename': self.video_name
                }
                
                # Calculate frame extraction points (1 frame per second)
                frame_times = range(0, int(video.duration), 1)
                total_frames = len(frame_times)
                
                self.update_status("Extracting and analyzing frames...")
                frames_data = []
                
                # Extract and analyze frames
                for i, t in enumerate(frame_times, 1):
                    frame = video.get_frame(t)
                    frame_path = self.output_dir / f"frame_{t:04d}.jpg"
                    Image.fromarray(frame).save(frame_path)
                    
                    # Get enhanced description
                    description = self.analyze_frame(frame_path, i, total_frames)
                    
                    frames_data.append({
                        'timestamp': t,
                        'frame_path': str(frame_path),
                        'narration': description
                    })
                    
                    # Add a small delay to avoid rate limits
                    time.sleep(0.5)

            # Save results
            self.update_status("Saving analysis results...")
            results = {
                'metadata': metadata,
                'video_name': self.video_name,
                'frames': frames_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            output_path = self.output_dir / 'narration_results.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            return str(output_path)

        except Exception as e:
            logging.error(f"Error processing video: {str(e)}")
            raise

def main():
    root = tk.Tk()
    root.withdraw()

    try:
        video_path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ],
            initialdir=os.path.expanduser("~\\Videos")
        )

        if video_path:
            progress_window = ProgressWindow("Analyzing Video")
            analyzer = EnhancedVideoAnalyzer(video_path, progress_window)
            output_path = analyzer.process_video()
            progress_window.close()
            
            tk.messagebox.showinfo(
                "Analysis Complete",
                f"Video analysis completed successfully!\n\nResults saved to:\n{output_path}"
            )

    except Exception as e:
        tk.messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main()