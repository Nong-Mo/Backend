# �ʿ��� ���̺귯��:
# pip install pytest
# pip install google-cloud-vision
# pip install python-dotenv

import pytest
from pathlib import Path
from google.cloud import vision
import os
from dotenv import load_dotenv

# �׽�Ʈ �̹��� ���丮 ����
TEST_IMAGE_DIR = Path(__file__).parent / "test_images"
TEST_IMAGE_DIR.mkdir(exist_ok=True)

@pytest.fixture(scope="module")
def vision_client():
    """Vision API Ŭ���̾�Ʈ �Ƚ�ó"""
    load_dotenv()
    return vision.ImageAnnotatorClient()

def test_text_detection(vision_client):
    """�ؽ�Ʈ ���� �׽�Ʈ"""
    # �׽�Ʈ �̹��� ���
    image_path = TEST_IMAGE_DIR / "sample.jpg"
    
    # �̹��� ���� ���� Ȯ��
    assert image_path.exists(), f"�׽�Ʈ �̹����� �����ϴ�: {image_path}"
    
    # �̹��� �ε�
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)
    
    # API ���� ����
    assert not response.error.message, f"API ����: {response.error.message}"
    assert len(response.text_annotations) > 0, "�ؽ�Ʈ�� �������� �ʾҽ��ϴ�"
    
    # ������ �ؽ�Ʈ ���
    detected_text = response.text_annotations[0].description
    print(f"\n������ �ؽ�Ʈ:\n{detected_text}")

def test_vision_client_initialization(vision_client):
    """Vision Ŭ���̾�Ʈ �ʱ�ȭ �׽�Ʈ"""
    assert vision_client is not None, "Vision Ŭ���̾�Ʈ �ʱ�ȭ ����" 