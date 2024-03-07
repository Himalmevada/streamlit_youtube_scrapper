from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

@st.cache_data()
def scrape_youtube_data(url):
    driver = webdriver.Chrome() # Offline
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # chrome_service = ChromeService(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=chrome_service, options=options)
    driver = webdriver.Chrome(service=ChromeDriverManager().install(), options=options)
    
    driver.get(url)
    driver.maximize_window()

    yt_channel_name = driver.find_element(By.XPATH, '//*[@id="text"]').text

    # st.subheader(yt_channel_name)

    # Scroll down to load more elements
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):  # Adjust the number of scrolls based on your needs
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    content = driver.page_source.encode("utf-8").strip()
    bs = BeautifulSoup(content, "lxml")

    video_title_links = bs.findAll("a", id="video-title-link")
    thumbnail = bs.findAll(
        "img",
        class_="yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded",
    )

    all_data = bs.findAll("div", id="metadata-line")
    csv_data = []

    try:
        for index in range(0, len(all_data) - 1):
            title = video_title_links[index].text
            link = f"https://www.youtube.com{video_title_links[index].get('href')}"
            views = (
                all_data[index]
                .findAll(
                    "span", "inline-metadata-item style-scope ytd-video-meta-block"
                )[0]
                .text
            )
            uploaded_time = (
                all_data[index]
                .findAll(
                    "span", "inline-metadata-item style-scope ytd-video-meta-block"
                )[1]
                .text
            )
            thumbnail_src = thumbnail[index].get("src")

            yt_dict = {
                "Url": link,
                "Thumbnail": thumbnail_src,
                "Title": title,
                "Views": views,
                "Posted": uploaded_time,
            }
            csv_data.append(yt_dict)
    except:
        driver.quit()
    finally:
        df = pd.DataFrame(csv_data)
        return df, yt_channel_name


st.header("Youtube Data Scrapper")

url = st.text_input("Enter Video Url:")

if url:
    if url.startswith("https://www.youtube.com/"):
        df, yt_channel_name = scrape_youtube_data(url)

        st.subheader(yt_channel_name)

        st.write(df, unsafe_allow_html=True)

        csv_file = df.to_csv(index=False)

        st.download_button(
            label="Download CSV",
            data=csv_file,
            file_name=f"{yt_channel_name.replace(' ','_')}.csv",
            mime="text/csv",
        )

    else:
        st.error("Please Enter Valid URL.")
