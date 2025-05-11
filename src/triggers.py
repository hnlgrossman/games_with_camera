from controller import ControllerTester

# Initialize controller tester with default Xbox 360 type
tester = ControllerTester(controller_type="xbox360")

def trigger_up():
    """Trigger up movement action"""
    tester.press_dpad_up()

def trigger_down():
    """Trigger down movement action"""
    tester.press_dpad_down()

def trigger_left():
    """Trigger left movement action"""
    tester.press_dpad_left()

def trigger_right():
    """Trigger right movement action"""
    tester.press_dpad_rsight()

# You can set controller type with:
# controller = Controller(controller_type="ds4")  # For PlayStation controller 