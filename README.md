# crimemapping-scraper

A scraper for crimemapping.com. The script dumps the scraped data to an Azure Cosmos DB.

## Get started

1. Install ChromeDriver `brew install --cask chromedriver`

2. Create a Conda environment `conda create --name crimemapping --file requirements.txt`

3. Activate the Conda environment `conda activate crimemapping`

4. Create `.env` file with the following environment variables for Azure Cosmos DB:

- `ACCOUNT_HOST` - Azure Cosmos DB's location (e.g., `https://***.documents.azure.com:443/`)
- `ACCOUNT_KEY` - aka Master Key
- `COSMOS_DATABASE` - Database ID
- `COSMOS_CONTAINER` - Container ID

5. Run `scrape.py`. Data will be dumped to the database.
