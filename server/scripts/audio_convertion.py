import os
import subprocess as sp

def convert_to_mp3(file_path):
    print('Converting ', file_path, ' to mp3')
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_basename = os.path.splitext(file_name)[0]
    output_path = os.path.join(dir_path, file_basename + '.mp3')

    # Check if the input file exists before conversion
    if not os.path.exists(file_path):
        print(f'Error: {file_path} does not exist')
        return None

    cmd = [
        'ffmpeg', 
        '-hide_banner', 
        '-i', file_path, 
        '-filter:a', 'loudnorm',
        '-b:a', '320k',  
        '-y', output_path
    ]

    print(f'Running command: {" ".join(cmd)}')
    
    # Capture both stdout and stderr for better error diagnostics
    ffmpeg = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = ffmpeg.communicate()

    if ffmpeg.returncode != 0:
        print('Error converting ', file_path)
        print(stderr.decode('utf-8'))  # Print detailed error output
        return None
    else:
        print('Finished processing ', output_path)
        return output_path
