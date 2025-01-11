#%% Lib
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
from datetime import datetime
import os
from tqdm import tqdm

header = {"user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"}

#%% Get journal overview URLs
def scrape_journal_overview_urls(start_ind, n_pages):
    def write_to_file(journal_urls, sleep_time=300):
        with open("journal_overview_urls.txt", "a") as f:
            for journal_url in journal_urls:
                f.write(f"{journal_url}\n")
        
        # Sleep for a bit, and start where we left off
        time.sleep(sleep_time)

    if start_ind == 1:
        # Start fresh
        try:
            os.remove("journal_overview_urls.txt")
        except OSError:
            pass

    journal_urls = []
    try:
        for i in tqdm(range(start_ind, n_pages + 1)):
            # Sleep for a random amount
            time.sleep(np.random.uniform(3, 6))
            
            # Fetch current page
            this_url = url + f"&page={i}"
            this_page = requests.get(this_url, headers=header)
            this_soup = BeautifulSoup(this_page.content, "html.parser")

            # Get links from the table
            table_div = this_soup.find("div", {"class": "div-main"})
            table = table_div.find_all("table")[1]
            rows = table.find_all("tr")
            journal_urls += [row.find("a")["href"] for i, row in enumerate(rows) if i != 0]
    except AttributeError as e:
        print(e)

        # Found none, likely Error 429: Too many requests
        # Append what was found to file and sleep a bit before starting again
        write_to_file(journal_urls)
        scrape_journal_overview_urls(i, n_pages)
    except requests.exceptions.ConnectionError as e:
        print(e)

        # Connection likely closed by host
        # Sleep a bit before starting again
        write_to_file(journal_urls)
        scrape_journal_overview_urls(i, n_pages)
    except Exception as e:
        raise e

    write_to_file(journal_urls)


# Load journals page
url = "https://www.crazyguyonabike.com/doc/?o=3d2&doctype=journal"
# page = requests.get(url, headers=header)
# soup = BeautifulSoup(page.content, "html.parser")

# # Get number of pages to parse
# page_counter_cell = soup.find_all("td", {"class": "navbar-td"})[-1]
# n_pages = int(page_counter_cell.text.replace("(", "").replace(")", "").split("/")[-1])

# Scrape journal overview urls
# scrape_journal_overview_urls(399, 645)

#%% Get journal entry URLs

def scrape_journal_page_urls(start_ind, n_pages, df_journal_overview_urls, header=header):
    def write_to_file(journal_urls):
        with open("journal_page_urls.txt", "a") as f:
            for journal_url in journal_urls:
                f.write(f"{journal_url}\n")


    if start_ind == 0:
        # Start fresh
        try:
            os.remove("journal_page_urls.txt")
            os.remove("blogs.txt")
        except OSError:
            pass

    print("Starting at: ", start_ind)
    journal_page_urls = []
    try:
        for i, row in tqdm(df_journal_overview_urls.loc[start_ind:n_pages].iterrows()):
            # Sleep for a random amount
            time.sleep(np.random.uniform(3, 6))

            # Fetch current page
            this_url = row["URL"]
            this_page = requests.get(this_url, headers=header)
            this_soup = BeautifulSoup(this_page.content, "lxml")

            try:
                if "Hint: To add pages to your journal, click 'Add Page' above." in [span.text for span in this_soup.find_all("span")]:
                    # Empty page
                    continue

                # Get links from page
                journal_page_spans = this_soup.find("dl").find_all("a")
                journal_page_urls += [span["href"] for span in journal_page_spans]
            except AttributeError as e:
                # Found no a tags
                try:
                    # Might be there was no content, just blog, try to scrape
                    content_div = this_soup.find("div", {"class": "content"})
                    blog = " ".join([p.text for p in content_div.find_all("p")]).replace("\n", " ")

                    with open("blogs.txt", "a", encoding="utf-8") as f:
                        f.write(f"{blog}\n")

                    continue
                except AttributeError as e:
                    # Otherwise likely Error 429: Too many requests
                    print("Error at: ", i)
                    print(this_url)
                    print(this_page)
                    print(e)
                
                    # Sleep for a bit, then start where we left off
                    print(f"Sleeping 10 minutes... ({datetime.now()})")
                    time.sleep(600)

                    # Append what was found to file and sleep a bit before starting again
                    write_to_file(journal_page_urls)
                    scrape_journal_page_urls(i, n_pages, df_journal_overview_urls, header)               
    except requests.exceptions.ConnectionError as e:
        # Connection likely closed by host
        print("Error at: ", i)
        print(this_url)
        print(this_page)
        print(e)

        # Sleep a bit before starting again
        write_to_file(journal_page_urls)

        # Sleep for a bit, then start where we left off
        print(f"Sleeping 30 minutes... ({datetime.now()})")
        time.sleep(1800)
        scrape_journal_page_urls(i, n_pages, df_journal_overview_urls, header)
    except Exception as e:
        # On other exceptions, print where we left off
        print("Error at: ", i)
        print(this_url)
        print(this_page)
        raise e

    # If no issues, write urls to file
    write_to_file(journal_page_urls)


# df_journal_overview_urls = pd.read_csv("journal_overview_urls.txt", index_col=0)
# scrape_journal_page_urls(1081, len(df_journal_overview_urls.index), df_journal_overview_urls)

#%% Scrape blogs

def scrape_blog_texts(start_ind, n_pages, df_journal_page_urls, header=header):
    def write_to_file(blog_texts):
        with open("blogs.txt", "a", encoding="utf-8") as f:
            for blog_text in blog_texts:
                f.write(f"{blog_text}\n")

    blog_texts = []
    try:
        for i, row in tqdm(df_journal_page_urls.loc[start_ind:n_pages].iterrows()):
            # Sleep for a random amount
            time.sleep(np.random.uniform(3, 6))

            # Fetch current page
            this_url = row["URL"]

            if "crazyguyonabike.com" not in this_url:
                continue

            this_page = requests.get(this_url, headers=header)
            this_soup = BeautifulSoup(this_page.content, "lxml")

            if "Hint: To add pages to your journal, click 'Add Page' above." in [span.text for span in this_soup.find_all("span")]:
                # Empty page
                continue
            else:
                # Try to scrape
                content_div = this_soup.find("div", {"class": "content"})
                blog = " ".join([p.text for p in content_div.find_all("p")]).replace("\n", " ")
                blog_texts.append(blog)
    except AttributeError as e:
        # Otherwise likely Error 429: Too many requests
        print("Error at: ", i)
        print(this_url)
        print(this_page)
        print(e)
    
        # Append what was found to file and sleep a bit before starting again
        write_to_file(blog_texts)

        # Sleep for a bit, then start where we left off
        print(f"Sleeping 10 minutes... ({datetime.now()})")
        time.sleep(600)
        scrape_blog_texts(i, n_pages, df_journal_page_urls, header)               
    except requests.exceptions.ConnectionError as e:
        # Connection likely closed by host
        print("Error at: ", i)
        print(this_url)
        print(this_page)
        print(e)

        # Append what was found to file and sleep a bit before starting again
        write_to_file(blog_texts)

        # Sleep for a bit, then start where we left off
        print(f"Sleeping 30 minutes... ({datetime.now()})")
        time.sleep(1800)
        scrape_blog_texts(i, n_pages, df_journal_page_urls, header)
    except Exception as e:
        # On other exceptions, print where we left off
        print("Error at: ", i)
        print(this_url)
        print(this_page)

        # Append what was found to file and sleep a bit before starting again
        write_to_file(blog_texts)
        raise e

    # If no issues, write urls to file
    write_to_file(blog_texts)


df_journal_page_urls = pd.read_csv("journal_page_urls.txt", header=None, names=["URL"])
scrape_blog_texts(2363, len(df_journal_page_urls.index), df_journal_page_urls, header)
#%%
