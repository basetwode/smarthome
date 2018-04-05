from django.core.exceptions import ValidationError


def validate_rgb(color):
    return ValidationError(_('%(value)s is not an valid rbg value'),
                           params={'value': color}) if color < 0 or color > 255 else None


def validate_brightness(brightness):
    return ValidationError(_('%(value)s is not an valid brightness value'),
                           params={'value': brightness}) if brightness < 0 or brightness > 100 else None