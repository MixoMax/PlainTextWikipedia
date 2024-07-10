from dewiki_functions import process_file_text

wiki_xml_file = "./enwiki-latest-pages-articles-multistream.xml"
json_save_dir = "./enwiki_jsons2/"

if __name__ == '__main__':
    process_file_text(wiki_xml_file, json_save_dir)