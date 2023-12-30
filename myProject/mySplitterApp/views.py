from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from spleeter.separator import Separator
from django.core.files.storage import default_storage
import os
import shutil
import zipfile
import threading

@csrf_exempt
def separate_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        file_path = default_storage.save('uploads/' + audio_file.name, audio_file)
        file_path = default_storage.path(file_path)

        base_output_path = 'media/output'
        output_folder_2stems = os.path.join(base_output_path, '2stems', os.path.splitext(audio_file.name)[0])
        output_folder_5stems = os.path.join(base_output_path, '5stems', os.path.splitext(audio_file.name)[0])

        separator_2stems = Separator('spleeter:2stems')
        separator_5stems = Separator('spleeter:5stems')

        separator_2stems.separate_to_file(file_path, output_folder_2stems, codec='wav')
        separator_5stems.separate_to_file(file_path, output_folder_5stems, codec='wav')

        zip_path_2stems = os.path.join('media/zips', '2stems_' + os.path.splitext(audio_file.name)[0] + '.zip')
        zip_path_5stems = os.path.join('media/zips', '5stems_' + os.path.splitext(audio_file.name)[0] + '.zip')

        with zipfile.ZipFile(zip_path_2stems, 'w', zipfile.ZIP_DEFLATED) as myzip_2stems:
            for root, dirs, files in os.walk(output_folder_2stems):
                for file in files:
                    myzip_2stems.write(os.path.join(root, file), arcname=file)

        with zipfile.ZipFile(zip_path_5stems, 'w', zipfile.ZIP_DEFLATED) as myzip_5stems:
            for root, dirs, files in os.walk(output_folder_5stems):
                for file in files:
                    myzip_5stems.write(os.path.join(root, file), arcname=file)

        # Construct URLs for the zip files
        url_2stems = request.build_absolute_uri('/media/zips/2stems_' + os.path.splitext(audio_file.name)[0] + '.zip')
        url_5stems = request.build_absolute_uri('/media/zips/5stems_' + os.path.splitext(audio_file.name)[0] + '.zip')

        # Delete the original uploaded file and the output folders
        os.remove(file_path)
        shutil.rmtree(output_folder_2stems)
        shutil.rmtree(output_folder_5stems)

        # Schedule deletion of zip files after 30 minutes (1800 seconds)
        threading.Timer(1800, lambda: os.remove(zip_path_2stems) if os.path.exists(zip_path_2stems) else None).start()
        threading.Timer(1800, lambda: os.remove(zip_path_5stems) if os.path.exists(zip_path_5stems) else None).start()

        return JsonResponse({
            'url_2stems': url_2stems,
            'url_5stems': url_5stems
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
