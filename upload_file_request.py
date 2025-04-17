import requests

def extract_text_from_pdf(url : str , file_path : str):
    """
    Extracts text, tables and images from a PDF file using Docling.
    Args:
        url (str): URL of the FastAPI endpoint.
        file_path (str): Path to the PDF file.
    Returns:
        dict : A dictionary containing extracted text, tables, and images.
    """

    # Open the file and send the POST request
    with open(file_path, "rb") as file:
        files = {"file": (file_path, file, "application/pdf")}
        response = requests.post(url, files=files)

    # Print the response
    print("Status Code:", response.status_code)
    try:
        return response.json()
    except Exception as e:
        print("Error decoding JSON:", str(e))
        return {"error": str(e)}

print(extract_text_from_pdf("http://localhost:8998/upload-pdf/", "test_pdf.pdf"))