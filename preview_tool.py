#!/usr/bin/python
from Tkinter import *
import FileDialog
import subprocess
from PIL import Image, ImageTk


class Preview_tool():
    """ a preview tool for the lvl_builder  """
    
    def __init__( self ):
        self.main_window = Tk()
        self.main_window.title("Preview tool")
        
        self.frames = {}
        self.labels = {}
        self.text_editor = 0
        
        
        self.create_widgets()
        self.place_widgets()
        self.create_key_response()
       
        # preload the template to guide users the syntax.
        fIn = open(".template.txt", "r")
        lines = fIn.readlines()
        for line in lines:
            self.text_editor.insert( CURRENT, line )
        
        self.main_window.mainloop()


    def create_widgets(self):
        """ create the widgets """
        # for menu 
        self.menu = Menu( self.main_window )
        self.menu.add_command( label="Load (ctl+o)", command=self.callback_open ) 
        self.menu.add_command( label="Save (ctl+s)", command=self.callback_save )
        self.menu.add_command( label="Plot (ctl+p)", command=self.callback_plot )
        self.menu.add_command( label="Exit", command=self.main_window.quit ) 
        self.main_window.config(menu=self.menu)

        # for frames
        self.frames['text'] = Frame( self.main_window ,  bd=1)
        self.frames['display'] = Frame( self.main_window, bd=1 )
         
        # for Text widgets
        self.text_editor = Text( self.frames['text'], height = 10 )

        # for Label widgets
        self.labels['figure'] = Label( self.frames['display'] );

        # add the starting figure 
        image = Image.open("start_figure.ps")
        self.photo = ImageTk.PhotoImage( image.rotate(270) )
        self.labels['figure'].configure(image = self.photo)
        self.labels['figure'].image = self.photo # keep a ref

    def place_widgets(self):
        """ place the widget """   
        self.frames['text'].pack(fill=BOTH, expand=True, side=BOTTOM)
        self.frames['display'].pack( fill=BOTH, expand=True, side=TOP)
         
        self.text_editor.pack(  fill=BOTH, expand=True )
        self.labels['figure'].pack( fill=BOTH, expand=True )

    
    def forget_widgets(self):
        # currently not in use.
        """ forget widget's previous placement """   
        self.frames['text'].pack_forget()
        self.frames['display'].pack_forget()
        self.text_editor.pack_forget()
        self.labels['figure'].pack_forget()



    ##### response methods ######    
    def callback_open(self,event=0):
        """ call FileDialog, to get the filename, 
        then we load the file into the Text object (text_editor)"""
        
        try:
            dialog = FileDialog.FileDialog(self.main_window)    
            filename = dialog.go( )
            readIn = open(filename,'r')
            lines = readIn.readlines()
            self.text_editor.delete( "1.0", END  )
            for line in lines:
                self.text_editor.insert( CURRENT, line )
            readIn.close()
        except:
            pass



    def callback_save(self,event=0):
        """ call FileDialog, to get the filename, 
        then we save the content in the Text object (text_editor) to file"""
        
        outStr= self.text_editor.get(1.0, END)
       
        try:
            dialog = FileDialog.FileDialog(self.main_window)    
            filename = dialog.go( )
            writeOut = open(filename,'w')
            writeOut.write( outStr )
            writeOut.close()
        except:
            pass
        
        
    def callback_plot(self,event=0):
        """ write out to a temp file, then use lvl_builder to plot according 
        the instruction in the temp file. we will get a figure. Put the figure 
        into the Label widget.
        """
        outStr= self.text_editor.get(1.0, END)
        writeOut = open(".temp.txt",'w')
        writeOut.write( outStr )
        writeOut.close()

        # call the lvl_builder to plot
        cmd  = "./lvl_builder.py .temp.txt previewParameter.txt"

        p = subprocess.Popen( cmd, shell=True,  stdout=subprocess.PIPE )
        (result,err) = p.communicate() 

        if( result=='' ):
            """ good case """
            image = Image.open("output.ps")
        else:
            """ bad case """
            # we just show the empty figure.
            image = Image.open("start_figure.ps")
            
        #print( "image size = ", image.size )
        self.photo = ImageTk.PhotoImage( image.rotate(270) )
        self.labels['figure'].configure(image = self.photo)
        self.labels['figure'].image = self.photo # keep a ref
       
        

    def create_key_response(self):
        self.main_window.bind("<Control-o>", self.callback_open )
        self.main_window.bind("<Control-s>", self.callback_save )
        self.main_window.bind("<Control-p>", self.callback_plot )
        pass




if __name__ == '__main__':

     gui = Preview_tool()
