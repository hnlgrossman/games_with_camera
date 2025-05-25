from controller import ControllerTester

# Initialize controller tester with default Xbox 360 type
tester = ControllerTester(controller_type="xbox360")

def trigger_up():
    """Trigger up movement action"""
    tester.press_dpad_up()
    pass

def trigger_down():
    """Trigger down movement action"""
    tester.press_dpad_down()
    pass

def trigger_left():
    """Trigger left movement action"""
    tester.press_dpad_left()
    pass

def trigger_right():
    print("Trigger right")
    """Trigger right movement action"""
    tester.press_dpad_right()
    pass

# You can set controller type with:
# controller = Controller(controller_type="ds4")  # For PlayStation controller 