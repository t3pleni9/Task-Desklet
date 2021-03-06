#!/usr/bin/env python

 
import pygtk
pygtk.require('2.0')
import gtk
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom
import getopt
import sys
import string
import time
import datetime


class GCalendarClient:   

    def __init__(self, email, password):
        """Creates a CalendarService and provides ClientLogin auth details to it.
        The email and password are required arguments for ClientLogin.  The
        CalendarService automatically sets the service to be 'cl', as is
        appropriate for calendar.  The 'source' defined below is an arbitrary
        string, but should be used to reference your name or the name of your
        organization, the app name and version, with '-' between each of the three
        values.  The account_type is specified to authenticate either
        Google Accounts or Google Apps accounts.  See gdata.service or
        http://code.google.com/apis/accounts/AuthForInstalledApps.html for more
        info on ClientLogin.  NOTE: ClientLogin should only be used for installed
        applications and not for multi-user web applications."""

        self.cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python_Sample-1.0')
        self.cal_client.ClientLogin(email, password, self.cal_client.source);
        self._weekPre = ['Mon', 'Tue','Wed','Thu','Fri', 'Sat ','Sun']
    def DateRangeQuery(self, start_date='2013-10-05', end_date='2013-10-06'):
        """Retrieves events from the server which occur during the specified date
        range.  This uses the CalendarEventQuery class to generate the URL which is
        used to retrieve the feed.  For more information on valid query parameters,
        see: http://code.google.com/apis/calendar/reference.html#Parameters"""
        event = []        
        query = gdata.calendar.client.CalendarEventQuery(start_min=start_date, start_max=end_date)
        feed = self.cal_client.GetCalendarEventFeed(q=query)
        for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
            if an_event.title.text is not None:
                for a_when in an_event.when:
                    event.append((an_event.title.text,a_when.start))                    
        return event
    def getWeek(self,year, week):
	'''Returns the start date and end date of the given week number for the given year, 
	works for weeks greater than 52 ( gives the date of next year)'''
        d = datetime.date(year,1,1)
        d = d - datetime.timedelta(d.weekday()+1)
        dlt = datetime.timedelta(days = (week-1)*7)
        return d + dlt,  d + dlt + datetime.timedelta(days=6)

    def Today(self):
	'''Return events for the today'''
        eventList =  self.DateRangeQuery(start_date=datetime.datetime.now().date().__str__(), end_date=(datetime.datetime.now().date() + datetime.timedelta(days=1)).__str__())
        return [('  ',x[0].__str__()) for x in eventList]

    def Tomorrow(self):        
	'''Return events for tomorrow'''
        eventList =  self.DateRangeQuery(start_date=(datetime.datetime.now().date() + datetime.timedelta(days=1)).__str__(), end_date=(datetime.datetime.now().date() + datetime.timedelta(days=2)).__str__())
        print eventList
        return [('  ',x[0].__str__()) for x in eventList]

    def ThisWeek(self):
	'''Returns the list of events to happen in the current week'''
        year = datetime.datetime.now().date().year
        weekNumber = datetime.datetime.now().date().isocalendar()[1]
        endDate = self.getWeek(year, weekNumber)[1]
        eventList =  self.DateRangeQuery(start_date=(datetime.datetime.now().date() + datetime.timedelta(days=2)).__str__(), end_date=endDate.__str__())
        try:        	
        	returnList =  [(self._weekPre[time.strptime(x[1].split('.')[0],"%Y-%m-%dT%H:%M:%S").tm_wday],x[0], time.strptime(x[1].split('.')[0],"%Y-%m-%dT%H:%M:%S").tm_wday) for x in eventList]
        except ValueError:		
    	    returnList =  [(self._weekPre[time.strptime(x[1].split('.')[0],"%Y-%m-%d").tm_wday],x[0],time.strptime(x[1].split('.')[0],"%Y-%m-%d").tm_wday) for x in eventList]
	    returnList.sort(lambda x, y : int(x[2]) - int(y[2]))
	    return returnList

    def NextWeek(self):
	'''Return the list of events to Happen in the comming week'''
        year = datetime.datetime.now().date().year
        weekNumber = datetime.datetime.now().date().isocalendar()[1]
        (startDate, endDate) = self.getWeek(year, weekNumber+1)
        if((datetime.datetime.now().date() + datetime.timedelta(days=1)) == startDate):
            startDate = startDate + datetime.timedelta(days=1) 

        eventList =  self.DateRangeQuery(start_date=startDate.__str__(), end_date=endDate.__str__())
        try:        	
    	    returnList =  [(self._weekPre[time.strptime(x[1].split('.')[0],"%Y-%m-%dT%H:%M:%S").tm_wday],x[0], time.strptime(x[1].split('.')[0],"%Y-%m-%dT%H:%M:%S").tm_wday) for x in eventList]
        except ValueError:		
    	    returnList =  [(self._weekPre[time.strptime(x[1].split('.')[0],"%Y-%m-%d").tm_wday],x[0],time.strptime(x[1].split('.')[0],"%Y-%m-%d").tm_wday) for x in eventList]
	    returnList.sort(lambda x, y : int(x[2]) - int(y[2]))
	    return returnList

class GTask:
    '''Window'''
    
    def insertTree(self, nodeName, nodeList):
        buffer = '<span foreground="lightgray" font="courier" size="large"><b>%s</b></span>' % nodeName
       
        nodeTree = self.treestore.append(None, [buffer])   
        self.rowCount += 1
        if len(nodeList) == 0:
            self.treestore.append(nodeTree, ['No Schedules'])
        else :
            for child in nodeList:
                if child is not None:
                    if child[0] == 'Sun':
                        colr = 'red'
                    elif child[0] == 'Sat':
                        colr = 'blue'
                    else :
                        colr = 'green'
                    buffer = '<span foreground="%s" size="x-small" font="monospace"><b>%s</b></span>          <span foreground="lightgray" size="small">%s</span>' % (colr, child[0],child[1])
                    self.treestore.append(nodeTree, [buffer])
                    self.rowCount += 1
                    
    def insertEmptyRow(self):
        print self.rowCount
        if self.rowCount < 11:
            self.window.set_size_request(500, 300)
            while self.rowCount < 11:
                nodeTree = self.treestore.append(None, [''])   
                self.rowCount += 1 
        elif self.rowCount < 17:
            self.window.set_size_request(500, 400)        
            while self.rowCount < 17:
                nodeTree = self.treestore.append(None, [''])   
                self.rowCount += 1  
        else :
            self.window.set_size_request(500, 500) 
    def destroy(self, widget):
        gtk.main_quit()

    def __init__(self, user , pw):
        # Create a new dialog window for the scrolled window to be
        # packed into. 
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_title("ScrolledWindow example")
        self.window.set_border_width(0)
        self.window.set_size_request(400, 400)
        self.window.set_decorated(False)
        self.window.set_opacity(0.8)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.window.move(800, 150)
        self.window.set_keep_below(True)

        self.uname = user
        self.pwd = pw
        

        # create a new scrolled window.
        scrolled_window = gtk.ScrolledWindow()  
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)      
        scrolled_window.freeze_child_notify()

        # the policy is one of POLICY AUTOMATIC, or POLICY_ALWAYS.
        # POLICY_AUTOMATIC will automatically decide whether you need
        # scrollbars, whereas POLICY_ALWAYS will always leave the scrollbars
        # there. The first one is the horizontal scrollbar, the second, the
        # vertical.
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # The dialog window is created with a vbox packed into it.
        #window.vbox.pack_start(scrolled_window, True, True, 0)
        scrolled_window.show()
    
        self.treestore = gtk.TreeStore(str)
        self.cell = gtk.CellRendererText()
        self.cell.set_property('cell-background', 'black')
        cal = GCalendarClient(self.uname,self.pwd )
        self.rowCount = 0
        self.insertTree('Today', cal.Today())
        self.insertTree('Tomorrow', cal.Tomorrow())

        weekday = (datetime.datetime.now().date() + datetime.timedelta(days=1)).weekday()
        if weekday < 5:
            self.insertTree('This Week', cal.ThisWeek())
        self.insertTree('Next Week', cal.NextWeek())
        self.insertEmptyRow()


        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn()
        self.tvcolumn.set_clickable(False)

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'markup', 0)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        self.treeview.set_show_expanders(False)
        self.treeview.expand_all()
        self.treeview.set_level_indentation(10)
        self.treeview.set_headers_visible(False)
        self.treeview.show()
        #self.treeview.set_state(gtk.STATE_INSENSITIVE)

        scrolled_window.add(self.treeview)
        self.window.add(scrolled_window)
        #table.show()

        # this simply creates a grid of toggle buttons on the table
        # to demonstrate the scrolled window.
        
        # Add a "close" button to the bottom of the dialog
        #button = gtk.Button("close")
        #button.connect_object("clicked", self.destroy, window)

        # this makes it so the button is the default.
        #button.set_flags(gtk.CAN_DEFAULT)
        #window.action_area.pack_start( button, True, True, 0)

        # This grabs this button to be the default button. Simply hitting
        # the "Enter" key will cause this button to activate.
        #button.grab_default()
        #button.show()
        self.window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw="])
    except getopt.error, msg:
        print ('python calendarExample.py --user [username] --pw [password] ')
        sys.exit(2)

    user = ''
    pw = ''  

    # Process options
    for o, a in opts:
        if o == "--user":
            user = a
        elif o == "--pw":
            pw = a    

    if user == '' or pw == '':
        print ('python calendarExample.py --user [username] --pw [password] ')
        sys.exit(2)
    

    gtask = GTask(user, pw)


    main()
