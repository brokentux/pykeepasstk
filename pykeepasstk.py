#!/usr/bin/env python3
import os
from pykeepass import PyKeePass
from tkinter import Tk, Canvas, Frame, Scrollbar, Grid, Pack, Label, Entry, Button, PhotoImage, Menu, StringVar, Text
from tkinter import filedialog
import uuid
import datetime
import sys

# Create main Window
root = Tk()
root.minsize(700, 400)  # width, height
root.geometry("300x300")
root.eval('tk::PlaceWindow . center')
root.title('PykeepassTK')

# Open database (browse) and show associated widget
def openDatabase():
	
    # Check credentials
    def setDatabase(filename, dbPasswordEntry, dbKeyEntry):
     		
        # Check that the password field isn't empty
        if not dbPasswordEntry.get():
            dbPasswordError.config(text="Password field cannot be empty")
            dbPasswordError.grid(row=4, column=1, sticky='ew')
        else :
            # Try to open the database, on success, unpack widget and display list Keepass group
            try:
                global KP
                
                if not dbKeyEntry.get():
                    KP = PyKeePass(filename, password=dbPasswordEntry.get())
                else:
                    KP = PyKeePass(filename, password=dbPasswordEntry.get(), keyfile=dbKeyEntry.get())

                # Reset Groups Frame
                dbFrame.pack_forget()

                # Delete all previous entries label
                for child in dbFrame.winfo_children():
                    child.destroy()
        
                # Display utils bar (search)
                utilsFrame.pack(fill='x')
                
                # Display groups list
                getGroups()
                # Display default entries list (root group)
                gUuid = str(KP.root_group.uuid)
                getEntries(gUuid)
                    
            except Exception as error:
                dbPasswordError.config(text=error)
                dbPasswordError.grid(row=4, column=1, sticky='ew')

    # Forget Group Canvas / Frame / Scrollbar (if a database was already opened)
    dbFrame.pack_forget()
    rootGroupsFrame.pack_forget()
    rootEntriesFrame.pack_forget()
    utilsFrame.pack_forget()
    groupsCanvas.pack_forget()
    groupsFrame.pack_forget()
    groupsScrollbarY.pack_forget()
    groupsScrollbarX.pack_forget()
    
    # Delete all widget inside the util frame
    for child in utilsFrame.winfo_children():
        child.destroy()
            
    # Delete all widget inside the group frame
    for child in groupsFrame.winfo_children():
        child.destroy()

    # Forget the Canvas / Frame / Scrollbar entries (if a database was already opened)
    entriesCanvas.pack_forget()
    entriesFrame.pack_forget()
    entriesScrollbarX.pack_forget()
    entriesScrollbarY.pack_forget()
    
    # Delete all widget inside the entries frame
    for child in entriesFrame.winfo_children():
        child.destroy()
          
    filename = filedialog.askopenfilename(initialdir = os.getcwd(), title="Select a Database", filetypes = (("Keepassx DB", "*.kdbx*"),("all files","*.*")))

    if filename:
		
        def selectKey(self):
           keyPath = filedialog.askopenfilename(initialdir = os.getcwd(), title="Select a Key")
           dbKeyString.set(keyPath)

        dbFrame.pack(side='left', fill='both', expand=True)
        
        Label(dbFrame, text="Enter the credential for " + filename, pady=20).grid(row=0, column=1, sticky='ew')
        
        dbPasswordLabel = Label(dbFrame, text="Password", anchor='w')
        dbPasswordLabel.grid(row=1, column=0, sticky='w')   
        dbPasswordEntry = Entry(dbFrame, show="*", bd=1)
        dbPasswordEntry.grid(row=1, column=1, sticky='ew')
        
        dbKeyLabel = Label(dbFrame, text="Key", anchor='w')
        dbKeyLabel.grid(row=2, column=0, sticky='w')
        dbKeyString = StringVar()
        dbKeyEntry = Entry(dbFrame, textvariable=dbKeyString, bd=1)
        dbKeyEntry.grid(row=2, column=1, sticky='ew')      
        dbKeyEntry.bind("<1>", selectKey)
        
        dbPasswordButton = Button(dbFrame, text="Send", command=lambda:setDatabase(filename, dbPasswordEntry, dbKeyEntry))
        dbPasswordButton.grid(row=3, column=1, sticky='e')
        
        dbPasswordError = Label(dbFrame, text="")
        
        dbFrame.grid_columnconfigure(1, weight=1)

# List groups
def getGroups():
    
    # Reset Groups Frame
    groupsFrame.pack_forget()

    # Delete all previous entries label
    for child in groupsFrame.winfo_children():
        child.destroy()
        
    rootGroupsFrame.pack(side="left", fill="y")
    
    # Display Group Frame/Canvas/Scrollbar
    groupsCanvas.configure(yscrollcommand=groupsScrollbarY.set)
    groupsCanvas.configure(xscrollcommand=groupsScrollbarX.set)
    groupsScrollbarX.pack(side="bottom", fill="x")
    groupsCanvas.pack(side="left", fill="both", expand=False)
    groupsScrollbarY.pack(side="left", fill="y")

    # Create the canvas window
    groupsCanvas.create_window((4,4), window=groupsFrame, anchor="nw")

    # Bind the frame to the canvas
    groupsFrame.bind("<Configure>", lambda event, canvas=entriesCanvas: onFrameConfigure(groupsCanvas))
    
    # Right click menu (add entry, edit group name)
    def openMenuGroup(self):
        menuGroup = Menu(root, tearoff=0)
        menuGroup.add_command(label="Add entry", command=lambda:addEntry(self.widget))
        menuGroup.add_command(label="Add group", command=lambda:addGroup(self.widget))
        menuGroup.add_command(label="Edit group", command=lambda:editGroup(self.widget))
        menuGroup.add_command(label="Delete group", command=lambda:delGroup(self.widget))
        menuGroup.add_command(label="Close")
        menuGroup.post(self.x_root, self.y_root)
                                          
    # Display root group first
    kpGroup =  Label(groupsFrame, text=KP.root_group.name, anchor="w", pady=2, background="white", cursor="hand2")
    kpGroup.uuid = str(KP.root_group.uuid)
    kpGroup.name = KP.root_group.name
    #
    # Quick reminder why the group uuid is pass as an argument instead of the object widget itself :
    # saveEntry() need the group uuid in order refresh the entries list (after modification), saveEntry is pass as an object
    # with his own property uuid
    #
    kpGroup.bind("<Button-1>", lambda event, gUuid=kpGroup.uuid: getEntries(gUuid))
    kpGroup.bind("<Button-3>", openMenuGroup)
    kpGroup.pack(fill="x", expand=False, padx=5)
             
    # Display the group/subgroups as Tree view style
    def tree(group, level=0):
        for g in group.subgroups:
            # Add 10 to padx on subgroups
            subpadx = 10 * (level - 1)
            # Manage empty group/subgroup name display 
            if(level and g.name):
                textLabel = "|-" + g.name
            elif(level and g.name is None):
                textLabel = "|-" + "***EmptyGroupName***"
            elif(level == 0 and g.name):
                textLabel = g.name
            else:
                textLabel = "***EmptyGroupName***"
            kpGroup =  Label(groupsFrame, text=textLabel, anchor="w", padx=subpadx, pady=1, background="white", cursor="hand2")
            kpGroup.uuid = str(g.uuid)
            kpGroup.name = g.name
            # See comment Quick reminder 
            kpGroup.bind("<Button-1>", lambda event, gUuid=kpGroup.uuid: getEntries(gUuid))
            kpGroup.bind("<Button-3>", openMenuGroup)
            kpGroup.pack(fill="x", expand=False, padx=5)
            tree(g, level + 1)

    tree(KP.root_group)

def addEntry(self):
	
    def save(titleString, usernameString, passwordString, urlString, noteEntryField, gUuid):

        # Add entry to targeted group      
        targetGroup = KP.find_groups(uuid=uuid.UUID(gUuid), first=True)
        
        # force_creation=True -> Otherwise won't allow 2 entry with same value
        KP.add_entry(targetGroup, titleString.get(), usernameString.get(), passwordString.get(), urlString.get(), noteEntryField.get("1.0","end-1c"), force_creation=True)
        
        # Save database
        KP.save()
        
        getEntries(gUuid)
            
        # Close window
        entryWindow.destroy()

    entryWindow = Tk()
    entryWindow.geometry("400x300")
    entryWindow.eval('tk::PlaceWindow . center')

    # Get Group uuid
    gUuid = self.uuid

    entryWindow.title(self.name)
    entryWindow.config(background="white")
    
    # Entry title label + field
    titleEntryLabel = Label(entryWindow, text="Title :", anchor='w', width=10, padx=3, background="white")
    titleEntryLabel.grid(row=0, column=0, sticky='nw')
    titleString = StringVar(entryWindow, "")
    titleEntryField = Entry(entryWindow, textvariable=titleString)
    titleEntryField.grid(row=0, column=1, sticky='ew')

    # Entry username label + field
    usernameEntryLabel = Label(entryWindow, text="Username :", anchor='w', width=10, padx=3, background="white")
    usernameEntryLabel.grid(row=1, column=0, sticky='nw')
    usernameString = StringVar(entryWindow, "")
    usernameEntryField = Entry(entryWindow, textvariable=usernameString, bd=1)
    usernameEntryField.grid(row=1, column=1, sticky='ew')

    # Entry password label + field
    passwordEntryLabel = Label(entryWindow, text="Password :", anchor='w', width=10, padx=3, background="white")
    passwordEntryLabel.grid(row=2, column=0, sticky='nw')
    passwordString = StringVar(entryWindow, "")
    passwordEntryField = Entry(entryWindow, textvariable=passwordString, bd=1)
    passwordEntryField.grid(row=2, column=1, sticky='ew')

    # Entry url label + field
    urlEntryLabel = Label(entryWindow, text="Url :", anchor='w', width=10, padx=3, background="white")
    urlEntryLabel.grid(row=3, column=0, sticky='nw')
    urlString = StringVar(entryWindow, "")
    urlEntryField = Entry(entryWindow, textvariable=urlString, bd=1)
    urlEntryField.grid(row=3, column=1, sticky='ew')
    
    # Entry Note label + field
    noteEntryLabel = Label(entryWindow, text="Note :", anchor='w', width=10, padx=3, background="white")
    noteEntryLabel.grid(row=4, column=0, sticky='nw')
    noteString = StringVar(entryWindow, "")
    noteEntryField = Text(entryWindow, height=14, border=1)
    noteEntryField.insert("1.0", noteString.get())
    noteEntryField.grid(row=4, column=1, sticky='nsew')

    # Save button
    buttonSaveEntry = Button(entryWindow, text="Save", command=lambda:save(titleString, usernameString, passwordString, urlString, noteEntryField, gUuid))
    buttonSaveEntry.grid(row=5, column=1, sticky='ne')

    # Fill field
    entryWindow.grid_columnconfigure(1, weight=1)
    entryWindow.grid_rowconfigure(4, weight=1)

def addGroup(self):

    def save(self, addGroupNameString):
        
        # Need the fetch with find_groups where the new group will be inserted
        gUuid = uuid.UUID(self.uuid)
        getGroup = KP.find_groups(uuid=gUuid, first=True)
        
        # Add group, save database and refresh groups list
        getGroup.touch(modify=True)
        KP.add_group(getGroup, addGroupNameString.get())      
        KP.save()
        KP.reload()
        getGroups()
        
        # Close window on save
        addGroupNameWindow.destroy()

    # Add group Window
    addGroupNameWindow = Tk()
    addGroupNameWindow.eval('tk::PlaceWindow . center')
    addGroupNameWindow.title("Add " + self.name if self.name else "***EmptyGroupName***")

    # Add group widget
    addGroupNameString = StringVar(addGroupNameWindow, "")
    addGroupNameField = Entry(addGroupNameWindow, width=50, textvariable=addGroupNameString, bd=1)
    addGroupNameField.pack(fill='x')

    # Save button
    buttonAddGroupName = Button(addGroupNameWindow, text="Save", command=lambda:save(self, addGroupNameString))
    buttonAddGroupName.pack()
    
def delGroup(self):

    def delete(self):
        
        # Need the fetch with find_groups where the new group will be inserted
        gUuid = uuid.UUID(self.uuid)
        getGroup = KP.find_groups(uuid=gUuid, first=True)
        
        # Check if the group isn't the root group
        if getGroup.is_root_group is False:		
            # Del group, save database, refresh groups list and resetEntriesFrame
            KP.delete_group(getGroup)      
            KP.save()
            getGroups()
            resetEntriesFrame()
            
            # Close window on save
            delGroupNameWindow.destroy()      
        else:
            delGroupNameLabel.config(text="You cannot delete the root group")
            buttonDelGroupName.pack_forget()

    # Add group Window
    delGroupNameWindow = Tk()
    delGroupNameWindow.eval('tk::PlaceWindow . center')
    delGroupNameWindow.title("Delete " + self.name if self.name else "***EmptyGroupName***")

    # Confirm delete
    delGroupNameLabel = Label(delGroupNameWindow, text="Delete " + self.name + " are you sure ?")
    delGroupNameLabel.pack(fill='x')

    # Save button
    buttonDelGroupName = Button(delGroupNameWindow, text="Delete", command=lambda:delete(self))
    buttonDelGroupName.pack()
	
def editGroup(self):

    def save(self, editGroupNameString):
        
        # Need the fetch with find_groups in order to update the group name
        gUuid = uuid.UUID(self.uuid)
        getGroup = KP.find_groups(uuid=gUuid, first=True)
        
        # Save group name, database and refresh groups list
        getGroup.name = editGroupNameString.get()      
        KP.save()
        getGroups()
        
        # Close window on save
        editGroupNameWindow.destroy()

    # Edit group Window
    editGroupNameWindow = Tk()
    #editGroupNameWindow.geometry("400x200")
    editGroupNameWindow.eval('tk::PlaceWindow . center')
    editGroupNameWindow.title("Edit " + self.name if self.name else "***EmptyGroupName***")

    # Edit group widget
    editGroupNameString = StringVar(editGroupNameWindow, self.name)
    editGroupNameField = Entry(editGroupNameWindow, width=50, textvariable=editGroupNameString, bd=1)
    editGroupNameField.pack(fill='x')

    # Save button
    buttonSaveGroupName = Button(editGroupNameWindow, text="Save", command=lambda:save(self, editGroupNameString))
    buttonSaveGroupName.pack()
    
def resetEntriesFrame():
    # Reset Entries Frame
    entriesFrame.pack_forget()

    # Delete all previous entries label
    for child in entriesFrame.winfo_children():
        child.destroy()
  
    rootEntriesFrame.pack(side="left", fill="both", expand=True)

    # Display entries Frame/Canvas/Scrollbar
    entriesScrollbarX.pack(side="bottom", fill="x")
    entriesCanvas.configure(xscrollcommand=entriesScrollbarX.set)
    entriesCanvas.pack(side="left", fill="both", expand=True)
    entriesScrollbarY.pack(side="left", fill="y")
    entriesCanvas.configure(yscrollcommand=entriesScrollbarY.set)

    # Create the canvas window
    entriesCanvas.create_window((4,4), window=entriesFrame, anchor="nw")

    # Bind the frame to the canvas
    entriesFrame.bind("<Configure>", lambda event, canvas=entriesCanvas: onFrameConfigure(entriesCanvas))
    
def resetUtilsBar():
	# Hide cancel icons
    for child in utilsFrame.winfo_children():
        child.destroy()
    
    # Display search icons
    searchButton = Button(utilsFrame, image=searchIcon, background="white", highlightthickness=0, border=0, command=searchEntries)
    searchButton.pack(fill='none', anchor='nw')
    	
# Search entries
def searchEntries():
    
    # Reset entries frame list
    resetEntriesFrame()
    
    # Hide search icons
    for child in utilsFrame.winfo_children():
        child.destroy()
        
    def searchOnInput(searchStringVar): 
	
        resetEntriesFrame()
        
        # Display Label Title, Username, Url
        Label(entriesFrame, text="Title", background="#edfaca").grid(row=0, column=0, sticky='w')
        Label(entriesFrame, text="Username", background="#edfaca").grid(row=0, column=1, sticky='w', padx=7)
        Label(entriesFrame, text="URL", background="#edfaca").grid(row=0, column=2, sticky='w', padx=7)
    
		# default row incrementation
        nr = 1
        
        # Display all entries if search input is empty
        if not searchStringVar.get():
            for i in KP.entries:
                entriesTitleLabel = Label(entriesFrame, text=(str(i.title)), width=27, anchor="w", background="white", cursor="hand2")
                entriesUsernameLabel = Label(entriesFrame, text=(str(i.username)), width=27, anchor="w", background="white")
                entriesUrlLabel = Label(entriesFrame, text=(str(i.url)), anchor="w", background="white")
                entriesTitleLabel.uuid = str(i.uuid)
                entriesTitleLabel.guuid = "search"
                entriesTitleLabel.bind("<Button-1>", getEntry)
                entriesTitleLabel.grid(row=nr, column=0, sticky='w')
                entriesUsernameLabel.grid(row=nr, column=1, sticky='w', padx=7)
                entriesUrlLabel.grid(row=nr, column=2, sticky='w', padx=7)
                # row incrementation
                nr = nr + 1
                
        # Otherwise, search by title and username
        else:
            searchTitle = KP.find_entries(title=".*" + searchStringVar.get() + ".*", regex=True, flags='i')
            searchUsername = KP.find_entries(username=".*" + searchStringVar.get() + ".*", regex=True, flags='i')
           
            # Remove double entries
            searchJoin = list(set(searchTitle) | set(searchUsername))
            
            for i in searchJoin:
                entriesTitleLabel = Label(entriesFrame, text=(str(i.title)), width=27, anchor="w", background="white", cursor="hand2")
                entriesUsernameLabel = Label(entriesFrame, text=(str(i.username)), width=27, anchor="w", background="white")
                entriesUrlLabel = Label(entriesFrame, text=(str(i.url)), anchor="w", background="white")
                entriesTitleLabel.uuid = str(i.uuid)
                entriesTitleLabel.guuid = "search"
                entriesTitleLabel.bind("<Button-1>", getEntry)
                entriesTitleLabel.grid(row=nr, column=0, sticky='w')
                entriesUsernameLabel.grid(row=nr, column=1, sticky='w', padx=7)
                entriesUrlLabel.grid(row=nr, column=2, sticky='w', padx=7)
                # row incrementation
                nr = nr + 1 
       
    # Display cancel icons and Search field
    cancelButton = Button(utilsFrame, image=cancelIcon, background="white", highlightthickness=0, border=0, command=searchCancel)
    cancelButton.pack(side='left')
    searchStringVar = StringVar()
    searchStringVar.trace("w", lambda name, index, mode, searchStringVar=searchStringVar: searchOnInput(searchStringVar))
    searchField = Entry(utilsFrame, textvariable=searchStringVar, border=1)
    searchField.pack(side='left', fill='x', expand=True)
    
    # Display all entries
    try:
		
        # Display Label Title, Username, Url
        Label(entriesFrame, text="Title", background="#edfaca").grid(row=0, column=0, sticky='w')
        Label(entriesFrame, text="Username", background="#edfaca").grid(row=0, column=1, sticky='w', padx=7)
        Label(entriesFrame, text="URL", background="#edfaca").grid(row=0, column=2, sticky='w', padx=7)
    
		# default row incrementation
        nr = 1
        
        for i in KP.entries:
            entriesTitleLabel = Label(entriesFrame, text=(str(i.title)), width=27, anchor="w", background="white", cursor="hand2")
            entriesUsernameLabel = Label(entriesFrame, text=(str(i.username)), width=27, anchor="w", background="white")
            entriesUrlLabel = Label(entriesFrame, text=(str(i.url)), anchor="w", background="white")
            entriesTitleLabel.uuid = str(i.uuid)
            entriesTitleLabel.guuid = "search"
            entriesTitleLabel.bind("<Button-1>", getEntry)
            entriesTitleLabel.grid(row=nr, column=0, sticky='w')
            entriesUsernameLabel.grid(row=nr, column=1, sticky='w', padx=7)
            entriesUrlLabel.grid(row=nr, column=2, sticky='w', padx=7)
            # row incrementation
            nr = nr + 1
            			
    # Manage 'NoneType' object has no attribute 'entries' error
    except:
        pass  
    
# Cancel Search entries
def searchCancel():
	
    # Display default entries list (root group)
    gUuid = str(KP.root_group.uuid)
    getEntries(gUuid)
    
# List entries on a targeted Keepass group (label click)
def getEntries(gUuid):
   
    resetUtilsBar()
    resetEntriesFrame()
      
    groupUuid = uuid.UUID(gUuid)

    # Find all entries of the group by his uuid
    kpEntries = KP.find_groups(uuid=groupUuid, first=True)

    # Display all entries of a group  
    try:
		# Change window name with the current group name
        root.title(kpEntries.name)
        
        # Display Label Title, Username, Url
        Label(entriesFrame, text="Title", background="#edfaca").grid(row=0, column=0, sticky='w')
        Label(entriesFrame, text="Username", background="#edfaca").grid(row=0, column=1, sticky='w', padx=7)
        Label(entriesFrame, text="URL", background="#edfaca").grid(row=0, column=2, sticky='w', padx=7)
    
		# default row incrementation
        nr = 1
        for i in kpEntries.entries:
            entriesTitleLabel = Label(entriesFrame, text=(str(i.title)), width=27, anchor="w", background="white", cursor="hand2")
            entriesUsernameLabel = Label(entriesFrame, text=(str(i.username)), width=27, anchor="w", background="white")
            entriesUrlLabel = Label(entriesFrame, text=(str(i.url)), anchor="w", background="white")
            entriesTitleLabel.uuid = str(i.uuid)
            entriesTitleLabel.guuid = gUuid
            entriesTitleLabel.bind("<Button-1>", getEntry)
            entriesTitleLabel.grid(row=nr, column=0, sticky='w')
            entriesUsernameLabel.grid(row=nr, column=1, sticky='w', padx=7)
            entriesUrlLabel.grid(row=nr, column=2, sticky='w', padx=7)
            # row incrementation
            nr = nr + 1
       
        
    # Manage 'NoneType' object has no attribute 'entries' error (if group has no entries)
    except:
        pass

def getEntry(self):

    def save(self, titleString, usernameString, passwordString, urlString, noteEntryField, gUuid):

        # mtime update
        self.touch(modify=True)
        # Save in history current Entry information (before updating new Entry)
        self.save_history()

        # Update the entry with new values
        self.title = titleString.get()
        self.username = usernameString.get()
        self.password = passwordString.get()
        self.url = urlString.get()
        self.notes = noteEntryField.get("1.0","end-1c")

        # Save database
        KP.save()
        
        #  Refresh the corresponding entries list
        if(gUuid == "search"):
            searchEntries()
        else:
            getEntries(gUuid)
            
        # Close window
        entryWindow.destroy()
        
    def delete(self):
        
        KP.delete_entry(self)
        KP.save()
        
        #  Refresh the corresponding entries list
        if(gUuid == "search"):
            searchEntries()
        else:
            getEntries(gUuid)
            
        # Close window
        entryWindow.destroy()       
        
    entryWindow = Tk()
    entryWindow.geometry("400x300")
    entryWindow.eval('tk::PlaceWindow . center')

    # Get Group uuid
    gUuid = self.widget.guuid

    # Get the entry uuid
    entryUuid = uuid.UUID(self.widget.uuid)

    kpEntry = KP.find_entries(uuid=entryUuid, first=True)

    entryWindow.title(kpEntry.title)
    entryWindow.config(background="white")
    
    # Entry title label + field
    titleEntryLabel = Label(entryWindow, text="Title :", anchor='w', width=10, padx=3, background="white")
    titleEntryLabel.grid(row=0, column=0, sticky='nw')
    titleString = StringVar(entryWindow, kpEntry.title)
    titleEntryField = Entry(entryWindow, textvariable=titleString)
    titleEntryField.grid(row=0, column=1, sticky='ew')

    # Entry username label + field
    usernameEntryLabel = Label(entryWindow, text="Username :", anchor='w', width=10, padx=3, background="white")
    usernameEntryLabel.grid(row=1, column=0, sticky='nw')
    usernameString = StringVar(entryWindow, kpEntry.username)
    usernameEntryField = Entry(entryWindow, textvariable=usernameString, bd=1)
    usernameEntryField.grid(row=1, column=1, sticky='ew')

    # Entry password label + field
    passwordEntryLabel = Label(entryWindow, text="Password :", anchor='w', width=10, padx=3, background="white")
    passwordEntryLabel.grid(row=2, column=0, sticky='nw')
    passwordString = StringVar(entryWindow, kpEntry.password)
    passwordEntryField = Entry(entryWindow, textvariable=passwordString, bd=1)
    passwordEntryField.grid(row=2, column=1, sticky='ew')

    # Entry url label + field
    urlEntryLabel = Label(entryWindow, text="Url :", anchor='w', width=10, padx=3, background="white")
    urlEntryLabel.grid(row=3, column=0, sticky='nw')
    urlString = StringVar(entryWindow, kpEntry.url)
    urlEntryField = Entry(entryWindow, textvariable=urlString, bd=1)
    urlEntryField.grid(row=3, column=1, sticky='ew')
    
    # Entry Note label + field
    noteEntryLabel = Label(entryWindow, text="Note :", anchor='w', width=10, padx=3, background="white")
    noteEntryLabel.grid(row=4, column=0, sticky='nw')
    noteString = StringVar(entryWindow, kpEntry.notes)
    noteEntryField = Text(entryWindow, height=14, border=1)
    noteEntryField.insert("1.0", noteString.get())
    noteEntryField.grid(row=4, column=1, sticky='nsew')

    # Frame button (Needed to align Save button and Delete button side by side, on the same row/column of the grid
    buttonFrame = Frame(entryWindow, background="white")
    buttonFrame.grid(row=5, column=1, sticky='se')
    
    # Save button
    buttonSaveEntry = Button(buttonFrame, text="Save", command=lambda:save(kpEntry, titleString, usernameString, passwordString, urlString, noteEntryField, gUuid))
    buttonSaveEntry.grid(row=0, column=0)
    
    # Delete button
    buttonDeleteEntry = Button(buttonFrame, text="Delete", command=lambda:delete(kpEntry))
    buttonDeleteEntry.grid(row=0, column=1)

    # Fill field
    entryWindow.grid_columnconfigure(1, weight=1)
    entryWindow.grid_rowconfigure(4, weight=1)
        
# Adjust scrollbar on frame size
def onFrameConfigure(self):
    self.configure(scrollregion=self.bbox("all"))


# DB Frame
dbFrame = Frame(root)

# Utils bar 
utilsFrame = Frame(root, background="white")
searchIcon = PhotoImage(file="icons/search.png")
cancelIcon = PhotoImage(file="icons/cancel.png")

# Left Canvas/Frame/Scrollbar (display groups)
# HACK : canvas need to be inside a frame to avoid any children widget of the canvas to overlap to the borderwidth 
rootGroupsFrame = Frame(root, background="white", highlightbackground="gray", borderwidth=1, highlightthickness=1)
groupsCanvas =  Canvas(rootGroupsFrame, width=200, background="white", borderwidth=0, highlightthickness=0)
groupsFrame = Frame(groupsCanvas, background="white")
groupsScrollbarY = Scrollbar(rootGroupsFrame, orient="vertical", command=groupsCanvas.yview, borderwidth=0, highlightthickness=0)
groupsScrollbarX = Scrollbar(rootGroupsFrame, orient="horizontal", command=groupsCanvas.xview, borderwidth=0, highlightthickness=0)

# Central Canvas/Frame/Scrollbar (display entries group)
# HACK : canvas need to be inside a frame to avoid any children widget of the canvas to overlap to the borderwidth 
rootEntriesFrame = Frame(root, background="white", highlightbackground="gray", borderwidth=1, highlightthickness=1)
entriesCanvas = Canvas(rootEntriesFrame, background="white", borderwidth=0, highlightthickness=0)
entriesFrame = Frame(entriesCanvas, background="white")
entriesScrollbarY = Scrollbar(rootEntriesFrame, orient="vertical", command=entriesCanvas.yview, borderwidth=0, highlightthickness=0)
entriesScrollbarX = Scrollbar(rootEntriesFrame, orient="horizontal", command=entriesCanvas.xview, borderwidth=0, highlightthickness=0)

# Create the Menubar
menubar = Menu(root)

# Menu File
mainMenu = Menu(menubar, tearoff = 0) 
menubar.add_cascade(label ='File', menu=mainMenu) 
mainMenu.add_command(label ='Open database', command=openDatabase)

# Display menubar
root.config(menu=menubar)

# Loop
root.mainloop()
