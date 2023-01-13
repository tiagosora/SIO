from playingArea.logging import LogReader

filename = "bingolog-2023-01-09_18-29-37" + ".txt"

def main():
    lr = LogReader(filename)

    lr.displayLogs()
    print(lr.verifyLogOrder())

if __name__ == '__main__':
    main()