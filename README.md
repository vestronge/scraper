# scraper
docker build -t realestatescraper .
mkdir -p ~/Desktop/results
docker run --rm -v ~/Desktop/results:/data realestatescraper python all.py
