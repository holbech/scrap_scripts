from bs4 import BeautifulSoup
import urllib2

if __name__ == "__main__":
    all_sets = BeautifulSoup(urllib2.urlopen('http://www.wizards.com/Magic/tcg/article.aspx?x=mtg/tcg/products/allproducts'))
    