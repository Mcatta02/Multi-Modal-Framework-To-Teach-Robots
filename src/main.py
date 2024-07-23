
# ----------------------
# |        MAIN        |
# ----------------------

def main():
    # open first ui (recording)
    from ui import UI as UI_1
    ui = UI_1()
    ui.root.mainloop()

    # wait for first ui to close
    from time import sleep
    sleep(0.5)

    # check if the first ui was not closed manually
    if not ui.closing:
        # open second ui (chatbot)
        from conversational_ui import UI as UI_2
        ui = UI_2(chat=True)
        ui.root.mainloop()

        # wait for second ui to close
        from time import sleep
        sleep(0.5)

        # check for close
        if ui.closing:
            return
        
        # run a garbage collection
        import gc
        gc.collect()

        # check for retry
        if ui.retrying:
            main()

if __name__ == '__main__':
    main()
