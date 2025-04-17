from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption
import base64
from io import BytesIO
import json


# Declare pdf pipeline options
IMAGE_RESOLUTION_SCALE = 2.0

# Explicitly set the accelerator
accelerator_options = AcceleratorOptions(
    num_threads=8, device=AcceleratorDevice.AUTO
)

pipeline_options = PdfPipelineOptions()
pipeline_options.accelerator_options = accelerator_options
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True
pipeline_options.generate_picture_images = True
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

#Loading test pdf for initial download of models

def load_test_pdf():
    """This function loads a test PDF file to trigger the download of models."""
    input_doc = Path('test_pdf.pdf')
    conversion_result = converter.convert(input_doc)
    del input_doc
    del conversion_result

def pdf_extract_docling(pdf_path, text_splitter):
    """
    Extracts text, tables and images from a PDF file using Docling.
    Args:
        pdf_path (str): Path to the PDF file.
        text_splitter: Text splitter instance to split the text into chunks.
    Returns:
        tuple: A tuple containing lists of extracted text, tables, and images.

    """
    input_doc = Path(pdf_path)


    # Enable the profiling to measure the time spent
    settings.debug.profile_pipeline_timings = True

    # Convert the document
    conversion_result = converter.convert(input_doc)
    doc = conversion_result.document
    print('Starting conversion to markdown')
    # List with total time per document
    doc_conversion_secs = conversion_result.timings["pipeline_total"].times
    text_list = []
    tables_list = []
    images_list = []
    for page_num in doc.pages:
        print(f'Extracting text from page {page_num}')
        text = doc.export_to_markdown(page_no=page_num)
        #Add filename and page number to text to make search more relevant
        if text:
            chunk_metadata = {'filename': pdf_path, 'page_number': page_num}
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                text_list.append((chunk, chunk_metadata))

    for table in doc.tables:
        table_df = table.export_to_dataframe()
        table_metadata = {'filename': pdf_path, 'page_number': table.prov[0].page_no}
        tables_list.append((table_df,table_metadata))
    print(f"Conversion secs: {doc_conversion_secs}")
    return text_list,tables_list,images_list