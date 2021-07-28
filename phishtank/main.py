# Import all necessary libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import csv
from string import punctuation
import time


# OK: Clear all unused libraries (completed)


# OK: Split code to functions (completed)
# OK: Get more links in other pages instead of home page: https://www.phishtank.com/phish_search.php?page=0 (completed?)
# OK: Set limit pages to prevent block by phishtank's server. Default = 500.
def get_to_visit_links(limit=500) -> list:
    # OK: Add code and document here (completed)

    """
    This function obtains every URLs suspected of phishing
    to be visited.

    :param: void
    :return: List of URLs suspected of phishing to be visited
    """
    to_visit = []
    pages = []
    counter = 0

    # # OK: Use soup.select(selector) method to get all detail links instead of this code block. (completed)
    # # OK: Use  more complex selector instead of one more step (link.find('a')) (completed)
    # # Learn more about selector: **https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Selectors**
    # OK: move code block get "soup" to here. (completed)

    # OK: Move this code block to function use it's result (soup), make it's easy to read code. (completed)

    # Set the base URL for crawler to begin crawling
    base_url = "https://www.phishtank.com/phish_search.php"
    pages.append(base_url)

    # Need extensive advice on this block of code
    # When using new link as base, this block of code works fine
    # But when navigate from HOME page, this block of code only runs until page 5
    # New URL and URL of page when navigating from HOME page appear different:
    #       New URL:  https://www.phishtank.com/phish_search.php?page=0
    #       When navigate from HOME page: https://www.phishtank.com/phish_archive.php
    while pages and counter < limit:
        page_link = pages.pop(0)
        # OK: Handle exceptions. Maybe server block request => this block will stop (completed)
        try:
            page = requests.get(page_link)
            soup = BeautifulSoup(page.text, "html.parser")
        except:
            print(f"Request blocked by server. Crawler limit allowed is {counter} pages")
            return to_visit
        else:

            next_page_link = soup.select('[align="right"] a')

            for link in soup.select("tr td:nth-of-type(1) a"):
                to_visit.append(urljoin(base_url, link['href']))
            #  OK: save "soup.select('[align="right"] a')" to a variable and reuse it to increase performance. (completed)
            if next_page_link:
                pages.append(urljoin(base_url, next_page_link[0]["href"]))

            counter = counter + 1

    return to_visit


# OK: Handle exceptions (completed)
def extract_info(visit_link) -> list:
    # OK: Add code and document here (completed)
    """
    This function visits a URL suspected of phishing and extracts
    relevant information from the web page of that URL

    :param visit_link: URL to be visited
    :return: List containing the URL's ID, Status, Date, User who submitted,
             Original URL and Verification Status
    """
    info = []

    # OK: Handle exceptions (completed)
    try:
        phish_page = requests.get(visit_link)
        phish_soup = BeautifulSoup(phish_page.text, "html.parser")
    except:
        print(f"Request for phishing links blocked by server.")
        return info
    else:
        # OK: This regex pattern wil false when status = "offline" (completed)
        # ex: https://www.phishtank.com/phish_detail.php?phish_id=6904987

        # Extract phishing URL's ID and Status
        if phish_soup.find("h2"):
            string = re.split(r'\s', phish_soup.find("h2").text)
            info.append(string[2])
            info.append(string[-1].strip(punctuation))

        # Extract phishing URL's submission date (need advice for more elegant code here)
        # OK: use phish_soup.select(selector) method instead of this method to get tags (completed)
        # ex: tags = phish_soup.select(".small")
        #     date = tags[0].contents[0].replace("Submitted","").replace("by","").strip()
        tags = phish_soup.select(".small")
        date = tags[0].contents[0].replace("Submitted", "").replace("by", "").strip()
        info.append(date)

        # OK: use phish_soup.select(selector) (completed)
        # Extract the user who submits the link
        user = tags[0].contents[1].find("a").text
        info.append(user)

        # OK: use phish_soup.select(selector) (completed)
        # Extract the original URL that is suspected of phishing
        og_link = phish_soup.select("[style*='word-wrap:break-word']")
        info.append(og_link[0].contents[0].text)

        # Extract verification status of the URL
        # OK: verification just has 2 value: Phishing/Unknown (completed)
        # OK: Check found condition and use index instead of for loop when you only extract "verification" one time (not completed) (completed)
        # OK: for loop is not necessary here because phish_soup.select("td > h3") return list with 1 element. (completed)

        # OK: if statement is not work, only else statement work (completed)
        # Extract verification status for vote-disabled URLs
        # OK: Why don't you use more precise condition? ("Is a phish").
        #  This condition may fail if an URL verified and it's not a phish.
        # OK: Check with not_a_phish case (read requirements to see detail and example) (completed)
        if "Is a phish" in phish_soup.select("td > h3")[0].text:
            info.append("Phishing")

            # Extract verification status for voted or vote-pending URLs
            # REQUEST FOR ADVICE: Some links seem to not have "h3[style]". Is this new condition for
            # checking not_a_phish case OK? Does this new condition need to be applied to "if" clause
            # as well?
        elif phish_soup.select("h3[style]") and "is not a phishing site" in phish_soup.select("h3[style]")[0].text:
            info.append("Benign")

        else:
            info.append("Unknown")

        # OK: Sleep 3s after an request to prevent server block. (completed)
        time.sleep(3.0)

    return info


# OK: implement function to extract all visit_links, return all info (completed)
def process_urls(visit_links: list) -> list:
    """
    This function extracts all relevant information from to_visit links
    and return their info in a 2D array

    :param visit_links: list of URLs to be visited to extract information from
    :return: 2D array of information extracted from URLs
    """
    print("Processsing.... ", len(visit_links), " links")
    processed_info = []
    for link in visit_links:
        processed_info.append(extract_info(link))
    return processed_info


# OK: use save_data only one time, when all info extracted instead of save_data for each url
#  (data is 2 dimensional array). (completed)
def save_data(data: list, file_name: str) -> bool:
    """
    This function save array of phishing's info, and save it to csv file

    :param data: list of phishing url's info
    :param file_name: name of file to save data
    :return: True if save done, False if it has any exception
    """
    # OK: Add code here (completed)
    file = open(file_name, "w")
    writer = csv.writer(file)
    writer.writerow(["ID", "Status", "Date", "Submitted by", "Phishing URL", "Verification"])
    # OK: By the function's document: ":param data: list of phishing url's info" => each element is one url's info,
    #  and each info is array with 6 values, so this check is wrong and this implement fail too. (completed?)

    for info in data:
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

    # Create CSV file, extract information from phishing-suspected URLs 
    # and save them to the CSV file 

    # OK: use save_data only one time, when all info extracted instead of save_data for each url.
    #  (avoid to open and close file many times) (completed)
    limit = 500
    save_data(process_urls(get_to_visit_links(limit)), "Crawling_Phishtank.csv")
