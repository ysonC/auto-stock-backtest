from setuptools import setup, find_packages

setup(
    name="auto_stock_backtest",
    version="1.0.0",
    author="Wyson Cheng",
    author_email="wyson002@gmail.com",
    description="A tool for automating stock data download, cleaning, and backtesting.",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "pandas",
        "selenium",
        "beautifulsoup4",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "run=app.main:main"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
