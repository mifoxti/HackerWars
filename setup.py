from setuptools import setup, find_packages

# Читаем описание проекта из файла README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='HackerWars',  # Замените на имя вашего проекта
    version='0.1',
    author='Timofey Lyakhov & Daria Abarenova',  # Укажите ваше имя
    author_email='mifoxti@gmail.com',  # Укажите ваш email
    description='Make your own bot game about Hackers',  # Краткое описание проекта
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mifoxti/HackerWars',  # URL вашего проекта на GitHub
    packages=find_packages(),
    install_requires=[
        'aiogram==2.15.1',
    ],
    entry_points={
        'console_scripts': [
            'HackerWars=hackerWars:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
