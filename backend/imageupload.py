from flask import Flask, request, jsonify, Response
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/upload", methods=["POST"])
def index():
    # If file is present in the request, proceed with the upload logic
    if "file" in request.files:
        return upload_file()

    my_res = Response("차단되지롱")
    my_res.headers["Access-Control-Allow-Origin"] = "*"
    return my_res
    

def upload_file():
    file = request.files["file"]

    try:
        # Get your connection string from an environment variable
        # connect_str = "DefaultEndpointsProtocol=https;AccountName=imageuploaded;AccountKey=bMub+NdEwHP/M+P9ht0HBGzzPrI1dgUIE9QQ/dWFh3JWIncYXxWwTTGEBjQDZTVB+KFuimNBcat5+ASttkQdCg==;EndpointSuffix=core.windows.net"
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "imageuploaded"

        blob_name = str(uuid.uuid4())
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)

        # Upload the file
        blob_client.upload_blob(file.read())

        # Log the file name and blob name
        app.logger.info(f"File '{file.filename}' uploaded successfully as blob '{blob_name}'")

        return (
            jsonify({"message": "File uploaded successfully", "blob_name": blob_name}),
            200,
        )
    except Exception as ex:
        app.logger.error("An error occurred during the file upload.", exc_info=True)  # 로그 기록
        return jsonify({"error": "An error occurred"}), 500


if __name__ == "__main__":
    app.run(port=2200, debug=False)  # debug=True will enable more detailed error logging
