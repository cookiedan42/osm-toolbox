import osmium
import os

class PBFwriter(osmium.SimpleWriter):
    '''
    wrapper around osmium SimpleWriter
    adds context manager --> with writer as w
    add overwriting existing target file as default behaviour
    '''

    def __init__(self,destPath:str,overwrite:bool=True):
        if overwrite and os.path.exists(destPath):
            os.remove(destPath)
        super().__init__(destPath)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()