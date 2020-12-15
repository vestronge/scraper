# scraper
docker build -t realestatescraper .

mkdir -p ~/Desktop/results

docker run --rm -v ~/Desktop/results:/data realestatescraper python all.py

# for individual
docker run --rm -v ~/Desktop/results:/data realestatescraper python bureaup.py

docker run --rm -v ~/Desktop/results:/data realestatescraper python bureaul.py

docker run --rm -v ~/Desktop/results:/data realestatescraper python immo.py
