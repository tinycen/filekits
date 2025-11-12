from setuptools import setup, find_packages

# 读取README文件
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'Filekits - 一个简洁高效的Python文件处理工具包，支持多种文件格式读写、网络文件下载、文件夹操作等常用功能。'

setup(  
    name='filekits',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl',
        'pyyaml',
        'funcguard',
    ],
    author='tinycen',
    author_email='sky_ruocen@qq.com',
    description='一个简洁高效的Python文件处理工具包，提供文件读写、网络下载、文件夹操作等常用功能',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tinycen/filekits',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
)
