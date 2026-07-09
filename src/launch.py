import sys
import os

def ensure_admin_privileges():
    """Ensure script has admin rights on Windows (needed for sleep management)."""
    import ctypes
    
    if sys.platform != "win32":
        return
    
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return
    except Exception:
        return
    
    print("[INFO] Admin privileges required for sleep management. Requesting elevation...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def launch_proc(args):
    from log import enable_logging
    from utils import parse_args, init_instance
    from coc_bot import CoC_Bot
    
    parse_args(args.debug, args.id, args.gui, args.gui_port)
    init_instance(args.id)
    enable_logging(args.id)
    bot = CoC_Bot()
    bot.run()

def cmd_launch(args):
    import utils
    if utils.DISABLE_DEVICE_SLEEP: utils.disable_sleep()
    launch_proc(args)

def gui_launch(args):
    from multiprocessing import Process
    import utils
    from gui import init_gui, get_gui
    from copy import deepcopy
    import signal
    
    procs = {}
    pipe = init_gui(args.id)
    args.gui_port = get_gui().server_port
    
    if utils.DISABLE_DEVICE_SLEEP: Process(target=utils.disable_sleep).start()

    if args.id is not None:
        p = Process(target=launch_proc, args=(args,))
        p.start()
        procs[args.id] = p
    try:
        while True:
            data = pipe.recv()
            if data == -1: raise SystemExit
            action, id = data.get("action"), data.get("id")
            if action == "start":
                args_copy = deepcopy(args)
                args_copy.id = data.get("id")
                p = Process(target=launch_proc, args=(args_copy,))
                p.start()
                procs[id] = p
            elif action == "stop":
                p = procs.pop(id, None)
                if p and p.is_alive():
                    if sys.platform == "win32":
                        p.terminate()
                        try:
                            p.join(timeout=2)
                            if p.is_alive():
                                p.kill()
                                p.join()
                        except:
                            pass
                    else:
                        try:
                            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                        except:
                            pass
                        p.join()
    except (EOFError, KeyboardInterrupt, SystemExit):
        get_gui().stop()
        pipe.close()
        for p in procs.values():
            if p and p.is_alive():
                if sys.platform == "win32":
                    p.terminate()
                    try:
                        p.join(timeout=1)
                        if p.is_alive():
                            p.kill()
                    except:
                        pass
                else:
                    try:
                        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                    except:
                        pass
                    p.join()

def launch():
    import utils
    args = utils.parse_args()
    if args.gui: gui_launch(args)
    else: cmd_launch(args)
