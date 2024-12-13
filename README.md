# Video Narration Script Generator

A tool for automatically generating natural-sounding narration scripts from video content. This project consists of two main components:
1. A video analyzer that processes video frames
2. A narrative formatter that creates flowing, natural language scripts suitable for voice-over recording

## Features

- Analyzes video content frame by frame
- Generates natural, conversational narration
- Maintains proper timing with video content
- Detects scene transitions automatically
- Creates coherent narrative flow
- Uses straightforward, clear language
- Includes progress tracking and error handling

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages:
```
moviepy
pillow
openai
python-dotenv
tkinter
```

## Setup

1. Clone the repository
2. Install required packages:
   ```bash
   pip install moviepy pillow openai python-dotenv
   ```
3. Create a `.env` file in the project directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-key-here
   ```

## Usage

1. Run the video analyzer first:
   ```bash
   python video_analyzer.py
   ```
   - Select your video file when prompted
   - The analyzer will create a JSON file with frame analysis

2. Run the narrative formatter:
   ```bash
   python narrative_formatter.py
   ```
   - Select the JSON file created in step 1
   - The formatter will create a natural narrative script

The final script will be saved in the same directory as your input file with "_natural_narrative.txt" appended to the original filename.

## Output

The generated script will include:
- Timestamps for sync points
- Natural transitions between scenes
- Clear, straightforward descriptions
- Professional but conversational tone

## File Structure

```
project_directory/
│
├── video_analyzer.py      # Analyzes video frames
├── narrative_formatter.py # Creates narration script
├── .env                  # API key (not in repo)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Notes

- The tool is designed to create scripts that sound natural when read by a narrator
- Timestamps are included for proper sync with video content
- Generated scripts focus on clear, practical descriptions
- Scene transitions are automatically detected and handled naturally

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)