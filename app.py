from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import time

app = Flask(__name__)
CORS(app)

def extract_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}:{remaining_seconds:02d}"

def get_transcript_with_retry(video_id, max_retries=2, delay=0.5):
    for attempt in range(max_retries):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                transcript = transcript_list.find_transcript(['hy'])
            except:
                transcript = transcript_list.find_transcript()
            
            transcript_data = transcript.fetch()
            
            # Process transcript in smaller chunks
            processed_transcript = []
            current_chunk = []
            chunk_size = 0
            max_chunk_size = 1000  # Maximum characters per chunk
            
            for entry in transcript_data:
                current_chunk.append(entry['text'])
                chunk_size += len(entry['text'])
                
                if chunk_size >= max_chunk_size:
                    processed_transcript.append({
                        'text': ' '.join(current_chunk),
                        'timestamp': format_time(entry['start'])
                    })
                    current_chunk = []
                    chunk_size = 0
            
            # Add remaining text
            if current_chunk:
                processed_transcript.append({
                    'text': ' '.join(current_chunk),
                    'timestamp': format_time(transcript_data[-1]['start'])
                })
            
            return {
                'transcript': processed_transcript,
                'language': transcript.language,
                'language_code': transcript.language_code,
                'raw_transcript': transcript_data
            }
            
        except TranscriptsDisabled:
            return {'error': 'Տեքստը անջատված է այս վիդեոյի համար'}, 400
        except NoTranscriptFound:
            return {'error': 'Տեքստ չի գտնվել այս վիդեոյի համար'}, 400
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            return {'error': f'Տեքստը ստանալը ձախողվեց: {str(e)}'}, 400
    
    return {'error': 'Տեքստը ստանալը ձախողվեց մի քանի փորձից հետո'}, 400

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'Հղումը նշված չէ'}), 400
    
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Անվավեր YouTube հղում'}), 400
    
    result = get_transcript_with_retry(video_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 