from xlrd import open_workbook
from xlrd import sheet
import os

from comicmodels.models import ProjectLink


    
class ProjectExcelReader(object):
    """ Records on challenges from grand-challenge.org are kept in an xls file
    This had the advantages of easy copy-pasting and quick simple and flexible
    editing and statistics. This class reads the grand-challenge xls file and
    renders html for each challenge found.
    
    TODO: This class combines functionality which should probably be separate:
    read xls, render projectlink to html etc. Split later.
    """

    def __init__(self,path,sheetname):
        self.path = path 
        self.sheetname = sheetname
        
        
    def write_link_html(self,path=""):
        items = self.get_excel_items(self.sheet)
        links = self.get_project_links().encode("utf-8")

        if path == "":
            path = "D:/temp/links.html"
        
        f = open(path,"w")
        print ("* wrote HTML for all projects to "+path)
        f.write(links)
        f.close()
    
    

    def get_project_links(self):
        """ Read excel file and with challenge listings and return an array of
        projectlinks describing each 
        """
        
        book = open_workbook(self.path)
        sheet = book.sheet_by_name(self.sheetname)
        
        html = ""
        items = self.get_excel_items(sheet)
        projectlinks = []
        
        for item in items:
            if item["abreviation"] != "":
                projectlink = ProjectLink(item)
                projectlinks.append(projectlink)
                        
        book.unload_sheet(self.sheetname)    
        return projectlinks
        
    
    def get_project_links_html(self):
        """ Read excel file and output html to show all challenge links
        listed there 
        """
        
        html = ""
        projectlinks = self.get_project_links()
            
        for projectlink in projectlinks:
            html += projectlink.render_to_html()
        
        return html

    
    def get_excel_items(self,sheet):
        """ Treat each row in excel sheet as an item. First row in sheet should
        contain column headers. Each item returned is an object that has a field
        for each column.
        
        """    
        items = []

        for row in range(1,sheet.nrows): #skip first row as those are titles        
            items.append(self.get_excel_item(sheet,row))
        return items
        
        
    def get_excel_item(self,sheet,row):
        """
        """
        item = {}
        
        col_titles = sheet.row_values(0,0)
        col_values = sheet.row_values(row,0)
        for (title,value) in zip(col_titles,col_values):
           
            if title != "":
                item[title] = value

        
        return item






    
