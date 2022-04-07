import argparse
import csv
import gzip
import os
import re
import shutil
from collections import defaultdict

import bz2file
import nlp2
import requests
from gensim.corpora.wikicorpus import extract_pages, filter_wiki
from nlp2 import get_dir_with_notexist_create, is_file_exist, create_new_dir_always, download_file, clean_all
from opencc import OpenCC
from tqdm import tqdm

from wikiext.utility.sql2csv import sql2csv


class WikiExt:
    wiki_pages = None

    def __init__(self, language_source, s2t=False):
        self.folder = get_dir_with_notexist_create('./source/')
        self.language_source = language_source
        self.download_address = "https://dumps.wikimedia.org/" + language_source + "/latest/"
        if s2t:
            self.cc = OpenCC('s2t')
            self.s2t = s2t
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
        if self.s2t:
            return self.cc.convert(d[0]).strip(), self.cc.convert(s).strip()
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

    def dump_entity(self, outfile, type="csv"):
        with open(outfile, 'w', encoding='utf-8') as output:
            if type == "csv":
                writer = csv.writer(output)
            for d in self._extract_article_onebyone():
                writer.writerow([d[0]])

    def dump_redirect_pair(self, outfile, type="csv"):
        with open(outfile, 'w', encoding='utf-8') as output:
            if type == "csv":
                writer = csv.writer(output)
            regex = r"\{\{(\w+)\}\}|\[\[(\w+)\]\]"
            for d in self._extract_article_onebyone():
                matches = re.finditer(regex, d[1], re.MULTILINE)
                for matchNum, match in enumerate(matches):
                    if match is not None and matchNum is not None:
                        groups = match.groups()
                        if groups[0] and matchNum == 0 and "#" not in groups[0]:
                            if type == "csv":
                                writer.writerow([d[0], groups[0]])
                            elif type == "dict":
                                output.write(d[0] + '\n')
                                output.write(groups[0] + '\n')

    def dump_articles(self, outfile, type="csv"):
        with open(outfile, 'w', encoding='utf-8') as output:
            if type == "csv":
                writer = csv.writer(output)
            for d in self._extract_article_onebyone():
                title, context = self._clean(d)
                context = clean_all(context)
                if type == "csv":
                    writer.writerow([title, context])
                elif type == "text":
                    output.write(title + " " + context)
                    output.write("\n")

    def dump_category(self, outfile, type="csv", must="", may=[""]):
        with open(outfile, 'w', encoding='utf-8') as output:
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

    def dump_langlink(self, outfile, type="csv"):
        with open(outfile, 'w', encoding='utf-8') as output:
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", type=str, default='zhwiki',
                        help="default:zhwiki, from https://dumps.wikimedia.org/backup-index-bydb.html")
    parser.add_argument("--dump", type=str, nargs='+', default=['all'], help="select what to extract",
                        choices=['entity', 'redirect_pair', 'langlink', 'category', 'articles', 'all'])
    parser.add_argument("--savedir", type=str, default="dump_result/", help="save dir, default /dump_result")
    parser.add_argument("--type", type=str, default="csv", choices=['csv', 'dict'])
    parser.add_argument("--s2t", action='store_true')

    arg = parser.parse_args()
    savedir = nlp2.get_dir_with_notexist_create(arg.savedir)
    wiki = WikiExt(language_source=arg.lang, s2t=arg.s2t)
    if 'entity' in arg.dump or 'all' in arg.dump:
        wiki.dump_entity(os.path.join(savedir, arg.lang + '_entity.' + arg.type), type=arg.type)
    if 'redirect_pair' in arg.dump or 'all' in arg.dump:
        wiki.dump_redirect_pair(os.path.join(savedir, arg.lang + '_redirect.' + arg.type), type=arg.type)
    if 'langlink' in arg.dump or 'all' in arg.dump:
        wiki.dump_langlink(os.path.join(savedir, arg.lang + '_translate.' + arg.type), type=arg.type)
    if 'category' in arg.dump or 'all' in arg.dump:
        wiki.dump_category(os.path.join(savedir, arg.lang + '_categories.' + arg.type), type=arg.type)
    if 'articles' in arg.dump or 'all' in arg.dump:
        wiki.dump_articles(os.path.join(savedir, arg.lang + '_wiki_article.' + arg.type), type=arg.type)


if __name__ == "__main__":
    main()
