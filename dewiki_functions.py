from threading import Thread
import json
import time
import datetime
from html2text import html2text as htt
import wikitextparser as wtp


def dewiki(text):
    text = wtp.parse(text).plain_text()  # wiki to plaintext 
    text = htt(text)  # remove any HTML
    text = text.replace('\n',' ')  # replace newlines
    text = text.strip()  # remove leading/trailing whitespace
    return text


def analyze_chunk(text):
    try:
        if '<redirect title="' in text:  # this is not the main article
            return None
        if '(disambiguation)' in text:  # this is not an article
            return None
        else:
            title = text.split('<title>')[1].split('</title>')[0]
            title = htt(title)
            if ':' in title:  # most articles with : in them are not articles we care about
                return None
        serial = text.split('<id>')[1].split('</id>')[0]
        content = text.split('</text')[0].split('<text')[1].split('>', maxsplit=1)[1]
        content = dewiki(content)
        return {'title': title.strip(), 'text': content.strip(), 'id': serial.strip()}
    except Exception as oops:
        print(oops)
        return None


def save_article(article, savedir):
    doc = analyze_chunk(article)
    if doc:
        filename = doc['id'] + '.json'
        with open(savedir + filename, 'w', encoding='utf-8') as outfile:
            json.dump(doc, outfile, sort_keys=True, indent=1, ensure_ascii=False)



estimated_n_articles = 6_843_803
def process_file_text(filename, savedir):
    article_lines = []
    with open(filename, 'r', encoding='utf-8') as infile:
        
        timestamps = []

        for line in infile:
            if '<page>' in line:
                article_lines = [line]
            elif '</page>' in line:  # end of article
                article = " ".join(article_lines)
                Thread(target=save_article, args=(article, savedir)).start()
                timestamps.append(time.time())

                n_articles_processed = len(timestamps)

                n_rolling_avg = 100
                if n_articles_processed > n_rolling_avg and n_articles_processed % 100 == 0:
                    last_10 = timestamps[-n_rolling_avg:]
                    avg_time = (last_10[-1] - last_10[0]) / n_rolling_avg
                    time_remaining = (estimated_n_articles - n_articles_processed) * avg_time
                    time_remaining = max(time_remaining, 0) # negitve time will throw an error
                    time_remaining_str = datetime.datetime.fromtimestamp(time_remaining).strftime('%H:%M:%S')

                    percentage = n_articles_processed / estimated_n_articles * 100
                    
                    _str = f'{n_articles_processed} / {estimated_n_articles} articles processed ({percentage:.2f}%) ETA: {time_remaining_str}'
                    print(_str, end='\r')

            else:
                article_lines.append(line)