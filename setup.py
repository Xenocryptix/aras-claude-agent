from setuptools import setup, find_packages

setup(
    name="api-mcp-server",
    version="1.0.0",
    description="MCP Server for generic API integration with Claude Desktop",
    author="D. Theoden",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/api-mcp-server",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "api-mcp-server=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 