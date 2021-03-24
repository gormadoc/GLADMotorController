from PyQt5 import QtWidgets


class ReadOnlyDial(QtWidgets.QDial):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyDial, self).__init__(*args, **kwargs)
        
        
    def mousePressEvent(self, event):
        pass
    
    def mouseReleaseEvent(self, event):
        pass
    
    def mouseMoveEvent(self, event):
        pass
    
    def keyPressEvent(self, event):
        pass
    
    def keyReleaseEvent(self, event):
        pass