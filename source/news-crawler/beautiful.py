from bs4 import BeautifulSoup
import html2text

soup = BeautifulSoup(open("wash.html"), 'lxml')
#soup = soup.prettify()


container =  soup.find_all(_class="zn-body__paragraph")

print html2text.html2text(str(container))