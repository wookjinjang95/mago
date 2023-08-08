import os

PATH_TO_TEMPLATE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "template")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PATH_TO_TEMPLATE],
    }
]

from django.conf import settings
import django

settings.configure(TEMPLATES=TEMPLATES)
django.setup()

from django.template.loader import get_template

"""
    TODO: Create a test for report_generator.py
"""
class ReportGenerator:
    def __init__(self, output: str):
        self.output_folder = output
        # self.timestamp = datetime.now()
        self.template_filepath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "template")

    """
        TODO: We have to move the rest of the logo to the 
        output folder.
    """
    def write_workers_content(self, content_data: dict):
        template = get_template('workers.html')
        filepath = os.path.join(self.output_folder, "workers.html")
        
        with open(filepath, 'w') as fp:
            fp.write(template.render(content_data))

    def write_home_content(self, content_data: dict = {}):
        template = get_template("index.html")
        filepath = os.path.join(self.output_folder, "index.html")

        with open(filepath, 'w') as fp:
            fp.write(template.render(content_data))

    def write_log_content(self, content_data: dict = {}):
        template = get_template("logs.html")
        filepath = os.path.join(self.output_folder, "logs.html")
        
        with open(filepath, 'w') as fp:
            fp.write(template.render(content_data))

        