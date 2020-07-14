from collections import defaultdict

from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from tqdm import tqdm
import bz2file
from nlp2 import *
import requests
import gzip
import shutil
from .sql2csv import *

from opencc import OpenCC

cc = OpenCC('s2t')


class WikiDump:
    wiki_pages = None

    def __init__(self, language_source, c2t=False):
        self.folder = get_dir_with_notexist_create('./source/')
        self.language_source = language_source
        self.download_address = "https://dumps.wikimedia.org/" + language_source + "/latest/"
        self.c2t = c2t
        request = requests.get(self.download_address)
        if request.status_code != 200:
            raise FileNotFoundError("source not found")

    def _clean(self, d):
        s = d[1]
        s = re.sub(':*{\|[\s\S]*?\|}', '', s)
        s = re.sub('<gallery>[\s\S]*?</gallery>', '', s)
        s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '', s)
        s = filter_wiki(s)
        s = re.sub('\* *\n|\'{2,}', '', s)
        s = re.sub('\n+', '\n', s)
        s = re.sub('\n[:;]|\n +', '\n', s)
        s = re.sub('(==+)', '\n', s)
        if self.c2t is True:
            return cc.convert(d[0]).strip(), cc.convert(s).strip()
        else:
            return d[0].strip(), s.strip()

    def _extract_article_onebyone(self):
        wiki_pages = extract_pages(bz2file.open(self.download_wiki_articles_dump()))
        counter = 0
        w = tqdm(wiki_pages, desc=u'get 0 article')
        for d in w:
            if not re.findall('^[a-zA-Z]+:', d[0]) and d[0] and not re.findall(u'^#', d[1]):
                yield d
                counter += 1
            if counter % 100 == 0:
                w.set_description(u'processed %s article' % counter)

    def check_outdated(self):
        version_address = self.download_address + self.language_source + "-latest-md5sums.txt"
        r = requests.get(version_address)
        version = r.text.split('\n')[0].split('  ')[1].split('-')[1]
        if not is_file_exist(self.folder + version):
            create_new_dir_always(self.folder)
            open(self.folder + version, 'w').close()
        print(self.folder + version)
        return not is_file_exist(self.folder + version)

    def download_wiki_langlink(self):
        self.check_outdated()
        down_result = download_file(
            self.download_address + self.language_source + "-latest-langlinks.sql.gz", self.folder)
        if down_result == "File not found":
            raise FileNotFoundError("source not found")

        unzip_result = down_result.replace(".gz", "")

        with gzip.open(down_result, 'r') as f_in, open(unzip_result, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        return unzip_result

    def download_wiki_articles_dump(self):
        self.check_outdated()
        down_result = download_file(
            self.download_address + self.language_source + "-latest-pages-articles-multistream.xml.bz2", self.folder)
        if down_result == "File not found":
            raise FileNotFoundError("source not found")
        return down_result

    def dump_redirect_pair(self, outfile, type="csv"):
        output = codecs.open(outfile, 'w', encoding='utf-8')
        if type == "csv":
            writer = csv.writer(output)
        regex = r"\[\[(.+)\]\]|\{\{(.+)\}\}"
        for d in self._extract_article_onebyone():
            matches = re.finditer(regex, d[1], re.MULTILINE)
            for matchNum, match in enumerate(matches):
                if match is not None and matchNum is not None:
                    groups = match.groups()
                    if groups[0] is not None and matchNum is 0 and "#" not in groups[0]:
                        if type == "csv":
                            writer.writerow([d[0], groups[0]])
                        elif type == "dict":
                            output.write(d[0] + '\n')
                            output.write(groups[0] + '\n')
        output.close()

    def dump_articles(self, outfile, type="csv"):
        output = codecs.open(outfile, 'w', encoding='utf-8')
        if type == "csv":
            writer = csv.writer(output)
        for d in self._extract_article_onebyone():
            title, context = self._clean(d)
            context = "\n".join(split_sentence_to_array(clean_httplink(context)))
            if type == "csv":
                writer.writerow([title, context])
            elif type == "text":
                output.write(title + " " + context)
                output.write("\n")

        output.close()

    def dump_category(self, outfile, type="csv", must="", may=[""]):
        output = codecs.open(outfile, 'w', encoding='utf-8')
        if type == "csv":
            writer = csv.writer(output)
        regex = r"\[\[Category:\w*\]\]"
        for d in self._extract_article_onebyone():
            matches = re.finditer(regex, d[1], re.MULTILINE)
            for matchNum, match in enumerate(matches):
                if match is not None and matchNum is not None:
                    key = match.group(0)
                    if type == "csv":
                        writer.writerow([d[0], key.replace("[[Category:", "").replace("]]", "")])
                    elif type == "dict":
                        output.write(d[0] + '\n')
                    # if len(must) < 1 or must in key:
                    #     if len(may) < 1 or key in may:
                    #         if type == "csv":
                    #             writer.writerow([d[0], key.replace("[[Category:", "").replace("]]", "")])
                    #         elif type == "dict":
                    #             output.write(d[0] + '\n')
        output.close()

    def dump_langlink(self, outfile, type="csv"):
        output = codecs.open(outfile, 'w', encoding='utf-8')
        jsondict = defaultdict(list)

        if type == "csv":
            writer = csv.writer(output)
        infile = self.download_wiki_langlink()
        print("loop all lang")
        for rows in sql2csv(infile):
            for row in rows:
                if type == "csv":
                    writer.writerow(row)
                elif type == "dict":
                    jsondict[row[1]].append(row)

        # if type == "dict":
        #     targetid = []
        #     print("filter main lang")
        #     for key in main_lang:
        #         for i in jsondict[key]:
        #             if i[0] not in targetid:
        #                 targetid.append(i[0])
        #     print("write result")
        #     for key in filter_lang:
        #         for i in jsondict[key]:
        #             if i[0] in targetid and len(i[2]) > 1:
        #                 output.write(i[2] + '\n')
        output.close()
