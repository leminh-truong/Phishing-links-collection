# Import all necessary libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import csv
from string import punctuation
import time


class LinkRetriever:
    '''
    This class collects all links suspected of phishing
    '''
    base_url = "https://www.phishtank.com/phish_search.php"

    def __init__(self, limit):
        self.limit = limit

    def get_visit_links(self):
        pages = []
        to_visit = []
        counter = 0
        pages.append(LinkRetriever.base_url)

        while pages and counter < self.limit:
            page_link = pages.pop(0)
        # Handle exceptions. Maybe server block request => this block will stop
            try:
                page = requests.get(page_link)
                soup = BeautifulSoup(page.text, "html.parser")
            except:
                print(f"Request blocked by server. Crawler limit allowed is {counter} pages")
                return to_visit
            else:

                next_page_link = soup.select('[align="right"] a')

                for link in soup.select("tr td:nth-of-type(1) a"):
                    to_visit.append(urljoin(LinkRetriever.base_url, link['href']))

                if next_page_link:
                    pages.append(urljoin(LinkRetriever.base_url, next_page_link[0]["href"]))

                counter = counter + 1

        return to_visit

class InfoExtractor:
    """
    This class extracts information from all phishing links to be visited
    """
    def __init__(self, visit_links):
        self.visit_links = visit_links

    def extract_info(self, link):
        """
        This method extracts all relevant information from every phishing links
        """
        info = []

        # Handle exceptions
        try:
            phish_page = requests.get(link)
            phish_soup = BeautifulSoup(phish_page.text, "html.parser")
        except:
            print(f"Request for phishing links blocked by server.")
            return info
        else:
            # Extract phishing URL's ID and Status
            if phish_soup.find("h2"):
                string = re.split(r'\s', phish_soup.find("h2").text)
                info.append(string[2])
                info.append(string[-1].strip(punctuation))

            # Extract phishing URL's submission date (need advice for more elegant code here)
            tags = phish_soup.select(".small")
            date = tags[0].contents[0].replace("Submitted", "").replace("by", "").strip()
            info.append(date)

            # Extract the user who submits the link
            user = tags[0].contents[1].find("a").text
            info.append(user)

            # Extract the original URL that is suspected of phishing
            og_link = phish_soup.select("[style*='word-wrap:break-word']")
            info.append(og_link[0].contents[0].text)

            # Extract verification status for vote-disabled URLs
            if "Is a phish" in phish_soup.select("td > h3")[0].text:
                info.append("Phishing")

            # Extract verification status for voted URLs
            elif phish_soup.select("h3[style]") and "is not a phishing site" in phish_soup.select("h3[style]")[0].text:
                info.append("Benign")

            # Extract verification status for vote-pending URLs
            else:
                info.append("Unknown")

        # Sleep 3s after an request to prevent server block
        time.sleep(3.0)

        return info
    
    def process_info(self):
        """
        This method stores the extracted information from phishing links as a 2D array
        """
        print("Processsing.... ", len(self.visit_links), " links")
        processed_info = []
        for link in self.visit_links:
            processed_info.append(self.extract_info(link))
        return processed_info

    
class DataSaver:
    """
    This class saves the extracted information to a CSV file
    """

    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    def save_data(self):
        """
        This method saves the extracted information into a CSV file
        """

        # Create CSV file
        file = open(self.filename, "w")
        writer = csv.writer(file)
        writer.writerow(["ID", "Status", "Date", "Submitted by", "Phishing URL", "Verification"])
       
        #  Extract information from phishing-suspected URLs and save them to the CSV file 
        for info in self.data:
            if "None" in info or len(info) != 6:
                ok = False
                break
            else:
                ok = True
                writer.writerow(info)
        file.close()
        return ok

if __name__ == "__main__":
    print("Crawling Phishtank...")

    visit_links = LinkRetriever(500)
    extracted_info = InfoExtractor(visit_links.get_visit_links())
    save_data = DataSaver(extracted_info.process_info(), "Phishtank_Crawling.csv")
