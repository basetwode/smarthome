from Application.settings import INSTANCE_TYPE


def setup():
    if INSTANCE_TYPE == 'CLIENT':
        setup_led()


led_pwm = None


def setup_led():
    global led_pwm
    import Adafruit_PCA9685
    led_pwm = Adafruit_PCA9685.PCA9685()
    led_pwm.set_pwm_freq(100)
