from __future__ import print_function
from scriptengine import * #If codesys must import this module, this has to be here
import os

#These guids serve as descriptors of existing objects inside of the project
GUIDS = {
    '8753fe6f-4a22-4320-8103-e553c4fc8e04' : 'Project Settings',
    '225bfe47-7336-4dbc-9419-4105a7c831fa' : 'Device',
    '40b404f9-e5dc-42c6-907f-c89f4a517386' : 'Plc Logic',
    '639b491f-5557-464c-af91-1471bac9f549' : 'Application',
    'adb5cb65-8e1d-4a00-b70a-375ea27582f3' : 'Library Manager',
    'ae1de277-a207-4a28-9efb-456c06bd52f3' : 'Task Configuration',
    '98a2708a-9b18-4f31-82ed-a1465b24fa2d' : 'Task',
    'ffbfa93a-b94d-45fc-a329-229860183b1d' : 'Global variable set',
    '2db5746d-d284-4425-9f7f-2663a34b0ebc' : 'data type',
    '8ac092e5-3128-4e26-9e7e-11016c6684f2' : 'action',
    '738bea1e-99bb-4f04-90bb-a7a567e74e3a' : 'Folder',
    '6f9dac99-8de1-4efc-8465-68ac443b7d08' : 'POU',
    '085afe48-c5d8-4ea5-ab0d-b35701fa6009' : 'Project Information',
    '8e687a04-7ca7-42d3-be06-fcbda676c5ef' : '__VisualizationStyle',
    '413e2a7d-adb1-4d2c-be29-6ae6e4fab820' : 'Call to POU'
}

def saveAndExport(project, arg):
    """Saves and exports the project to the xml type provided in the argument
    Args : 
        '-p', '-plcopenxml' -> PLC OpenXml format
        '-n', '--nativexml' -> Codesys native format
    The xml file is saved as the project name in the same folder as the .project file"""

    if project == None:
        raise Exception('Project argument invalid')
    
    #Save project if unsave
    if project.dirty:
        project.save()

    #Calculate the projects name based on path
    proj_name = os.path.basename(project.path).split('.')[0]

    #Calculate the new file name
    fpath = os.path.join(os.path.dirname(project.path), proj_name + '.xml')

    if arg in ['-p', '--plcopenxml']:
        #Export to PLCOpenXML
        project.export_xml(project.get_children(recursive=True), path=fpath, recursive=True, export_folder_structure=True)
        #Return the saved file path
        return fpath

    elif arg in ['-n', '--nativexml']:
        #Export to native codesys xml
        project.export_native(objects=project.get_children(recursive=True), destination=fpath, recursive=True, profile_name=None, reporter=None)
        #Return the saved file path
        return fpath
    #If no argument passed
    raise Exception('Invalid format argument')

def createFolder(root, name):
    """Creates a folder inside of the CODESYS IDE and returns its handler class. If the folder already
    exists then it returns its handler. If there is multiple folders with the same name it returns the first"""
    
    #Check if it exists first
    print('Creating folder ', name)
    folders = root.find(name, recursive = True)
    for folder in folders:
        if folder.is_folder:
            print('Folder already exists')
            return folder
    else:
        #Folder doesnt exists, create a new folder
        root.create_folder(name)
    
    #Find the newly created folder and return its handler (root.create_folder doesnt return the handler unfortunately)
    folders = root.find(name, recursive = True)
    for folder in folders:
        if folder.is_folder:
            return folder
    else:
        raise Exception('Folder {1} couldnt be created'.format(name))

def deleteTextualObject(text, decl=False):
    if decl == True:
        for lineno in range(1, text.linecount):
            text.remove(lineno, 0, len(text.get_line(lineno)))
    else:
        for lineno in range(0, text.linecount):
            text.remove(lineno, 0, len(text.get_line(lineno)))

def updatePou(existingPou, newPou):
    #Update the pou
    try:
        #Remove everything after the pou name in the declaration
        deleteTextualObject(existingPou.textual_declaration, decl=True)

        #Remove all code
        deleteTextualObject(existingPou.textual_implementation)

        #Write the textual declaration
        existingPou.textual_declaration.insert(1, 0, newPou.get('declaration', ''))

        #Write the code
        existingPou.textual_implementation.insert(0,0, newPou.get('code', ''))

    except Exception as e:
        print('Update failed: ', e)

def updateDut(existingDt, newDt):
    #Update the dt
    try:
        #Remove everything in the declaration
        deleteTextualObject(existingDt.textual_declaration)

        #Write the textual declaration
        existingDt.textual_declaration.insert(1, 0, newDt.get('declaration', ''))

    except Exception as e:
        print('Update failed: ', e)

def createDut(root, dt):
    """Creates a datatype inside of the root codesys object(folder). Takes in a dictionary in correct format"""

    #Create the pou
    try:
        crpFct = root.create_dut(dt.get('name'))
            
        #Remove all text from the textual declaration
        deleteTextualObject(crpFct.textual_declaration)

        #Write the textual declaration
        crpFct.textual_declaration.insert(1, 0, dt.get('declaration', ''))

    except Exception as e:
        print('Import failed: ', e)

def createPou(root, pou):
    """Creates a pou inside of the root codesys object(folder). Takes in a dictionary in correct format"""

    #Create the pou
    try:
        if pou.get('type') == 'Function':
            crpFct = root.create_pou(name=pou.get('name'), type=PouType.Function, return_type=pou.get('returnType'))
        elif pou.get('type') == 'Program':
            crpFct = root.create_pou(name=pou.get('name'), type=PouType.Program)
        elif pou.get('type') == 'Function block':
            crpFct = root.create_pou(name=pou.get('name'), type=PouType.FunctionBlock)
            
        #Remove everything after the function name
        deleteTextualObject(crpFct.textual_declaration, decl=True)

        #Write the textual declaration
        crpFct.textual_declaration.insert(1, 0, pou.get('declaration', ''))

        #This writes code
        crpFct.textual_implementation.insert(0,0, pou.get('code', ''))

    except Exception as e:
        print('Import failed: ', e)
