import os
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from minio import Minio
from minio.error import S3Error

# Configuration
watch_folder = '/path/to/watch/folder'
minio_bucket = 'audio'
minio_client = Minio(
    "play.min.io",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=True
)

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.process_new_file(event.src_path)

    def process_new_file(self, file_path):
        # Convert file to MP3
        mp3_file_path = self.convert_to_mp3(file_path)
        
        # Rename and move file
        new_file_path = self.rename_and_move(mp3_file_path)
        
        # Upload to MinIO
        self.upload_to_minio(new_file_path)

    def convert_to_mp3(self, file_path):
        mp3_file_path = file_path.rsplit('.', 1)[0] + '.mp3'
        subprocess.run(['ffmpeg', '-i', file_path, mp3_file_path])
        return mp3_file_path

    def rename_and_move(self, file_path):
        now = datetime.now()
        new_file_name = now.strftime("%Y-%m-%d_%H-%M-%S.mp3")
        month_subdir = now.strftime("%B-%y").lower()
        new_dir_path = os.path.join(watch_folder, month_subdir)
        os.makedirs(new_dir_path, exist_ok=True)
        new_file_path = os.path.join(new_dir_path, new_file_name)
        os.rename(file_path, new_file_path)
        return new_file_path

    def upload_to_minio(self, file_path):
        try:
            with open(file_path, 'rb') as file_data:
                file_stat = os.stat(file_path)
                minio_client.put_object(
                    minio_bucket,
                    os.path.basename(file_path),
                    file_data,
                    file_stat.st_size
                )
            print(f"Uploaded {file_path} to MinIO bucket {minio_bucket}")
        except S3Error as e:
            print("MinIO upload failed:", e)

def main():
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()