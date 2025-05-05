from setuptools import setup, find_packages

setup(
    name="games_with_camera",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'mediapipe',
        'numpy',
    ],
)