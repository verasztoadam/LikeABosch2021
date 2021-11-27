from gui import GUI

if __name__ == '__main__':
    try:
        gui = GUI()
        while True:
            gui.update()
    except KeyboardInterrupt:
        print("Script terminated")
