#tasks.py
from celery import shared_task
from spleeter.separator import Separator
import os
import shutil
import zipfile
from .models import Task
import threading

@shared_task
def process_audio_task(file_path, output_folder_2stems, output_folder_5stems, task_id):
    try:
        # Update task status to processing
        task = Task.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        # Perform audio separation
        separator_2stems = Separator('spleeter:2stems')
        separator_5stems = Separator('spleeter:5stems')

        separator_2stems.separate_to_file(file_path, output_folder_2stems, codec='wav')
        separator_5stems.separate_to_file(file_path, output_folder_5stems, codec='wav')

        # Create zip files
        zip_path_2stems = os.path.join('media/zips', '2stems_' + os.path.splitext(os.path.basename(file_path))[0] + '.zip')
        zip_path_5stems = os.path.join('media/zips', '5stems_' + os.path.splitext(os.path.basename(file_path))[0] + '.zip')

        with zipfile.ZipFile(zip_path_2stems, 'w', zipfile.ZIP_DEFLATED) as myzip_2stems:
            for root, dirs, files in os.walk(output_folder_2stems):
                for file in files:
                    myzip_2stems.write(os.path.join(root, file), arcname=file)

        with zipfile.ZipFile(zip_path_5stems, 'w', zipfile.ZIP_DEFLATED) as myzip_5stems:
            for root, dirs, files in os.walk(output_folder_5stems):
                for file in files:
                    myzip_5stems.write(os.path.join(root, file), arcname=file)

        # Schedule deletion of zip files after 15 minutes
        threading.Timer(900, lambda: os.remove(zip_path_2stems) if os.path.exists(zip_path_2stems) else None).start()
        threading.Timer(900, lambda: os.remove(zip_path_5stems) if os.path.exists(zip_path_5stems) else None).start()

        # Update task status to completed
        task.status = 'completed'
        task.url_2stems = os.path.join('/media/zips', os.path.basename(zip_path_2stems))
        task.url_5stems = os.path.join('/media/zips', os.path.basename(zip_path_5stems))
        task.save()

    except Exception as e:
        # Handle exceptions
        task.status = 'failed'
        task.save()
        raise e
