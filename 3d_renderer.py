

class Mesh:
    def __init__(self) -> None:
        pass




class Projection:
    def __init__(self) -> None:
        pass





class Display:
    def __init__(self, size=None, bottom_bar=0) -> None:
        from shutil import get_terminal_size
        self.get_terminal_size = get_terminal_size
        self.width, self.height = Display.get_screen_size(size, bottom_bar)
        pass


    def get_screen_size(self,size=None, bottom_bar=0):
        """size - None/tuple (int, int)/list [int, int]
           bottom_bar - int - bottom_bar >= 0"""
        if size == None:
            w, h = self.get_terminal_size()
            # When printing a really long and complex string, bug character may appear from nowhere
            # so -3 in case such thing happens
            w = w // 2 - 3
            h = h - 3 - bottom_bar
            return w, h
        elif size[0] == None:
            w, _ = self.get_terminal_size()
            w = w // 2 - 3
            h = size[1] - 3 - bottom_bar
            return w, h
        elif size[1] == None:
            _, h = self.get_terminal_size()
            w = size[0] // 2 - 3
            h = h - 3 - bottom_bar
            return w, h
    

    def draw(self, frame, space="  "):
        """frame - dict {y:{x:str}}"""
        output = []
        for y in range(self.height):
            for x in range(self.width):
                if x not in frame[y]:
                    output.append(space)
                else:
                    output.append(frame[y][x])
            output.append("\n")
        print("".join(output))




display = Display()
while True:
    pass