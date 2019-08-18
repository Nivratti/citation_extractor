from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
import os

import pandas as pd

from citation.util_error_handling import trace_error
from citation.get_articles import start_extarcting_articles


# Create your views here.

def dashboard(request):
    context = {}
    return render(request, 'citation/dashboard.html', context)

def get_citation(request):
    context = {}
    return render(request, 'citation/extractor.html', context)


@csrf_exempt
def extract_citations(request):
    # import pandas as pd
    # import pdb;pdb.set_trace()
    try:
        # url_link = 'https://scholar.google.co.in/citations?user=IrlPkbMAAAAJ&hl=en"'
        url_citation = request.POST.get("url_citation")
        all_article_data = start_extarcting_articles(url_citation)
        # print(all_article_data)


        df = pd.DataFrame.from_dict(all_article_data)

        excel_folder = os.path.join(
            settings.MEDIA_ROOT, "excel"
        )
        # make dir if not exists
        os.makedirs(excel_folder, exist_ok=True)

        excel_file = os.path.join(
            excel_folder, 'output.xlsx'
        )

        with pd.ExcelWriter(excel_file) as writer:
            df.to_excel(writer, sheet_name='Articles')
            # df2.to_excel(writer, sheet_name='Sheet_name_2')

        media_path_only = excel_file.replace(settings.BASE_DIR, '')
        # print(f"media_path_only : {media_path_only}")

        response = {
            "message": {
                "type": "success",
                "title": "success Info",
                "text": "Articles extracted successfully"
            },
            "generated_excel_file":{
                "path": media_path_only,
            }
        }

    except Exception as e:
        error = trace_error()
        print(error)

        response = {
            "message": {
                "type": "error",
                "title": "Error Info",
                "text": error
            }
        }

    return JsonResponse(response, safe=True)
