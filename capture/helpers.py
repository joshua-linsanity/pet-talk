##############################
# Round Out the Profile Pic  #
##############################
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def create_circular_pixmap(image_path, size):
    # Load the image
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        # Create a placeholder pixmap if loading fails
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.gray)

    # Crop the pixmap to a square based on the smallest dimension
    s = min(pixmap.width(), pixmap.height())
    rect = QRect((pixmap.width() - s) // 2, (pixmap.height() - s) // 2, s, s)
    pixmap = pixmap.copy(rect)

    # Create a square pixmap with transparency to hold the circular image
    circular = QPixmap(s, s)
    circular.fill(Qt.transparent)

    # Draw the circular image
    painter = QPainter(circular)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, s, s)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    # Scale the resulting pixmap to the desired size
    return circular.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

##############################
# Text and Image Embeddings  #
##############################
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from PIL import Image

clip_embeddings = OpenCLIPEmbeddings(model_name="ViT-B-32", checkpoint="laion2b_s34b_b79k")

def process_image(image_path):
    image = Image.open(image_path)
    image_embedding = clip_embeddings.embed_image([image_path])[0]
    return image_embedding

def process_text(text):
    text_embedding = clip_embeddings.embed_documents([text])[0]
    return text_embedding


##############################
# Text and Image Embeddings  #
##############################
# from vespa.deployment import VespaDocker
# from vespa.application import Vespa
# 
# vespa_docker = VespaDocker()
# app = vespa_docker.deploy()
# app = Vespa("http://localhost:8080")
# 
# def feed_data(image_path, text_content):
#     image_embedding = process_image(image_path)
#     app.feed_data_point(
#         schema="image_text_search",
#         data_id=f"doc:{image_path}",
#         fields={
#             "image_file_name": image_path,
#             "image_features": image_embedding,
#             "text_content": text_content
#         }
#     )
# 
# def query_vespa(image_path, text_query):
#     image_embedding = process_image(image_path)
#     text_embedding = process_text(text_query)
#     
#     response = app.query(
#         yql="select * from sources * where ({targetHits:10}nearestNeighbor(image_features, query_image_embedding)) or userInput(@text_query)",
#         ranking="image_text_similarity",
#         body={
#             "input.query(query_image_embedding)": image_embedding,
#             "text_query": text_query
#         }
#     )
#     return response
# 
# def handle_user_query(image_path, text_query):
#     response = query_vespa(image_path, text_query)
#     results = response.hits
#     
#     # Process and return results
#     return [{"id": hit["id"], "relevance": hit["relevance"]} for hit in results]
# 
