from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time


from citation.util_error_handling import trace_error

url = None
driver = None
wait = None

def click_show_more_btn():
    while True:
    	# click on show more button -- multiple time until it is disabled
        try:
            button = wait.until(EC.visibility_of_element_located((By.XPATH,'//*[contains(@id,"gsc_bpf_more")]/button')))
            button.click()
            
        except Exception:
        	break

def find_all_anchors(table_selector='#gsc_a_t', anchor_selector="tbody tr td a.gsc_a_at"):
    for table in wait.until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, table_selector)
            )
        ):
        # find all anchors
        anchors = table.find_elements(By.CSS_SELECTOR, anchor_selector)
        # print(anchors)
        return anchors

def get_article_popup_data(popup_article_body):
    article_data = {}
    title = popup_article_body.find_element(By.CSS_SELECTOR, ".gsc_vcd_title_link")
    # print("Popup title:", title.text)
    article_data["title"] = title.text

    all_data_rows = popup_article_body.find_elements(By.CSS_SELECTOR, "#gsc_vcd_table .gs_scl")
    # print("\n first data_row text : ", all_data_rows[0].text)

    for row in all_data_rows:
        field_name = row.find_element(By.CSS_SELECTOR, ".gsc_vcd_field")
        field_value = row.find_element(By.CSS_SELECTOR, ".gsc_vcd_value")

        # print("Field name : ", field_name.text)
        # print("Field value:", field_value.text)

        field_data = {
            str(field_name.text.strip()): str(field_value.text.strip())
        }

        article_data.update(field_data)

    if 'Total citations' in article_data:
        tot_citations = article_data["Total citations"]
        # modify value
        first_number = re.search(r'\d+', tot_citations).group()
        article_data["Total citations"] = first_number

    return article_data

def get_anchors_data(anchors):
    all_article_data = []
    for anchor in anchors:
        # print(anchor.text)
        anchor.click()

        try:
            popup_article_body = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '#gsc_ocd_view')
                )
            )
            # print("Popup data:", popup_article_info.text)

            article_data = get_article_popup_data(popup_article_body)
            all_article_data.append(
                article_data
            )

            time.sleep(5)

            # close popup
            ele_close = driver.find_element(By.CSS_SELECTOR, "#gs_md_cita-d-x")
            ele_close.click()

            time.sleep(10)
            
        except Exception:
            error = trace_error()
            print(error)

        # break

    return all_article_data


def start_extarcting_articles(url_link):
    global url
    global driver
    global wait

    url = url_link

    driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver")

    driver.get(url)

    wait = WebDriverWait(driver, 10)

    anchors = find_all_anchors()
    all_article_data = get_anchors_data(anchors)

    driver.close()

    return all_article_data

def main():
    import pandas as pd

    url_link = 'https://scholar.google.co.in/citations?user=IrlPkbMAAAAJ&hl=en"'
    all_article_data = start_extarcting_articles(url_link)
    print(all_article_data)


    df = pd.DataFrame.from_dict(all_article_data)

    with pd.ExcelWriter('output.xlsx') as writer:
        df.to_excel(writer, sheet_name='Articles')
        # df2.to_excel(writer, sheet_name='Sheet_name_2')


if __name__ == "__main__":
    main()
    driver.quit()